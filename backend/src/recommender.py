"""
recommender.py

ISO Principle recommendation engine.

Given a detected emotion, calculates 3 waypoints through Russell's Circumplex
Model from the user's current emotional state toward the target (Happy).
Finds the nearest song in the labeled dataset to each waypoint using
Euclidean distance in (valence, energy) space.

Returns 3 song dicts — one per waypoint:
  track_name, artists, emotion, valence, energy, track_id, spotify_url
"""

import numpy as np
import pandas as pd

TARGET_VALENCE = 0.80
TARGET_ENERGY = 0.80

# Emotion coordinates in Russell's Circumplex Model (valence, energy)
EMOTION_COORDS: dict[str, tuple[float, float]] = {
    "Happy":    (0.80, 0.80),
    "Surprise": (0.60, 0.85),
    "Angry":    (0.20, 0.80),
    "Fear":     (0.20, 0.60),
    "Disgust":  (0.15, 0.50),
    "Sad":      (0.20, 0.20),
}


def spotify_url(track_id: str) -> str:
    return f"https://open.spotify.com/track/{track_id}"


def find_nearest_song(
    df: pd.DataFrame,
    v_target: float,
    e_target: float,
    exclude_ids: list[str],
) -> dict:
    candidates = df[~df["track_id"].isin(exclude_ids)].copy()
    candidates["dist"] = np.sqrt(
        (candidates["valence"] - v_target) ** 2 +
        (candidates["energy"] - e_target) ** 2
    )
    row = candidates.nsmallest(1, "dist").iloc[0]
    return {
        "track_name":   row["track_name"],
        "artists":      row["artists"],
        "emotion":      row["emotion"],
        "valence":      round(float(row["valence"]), 3),
        "energy":       round(float(row["energy"]), 3),
        "track_id":     row["track_id"],
        "spotify_url":  spotify_url(row["track_id"]),
    }


def recommend(emotion: str, df: pd.DataFrame) -> list[dict]:
    if emotion not in EMOTION_COORDS:
        emotion = "Sad"  # safe default

    cv, ce = EMOTION_COORDS[emotion]

    waypoints = [
        (cv, ce),                                          # match current mood
        ((cv + TARGET_VALENCE) / 2, (ce + TARGET_ENERGY) / 2),  # bridge
        (TARGET_VALENCE, TARGET_ENERGY),                   # destination: Happy
    ]

    songs = []
    used_ids: list[str] = []
    for v, e in waypoints:
        song = find_nearest_song(df, v, e, used_ids)
        songs.append(song)
        used_ids.append(song["track_id"])

    return songs


if __name__ == "__main__":
    df = pd.read_csv("data/processed/dataset_labeled.csv")

    test_emotions = ["Sad", "Angry", "Fear", "Happy"]
    for emotion in test_emotions:
        print(f"\n{'─' * 52}")
        print(f"  Starting from: {emotion}")
        print(f"{'─' * 52}")
        songs = recommend(emotion, df)
        labels = ["Matching your mood", "The bridge", "Your destination"]
        for song, label in zip(songs, labels):
            print(f"\n  [{label}]")
            print(f"    {song['track_name']} — {song['artists']}")
            print(f"    Emotion: {song['emotion']}  |  "
                  f"Valence: {song['valence']}  |  Energy: {song['energy']}")
            print(f"    {song['spotify_url']}")
