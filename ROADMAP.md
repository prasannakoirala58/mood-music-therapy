# Music Mood Therapy — Project Roadmap & System Design
## Final Version — All Decisions Locked

> **Core concept:** User describes their mood in 2–3 sentences → AI detects their emotion → 3 songs guide them from that state toward happy/calm via the **ISO Principle** from music therapy (match → bridge → target).

---

## Status Checklist

- [x] Dataset identified — Kaggle "Spotify Tracks Dataset" (9MB zip, 114k songs)
- [x] GitHub repo created — `github.com/prasannakoirala58/mood-music-therapy`
- [x] `.env` created locally — OPENAI_API_KEY + SPOTIFY credentials
- [x] `uv` installed
- [x] Docker available
- [x] System design finalised (below)
- [ ] Dataset downloaded and placed in `backend/data/raw/`
- [ ] Phase 0 complete
- [ ] Phase 1 complete
- [ ] Phase 2 complete
- [ ] Phase 3 complete
- [ ] Phase 4 complete

---

## 1. System Architecture

```
USER (terminal): "I feel completely empty and nothing excites me"
                              │
                              ▼
                    ┌──────────────────┐
                    │  OpenAI API      │  GPT-4o-mini
                    │  Mood Parser     │  Strict prompt: return ONE of 6 labels
                    └────────┬─────────┘
                             │  "Sad"
                             ▼
                    ┌──────────────────┐
                    │  ISO Engine      │  Maps "Sad" → (valence=0.20, energy=0.20)
                    │  (recommender)   │  Computes 3 waypoints toward Happy
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
         (0.20, 0.20)   (0.50, 0.50)   (0.80, 0.80)
         match mood      bridge         target
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                    ┌──────────────────┐
                    │  114k Song DB    │  Nearest neighbor search
                    │  dataset_labeled │  Find closest song to each waypoint
                    │  .csv            │  in (valence, energy) space
                    └────────┬─────────┘
                             │
                             ▼
              Song 1 — Matching your mood    (Spotify link)
              Song 2 — The bridge            (Spotify link)
              Song 3 — Your destination      (Spotify link)
                             │
                             ▼
              "How are you feeling now?"
              → if not happy → next set of 3
```

---

## 2. ML Architecture — Two Models, One Purpose

We train TWO classifiers and compare them. Both answer the same question:
**"Given these 8 audio features, what emotion is this song?"**

### Features used for classification (8 total)
```
valence        — musical positiveness (0.0 → 1.0)
energy         — intensity and activity (0.0 → 1.0)
tempo          — beats per minute
mode           — major (1) or minor (0) key
danceability   — how suitable for dancing (0.0 → 1.0)
loudness       — overall loudness in dB (-60 → 0)
acousticness   — confidence the track is acoustic (0.0 → 1.0)
genre_encoded  — 125 genres numerically encoded (NEW: massive signal)
```

### Model 1 — Random Forest (baseline)
```
100 decision trees, each votes on emotion → majority wins
Scale-invariant (no preprocessing needed)
Gives feature importance chart for free
NOT a neural network — ensemble of decision trees
Expected accuracy: ~82–88%
```

### Model 2 — MLP Neural Network (your neural network)
```
Input layer:    8 neurons  (one per feature)
Hidden layer 1: 128 neurons (ReLU activation)
Hidden layer 2:  64 neurons (ReLU activation)
Output layer:    6 neurons  (Softmax — one per emotion)

Training: backpropagation, up to 500 iterations
Regularisation: early_stopping=True (prevents overfitting automatically)
Scaling: StandardScaler applied (MLP requires normalised inputs)
Expected accuracy: ~84–90%
```

### Why two models?
- RF is the gold standard baseline for tabular data — hard to beat
- If MLP ≥ RF: neural net learned something real → present the win
- If MLP < RF: explain WHY (genre encoding complexity, tabular data advantage)
- Either way you have a story — this is what professional ML work looks like
- Feature importance from RF tells you which features matter most (slide in presentation)

### Overfitting / Underfitting — handled explicitly
```
Problem              Solution
──────────────────────────────────────────────────────
Class imbalance      class_weight='balanced' on both models
MLP overfitting      early_stopping=True, validation_fraction=0.1
Feature scale        StandardScaler before MLP only
Evaluation           80/20 train/test split, classification report
Label noise          Rule-based labels are acknowledged as limitation
Duplicate tracks     Deduplicate by track_id after labeling
```

---

## 3. Emotion Mapping — Russell's Circumplex Model

