"""
Command line runner for the Music Recommender Simulation.

Run from the project root, for example:
  python -m src.main                                  # all profiles, balanced mode, table
  python -m src.main --mode mood-first --diversity
  python -m src.main --profile "Chill Lofi" --mode all
  python -m src.main --basic --plain                  # baseline 3-term scoring, plain text
"""

import argparse
from typing import Dict, List

from tabulate import tabulate

from src.recommender import STRATEGIES, get_strategy, load_songs, recommend_songs

# Core preferences (genre / mood / energy) plus optional extra-attribute preferences.
PROFILES: Dict[str, Dict] = {
    "High-Energy Pop": {
        "genre": "pop", "mood": "happy", "energy": 0.90,
        "mood_tag": "uplifting", "target_decade": 2020, "target_popularity": 80,
        "target_danceability": 0.85,
    },
    "Chill Lofi": {
        "genre": "lofi", "mood": "chill", "energy": 0.35,
        "mood_tag": "cozy", "target_decade": 2020, "target_popularity": 55,
        "target_acousticness": 0.80, "target_instrumentalness": 0.60,
    },
    "Deep Intense Rock": {
        "genre": "rock", "mood": "intense", "energy": 0.92,
        "mood_tag": "aggressive", "target_decade": 2010, "target_popularity": 60,
        "target_liveness": 0.40,
    },
    # Adversarial: the saddest genre in the catalog paired with an energy level no sad song has,
    # and a "gritty 1970s" taste that contradicts the high-energy, low-acousticness targets.
    "Adversarial (sad blues at max energy)": {
        "genre": "blues", "mood": "sad", "energy": 0.95,
        "mood_tag": "gritty", "target_decade": 1970, "target_popularity": 90,
        "target_acousticness": 0.10,
    },
}

CORE_KEYS = ("genre", "mood", "energy")


def format_results(results, as_table: bool) -> str:
    if as_table:
        rows = [
            [rank, song["title"], song["artist"], f"{score:.2f}", explanation]
            for rank, (song, score, explanation) in enumerate(results, start=1)
        ]
        return tabulate(rows, headers=["Rank", "Title", "Artist", "Score", "Reasons"], tablefmt="github")
    lines: List[str] = []
    for rank, (song, score, explanation) in enumerate(results, start=1):
        lines.append(f"{rank}. {song['title']} by {song['artist']} - Score: {score:.2f}")
        lines.append(f"   Because: {explanation}")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Music Recommender Simulation")
    parser.add_argument("--mode", default="balanced", choices=sorted(STRATEGIES) + ["all"],
                        help="ranking strategy (default: balanced); 'all' runs every mode")
    parser.add_argument("--profile", default="all",
                        help="profile name (or unique substring); default: all profiles")
    parser.add_argument("--diversity", action="store_true",
                        help="re-rank the top k with artist/genre repetition penalties")
    parser.add_argument("--basic", action="store_true",
                        help="ignore extra-attribute preferences; use only genre/mood/energy")
    parser.add_argument("--plain", action="store_true", help="print plain text instead of a table")
    parser.add_argument("-k", type=int, default=5, help="number of recommendations (default: 5)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    songs = load_songs("data/songs.csv")

    profiles = {n: p for n, p in PROFILES.items() if args.profile == "all" or args.profile.lower() in n.lower()}
    if not profiles:
        raise SystemExit(f"no profile matches '{args.profile}'; choose from {list(PROFILES)}")
    modes = sorted(STRATEGIES) if args.mode == "all" else [args.mode]

    for name, prefs in profiles.items():
        if args.basic:
            prefs = {key: prefs[key] for key in CORE_KEYS}
        for mode in modes:
            label = f"{name} | mode={mode} | diversity={'on' if args.diversity else 'off'}"
            print(f"\n=== {label} ===")
            print("Profile: " + ", ".join(f"{key}={value}" for key, value in prefs.items()) + "\n")
            results = recommend_songs(prefs, songs, k=args.k, strategy=get_strategy(mode), diversity=args.diversity)
            print(format_results(results, as_table=not args.plain))


if __name__ == "__main__":
    main()
