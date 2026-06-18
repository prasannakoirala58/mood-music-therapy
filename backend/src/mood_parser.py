"""
mood_parser.py

Sends user mood text to OpenAI GPT-4o-mini with a strict classification prompt.
Returns exactly one of 6 emotion labels: Happy, Sad, Angry, Fear, Disgust, Surprise.

Cost: ~0.0001 USD per call (10 output tokens max).
"""

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

VALID_EMOTIONS = {"Happy", "Sad", "Angry", "Fear", "Disgust", "Surprise"}

SYSTEM_PROMPT = """
You are an emotion classifier for a music therapy application.
The user will describe how they are feeling in natural language.
Classify their mood into exactly ONE of these 6 labels:
Happy, Sad, Angry, Fear, Disgust, Surprise

Rules:
- Return ONLY the label — no punctuation, no explanation, nothing else.
- If the mood is ambiguous, return the closest match.
- Never return anything other than one of the 6 labels above.
"""


def parse_mood(user_text: str) -> str:
    # TODO: call OpenAI, validate response is in VALID_EMOTIONS, return label
    pass


if __name__ == "__main__":
    # Quick smoke test
    test_inputs = [
        "I feel empty and hopeless, nothing excites me",
        "Everything is making me so angry right now",
        "I'm so pumped and happy, best day ever!",
        "I'm nervous and my heart is racing",
        "Feeling gross, disgusted by everything",
    ]
    for text in test_inputs:
        result = parse_mood(text)
        print(f"  {result:10s} ← {text[:60]}")