```
                    HIGH ENERGY
                        │
        Angry           │         Surprise
       (0.20, 0.80)     │        (0.60, 0.85)
                        │
NEGATIVE ───────────────┼─────────────────── POSITIVE
(valence)               │                   (valence)
                        │
        Sad             │         Happy
       (0.20, 0.20)     │        (0.80, 0.80)  ← TARGET
                        │
        Disgust         │
       (0.15, 0.50)     │
                        │
        Fear            │
       (0.20, 0.60)     │
                    LOW ENERGY
```

### Emotion labeling rules (label_emotions.py)
```python
Happy:   valence > 0.6  AND energy > 0.6
Sad:     valence < 0.4  AND energy < 0.4
Angry:   valence < 0.4  AND energy > 0.65
Fear:    valence < 0.5  AND 0.4 <= energy <= 0.7  AND mode == 0
Disgust: valence < 0.35 AND energy < 0.5
Surprise: energy > 0.75 (anything else high energy)
```

### ISO waypoints — how the 3-song path is calculated
```python
# Current emotion coords → target (Happy) coords
# Waypoint 1: current state     → match the user WHERE THEY ARE
# Waypoint 2: arithmetic midpoint → bridge
# Waypoint 3: target (Happy)    → destination

waypoints = [
    (current_v, current_e),
    ((current_v + 0.80) / 2, (current_e + 0.80) / 2),
    (0.80, 0.80)
]
```

---

## 4. Spotify Integration — Zero API Calls Needed

The dataset already contains `track_id` — the Spotify track identifier.

```python
spotify_url = f"https://open.spotify.com/track/{row['track_id']}"
# Works instantly. No API key. No authentication. Just a URL.
```

Anyone clicking that link opens the song directly in Spotify (web or app).

**Spotify Client ID / Secret:** Stored in `.env` for future use (Spotify search API is not
deprecated — only recommendations was). Not used in Phase 0–4 of this build.

---

## 5. Folder Structure

```
mood-music-therapy/
│
├── backend/                         ← All ML + pipeline logic
│   ├── src/
│   │   ├── __init__.py
│   │   ├── label_emotions.py        ← Rule-based emotion labeling
│   │   ├── train_classifier.py      ← Trains RF + MLP, prints comparison
│   │   ├── mood_parser.py           ← OpenAI: text → emotion label
│   │   ├── recommender.py           ← ISO engine: emotion → 3 songs
│   │   └── pipeline.py              ← CLI interaction loop (main app)
│   ├── data/
│   │   ├── raw/
│   │   │   └── dataset.csv          ← Kaggle download goes here (git-ignored)
│   │   └── processed/
│   │       └── dataset_labeled.csv  ← Output of label_emotions.py (git-ignored)
│   ├── models/
│   │   ├── emotion_classifier_rf.pkl   ← Trained Random Forest (git-ignored)
│   │   └── emotion_classifier_mlp.pkl  ← Trained MLP neural net (git-ignored)
│   ├── demo/
│   │   └── librosa_demo.py          ← Presentation: raw audio → features
│   ├── pyproject.toml               ← uv project config
│   ├── uv.lock
│   ├── .python-version              ← 3.11
│   └── Dockerfile
│
├── frontend/                        ← Streamlit UI (Phase 5, post-CLI)
│   ├── app.py
│   ├── pages/
│   │   └── about.py
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── .python-version
│   └── Dockerfile
│
├── docker-compose.yml
├── .env                             ← NEVER committed
├── .env.example                     ← Committed (empty values)
├── .gitignore
├── README.md
└── ROADMAP.md                       ← This file
```

---

## 6. Tech Stack — Final Decisions

| Tool | Version | Why |
|------|---------|-----|
| Python | 3.11 | Stable, excellent ML library support |
| uv | latest | 10–100x faster than pip, deterministic lockfile |
| Docker | latest | Reproducible builds, pro portfolio signal |
| docker-compose | latest | One command to run everything |
| pandas | ^2.0 | Data manipulation and CSV handling |
| scikit-learn | ^1.4 | RF + MLP classifiers, StandardScaler |
| numpy | ^1.26 | Numerical operations |
| openai | ^1.0 | GPT-4o-mini for mood text classification |
| librosa | ^0.10 | Audio feature extraction (demo only) |
| joblib | ^1.3 | Save/load .pkl model files |
| python-dotenv | ^1.0 | Load .env variables |
| streamlit | ^1.35 | Frontend UI (Phase 5) |
| spotipy | ^2.23 | Spotify API client (future use) |

---

## 7. Build Phases

### BEFORE STARTING — One manual step required
Download the dataset:
1. Go to `kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset`
2. Click "Download dataset as zip (9 MB)" in the browser (no API key needed)
3. Unzip it → you get `dataset.csv`
4. Place it at `backend/data/raw/dataset.csv`

