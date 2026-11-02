import csv
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional, Tuple

GENRE_WEIGHT = 2.0
MOOD_WEIGHT = 1.0
ENERGY_WEIGHT = 1.0

# Optional "extra attribute" terms. Each only fires when the user profile asks for it,
# and each contributes at most EXTRA_WEIGHT, so the three core terms stay dominant.
EXTRA_WEIGHT = 0.5
NUMERIC_EXTRAS = {
    # profile key: song column
    "target_acousticness": "acousticness",
    "target_danceability": "danceability",
    "target_instrumentalness": "instrumentalness",
    "target_liveness": "liveness",
}

# Diversity re-ranking penalties (points subtracted per earlier pick in the top-k).
ARTIST_REPEAT_PENALTY = 1.0
GENRE_REPEAT_PENALTY = 0.5

INT_FIELDS = {"id", "tempo_bpm", "popularity", "release_decade"}
FLOAT_FIELDS = {"energy", "valence", "danceability", "acousticness", "instrumentalness", "liveness"}


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    popularity: int = 50
    release_decade: int = 2010
    mood_tag: str = ""
    instrumentalness: float = 0.0
    liveness: float = 0.0


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


def score_song(
    user_prefs: Dict,
    song: Dict,
    weights: Optional[Dict[str, float]] = None,
) -> Tuple[float, List[str]]:
    """
    Scores one song against user preferences. Returns (score, reasons), where
    reasons lists only the scoring terms that fired, with their exact contribution.

    With the default weights this is the baseline rule:
      genre match +2.0, mood match +1.0, energy similarity 1 - |song - target|.
    Optional profile keys (target_popularity, target_decade, mood_tag and the
    target_* numeric keys) add up to EXTRA_WEIGHT each.
    """
    w = {"genre": GENRE_WEIGHT, "mood": MOOD_WEIGHT, "energy": ENERGY_WEIGHT}
    if weights:
        w.update(weights)

    score = 0.0
    reasons: List[str] = []

    if song["genre"] == user_prefs.get("genre"):
        score += w["genre"]
        reasons.append(f"genre match (+{w['genre']:.1f})")

    if song["mood"] == user_prefs.get("mood"):
        score += w["mood"]
        reasons.append(f"mood match (+{w['mood']:.1f})")

    if "energy" in user_prefs:
        energy_sim = w["energy"] * (1 - abs(float(song["energy"]) - float(user_prefs["energy"])))
        score += energy_sim
        reasons.append(f"energy similarity (+{energy_sim:.2f})")

    # --- extra attributes (only when the profile provides them) ---
    if "mood_tag" in user_prefs and song.get("mood_tag") == user_prefs["mood_tag"]:
        score += EXTRA_WEIGHT
        reasons.append(f"mood tag '{song['mood_tag']}' match (+{EXTRA_WEIGHT:.2f})")

    if "target_decade" in user_prefs and song.get("release_decade") == user_prefs["target_decade"]:
        score += EXTRA_WEIGHT
        reasons.append(f"{song['release_decade']}s release (+{EXTRA_WEIGHT:.2f})")

    if "target_popularity" in user_prefs and "popularity" in song:
        pop_sim = EXTRA_WEIGHT * (1 - abs(song["popularity"] - user_prefs["target_popularity"]) / 100)
        score += pop_sim
        reasons.append(f"popularity similarity (+{pop_sim:.2f})")

    for pref_key, column in NUMERIC_EXTRAS.items():
        if pref_key in user_prefs and column in song:
            sim = EXTRA_WEIGHT * (1 - abs(float(song[column]) - float(user_prefs[pref_key])))
            score += sim
            reasons.append(f"{column} similarity (+{sim:.2f})")

    return score, reasons


# ---------------------------------------------------------------------------
# Strategy pattern: interchangeable ranking modes behind one interface.
# ---------------------------------------------------------------------------

