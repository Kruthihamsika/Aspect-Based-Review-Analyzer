from __future__ import annotations

from functools import lru_cache
from typing import Iterable

import spacy
from spacy.language import Language
from spacy.tokens import Span, Token


SPACY_MODEL_NAME = "en_core_web_sm"

# Domain-neutral words that appear in reviews but are rarely actionable aspects.
GENERIC_ASPECT_TERMS = {
    "app",
    "brand",
    "experience",
    "item",
    "one",
    "order",
    "package",
    "product",
    "purchase",
    "service",
    "stuff",
    "thing",
    "time",
    "unit",
    "use",
    "way",
}

ALLOWED_ASPECT_POS = {"NOUN", "PROPN"}


@lru_cache(maxsize=1)
def get_nlp_model() -> Language:
    """Load spaCy once per process so repeated requests do not reload the model."""
    try:
        return spacy.load(SPACY_MODEL_NAME)
    except OSError as exc:
        raise RuntimeError(
            f"spaCy model '{SPACY_MODEL_NAME}' is not installed. "
            f"Install it with: python -m spacy download {SPACY_MODEL_NAME}"
        ) from exc


def extract_aspects(text: str) -> list[str]:
    """Extract normalized product aspects from review text."""
    if not text or not text.strip():
        return []

    doc = get_nlp_model()(text)
    aspects: dict[str, None] = {}

    for chunk in doc.noun_chunks:
        aspect = _normalize_noun_chunk(chunk)
        if _is_meaningful_aspect(aspect):
            aspects.setdefault(aspect, None)

    return list(aspects)


def _normalize_noun_chunk(chunk: Span) -> str:
    """Convert a noun chunk into a clean aspect phrase."""
    tokens = [_normalize_token(token) for token in _aspect_tokens(chunk)]
    tokens = [token for token in tokens if token]
    return " ".join(tokens)


def _aspect_tokens(chunk: Span) -> Iterable[Token]:
    """Keep the useful noun/proper-noun words from a chunk and drop filler."""
    for token in chunk:
        if token.is_stop or token.is_punct or token.is_space or token.like_num:
            continue
        if not token.is_alpha or len(token.text) < 2:
            continue
        if token.pos_ not in ALLOWED_ASPECT_POS:
            continue
        yield token


def _normalize_token(token: Token) -> str:
    """Lowercase and lemmatize tokens while preserving a sane fallback."""
    lemma = token.lemma_.strip().lower()
    if lemma and lemma != "-pron-":
        return lemma
    return token.text.strip().lower()


def _is_meaningful_aspect(aspect: str) -> bool:
    """Filter out empty, generic, or overly noisy aspect candidates."""
    if not aspect:
        return False

    words = aspect.split()
    if len(words) > 4:
        return False

    if all(word in GENERIC_ASPECT_TERMS for word in words):
        return False

    return True