That's it. No other manual steps.

---

### Phase 0 — Scaffold & GitHub (30 min)
**Goal: Full project structure exists, Docker runs, code is on GitHub.**

Steps:
- [ ] Create complete folder structure
- [ ] `backend/pyproject.toml` — uv config with all backend dependencies
- [ ] `frontend/pyproject.toml` — uv config with streamlit
- [ ] `backend/.python-version` → `3.11`
- [ ] `frontend/.python-version` → `3.11`
- [ ] `backend/Dockerfile` — uv-based Python image
- [ ] `frontend/Dockerfile` — uv-based Python image
- [ ] `docker-compose.yml` — backend + frontend services
- [ ] `.env.example` — template with empty values
- [ ] `.gitignore` — exclude `.env`, `data/raw/`, `data/processed/`, `models/`
- [ ] `README.md` — project overview, setup instructions, architecture
- [ ] Connect to GitHub repo `prasannakoirala58/mood-music-therapy`
- [ ] `git push` — clean first commit
- [ ] Verify `docker-compose up --build` starts both containers

**Commit:** `chore: project scaffold — docker, uv, folder structure`

---

### Phase 1 — Data Pipeline (45–60 min)
**Goal: 114k songs labeled, two models trained, accuracy printed side by side.**

Steps:
- [ ] Build `label_emotions.py`
  - Load `backend/data/raw/dataset.csv`
  - Deduplicate by `track_id` (removes cross-genre duplicates)
  - Apply emotion rules using valence, energy, mode
  - Print `value_counts()` — verify all 6 emotions have meaningful count
  - Save to `backend/data/processed/dataset_labeled.csv`
- [ ] Build `train_classifier.py`
  - Load labeled CSV
  - Encode `track_genre` with `LabelEncoder`
  - Features: 8 columns (7 audio + genre_encoded)
  - 80/20 train/test split, `random_state=42`
  - Train Random Forest: `n_estimators=100, class_weight='balanced'`
  - Train MLP: `hidden_layer_sizes=(128,64), early_stopping=True, class_weight='balanced'`
  - Apply `StandardScaler` to MLP pipeline only
  - Print classification report for BOTH models side by side
  - Print top 5 feature importances from RF (presentation slide)
  - Save both models to `backend/models/`
- [ ] Run both scripts inside Docker container
- [ ] Verify `.pkl` files created

**Commit:** `feat: data labeling pipeline and dual-model training RF vs MLP`

---

### Phase 2 — Core Intelligence (60 min)
**Goal: Given any mood text, returns 3 Spotify-linked songs following the ISO principle.**

Steps:
- [ ] Build `mood_parser.py`
  - OpenAI client from env
  - System prompt: strict 6-label classifier, return label only
  - Test: all 5 standard test cases return correct labels
- [ ] Build `recommender.py`
  - `EMOTION_COORDS` dict — 6 emotions mapped to (valence, energy)
  - `find_nearest_song(df, v_target, e_target, exclude_ids)` — Euclidean distance search
  - `recommend(emotion, df)` — 3 waypoints → 3 distinct songs
  - Each song result includes: `track_name`, `artists`, `emotion`, `valence`, `energy`, `track_id`, `spotify_url`
  - Standalone test: `recommend("Sad", df)` prints 3-song arc
- [ ] Run standalone tests for both files

**Commit:** `feat: OpenAI mood parser and ISO principle recommender engine`

---

### Phase 3 — CLI App (45 min)
**Goal: Full conversational terminal experience. This IS the demo.**

Steps:
- [ ] Build `pipeline.py` — the main runnable script
  - Loads labeled CSV + models on startup
  - Prints banner: "Music Mood Therapy"
  - Asks: "How are you feeling right now?"
  - Classifies with `mood_parser`
  - Gets 3 songs with `recommender`
  - Prints formatted output:
    ```
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Detected: Sad

    Your 3-song journey to Happy:

    [1] MATCHING YOUR MOOD
        Track Name — Artist
        Valence: 0.19 | Energy: 0.21
        open.spotify.com/track/...

    [2] THE BRIDGE
        Track Name — Artist
        Valence: 0.50 | Energy: 0.51
        open.spotify.com/track/...

    [3] YOUR DESTINATION
        Track Name — Artist
        Valence: 0.81 | Energy: 0.79
        open.spotify.com/track/...
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Listen through them. How are you feeling now?
    ```
  - If user says anything not "great/good/happy": offer next set
  - Loop continues until user is happy or types "quit"
