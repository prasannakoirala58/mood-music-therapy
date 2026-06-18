# CLAUDE.md — Music Mood Therapy Project

This file is the source of truth for how Claude Code should behave in this project.
Read this before touching any file.

---

## What This Project Is

A Music Mood Therapy recommendation engine built as a Data Analytics academic project.

**Core concept:** User describes their mood in 2–3 sentences → OpenAI classifies their emotion → 3 songs guide them from that emotional state toward Happy via the **ISO Principle** from music therapy (match → bridge → target).

**Academic backbone:** Russell's Circumplex Model (1980), Ekman's 6 basic emotions, ISO Principle from clinical music therapy.

**Defense date:** Coming up soon. Quality over speed, but both matter.

---

## Tech Stack — Non-Negotiable

| Layer | Tool | Decision |
|-------|------|----------|
| Language | Python 3.11 | Pinned in `backend/.python-version` |
| Package manager | `uv` | NOT pip, NOT poetry, NOT conda — ever |
| Containers | Docker + docker-compose | Full stack runs in containers |
| LLM | OpenAI GPT-4o-mini | `OPENAI_API_KEY` in `.env` — cheapest, fastest |
| ML | scikit-learn RF + MLPClassifier | Both trained, accuracy compared side-by-side |
| Frontend | React 18 + Tailwind CSS + Vite | NOT Streamlit — proper JS frontend |
| Frontend runtime | Node 20 | Dockerfile in `frontend/` |
| Entry point | `make start` | Single command to run the whole project |

**Never suggest `pip install`.** Always `uv add <package>` run from `backend/`.
**Never suggest Streamlit.** Frontend is React/JSX.

---

## Project Structure

```
mood-music-therapy/
│
├── backend/                    ← All Python — ML pipeline + CLI app
│   ├── src/
│   │   ├── label_emotions.py   ← Phase 1: stamp 114k songs with emotion labels
│   │   ├── train_classifier.py ← Phase 1: train RF + MLP, save .pkl files
│   │   ├── mood_parser.py      ← Phase 2: OpenAI text → emotion label
│   │   ├── recommender.py      ← Phase 2: ISO engine → 3 Spotify-linked songs
│   │   └── pipeline.py         ← Phase 3: conversational CLI loop (main app)
│   ├── data/
│   │   ├── raw/dataset.csv     ← Kaggle download (git-ignored, 20MB)
│   │   └── processed/          ← dataset_labeled.csv (git-ignored, generated)
│   ├── models/                 ← .pkl files (git-ignored, generated)
│   ├── demo/librosa_demo.py    ← Phase 4: raw audio → features → recommend
│   ├── pyproject.toml          ← uv dependency manifest
│   ├── uv.lock                 ← pinned exact versions (committed)
│   └── Dockerfile
│
├── frontend/                   ← React 18 + Tailwind CSS + Vite
│   ├── src/
│   │   ├── components/
│   │   │   └── ChatInterface.jsx  ← Phase 5
│   │   ├── hooks/useChat.js       ← Phase 5
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── Dockerfile              ← Node 20 Alpine
│
├── Makefile                    ← ALL run commands live here
├── docker-compose.yml
├── .env                        ← NEVER committed
├── .env.example                ← committed, empty values
├── .gitignore
├── README.md
├── ROADMAP.md                  ← Full system design and phase breakdown
└── CLAUDE.md                   ← This file
```

---

## How to Run — All Commands via Makefile

```bash
make install    # Install backend Python deps via uv (run once after cloning)
make train      # Label data + train RF + MLP models (run once before first use)
make run        # Run the CLI app (requires models to exist)
make start      # Smart: trains models if missing, then runs the app
make clean      # Delete generated data + model files (forces retrain)
make help       # List all available commands
```

**Locally (recommended during dev):**
```bash
cd mood-music-therapy
make start
```

**Via Docker:**
```bash
make docker-build
make docker-run
```

**You never need to remember a `uv run python src/...` command.** Use `make`.

---

## Build Phases — Current State

