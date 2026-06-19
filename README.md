# Music Mood Therapy

A mood-to-music recommendation engine grounded in clinical music therapy and machine learning.

> Tell me how you feel. I'll find three songs that move you from where you are to somewhere better.

---

## How It Works

The system applies the **ISO Principle** from clinical music therapy: you cannot jump from sad to happy — the emotional gap creates dissonance. Instead, music therapy starts by *matching* the listener's current state, then *bridges*, then arrives at the *destination*.

```
You type:  "I feel completely empty and hopeless"

Step 1 — OpenAI GPT-4o-mini classifies your mood
         → "Sad"

Step 2 — ISO engine maps "Sad" to coordinates on Russell's Circumplex Model
         → (valence=0.20, energy=0.20)
         → Calculates 3 waypoints toward Happy (0.80, 0.80)

Step 3 — Nearest-neighbour search across 89,740 Spotify tracks
         → Finds the closest song to each waypoint

Step 4 — MLP neural network classifies each song live
         → Predicts emotion from its 8 audio features in real time

Step 5 — You get three songs + Spotify links:
         [1] matching your mood   — meets you where you are
         [2] the bridge           — starts shifting the energy
         [3] your destination     — where you're headed
```

---

## Academic Foundation

| Concept | Source |
|---------|--------|
| ISO Principle | Clinical music therapy — match emotional state before guiding |
| Russell's Circumplex Model | Russell (1980) — 2D emotion space: valence × arousal |
| Ekman's 6 basic emotions | Happy, Sad, Angry, Fear, Disgust, Surprise |
| Audio features | Spotify pre-extracted: valence, energy, tempo, mode, danceability, loudness, acousticness, genre |

---

## ML Architecture

Two classifiers trained on 89,740 labeled Spotify tracks. Both answer the same question: **"Given these 8 audio features, what emotion is this song?"**

```
Random Forest (baseline)
  100 decision trees · class_weight='balanced' · feature importance chart
  Accuracy: 100% (expected — label circularity, acknowledged limitation)

MLP Neural Network  ← used live in recommendations
  Input: 8 features
  Hidden: 128 → 64 neurons (ReLU)
  Output: 6 emotions (softmax)
  StandardScaler + early_stopping
  Accuracy: 99.26% · converged at iteration 39
```

The MLP runs on every recommendation request — song emotion labels you see in the app are live neural network predictions, not pre-assigned tags.

---

## Setup

### Prerequisites
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) — `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Node 20+
- Docker Desktop (optional, for containerised run)
- OpenAI API key

### 1. Clone and configure
```bash
git clone git@github.com:prasannakoirala58/mood-music-therapy.git
cd music-therapy
cp .env.example .env
# Add your OPENAI_API_KEY to .env
```

### 2. Get the dataset
Download `dataset.csv` from [Kaggle — Spotify Tracks Dataset](https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset) and place it at:
```
backend/data/raw/dataset.csv
```

### 3. Install backend dependencies
```bash
cd backend && uv sync
```

### 4. Train the models (one-time, ~5 minutes)
```bash
make train
# Labels 89k songs with emotions
# Trains Random Forest + MLP neural network
# Saves .pkl files to backend/models/
```

### 5. Run

**Web app (recommended):**
```bash
# Terminal 1
make api        # FastAPI backend on http://localhost:8000

# Terminal 2
make frontend   # React frontend on http://localhost:5173
```
Open `http://localhost:5173` in your browser.

**CLI:**
```bash
make run        # or: make start (trains first if models are missing)
```

**Full stack via Docker:**
```bash
docker compose up --build
```

---

## Project Structure

```
music-therapy/
├── backend/
│   ├── src/
│   │   ├── label_emotions.py     ← Rule-based emotion labeling
│   │   ├── train_classifier.py   ← Trains RF + MLP, prints comparison
│   │   ├── mood_parser.py        ← OpenAI: text → emotion label
│   │   ├── recommender.py        ← ISO engine + live MLP inference
│   │   ├── pipeline.py           ← CLI conversation loop
│   │   └── api.py                ← FastAPI REST server
│   ├── data/raw/                 ← dataset.csv (not committed, 20MB)
│   ├── data/processed/           ← dataset_labeled.csv (generated)
│   ├── models/                   ← .pkl files (generated)
│   └── demo/librosa_demo.py      ← Raw audio demo
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── MoodInput.tsx     ← Input form
│   │   │   ├── ResultsPanel.tsx  ← 3-card results
│   │   │   ├── SongCard.tsx      ← Song card + Spotify button
│   │   │   └── ResonanceMap.tsx  ← SVG: song position on Circumplex
│   │   ├── hooks/useRecommend.ts ← API calls
│   │   └── lib/emotions.ts       ← Emotion colours + metadata
│   └── ...
│
├── Makefile                      ← All commands live here
├── docker-compose.yml
└── ROADMAP.md                    ← Full system design + defense talking points
```

---

## Makefile Commands

```bash
make install    # Install backend Python deps
make train      # Label data + train both models (run once)
make run        # Run the CLI app
make start      # Smart: trains if missing, then runs CLI
make api        # Start FastAPI server on :8000
make frontend   # Start React dev server on :5173
make typecheck  # TypeScript strict type-check
make demo FILE= # Librosa audio demo: make demo FILE=song.mp3
make clean      # Remove generated data + models (forces retrain)
make help       # Show all commands
```

---

## Built With

**Backend:** Python 3.11 · uv · FastAPI · scikit-learn · OpenAI · librosa · pandas · numpy · joblib · loguru

**Frontend:** React 18 · TypeScript · Tailwind CSS · Vite · framer-motion

**Infrastructure:** Docker · docker-compose

**Dataset:** [Kaggle — Spotify Tracks Dataset](https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset) by maharshipandya (114k tracks, 125 genres)
