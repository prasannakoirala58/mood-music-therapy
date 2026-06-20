"""
collect_spotify_data.py

Pulls Nepali emotion playlists from Spotify, downloads each song's
30-second preview, extracts audio features with librosa, and saves
a labeled CSV ready for model training.

Why librosa and not Spotify's audio-features API?
Spotify deprecated GET /v1/audio-features for new apps in late 2024.
We compute equivalent features ourselves from the audio preview.

Run (test 5 songs from one playlist):
  cd backend
  uv run python src/collect_spotify_data.py Happy --limit 5

Run all six playlists fully:
  uv run python src/collect_spotify_data.py

Requires http://127.0.0.1:3000 in your Spotify app's Redirect URIs.
"""

import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import spotipy
from dotenv import load_dotenv
from loguru import logger
from spotipy.oauth2 import SpotifyOAuth

from common.features import extract_features as _extract_from_file

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────

REDIRECT_URI = "http://127.0.0.1:3000"
SCOPE        = "playlist-read-private playlist-read-collaborative"
CACHE_PATH   = Path(__file__).parent.parent / ".spotify_cache"
OUTPUT_PATH  = Path(__file__).parent.parent / "data/processed/nepali_dataset.csv"

EMOTION_PLAYLIST_NAMES = {
    "Happy":    "Songs - Happy",
    "Sad":      "Songs - Sad",
    "Angry":    "Songs - Angry",
    "Fear":     "Songs - Fear",
    "Disgust":  "Songs - Disgust",
    "Surprise": "Songs - Surprise",
}

# ── Auth ──────────────────────────────────────────────────────────────────────

def get_client() -> spotipy.Spotify:
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        cache_path=str(CACHE_PATH),
        open_browser=True,
    ))


# ── Playlist discovery ────────────────────────────────────────────────────────

def find_emotion_playlists(sp: spotipy.Spotify) -> dict[str, str]:
    found: dict[str, str] = {}
    results = sp.current_user_playlists(limit=50)
    while results:
        for item in results["items"]:
            name = item["name"].strip()
            for emotion, expected in EMOTION_PLAYLIST_NAMES.items():
                if name == expected:
                    found[emotion] = item["id"]
                    logger.info(f"  Found: '{name}' → {emotion}")
        results = sp.next(results) if results["next"] else None
    return found


# ── Track collection ──────────────────────────────────────────────────────────

def get_playlist_tracks(sp: spotipy.Spotify, playlist_id: str, limit: int | None = None) -> list[dict]:
    """Return list of {id, name, artists, preview_url} for each track."""
    tracks: list[dict] = []
    results = sp.playlist_tracks(playlist_id)

    while results:
        for item in results["items"]:
            track = item.get("item") or item.get("track")
            if not track or not track.get("id"):
                continue
            tracks.append({
                "id":          track["id"],
                "name":        track["name"],
                "artists":     ", ".join(a["name"] for a in track.get("artists", [])),
                "preview_url": track.get("preview_url"),
            })
            if limit and len(tracks) >= limit:
                return tracks
        results = sp.next(results) if results.get("next") else None

    return tracks


# ── Audio feature extraction ──────────────────────────────────────────────────

def extract_features(track_name: str, artists: str) -> dict | None:
    """
    Search YouTube for the song, download full audio, extract features via common/features.py.
    Temp directory is deleted automatically after processing.
    """
    query = f"{track_name} {artists}"
    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            subprocess.run([
                "yt-dlp", f"ytsearch1:{query}",
                "--extract-audio", "--audio-format", "mp3", "--audio-quality", "9",
                "--no-playlist", "--quiet",
                "-o", str(Path(tmp_dir) / "%(title)s.%(ext)s"),
            ], capture_output=True, text=True, timeout=90)

            mp3_files = list(Path(tmp_dir).glob("*.mp3"))
            if not mp3_files:
                logger.warning(f"  yt-dlp found nothing for: {query}")
                return None

            return _extract_from_file(str(mp3_files[0]))

    except Exception as e:
        logger.warning(f"  Download/load failed: {e}")
        return None


