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

| Tool | Decision | Reason |
|------|----------|--------|
| Python | 3.11 | pinned in `.python-version` |
| Package manager | `uv` | NOT pip, NOT poetry, NOT conda |
| Containers | Docker + docker-compose | All code runs in containers |
| LLM | OpenAI GPT-4o-mini | `OPENAI_API_KEY` in `.env` |
| ML | scikit-learn RF + MLPClassifier | Both trained, both compared |
| Frontend | Streamlit (Phase 5 only) | CLI runs first |

**Never suggest pip install.** Always `uv add <package>` for new dependencies.

---

## Project Structure

```
mood-music-therapy/
├── backend/          ← ML pipeline, CLI app, all Python logic
│   ├── src/          ← importable modules
│   ├── data/raw/     ← dataset.csv (git-ignored, 20MB)
│   ├── data/processed/ ← dataset_labeled.csv (git-ignored, generated)
│   ├── models/       ← .pkl files (git-ignored, generated)
│   └── demo/         ← librosa demo for presentation
├── frontend/         ← Streamlit UI (Phase 5)
├── docker-compose.yml
├── .env              ← NEVER committed
└── ROADMAP.md        ← Full system design and phase plan
```

---

## Build Phases — Current State

- [x] Phase 0 — Scaffold complete (this setup)
- [ ] Phase 1 — Data labeling + model training
- [ ] Phase 2 — Mood parser + ISO recommender
- [ ] Phase 3 — CLI pipeline (main app)
- [ ] Phase 4 — Librosa demo + polish
- [ ] Phase 5 — Streamlit frontend

**See ROADMAP.md for the full detailed breakdown of each phase.**

---

## How to Run

```bash
# Install dependencies (backend)
cd backend && uv sync

# Run the CLI app
uv run python src/pipeline.py

# Run data labeling (Phase 1)
uv run python src/label_emotions.py

# Run model training (Phase 1)
uv run python src/train_classifier.py

# Run via Docker
docker-compose run backend

# Run frontend (Phase 5)
docker-compose up frontend
```

---

## Rules for Claude Code — Read Carefully

### 1. Never assume. Always ask.
If a decision is not already documented in ROADMAP.md or this file, ask before implementing.
This includes: library choices, model hyperparameters, emotion threshold values, UI layout decisions, API choices.
The student (Prasanna) needs to understand and defend every decision. Surprises are bad.

### 2. Work like a senior engineer, not a code generator.
- Explain WHY before writing code, not just WHAT.
- Flag tradeoffs when they exist.
- If two approaches are valid, present them briefly and ask which to use.
- Don't over-engineer. Simple, readable, correct beats clever.

### 3. No silent decisions.
If you change something that was previously decided (a threshold, a model parameter, a file path), say so explicitly. Never silently upgrade or refactor existing working code without flagging it.

### 4. One phase at a time.
Do not jump ahead to Phase 3 code while Phase 1 is incomplete. Complete each phase fully before starting the next.

### 5. Keep implementation lean.
- No comments explaining WHAT the code does — use good names instead.
- Only add a comment when the WHY is non-obvious (a known edge case, a workaround, a constraint).
- No unused imports or variables.
- No TODO comments in production code — either implement it or raise it in conversation.

### 6. Data files are git-ignored for a reason.
Never suggest committing `dataset.csv`, `dataset_labeled.csv`, or `.pkl` files.
They are either too large (20MB CSV) or generated artifacts.

### 7. Environment variables only.
API keys and credentials live in `.env` only. Never hardcode them. Never print them. Never suggest storing them anywhere else.

### 8. uv is the package manager.
- To add a dependency: `uv add <package>` (run from the backend/ or frontend/ directory)
- To install all deps: `uv sync`
- To run a script: `uv run python src/script.py`
- Never use `pip install` in this project.

---

## Key Files to Know

| File | Purpose |
|------|---------|
| `ROADMAP.md` | Full system design, architecture diagrams, phase breakdown |
| `backend/src/label_emotions.py` | Rule-based emotion labeling — Phase 1 |
| `backend/src/train_classifier.py` | RF + MLP training — Phase 1 |
| `backend/src/mood_parser.py` | OpenAI mood classification — Phase 2 |
| `backend/src/recommender.py` | ISO engine + nearest neighbor search — Phase 2 |
| `backend/src/pipeline.py` | CLI conversation loop — Phase 3 |
| `backend/demo/librosa_demo.py` | Raw audio demo — Phase 4 |

---

## Important Context for Responses

- **Audience:** The code will be demoed to a university assessor. It needs to be clean, explainable, and defensible.
- **The student is learning.** Prasanna is a Data Analytics student — he understands concepts but is building toward engineering fluency. Meet him at his level. Explain decisions in plain language, not jargon.
- **Time-boxed.** This is a 3-day build. Don't suggest scope beyond what's in ROADMAP.md unless explicitly asked.
- **Emotion labels are always these 6:** Happy, Sad, Angry, Fear, Disgust, Surprise. Do not add more. Do not reduce to fewer.
- **Target emotion is always Happy.** The ISO journey always ends at Happy. Do not make this configurable unless asked.
