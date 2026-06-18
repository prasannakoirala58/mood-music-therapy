"""
label_emotions.py

Loads the raw Kaggle dataset, deduplicates by track_id,
applies rule-based emotion labels using valence + energy + mode,
and writes dataset_labeled.csv to data/processed/.

Academic basis: Russell's Circumplex Model of Affect (1980).
6 target labels: Happy, Sad, Angry, Fear, Disgust, Surprise.
"""

import pandas as pd
from pathlib import Path

RAW_PATH = Path("data/raw/dataset.csv")
PROCESSED_PATH = Path("data/processed/dataset_labeled.csv")


def label_emotion(row: pd.Series) -> str:
    v = row["valence"]
    e = row["energy"]
    m = row["mode"]  # 1 = major key, 0 = minor key

    if v > 0.6 and e > 0.6:
        return "Happy"
    if v < 0.4 and e < 0.4:
        return "Sad"
    if v < 0.4 and e > 0.65:
        return "Angry"
    # Minor key (mode=0) + mid energy + low-ish valence → tense/fearful
    if v < 0.5 and 0.4 <= e <= 0.7 and m == 0:
        return "Fear"
    if v < 0.35 and e < 0.5:
        return "Disgust"
    # Catch-all for high-energy tracks that don't fit above
    return "Surprise"


def run() -> None:
    print("Loading dataset...")
    df = pd.read_csv(RAW_PATH, index_col=0)
    print(f"  Loaded {len(df):,} rows")

    # Drop rows missing any column we depend on
    required = ["track_id", "valence", "energy", "mode", "track_name",
                "artists", "tempo", "danceability", "loudness",
                "acousticness", "track_genre"]
    before = len(df)
    df = df.dropna(subset=required)
    if len(df) < before:
        print(f"  Dropped {before - len(df):,} rows with missing values")

    # Some tracks appear in multiple genres — keep the first occurrence
    df = df.drop_duplicates(subset="track_id", keep="first")
    print(f"  {len(df):,} unique tracks after deduplication")

    print("Labeling emotions...")
    df["emotion"] = df.apply(label_emotion, axis=1)

    distribution = df["emotion"].value_counts()
    print("\n  Emotion distribution:")
    for emotion, count in distribution.items():
        pct = count / len(df) * 100
        print(f"    {emotion:<10} {count:>6,}  ({pct:.1f}%)")

    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_PATH, index=False)
    print(f"\n  Saved → {PROCESSED_PATH}  ({len(df):,} songs)")


if __name__ == "__main__":
    run()