# ── Main ──────────────────────────────────────────────────────────────────────

def collect(emotions: list[str] | None = None, limit: int | None = None) -> pd.DataFrame:
    sp = get_client()

    # Load already-processed track IDs so we skip re-downloading them.
    # This makes the command incremental: only new songs added to Spotify get downloaded.
    already_done: set[str] = set()
    if OUTPUT_PATH.exists():
        already_done = set(pd.read_csv(OUTPUT_PATH)["track_id"].astype(str))
        logger.info(f"Existing dataset: {len(already_done)} songs — will skip these")

    logger.info("Discovering emotion playlists…")
    playlist_map = find_emotion_playlists(sp)

    target_emotions = emotions or list(EMOTION_PLAYLIST_NAMES.keys())
    rows: list[dict] = []

    for emotion in target_emotions:
        if emotion not in playlist_map:
            logger.warning(f"Skipping {emotion} — playlist not found")
            continue

        logger.info(f"\n[{emotion}] Fetching tracks…")
        tracks = get_playlist_tracks(sp, playlist_map[emotion], limit=limit)

        new_tracks = [t for t in tracks if t["id"] not in already_done]
        skipped    = len(tracks) - len(new_tracks)

        if skipped:
            logger.info(f"[{emotion}] {len(tracks)} in playlist — {skipped} already processed, {len(new_tracks)} new")
        else:
            logger.info(f"[{emotion}] {len(new_tracks)} new tracks to process")

        if not new_tracks:
            continue

        for i, track in enumerate(new_tracks):
            name = track["name"]

            logger.info(f"  [{i+1}/{len(new_tracks)}] '{name}' by {track['artists']}")
            features = extract_features(name, track["artists"])

            if not features:
                logger.warning(f"  └─ feature extraction failed, skipping")
                continue

            logger.info(
                f"  └─ V={features['valence']} E={features['energy']} "
                f"T={features['tempo']} mode={'major' if features['mode'] else 'minor'}"
            )

            rows.append({
                "track_id":   track["id"],
                "track_name": name,
                "artists":    track["artists"],
                "emotion":    emotion,
                **features,
            })

            time.sleep(0.05)

    if not rows:
        logger.info("No new songs to add.")
        return pd.DataFrame()

    df = pd.DataFrame(rows).drop_duplicates(subset="track_id")
    logger.info(f"\n{'─'*50}")
    logger.info(f"New songs collected: {len(df)}")
    logger.info(f"\n{df['emotion'].value_counts().to_string()}")
    return df


if __name__ == "__main__":
    # Usage:
    #   uv run python src/collect_spotify_data.py                  → all 6 playlists
    #   uv run python src/collect_spotify_data.py Happy            → one playlist
    #   uv run python src/collect_spotify_data.py Happy --limit 5  → first 5 songs only

    emotions = None
    limit    = None

    args = sys.argv[1:]
    if args and not args[0].startswith("--"):
        emotions = [args[0]]
        args = args[1:]
    if "--limit" in args:
        limit = int(args[args.index("--limit") + 1])

    df = collect(emotions=emotions, limit=limit)

    if df.empty:
        logger.error("No data collected.")
        sys.exit(1)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Merge with existing data so running one playlist at a time doesn't wipe others
    if OUTPUT_PATH.exists():
        existing = pd.read_csv(OUTPUT_PATH)
        df = pd.concat([existing, df], ignore_index=True).drop_duplicates(subset="track_id")
        logger.info(f"Merged with existing data → {len(df)} total tracks")

    df.to_csv(OUTPUT_PATH, index=False)
    logger.success(f"\nSaved → {OUTPUT_PATH}  ({len(df)} tracks)")
    logger.info("\nSample rows:")
    print(df[["track_name", "artists", "emotion", "valence", "energy", "tempo", "mode"]].head(5).to_string(index=False))
