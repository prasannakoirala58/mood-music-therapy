"""
mood_parser.py

Sends user mood text to OpenAI GPT-4o-mini with a strict classification prompt.
Returns exactly one of 6 emotion labels: Happy, Sad, Angry, Fear, Disgust, Surprise.

Cost: ~$0.0001 per call (10 output tokens max at GPT-4o-mini pricing).
"""

import os
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

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=10,
        temperature=0,        # deterministic — same input always returns same label
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
    )

    label = response.choices[0].message.content.strip()

    # Normalise capitalisation in case the model returns "sad" instead of "Sad"
    label = label.capitalize()

    if label not in VALID_EMOTIONS:
        # Fallback: if model somehow returns something unexpected, default to Sad
        # (low-energy, low-valence is the safest neutral fallback for a therapy app)
        return "Sad"

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
