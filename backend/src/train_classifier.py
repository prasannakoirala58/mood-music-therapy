"""
train_classifier.py

Trains two classifiers on the labeled dataset and saves both to models/:
  - Random Forest        → emotion_classifier_rf.pkl
  - MLP Neural Network   → emotion_classifier_mlp.pkl
  - Genre LabelEncoder   → genre_label_encoder.pkl  (needed at inference time)

Prints a side-by-side accuracy + classification report for both models.
Prints feature importance from the Random Forest (presentation slide).

Features used: valence, energy, tempo, mode, danceability,
               loudness, acousticness, genre_encoded (8 total)
"""

import joblib
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.pipeline import Pipeline


PROCESSED_PATH = Path("data/processed/dataset_labeled.csv")
MODELS_DIR = Path("models")

FEATURES = [
    "valence", "energy", "tempo", "mode",
    "danceability", "loudness", "acousticness", "genre_encoded",
]
TARGET = "emotion"


def encode_genre(df: pd.DataFrame) -> tuple[pd.DataFrame, LabelEncoder]:
    le = LabelEncoder()
    df = df.copy()
    df["genre_encoded"] = le.fit_transform(df["track_genre"])
    return df, le


def train_random_forest(X_train, y_train) -> RandomForestClassifier:
    rf = RandomForestClassifier(
        n_estimators=100,
        class_weight="balanced",   # compensates for Disgust/Fear being small classes
        random_state=42,
        n_jobs=-1,                 # uses all CPU cores — M4 will fly here
    )
    rf.fit(X_train, y_train)
    return rf


def train_mlp(X_train, y_train) -> Pipeline:
    # StandardScaler inside the Pipeline so scaling is part of the model object —
    # the same scaler is applied automatically at inference time
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("mlp", MLPClassifier(
            hidden_layer_sizes=(128, 64),
            activation="relu",
            max_iter=500,
            early_stopping=True,        # halts when validation accuracy stops improving
            validation_fraction=0.1,    # 10% of training set used for early-stop check
            random_state=42,
            verbose=False,
        )),
    ])
    pipeline.fit(X_train, y_train)
    return pipeline


def print_feature_importances(rf: RandomForestClassifier) -> None:
    ranked = sorted(
        zip(FEATURES, rf.feature_importances_),
        key=lambda x: x[1],
        reverse=True,
    )
    print("\n  Feature importances (Random Forest):")
    for name, score in ranked:
        bar = "█" * int(score * 50)
        print(f"    {name:<20} {score:.4f}  {bar}")


def run() -> None:
    print("Loading labeled dataset...")
    raw_features = [f for f in FEATURES if f != "genre_encoded"]
    df = pd.read_csv(PROCESSED_PATH).dropna(subset=raw_features + [TARGET, "track_genre"])
    print(f"  {len(df):,} songs")

    df, le = encode_genre(df)

    X = df[FEATURES].values
    y = df[TARGET].values

    # stratify=y keeps emotion class ratios the same in train and test splits
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"  Train: {len(X_train):,}  |  Test: {len(X_test):,}\n")

    print("Training Random Forest (100 trees, all cores)...")
    rf = train_random_forest(X_train, y_train)
    rf_preds = rf.predict(X_test)
    rf_acc = (rf_preds == y_test).mean()
    print(f"  Accuracy: {rf_acc * 100:.2f}%")

    print("\nTraining MLP Neural Network (128 → 64 → 6)...")
    mlp = train_mlp(X_train, y_train)
    mlp_preds = mlp.predict(X_test)
    mlp_acc = (mlp_preds == y_test).mean()
    n_iter = mlp.named_steps["mlp"].n_iter_
    print(f"  Accuracy: {mlp_acc * 100:.2f}%  (stopped at iteration {n_iter})")

    print("\n" + "─" * 56)
    print(f"  RF  accuracy: {rf_acc * 100:.2f}%   "
          f"MLP accuracy: {mlp_acc * 100:.2f}%")
    winner = "Random Forest" if rf_acc >= mlp_acc else "MLP Neural Network"
    print(f"  Winner: {winner}")
    print("─" * 56)

    print("\nRANDOM FOREST — per-class breakdown")
    print(classification_report(y_test, rf_preds))

    print("MLP NEURAL NETWORK — per-class breakdown")
    print(classification_report(y_test, mlp_preds))

    print_feature_importances(rf)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    rf_path = MODELS_DIR / "emotion_classifier_rf.pkl"
    mlp_path = MODELS_DIR / "emotion_classifier_mlp.pkl"
    le_path = MODELS_DIR / "genre_label_encoder.pkl"

    joblib.dump(rf, rf_path)
    joblib.dump(mlp, mlp_path)
    joblib.dump(le, le_path)   # saved separately — needed to encode genre at inference

    print(f"\n  Saved → {rf_path}")
    print(f"  Saved → {mlp_path}")
    print(f"  Saved → {le_path}")
    print("\nPhase 1 complete. Run 'make run' when Phase 2 is done.")


if __name__ == "__main__":
    run()
