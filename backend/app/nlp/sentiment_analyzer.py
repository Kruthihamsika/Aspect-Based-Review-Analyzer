from __future__ import annotations

import re
from typing import Final

POSITIVE_WORDS: Final[set[str]] = {
    "good",
    "great",
    "excellent",
    "awesome",
    "love",
    "best",
    "nice",
    "happy",
    "fantastic",
    "amazing",
    "perfect",
    "satisfied",
    "recommend",
    "fast",
    "easy",
    "beautiful",
    "worth",
}

NEGATIVE_WORDS: Final[set[str]] = {
    "bad",
    "terrible",
    "awful",
    "poor",
    "hate",
    "worst",
    "disappointing",
    "slow",
    "hard",
    "broken",
    "useless",
    "problem",
    "issue",
    "complaint",
    "expensive",
    "annoying",
    "bug",
    "weak",
}


def analyze_sentiment(text: str) -> str:
    if not text:
        return "Neutral"

    normalized = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    tokens = set(normalized.split())

    positive_hits = sum(1 for token in tokens if token in POSITIVE_WORDS)
    negative_hits = sum(1 for token in tokens if token in NEGATIVE_WORDS)

    if positive_hits > negative_hits:
        return "Positive"
    if negative_hits > positive_hits:
        return "Negative"
    return "Neutral"
