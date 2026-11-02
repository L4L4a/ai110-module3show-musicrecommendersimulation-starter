"""
Command line runner for the Music Recommender Simulation.

Run from the project root with:  python -m src.main
"""

from src.recommender import load_songs, recommend_songs

PROFILES = {
    "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.90},
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.35},
    "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.92},
    # Adversarial: the saddest genre in the catalog paired with an energy level no sad song has.
    "Adversarial (sad blues at max energy)": {"genre": "blues", "mood": "sad", "energy": 0.95},
}


def main() -> None:
    songs = load_songs("data/songs.csv")

    for name, user_prefs in PROFILES.items():
        print(f"\n=== {name} ===")
        print(f"Profile: genre={user_prefs['genre']}, mood={user_prefs['mood']}, energy={user_prefs['energy']}\n")
        for rank, (song, score, explanation) in enumerate(recommend_songs(user_prefs, songs, k=5), start=1):
            print(f"{rank}. {song['title']} by {song['artist']} - Score: {score:.2f}")
            print(f"   Because: {explanation}")


if __name__ == "__main__":
    main()
