import re
from html import unescape


def clean_text(text: str) -> str:
    if not text:
        return ""

    cleaned = unescape(text)
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    cleaned = re.sub(r"http\S+|www\.\S+", " ", cleaned)
    cleaned = re.sub(r"[^\w\s.,!?;:'\-]", " ", cleaned)
    cleaned = re.sub(r"([.,!?;:'-])\1+", r"\1", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip().lower()
