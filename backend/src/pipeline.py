"""
pipeline.py

Main entry point — conversational CLI mood-to-music journey.

Run with:  uv run python src/pipeline.py
       or: make run  (from project root)
"""

import sys
import pandas as pd
from pathlib import Path
from mood_parser import parse_mood
from recommender import recommend

DATASET_PATH = Path("data/processed/dataset_labeled.csv")

BANNER = """
╔══════════════════════════════════════════════════╗
║          🎵  Music Mood Therapy  🎵               ║
║   Tell me how you feel. I'll find your path.    ║
╚══════════════════════════════════════════════════╝
"""

SEP = "─" * 54

SONG_LABELS = ["MATCHING YOUR MOOD", "THE BRIDGE", "YOUR DESTINATION"]

POSITIVE_WORDS = {
    "good", "great", "better", "much better", "amazing", "awesome",
    "happy", "fantastic", "fine", "wonderful", "yes", "yeah", "yep",
    "lifted", "lighter", "nice", "improved", "refreshed",
}


def is_feeling_better(text: str) -> bool:
    lowered = text.lower().strip()
    return any(word in lowered for word in POSITIVE_WORDS)


def print_songs(emotion: str, songs: list[dict]) -> None:
    print(f"\n  Detected emotion: {emotion}")
    print(f"\n  Here's your journey to a better place:\n")
    print(SEP)

    for song, label in zip(songs, SONG_LABELS):
        print(f"\n  {label}")
        print(f"  {song['track_name']}")
        print(f"  {song['artists']}")
        print(f"  Valence: {song['valence']}  |  Energy: {song['energy']}")
        print(f"  {song['spotify_url']}")

    print(f"\n{SEP}")


def run() -> None:
    print(BANNER)

    if not DATASET_PATH.exists():
        print("  Error: labeled dataset not found.")
        print("  Run 'make train' first to set up the data pipeline.")
        sys.exit(1)

    print("  Loading song database...", end=" ", flush=True)
    df = pd.read_csv(DATASET_PATH)
    print(f"done  ({len(df):,} songs)\n")

    while True:
        print("  How are you feeling right now?")
        print("  (type 'quit' to exit)\n")

        user_input = input("  > ").strip()

        if user_input.lower() in {"quit", "exit", "q"}:
            print("\n  Take care. Come back whenever you need it. 🎵\n")
            break

        if not user_input:
            print("\n  Tell me a bit more about how you're feeling.\n")
            continue

        print("\n  Detecting your mood...", end=" ", flush=True)
        emotion = parse_mood(user_input)
        songs = recommend(emotion, df)
        print("done\n")

        print_songs(emotion, songs)

        print("\n  Listen through them in order.")
        print("  How are you feeling now?\n")
        follow_up = input("  > ").strip()

        if is_feeling_better(follow_up):
            print("\n  Glad to hear it. Music has a way of doing that. 🎵\n")
            print("  Want to go again? How are you feeling?\n")
            continue

        # User still not feeling great — give them another set
        print("\n  Let's try another set.\n")
        print("  Detecting your mood...", end=" ", flush=True)
        emotion2 = parse_mood(follow_up)
        songs2 = recommend(emotion2, df)
        print("done\n")

        print_songs(emotion2, songs2)
        print("\n  Take your time with these. 🎵\n")


if __name__ == "__main__":
    run()