- [ ] Run via Docker: `docker-compose run backend python src/pipeline.py`
- [ ] Test all 5 mood inputs

**Commit:** `feat: conversational CLI pipeline with ISO song journey`

---

### Phase 4 — Librosa Demo + Polish (30 min)
**Goal: Presentation-ready. Nothing breaks live.**

Steps:
- [ ] Build `demo/librosa_demo.py`
  - Load any local MP3/WAV
  - Extract: tempo, RMS energy, MFCCs (13), chroma (12), spectral centroid
  - Load saved MLP model
  - Predict emotion from extracted features
  - Print features + predicted emotion
  - Run through recommender → show 3 songs
- [ ] Source 2–3 MP3/WAV files for the demo (any local music files)
- [ ] Complete `README.md`:
  - Project description + ISO principle explanation
  - Setup instructions (uv, Docker, .env)
  - How to run: `docker-compose up`
  - Architecture diagram (copy from this file)
  - Defense talking points section
- [ ] Final smoke test: cold `docker-compose up --build`, all 5 test inputs
- [ ] Clean git history — squash any debug commits
- [ ] Final push

**Commit:** `feat: librosa audio demo and complete README`

---

### Phase 5 — Streamlit Frontend (if time allows)
**Build AFTER CLI is fully working. Not required for defense — nice to have.**

- [ ] `frontend/app.py` — text area, button, 3-song display with Spotify links
- [ ] `frontend/pages/about.py` — ISO principle + model explainer
- [ ] Wire via `docker-compose up`

**Commit:** `feat: streamlit UI frontend`

---

## 8. CLI Test Suite — Run These Before Defense

| Input | Expected emotion |
|-------|-----------------|
| "I feel empty and hopeless, nothing excites me" | Sad |
| "Everything is making me so angry right now" | Angry |
| "I'm so pumped and happy, best day ever!" | Happy |
| "I'm nervous and my heart is racing" | Fear |
| "Feeling gross, disgusted by everything" | Disgust |

---

## 9. Defense Talking Points

**"What neural network did you build?"**
A Multi-Layer Perceptron with two hidden layers (128→64 neurons), ReLU activations, and trained with backpropagation on 8 audio features extracted from 114k Spotify tracks. We compared it against a Random Forest baseline.

**"What is the ISO Principle?"**
A technique from clinical music therapy: match the listener's current emotional state first, then gradually guide them toward the target emotion. Jumping straight to happy music when someone is sad creates emotional dissonance. Three songs, three emotional waypoints.

**"What is Russell's Circumplex Model?"**
A 2D psychological model representing emotions on two axes: valence (positive vs negative) and arousal (high vs low energy). Widely used in affective computing. It's how we map emotion labels to numerical coordinates.

**"How does the mood detection work?"**
We send the user's natural language text to GPT-4o-mini with a strict system prompt. It classifies into one of 6 Ekman basic emotions in under 200ms.

**"How do you prevent overfitting?"**
StandardScaler normalises features before the MLP. Early stopping halts training when validation accuracy stops improving. class_weight='balanced' handles class imbalance. 80/20 train/test split gives us an honest accuracy estimate.

**"What are the limitations?"**
Emotion labeling is rule-based from Spotify's pre-extracted features, not human-annotated ground truth. Disgust and Fear overlap acoustically. Emotion is subjective — same song hits differently for different people. The Spotify recommendations API was deprecated so we use a fixed 114k-song catalog.

---

## 10. Key Decisions Log

| Decision | Choice | Reason |
|----------|--------|--------|
| Package manager | `uv` | Modern, fast, deterministic |
| LLM provider | OpenAI GPT-4o-mini | Fast, cheap, great at classification |
| New song discovery | 114k Kaggle catalog + Spotify track_id URLs | Recommendations API deprecated for new apps |
| Frontend | CLI first, Streamlit as Phase 5 | Prove the logic works before building UI |
| Neural network | sklearn MLPClassifier | Real neural network you own and can explain |
| Baseline | Random Forest | Industry standard tabular baseline |
| Extra feature | track_genre encoded | 125 genres = massive emotional signal |
| Deduplication | By track_id | Some tracks span multiple genres in dataset |
| Target emotion | Happy (0.80, 0.80) | Simplest, most defensible |
| GitHub repo | prasannakoirala58/mood-music-therapy | Created |

---

## 11. .env Structure

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Spotify (stored for future use — not used in Phases 0–4)
SPOTIFY_CLIENT_ID=...
SPOTIFY_CLIENT_SECRET=...
```

---

*Last updated: 2026-06-18 — All decisions locked. Ready to execute.*
