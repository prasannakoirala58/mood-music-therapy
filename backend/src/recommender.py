"""
recommender.py

ISO Principle recommendation engine.

Given a detected emotion, calculates 3 waypoints through Russell's Circumplex
Model from the user's current emotional state toward the target (Happy).
Finds the nearest song in the labeled dataset to each waypoint using
Euclidean distance in (valence, energy) space.

Returns 3 songs — each a dict with:
  track_name, artists, emotion, valence, energy, track_id, spotify_url
"""

import pandas as pd
import numpy as np


TARGET_EMOTION = "Happy"
TARGET_V, TARGET_E = 0.80, 0.80

# Emotion → (valence, energy) coordinates in Russell's Circumplex Model
EMOTION_COORDS: dict[str, tuple[float, float]] = {
    "Happy":    (0.80, 0.80),
    "Surprise": (0.60, 0.85),
    "Angry":    (0.20, 0.80),
    "Fear":     (0.20, 0.60),
    "Disgust":  (0.15, 0.50),
    "Sad":      (0.20, 0.20),
}


def build_spotify_url(track_id: str) -> str:
    return f"https://open.spotify.com/track/{track_id}"


def find_nearest_song(df: pd.DataFrame, v_target: float, e_target: float, exclude_ids: list) -> pd.Series:
    # TODO: filter excluded, compute Euclidean distance, return closest row
    pass


def recommend(emotion: str, df: pd.DataFrame) -> list[dict]:
    # TODO: compute 3 waypoints, call find_nearest_song for each, build result dicts
    pass


if __name__ == "__main__":
    df = pd.read_csv("data/processed/dataset_labeled.csv")
    songs = recommend("Sad", df)
    for i, song in enumerate(songs, 1):
        print(f"\nSong {i}: {song['track_name']} — {song['artists']}")
        print(f"  Emotion: {song['emotion']} | Valence: {song['valence']:.2f} | Energy: {song['energy']:.2f}")
        print(f"  {song['spotify_url']}")
