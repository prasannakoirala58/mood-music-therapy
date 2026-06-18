"""
pipeline.py

Main entry point — conversational CLI mood-to-music journey.

Flow:
  1. Load labeled dataset on startup
  2. Ask user how they feel
  3. Detect emotion via OpenAI
  4. Run ISO recommender → 3 songs
  5. Print formatted output with Spotify links
  6. Ask "how are you feeling now?" — loop with fresh songs if needed
  7. Exit when user is happy or types 'quit'
"""

import pandas as pd
from mood_parser import parse_mood
from recommender import recommend


DATASET_PATH = "data/processed/dataset_labeled.csv"

BANNER = """
╔══════════════════════════════════════════════╗
║         🎵  Music Mood Therapy  🎵            ║
║  Tell me how you feel. I'll find your path.  ║
╚══════════════════════════════════════════════╝
"""

SEPARATOR = "─" * 50

SONG_LABELS = [
    "MATCHING YOUR MOOD",
    "THE BRIDGE",
    "YOUR DESTINATION",
]

HAPPY_TRIGGERS = {"happy", "great", "good", "better", "amazing", "awesome", "fantastic", "fine"}


def format_song(song: dict, label: str, index: int) -> str:
    # TODO: return formatted string block for one song
    pass


def print_recommendations(emotion: str, songs: list[dict]) -> None:
    # TODO: print detected emotion + 3 formatted songs
    pass


def is_happy_response(text: str) -> bool:
    # TODO: check if user's response indicates they feel better
    pass


def run() -> None:
    # TODO: main loop — load data, greet, detect mood, recommend, loop
    pass


if __name__ == "__main__":
    run()
