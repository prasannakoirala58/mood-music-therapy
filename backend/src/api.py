"""
api.py — FastAPI REST API server

Exposes the mood recommendation pipeline over HTTP so the React frontend
can call it. Single endpoint: POST /api/recommend

The MLP neural network is loaded once at startup and passed into every
recommendation call — each song's emotion label is a live ML prediction.

Run with:  cd backend && uv run uvicorn src.api:app --reload --port 8000
       or: make api (from project root)
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import BaseModel

from mood_parser import parse_mood
from recommender import recommend

app = FastAPI(title="Music Mood Therapy API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

DATASET_PATH = Path(__file__).parent.parent / "data/processed/dataset_labeled.csv"
MLP_PATH     = Path(__file__).parent.parent / "models/emotion_classifier_mlp.pkl"
ENCODER_PATH = Path(__file__).parent.parent / "models/genre_label_encoder.pkl"


@app.on_event("startup")
async def load_resources() -> None:
    for path in (DATASET_PATH, MLP_PATH, ENCODER_PATH):
        if not path.exists():
            logger.error(f"Required file not found: {path}")
            raise RuntimeError(
                f"Required file not found: {path}\n"
                "Run 'make train' from the project root first."
            )

    app.state.df            = pd.read_csv(DATASET_PATH)
    app.state.mlp           = joblib.load(MLP_PATH)
    app.state.genre_encoder = joblib.load(ENCODER_PATH)

    logger.info(f"Dataset loaded       | {len(app.state.df):,} songs")
    logger.info(f"MLP model loaded     | {MLP_PATH.name}")
    logger.info(f"Genre encoder loaded | {ENCODER_PATH.name}")
    logger.info("API ready — listening on :8000")


# ── Request / Response models ────────────────────────────────────────────────

class MoodRequest(BaseModel):
    text: str


class Song(BaseModel):
    track_name: str
    artists: str
    emotion: str       # live MLP prediction — not a CSV tag
    valence: float
    energy: float
    track_id: str
    spotify_url: str


class RecommendResponse(BaseModel):
    emotion: str       # detected user emotion (OpenAI)
    songs: list[Song]


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.post("/api/recommend", response_model=RecommendResponse)
async def recommend_songs(req: MoodRequest, request: Request) -> RecommendResponse:
    if not req.text.strip():
        raise HTTPException(status_code=422, detail="Mood text cannot be empty.")

    logger.info("─" * 60)
    logger.info(f"POST /api/recommend  | client={request.client.host if request.client else 'unknown'}")

    t0 = time.perf_counter()

    emotion = parse_mood(req.text)
    songs   = recommend(
        emotion,
        app.state.df,
        mlp_model=app.state.mlp,
        genre_encoder=app.state.genre_encoder,
    )

    elapsed_ms = (time.perf_counter() - t0) * 1000
    logger.info(
        f"[DONE] emotion={emotion} | songs={len(songs)} | total={elapsed_ms:.0f}ms"
    )

    return RecommendResponse(emotion=emotion, songs=songs)


@app.get("/health")
async def health() -> dict:
    songs_loaded = len(app.state.df) if hasattr(app.state, "df") else 0
    model_status = "MLP loaded" if hasattr(app.state, "mlp") else "not loaded"
    logger.info(f"GET /health | songs={songs_loaded:,} | model={model_status}")
    return {
        "status": "ok",
        "songs_loaded": songs_loaded,
        "model": model_status,
    }