class RankingStrategy(ABC):
    """Common interface: every ranking mode turns (user_prefs, song) into (score, reasons)."""

    name: str = ""

    @abstractmethod
    def score(self, user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
        ...


class BalancedStrategy(RankingStrategy):
    """Baseline rule: genre +2.0, mood +1.0, energy similarity up to +1.0."""
    name = "balanced"

    def score(self, user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
        return score_song(user_prefs, song)


class GenreFirstStrategy(RankingStrategy):
    """Genre dominates: a genre match is worth more than every other term combined."""
    name = "genre-first"

    def score(self, user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
        return score_song(user_prefs, song, {"genre": 4.0, "mood": 1.0, "energy": 1.0})


class MoodFirstStrategy(RankingStrategy):
    """Mood dominates; genre is demoted to a minor bonus."""
    name = "mood-first"

    def score(self, user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
        return score_song(user_prefs, song, {"genre": 1.0, "mood": 3.0, "energy": 1.0})


class EnergySimilarityStrategy(RankingStrategy):
    """Energy closeness dominates; genre and mood are only small tie-breaking bonuses."""
    name = "energy-similarity"

    def score(self, user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
        return score_song(user_prefs, song, {"genre": 0.5, "mood": 0.5, "energy": 3.0})


STRATEGIES: Dict[str, RankingStrategy] = {
    s.name: s
    for s in (BalancedStrategy(), GenreFirstStrategy(), MoodFirstStrategy(), EnergySimilarityStrategy())
}


def get_strategy(name: str) -> RankingStrategy:
    try:
        return STRATEGIES[name]
    except KeyError:
        raise ValueError(f"unknown ranking mode '{name}'; choose from {sorted(STRATEGIES)}")


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    @staticmethod
    def _prefs(user: UserProfile) -> Dict:
        return {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
        }

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        prefs = self._prefs(user)
        ranked = sorted(
            self.songs,
            key=lambda song: score_song(prefs, asdict(song))[0],
            reverse=True,
        )
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        _, reasons = score_song(self._prefs(user), asdict(song))
        return ", ".join(reasons) if reasons else "no scoring terms matched"


def load_songs(csv_path: str) -> List[Dict]:
    """Loads songs from a CSV file, converting numeric columns to numbers."""
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for key in INT_FIELDS & row.keys():
                row[key] = int(row[key])
            for key in FLOAT_FIELDS & row.keys():
                row[key] = float(row[key])
            songs.append(row)
    return songs


def _diversify(scored: List[Tuple[Dict, float, List[str]]], k: int) -> List[Tuple[Dict, float, List[str]]]:
    """
    Greedy re-ranking: repeatedly pick the best remaining song after subtracting
    a penalty for each already-selected song by the same artist (-1.0) or in the
    same genre (-0.5). Penalties are recorded in the reasons.
    """
    remaining = list(scored)
    picked: List[Tuple[Dict, float, List[str]]] = []
    while remaining and len(picked) < k:
        best = None
        for song, score, reasons in remaining:
            artist_hits = sum(1 for p, _, _ in picked if p["artist"] == song["artist"])
            genre_hits = sum(1 for p, _, _ in picked if p["genre"] == song["genre"])
            penalty = artist_hits * ARTIST_REPEAT_PENALTY + genre_hits * GENRE_REPEAT_PENALTY
            adjusted_reasons = list(reasons)
            if artist_hits:
                adjusted_reasons.append(f"artist repeat (-{artist_hits * ARTIST_REPEAT_PENALTY:.1f})")
            if genre_hits:
                adjusted_reasons.append(f"genre repeat (-{genre_hits * GENRE_REPEAT_PENALTY:.1f})")
            candidate = (song, score - penalty, adjusted_reasons)
            if best is None or candidate[1] > best[1]:
                best = candidate
        picked.append(best)
        remaining = [r for r in remaining if r[0] is not best[0]]
    return picked


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    strategy: Optional[RankingStrategy] = None,
    diversity: bool = False,
) -> List[Tuple[Dict, float, str]]:
    """
    Scores every song with the chosen strategy (default: balanced), sorts by score
    descending (ties keep catalog order) and returns the top k as
    (song_dict, score, explanation). With diversity=True the top k is re-ranked
    with artist/genre repetition penalties.
    """
    strategy = strategy or BalancedStrategy()
    scored = []
    for song in songs:
        score, reasons = strategy.score(user_prefs, song)
        scored.append((song, score, reasons))
    scored.sort(key=lambda item: item[1], reverse=True)
    top = _diversify(scored, k) if diversity else scored[:k]
    return [
        (song, score, ", ".join(reasons) if reasons else "no scoring terms matched")
        for song, score, reasons in top
    ]
