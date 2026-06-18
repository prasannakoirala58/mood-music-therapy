"""
label_emotions.py

Loads the raw Kaggle dataset, deduplicates by track_id,
applies rule-based emotion labels using valence + energy + mode,
and writes dataset_labeled.csv to data/processed/.

Academic basis: Russell's Circumplex Model of Affect (1980).
6 target labels: Happy, Sad, Angry, Fear, Disgust, Surprise.
"""

import pandas as pd


RAW_PATH = "data/raw/dataset.csv"
PROCESSED_PATH = "data/processed/dataset_labeled.csv"


def label_emotion(row: pd.Series) -> str:
    # TODO: implement threshold logic
    pass


def run() -> None:
    # TODO: load → deduplicate → apply labels → save → print value_counts
    pass


if __name__ == "__main__":
    run()
