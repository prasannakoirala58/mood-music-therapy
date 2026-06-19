# CLAUDE.md — Music Mood Therapy Project

This file is the source of truth for how Claude Code should behave in this project.
Read this before touching any file.

---

## What This Project Is

A Music Mood Therapy recommendation engine built as a Data Analytics academic project.

**Core concept:** User describes their mood → OpenAI classifies their emotion → MLP neural network classifies each recommended song live → 3 songs guide them from that emotional state toward Happy via the **ISO Principle** from clinical music therapy (match → bridge → target).

**Academic backbone:** Russell's Circumplex Model (1980), Ekman's 6 basic emotions, ISO Principle from clinical music therapy.

---

## Tech Stack — Non-Negotiable

| Layer | Tool | Notes |
|-------|------|-------|
| Language | Python 3.11 | Pinned in `backend/.python-version` |
| Package manager | `uv` | NOT pip, NOT poetry, NOT conda — ever |
| Containers | Docker + docker-compose | Full stack via `docker compose up --build` |
| LLM | OpenAI GPT-4o-mini | `OPENAI_API_KEY` in `.env` |
| ML | scikit-learn RF + MLPClassifier | Both trained; MLP runs live in recommendations |
| REST API | FastAPI + uvicorn | `backend/src/api.py`, port 8000 |
| Logging | Loguru | `from loguru import logger` — zero config, colored, structured |
| Frontend | React 18 + TypeScript + Tailwind CSS + Vite | NOT Streamlit, NOT plain JSX |
| Frontend runtime | Node 20 | Dockerfile in `frontend/` |
| Entry point (CLI) | `make start` | Trains if needed, then runs CLI |
| Entry point (web) | `make api` + `make frontend` | Two terminals, or `docker compose up` |

**Never suggest `pip install`.** Always `uv add <package>` run from `backend/`.
**Never suggest Streamlit.** Frontend is React + TypeScript in `frontend/src/`.
**Frontend source files use `.tsx` and `.ts` — never `.jsx` or `.js`.**

---

## Project Structure — Current State

```
music-therapy/
│
├── backend/                        ← Python: ML pipeline + API + CLI
│   ├── src/
│   │   ├── label_emotions.py       ← Rule-based emotion labeling (89k songs)
│   │   ├── train_classifier.py     ← Trains RF + MLP, saves .pkl files
│   │   ├── mood_parser.py          ← OpenAI: text → emotion label
│   │   ├── recommender.py          ← ISO engine + live MLP inference per song
│   │   ├── pipeline.py             ← Conversational CLI loop
│   │   └── api.py                  ← FastAPI REST server (POST /api/recommend)
│   ├── data/
│   │   ├── raw/dataset.csv         ← Kaggle download (git-ignored, 20MB)
│   │   └── processed/              ← dataset_labeled.csv (git-ignored, generated)
│   ├── models/                     ← .pkl files (git-ignored, generated)
│   │   ├── emotion_classifier_rf.pkl
│   │   ├── emotion_classifier_mlp.pkl
│   │   └── genre_label_encoder.pkl
│   ├── demo/librosa_demo.py        ← Raw audio → features → recommend
│   ├── pyproject.toml
│   ├── uv.lock
│   └── Dockerfile
│
├── frontend/                       ← React 18 + TypeScript + Tailwind + Vite
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── types.ts                ← Shared TypeScript interfaces
│   │   ├── vite-env.d.ts
│   │   ├── index.css
│   │   ├── components/
│   │   │   ├── MoodInput.tsx
│   │   │   ├── ResultsPanel.tsx
│   │   │   ├── SongCard.tsx
│   │   │   └── ResonanceMap.tsx    ← Signature element: dot on Russell's Circumplex
│   │   ├── hooks/useRecommend.ts
│   │   └── lib/emotions.ts
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── .env.local                  ← VITE_API_URL (git-ignored)
│   ├── .env.local.example
│   └── Dockerfile
│
├── Makefile
├── docker-compose.yml
├── .env                            ← NEVER committed
├── .env.example
├── .gitignore
├── README.md
├── ROADMAP.md
└── CLAUDE.md                       ← This file
```

---

## Execution Flow

