from __future__ import annotations

from functools import lru_cache
from typing import List

import spacy


@lru_cache(maxsize=1)
def get_nlp_model() -> object:
    return spacy.load("en_core_web_sm")


def extract_aspects(text: str) -> list[str]:
    if not text:
        return []

    nlp = get_nlp_model()
    doc = nlp(text)

    aspects: set[str] = set()
    for chunk in doc.noun_chunks:
        candidate = " ".join(token.text.lower() for token in chunk if token.is_alpha and len(token.text) >= 2)
        if candidate and candidate not in {"", "the", "and", "or"}:
            aspects.add(candidate)

    for token in doc:
        if token.is_alpha and len(token.text) >= 2 and not token.is_stop and token.pos_ in {"NOUN", "PROPN"}:
            aspects.add(token.text.lower())

    return sorted(aspects)
