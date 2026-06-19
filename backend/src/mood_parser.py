"""
mood_parser.py

Sends user mood text to OpenAI GPT-4o-mini with a strict classification prompt.
Returns exactly one of 6 emotion labels: Happy, Sad, Angry, Fear, Disgust, Surprise.

Cost: ~$0.0001 per call (10 output tokens max at GPT-4o-mini pricing).
"""

import os
import time

from loguru import logger
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

VALID_EMOTIONS = {"Happy", "Sad", "Angry", "Fear", "Disgust", "Surprise"}

SYSTEM_PROMPT = """You are an emotion classifier for a music therapy application.
The user will describe how they are feeling in natural language.
Classify their mood into exactly ONE of these 6 labels:
Happy, Sad, Angry, Fear, Disgust, Surprise

Rules:
- Return ONLY the label. No punctuation. No explanation. Nothing else.
- If the mood is ambiguous, return the closest match.
- Never return anything other than one of the 6 labels above."""


def parse_mood(user_text: str) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    logger.info(f"[MOOD] parsing: '{user_text[:80]}{'...' if len(user_text) > 80 else ''}'")

    t0 = time.perf_counter()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=10,
        temperature=0,        # deterministic — same input always returns same label
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
    )
    elapsed_ms = (time.perf_counter() - t0) * 1000

    raw = response.choices[0].message.content.strip()
    label = raw.capitalize()

    if label not in VALID_EMOTIONS:
        # Fallback: if model somehow returns something unexpected, default to Sad
        logger.warning(f"[MOOD] unexpected label from GPT: {raw!r} — defaulting to Sad")
        return "Sad"

    logger.info(f"[MOOD] '{label}' ({elapsed_ms:.0f}ms)")
    return label


if __name__ == "__main__":
    test_cases = [
        ("I feel empty and hopeless, nothing excites me",          "Sad"),
        ("Everything is making me so angry right now",             "Angry"),
        ("I'm so pumped and happy, best day ever!",                "Happy"),
        ("I'm nervous and my heart is racing",                     "Fear"),
        ("Feeling gross and disgusted by everything around me",    "Disgust"),
        ("I just got the most unexpected news, totally shocked",   "Surprise"),
    ]

    print("Testing mood parser...\n")
    passed = 0
    for text, expected in test_cases:
        result = parse_mood(text)
        status = "✓" if result == expected else "✗"
        print(f"  {status} [{result:<9}] {text[:55]}")
        if result == expected:
            passed += 1

    print(f"\n  {passed}/{len(test_cases)} passed")