```
SETUP (run once per machine):
  make train
    └─ label_emotions.py    →  dataset_labeled.csv  (89k songs with emotion labels)
    └─ train_classifier.py  →  emotion_classifier_rf.pkl
                            →  emotion_classifier_mlp.pkl
                            →  genre_label_encoder.pkl

WEB APP (two terminals):
  Terminal 1:  make api          →  FastAPI on http://localhost:8000
  Terminal 2:  make frontend     →  React   on http://localhost:5173

  Request flow (POST /api/recommend):
    1. user text → OpenAI GPT-4o-mini       → emotion label (e.g. "Sad")
    2. emotion  → ISO waypoints              → 3 (valence, energy) coordinates
    3. waypoint → nearest-neighbour in CSV  → candidate song
    4. song features → MLP.predict()        → live emotion classification
    5. return { emotion, songs[3] }          → React frontend

CLI APP:
  make start   →  pipeline.py  (trains models first if missing)

FULL STACK VIA DOCKER:
  docker compose up --build

DEMO:
  make demo FILE=path/to/song.mp3
```

---

## Build Phases — All Complete

- [x] Phase 0 — Scaffold, Docker, uv, folder structure, GitHub
- [x] Phase 1 — Data labeling (`label_emotions.py`) + RF + MLP training
- [x] Phase 2 — Mood parser (`mood_parser.py`) + ISO recommender with live MLP inference
- [x] Phase 3 — Conversational CLI pipeline (`pipeline.py`)
- [x] Phase 4 — Librosa audio demo (`demo/librosa_demo.py`)
- [x] Phase 5 — React + TypeScript frontend + FastAPI REST API
- [x] Phase 6 — Structured Loguru logging + MLP quality gate (retry on mismatch)

---

## Security Practices

### Secrets and credentials
- All API keys live in `.env` only — never hardcoded, never printed, never logged.
- `.env` is in `.gitignore` and must never be committed under any circumstance.
- `.env.example` is committed with empty placeholder values only.
- Frontend API URL is in `frontend/.env.local` — also git-ignored.

### API surface
- CORS is locked to `localhost:5173` and `localhost:3000` — no wildcard `*` origins.
- All request bodies validated by Pydantic before any processing.
- The API is stateless — no user data is stored anywhere.
- If deployed publicly, add authentication before exposing the endpoint.

### Dependencies
- `backend/uv.lock` pins every Python dependency to exact versions — `uv sync` reproduces exactly.
- `frontend/package-lock.json` pins every JS dependency.
- Never run `npm audit fix --force` without reviewing the changes.

### Code
- No shell commands constructed from user input — zero command injection surface.
- OpenAI call uses `temperature=0` — deterministic, minimises prompt injection impact.
- Model `.pkl` files are loaded with `joblib` — never unpickle files from untrusted sources.

---

## Rules for Claude Code

### 1. Never assume. Always ask.
If a decision is not documented here or in ROADMAP.md, ask before implementing.
Prasanna must understand and defend every decision at assessment. No surprises.

### 2. Work like a senior engineer, not a code generator.
- Explain WHY before writing code.
- Flag tradeoffs when they exist.
- Simple, readable, correct beats clever. Don't over-engineer.

### 3. No silent decisions.
If you change anything previously decided (a threshold, a hyperparameter, a file path), say so explicitly. Never silently refactor working code without flagging it.

### 4. Keep implementation lean.
- No comments explaining WHAT the code does — good names do that.
- Only add a comment when the WHY is non-obvious (a constraint, a known edge case).
- No unused imports. No dead code.

### 5. Data and model files are git-ignored for a reason.
Never suggest committing `dataset.csv`, `dataset_labeled.csv`, or `.pkl` files.

### 6. Environment variables only.
API keys in `.env`. Never hardcode. Never print. Never log.

### 7. uv is the package manager — without exception.
- Add a dependency: `cd backend && uv add <package>`
- Install all deps: `cd backend && uv sync`
- User-facing commands: always `make <target>`.

### 8. Frontend is React + TypeScript. Not Streamlit. Not Flask.
All frontend source files are `.tsx` / `.ts` in `frontend/src/`.
The REST API layer is FastAPI — do not add a different server framework.

### 9. Six emotions only. Target is always Happy.
`Happy, Sad, Angry, Fear, Disgust, Surprise` — never add or remove labels.
ISO journey always ends at `(valence=0.80, energy=0.80)`. Not configurable.

---

## Key Context for Every Response

- **Audience:** University assessor. Code must be clean, explainable, and defensible.
- **Student level:** Data Analytics student — explain decisions in plain language.
- **Spotify links are free:** `https://open.spotify.com/track/{track_id}` — no API calls.
- **Spotify Recommendations API is deprecated** (post late 2024). Use Kaggle dataset only.
- **MLP is live:** The neural network runs inference on every recommended song — it is not just a training artifact.
- **Variety by design:** Recommender samples from top-K nearest songs so each session gets different results.
