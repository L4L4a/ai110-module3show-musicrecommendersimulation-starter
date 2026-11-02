from src.recommender import Song, UserProfile, Recommender

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_score_song_returns_numeric_score_and_reasons_for_every_song():
    from src.recommender import load_songs, score_song

    prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    for song in load_songs("data/songs.csv"):
        score, reasons = score_song(prefs, song)
        assert isinstance(score, float)
        assert isinstance(reasons, list) and all(isinstance(r, str) for r in reasons)


def test_strategies_change_the_ranking():
    from src.recommender import STRATEGIES, load_songs, recommend_songs

    songs = load_songs("data/songs.csv")
    prefs = {"genre": "rock", "mood": "chill", "energy": 0.3}
    top = {name: recommend_songs(prefs, songs, k=1, strategy=s)[0][0]["title"] for name, s in STRATEGIES.items()}
    assert top["genre-first"] == "Storm Runner"          # the only rock song wins on genre alone
    assert top["mood-first"] != top["genre-first"]       # a chill song wins when mood leads


def test_diversity_penalty_demotes_repeated_artist():
    from src.recommender import load_songs, recommend_songs

    songs = load_songs("data/songs.csv")
    prefs = {"genre": "lofi", "mood": "chill", "energy": 0.35}
    plain = [s["title"] for s, _, _ in recommend_songs(prefs, songs, k=3)]
    diverse = [s["title"] for s, _, _ in recommend_songs(prefs, songs, k=3, diversity=True)]
    assert "Focus Flow" in plain and "Focus Flow" not in diverse
