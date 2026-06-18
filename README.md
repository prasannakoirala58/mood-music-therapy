# Music Mood Therapy 🎵

A mood-to-music recommendation engine built on the **ISO Principle** from clinical music therapy.

> Tell me how you feel. I'll walk you through 3 songs from where you are to somewhere better.

---

## What It Does

1. You describe your mood in natural language
2. GPT-4o-mini classifies your emotion into one of 6 categories
3. The ISO engine calculates a 3-song emotional journey toward Happy
4. You get 3 real Spotify-linked songs — one matching your mood, one bridging, one at the destination
5. After listening, tell the app how you feel — it loops with a fresh set if needed

---

## Academic Foundation

| Concept | Source |
|---------|--------|
| ISO Principle | Clinical music therapy — match emotional state before guiding |
| Russell's Circumplex Model | Russell (1980) — 2D emotion space: valence × arousal |
| Emotion labels | Ekman's 6 basic emotions |
| Feature extraction | Spotify audio features: valence, energy, tempo, mode, danceability, loudness, acousticness, genre |

---

## ML Architecture

Two classifiers trained on 114k labeled Spotify tracks:

```
Random Forest (baseline)   — 100 decision trees, feature importance analysis
MLP Neural Network         — 128→64 hidden layers, ReLU, backpropagation, early stopping
```

Both trained on 8 audio features. Accuracy compared side-by-side.

---

## Setup

### Prerequisites
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) — `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Docker Desktop
- OpenAI API key

### 1. Clone and configure
```bash
git clone git@github.com:prasannakoirala58/mood-music-therapy.git
cd mood-music-therapy
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 2. Download dataset
Get `dataset.csv` from [Kaggle](https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset)
and place it at `backend/data/raw/dataset.csv`

### 3. Install dependencies
```bash
cd backend && uv sync
```

### 4. Run the data pipeline (one-time setup)
```bash
uv run python src/label_emotions.py      # Labels 114k songs with emotions
uv run python src/train_classifier.py    # Trains RF + MLP, prints accuracy
```

### 5. Run the app
```bash
uv run python src/pipeline.py            # Start the CLI conversation
```

### Or run everything via Docker
```bash
docker-compose up --build
docker-compose run backend               # Interactive CLI
```

---

## Project Structure

```
mood-music-therapy/
├── backend/
│   ├── src/
│   │   ├── label_emotions.py    ← Rule-based emotion labeling
│   │   ├── train_classifier.py  ← RF + MLP training
│   │   ├── mood_parser.py       ← OpenAI mood classification
│   │   ├── recommender.py       ← ISO principle engine
│   │   └── pipeline.py          ← CLI conversation loop
│   ├── data/raw/                ← dataset.csv (not committed)
│   ├── data/processed/          ← dataset_labeled.csv (generated)
│   ├── models/                  ← .pkl model files (generated)
│   └── demo/librosa_demo.py     ← Raw audio demo
├── frontend/                    ← Streamlit UI (Phase 5)
├── docker-compose.yml
└── ROADMAP.md                   ← Full system design
```

---

## Built With

- Python 3.11 · uv · Docker
- scikit-learn (RandomForest, MLPClassifier)
- OpenAI GPT-4o-mini
- librosa · pandas · numpy
- Streamlit (Phase 5)
- Kaggle Spotify Tracks Dataset (maharshipandya)
