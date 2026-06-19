"""
recommender.py

ISO Principle recommendation engine.

Given a detected emotion, calculates 3 waypoints through Russell's Circumplex
Model from the user's current emotional state toward the target (Happy).
Finds the nearest song in the labeled dataset to each waypoint using
Euclidean distance in (valence, energy) space.

Each recommended song is classified in real-time by the trained MLP neural
network — so the emotion label on every card is a live model prediction,
not a pre-assigned tag from the CSV.

Returns 3 song dicts — one per waypoint:
  track_name, artists, emotion, valence, energy, track_id, spotify_url
"""

import numpy as np
import pandas as pd
from loguru import logger

TARGET_VALENCE = 0.80
TARGET_ENERGY  = 0.80

# Each emotion's position in Russell's Circumplex Model (valence, energy)
EMOTION_COORDS: dict[str, tuple[float, float]] = {
    "Happy":    (0.80, 0.80),
    "Surprise": (0.60, 0.85),
    "Angry":    (0.20, 0.80),
    "Fear":     (0.20, 0.60),
    "Disgust":  (0.15, 0.50),
    "Sad":      (0.20, 0.20),
}

# Features the MLP was trained on — must match train_classifier.py exactly
MLP_FEATURES = [
    "valence", "energy", "tempo", "mode",
    "danceability", "loudness", "acousticness", "genre_encoded",
]

# How many nearest candidates to sample from per waypoint.
# Sampling from a pool (instead of always picking rank-1) means different
# journeys on different sessions while still staying close to the target.
TOP_K_MATCH  = 30   # more variety for the "match" song
TOP_K_BRIDGE = 20
TOP_K_DEST   = 10   # tighter range for the destination — we want it near Happy


def spotify_url(track_id: str) -> str:
    return f"https://open.spotify.com/track/{track_id}"


def _mlp_predict(row: pd.Series, mlp_model, genre_encoder) -> str:
    """Run a single song's audio features through the MLP and return its predicted emotion."""
    try:
        genre_enc = genre_encoder.transform([row["track_genre"]])[0]
        features = np.array([[
            row["valence"], row["energy"], row["tempo"], row["mode"],
            row["danceability"], row["loudness"], row["acousticness"], genre_enc,
        ]])
        return str(mlp_model.predict(features)[0])
    except Exception:
        return str(row["emotion"])   # fallback: use rule-based label


def find_nearest_song(
    df: pd.DataFrame,
    v_target: float,
    e_target: float,
    exclude_ids: list[str],
    top_k: int = 20,
    mlp_model=None,
    genre_encoder=None,
    expected_emotion: str | None = None,  # MLP quality gate: prefer this emotion
) -> dict:
    candidates = df[~df["track_id"].isin(exclude_ids)].copy()
    candidates["dist"] = np.sqrt(
        (candidates["valence"] - v_target) ** 2 +
        (candidates["energy"] - e_target) ** 2
    )
    pool = candidates.nsmallest(top_k, "dist")

    # Try up to 3 random samples from the pool.
    # If MLP predicts the expected emotion, accept immediately.
    # If not, log the mismatch and try again — on the 3rd attempt accept whatever we get.
    # This keeps variety (random sampling) while making the MLP a quality gate.
    MAX_ATTEMPTS = 3
    tried_ids: set[str] = set()
    row = pool.sample(1).iloc[0]
    emotion = _mlp_predict(row, mlp_model, genre_encoder) if mlp_model is not None else str(row["emotion"])

    for attempt in range(1, MAX_ATTEMPTS + 1):
        tried_ids.add(row["track_id"])

        if expected_emotion is None or emotion == expected_emotion:
            break

        remaining = pool[~pool["track_id"].isin(tried_ids)]
        if remaining.empty or attempt == MAX_ATTEMPTS:
            logger.warning(
                f"[MLP MISMATCH] after {attempt} attempt(s): "
                f"'{row['track_name']}' predicted as {emotion!r}, "
                f"expected {expected_emotion!r} — keeping best available"
            )
            break

        logger.debug(
            f"[MLP RETRY {attempt}] '{row['track_name']}' → {emotion!r} "
            f"(expected {expected_emotion!r}), trying next candidate"
        )
        row = remaining.sample(1).iloc[0]
        emotion = _mlp_predict(row, mlp_model, genre_encoder) if mlp_model is not None else str(row["emotion"])

    dist = float(row["dist"])
    logger.info(
        f"  ↳ '{row['track_name']}' by {row['artists'][:40]} | "
        f"dist={dist:.3f} | MLP→{emotion}"
    )

    return {
        "track_name":  row["track_name"],
        "artists":     row["artists"],
        "emotion":     emotion,
        "valence":     round(float(row["valence"]), 3),
        "energy":      round(float(row["energy"]), 3),
        "track_id":    row["track_id"],
        "spotify_url": spotify_url(row["track_id"]),
    }


def recommend(
    emotion: str,
    df: pd.DataFrame,
    mlp_model=None,
    genre_encoder=None,
) -> list[dict]:
    if emotion not in EMOTION_COORDS:
        emotion = "Sad"

    cv, ce = EMOTION_COORDS[emotion]

    waypoints = [
        # (v_target, e_target, top_k, expected_emotion)
        (cv,                               ce,                               TOP_K_MATCH,  emotion),   # match — should reflect user's mood
        ((cv + TARGET_VALENCE) / 2,        (ce + TARGET_ENERGY) / 2,        TOP_K_BRIDGE, None),      # bridge — any emotion is fine
        (TARGET_VALENCE,                   TARGET_ENERGY,                   TOP_K_DEST,   "Happy"),   # destination — want MLP to confirm Happy
    ]

    step_labels = ["match", "bridge", "destination"]

    songs: list[dict] = []
    used_ids: list[str] = []

    for i, (v, e, k, expected) in enumerate(waypoints):
        label = step_labels[i]
        logger.info(
            f"[WAYPOINT {i+1}/3] {label.upper()} | "
            f"target=({v:.2f}, {e:.2f}) | top_k={k} | expect={expected or 'any'}"
        )
        song = find_nearest_song(
            df, v, e, used_ids,
            top_k=k,
            mlp_model=mlp_model,
            genre_encoder=genre_encoder,
            expected_emotion=expected,
        )
        songs.append(song)
        used_ids.append(song["track_id"])

    return songs


if __name__ == "__main__":
    import joblib

    df  = pd.read_csv("data/processed/dataset_labeled.csv")
    mlp = joblib.load("models/emotion_classifier_mlp.pkl")
    le  = joblib.load("models/genre_label_encoder.pkl")

    test_emotions = ["Sad", "Angry", "Fear", "Disgust", "Surprise", "Happy"]
    labels = ["Matching your mood", "The bridge", "Your destination"]

    for em in test_emotions:
        print(f"\n{'─' * 56}")
        print(f"  Starting from: {em}")
        print(f"{'─' * 56}")
        songs = recommend(em, df, mlp, le)
        for song, label in zip(songs, labels):
            print(f"\n  [{label}]")
            print(f"    {song['track_name']} — {song['artists']}")
            print(f"    MLP emotion: {song['emotion']}  "
                  f"V={song['valence']}  E={song['energy']}")
            print(f"    {song['spotify_url']}")
