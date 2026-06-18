"""
train_classifier.py

Trains two classifiers on the labeled dataset and saves both to models/:
  - Random Forest   → emotion_classifier_rf.pkl
  - MLP Neural Net  → emotion_classifier_mlp.pkl

Prints a side-by-side classification report (accuracy, precision, recall, f1).
Prints top 5 feature importances from the Random Forest.

Features: valence, energy, tempo, mode, danceability, loudness, acousticness, genre_encoded
Labels:   Happy, Sad, Angry, Fear, Disgust, Surprise
"""

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.pipeline import Pipeline


PROCESSED_PATH = "data/processed/dataset_labeled.csv"
MODELS_DIR = "models"

FEATURES = [
    "valence", "energy", "tempo", "mode",
    "danceability", "loudness", "acousticness", "genre_encoded"
]
TARGET = "emotion"


def train(df: pd.DataFrame):
    # TODO: encode genre, split, train RF, train MLP pipeline, print reports, save .pkl files
    pass


def run() -> None:
    # TODO: load processed CSV → call train()
    pass


if __name__ == "__main__":
    run()