- [x] Phase 0 — Scaffold, Docker, uv, folder structure, GitHub
- [ ] Phase 1 — Data labeling (`label_emotions.py`) + model training (`train_classifier.py`)
- [ ] Phase 2 — Mood parser (`mood_parser.py`) + ISO recommender (`recommender.py`)
- [ ] Phase 3 — CLI pipeline (`pipeline.py`) — the main demo
- [ ] Phase 4 — Librosa audio demo + README polish
- [ ] Phase 5 — React + Tailwind frontend (after CLI works end-to-end)

**See ROADMAP.md for full per-phase breakdown with step-by-step tasks.**

---

## Execution Flow (burn this into memory)

```
SETUP (runs once):
  make train
    └─ label_emotions.py    →  data/processed/dataset_labeled.csv
    └─ train_classifier.py  →  models/emotion_classifier_rf.pkl
                            →  models/emotion_classifier_mlp.pkl

APP (runs every time):
  make run
    └─ pipeline.py
         ├─ mood_parser.py   →  OpenAI API  →  "Sad"
         └─ recommender.py   →  CSV search  →  3 songs + Spotify links

DEMO (presentation only):
  uv run python demo/librosa_demo.py <audio.mp3>
    └─ librosa → features → MLP predict → recommender → 3 songs
```

---

## Rules for Claude Code — Read Carefully

### 1. Never assume. Always ask.
If a decision is not already documented in ROADMAP.md or this file, ask before implementing.
This includes: library choices, model hyperparameters, emotion threshold values, UI layout.
Prasanna needs to understand and defend every decision at his assessment. No surprises.

### 2. Work like a senior engineer, not a code generator.
- Explain WHY before writing code, not just WHAT.
- Flag tradeoffs when they exist.
- If two valid approaches exist, present them briefly and ask which to use.
- Simple, readable, correct beats clever. Don't over-engineer.

### 3. No silent decisions.
If you change something previously decided (a threshold, a hyperparameter, a file path),
say so explicitly. Never silently refactor working code without flagging it.

### 4. One phase at a time.
Do not write Phase 3 code while Phase 1 is incomplete. Finish each phase fully first.

### 5. Keep implementation lean.
- No comments that explain WHAT the code does — good names do that.
- Only add a comment when the WHY is non-obvious (a constraint, a known edge case).
- No unused imports. No dead code. No TODO comments in final implementations.

### 6. Data files are git-ignored for a reason.
Never suggest committing `dataset.csv`, `dataset_labeled.csv`, or `.pkl` files.
They are either too large (20MB) or generated artifacts.

### 7. Environment variables only.
API keys and credentials live in `.env` only. Never hardcode. Never print. Never suggest
storing them anywhere else.

### 8. uv is the package manager — without exception.
- Add a dependency: `cd backend && uv add <package>`
- Install all deps: `cd backend && uv sync`
- Run a script directly: `cd backend && uv run python src/script.py`
- User-facing command: `make <target>` — never raw uv commands to the user.

### 9. Frontend is React + Tailwind. Not Streamlit. Not Flask. Not Jinja.
Phase 5 frontend is JSX components in `frontend/src/`. API between backend and frontend
will be discussed when Phase 5 begins. Do not add any server framework to backend
until that decision is made explicitly.

---

## Key Context for Every Response

- **Audience:** University assessor. Code must be clean, explainable, and defensible.
- **Student level:** Data Analytics student building toward engineering fluency. Explain decisions in plain language. Don't assume deep CS knowledge.
- **Time-boxed:** 3-day build. No scope beyond ROADMAP.md unless explicitly requested.
- **6 emotions only:** Happy, Sad, Angry, Fear, Disgust, Surprise. Never add or remove.
- **Target is always Happy:** ISO journey always ends at (valence=0.80, energy=0.80). Not configurable.
- **Spotify links are free:** `https://open.spotify.com/track/{track_id}` — no API calls needed.
- **Spotify Recommendations API is deprecated** for apps created after late 2024. Use 114k Kaggle dataset only.
