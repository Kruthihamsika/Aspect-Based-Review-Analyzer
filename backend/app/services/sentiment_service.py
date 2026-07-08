from __future__ import annotations

from functools import lru_cache
from typing import Any
import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.aspect_sentiment import AspectSentiment
from app.models.detected_aspect import DetectedAspect
from app.models.review import Review
from app.models.uploaded_file import UploadedFile
from app.services.aspect_extractor import extract_aspects, get_nlp_model


SENTIMENT_MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"
LABEL_MAP = {
    "negative": "Negative",
    "neutral": "Neutral",
    "positive": "Positive",
}
CLAUSE_BOUNDARIES = {
    "but",
    "however",
    "though",
    "although",
    "whereas",
    "while",
    ";",
}


@lru_cache(maxsize=1)
def get_sentiment_pipeline() -> Any:
    """Load the HuggingFace sentiment pipeline once per process."""
    try:
        from transformers import pipeline

        return pipeline(
            task="sentiment-analysis",
            model=SENTIMENT_MODEL_NAME,
            tokenizer=SENTIMENT_MODEL_NAME,
        )
    except Exception as exc:
        raise RuntimeError(
            f"Failed to load sentiment model '{SENTIMENT_MODEL_NAME}'."
        ) from exc


class SentimentService:
    def __init__(self, db: Session | None = None) -> None:
        self.db = db

    def analyze_review_aspects(self, review_text: str) -> list[dict[str, str]]:
        """Extract aspects and score sentiment for each aspect-specific context."""
        results: list[dict[str, str]] = []

        for aspect in extract_aspects(review_text):
            context = find_aspect_context(review_text, aspect)
            sentiment = self.analyze_text(context)
            results.append(
                {
                    "aspect": aspect,
                    "sentiment": str(sentiment["label"]),
                }
            )

        return results

    def analyze_text(self, review_text: str) -> dict[str, str | float]:
        if not review_text or not review_text.strip():
            return {"label": "Neutral", "score": 0.0}

        classifier = get_sentiment_pipeline()

        result = classifier(
            review_text,
            truncation=True,
            max_length=512
        )

        prediction = self._first_prediction(result)

        raw_label = prediction["label"].lower()
        score = float(prediction["score"])

        return {
            "label": LABEL_MAP.get(raw_label, raw_label.title()),
            "score": round(score, 4)
        }

    def analyze_for_upload(self, upload_id: str) -> dict[str, Any]:
        if self.db is None:
            raise RuntimeError("Database session is required for upload analysis.")

        # Convert string UUID to UUID object
        try:
            upload_uuid = uuid.UUID(upload_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid upload_id format.",
            )

        uploaded_file = (
            self.db.query(UploadedFile)
            .filter(UploadedFile.id == upload_uuid)
            .first()
        )

        if not uploaded_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Upload not found.",
            )

        aspects = (
            self.db.query(DetectedAspect)
            .join(Review, Review.id == DetectedAspect.review_id)
            .filter(Review.uploaded_file_id == uploaded_file.id)
            .all()
        )

        if not aspects:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No detected aspects found for the provided upload.",
            )

        processed_aspects = 0
        positive = 0
        negative = 0
        neutral = 0

        for detected_aspect in aspects:

            existing = (
                self.db.query(AspectSentiment)
                .filter(
                    AspectSentiment.detected_aspect_id == detected_aspect.id
                )
                .first()
            )

            if existing:
                continue

            review = (
                self.db.query(Review)
                .filter(Review.id == detected_aspect.review_id)
                .first()
            )

            if review is None:
                continue

            context = find_aspect_context(
                review.review_text or "",
                detected_aspect.aspect or detected_aspect.aspect_name,
            )
            sentiment_result = self.analyze_text(context)
            sentiment = str(sentiment_result["label"])
            confidence_score = float(sentiment_result["score"])

            detected_aspect.aspect = detected_aspect.aspect or detected_aspect.aspect_name
            detected_aspect.sentiment = sentiment
            detected_aspect.confidence = confidence_score

            if sentiment == "Positive":
                positive += 1
            elif sentiment == "Negative":
                negative += 1
            else:
                neutral += 1

            new_record = AspectSentiment(
                detected_aspect_id=detected_aspect.id,
                review_id=review.id,
                aspect=detected_aspect.aspect,
                sentiment=sentiment,
                confidence_score=confidence_score,
                confidence=confidence_score,
            )

            self.db.add(new_record)

            processed_aspects += 1

        self.db.commit()

        return {
            "message": "Sentiment analysis completed",
            "upload_id": str(uploaded_file.id),
            "processed_aspects": processed_aspects,
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
        }

    def _first_prediction(self, result: Any) -> dict[str, Any]:
        if isinstance(result, list) and result:
            first_result = result[0]
            if isinstance(first_result, dict):
                return first_result

        raise RuntimeError("Sentiment model returned an invalid response.")


def find_aspect_context(review_text: str, aspect: str) -> str:
    """Return the most relevant text span to score sentiment for an aspect."""
    if not review_text or not review_text.strip():
        return ""

    sentence = find_sentence_containing_aspect(review_text, aspect)
    return find_clause_containing_aspect(sentence, aspect)


def find_sentence_containing_aspect(review_text: str, aspect: str) -> str:
    """Find the sentence that mentions the aspect, falling back to full text."""
    normalized_aspect = normalize_text(aspect)
    if not normalized_aspect:
        return review_text.strip()

    doc = get_nlp_model()(review_text)
    for sentence in doc.sents:
        sentence_text = sentence.text.strip()
        if contains_aspect(sentence_text, normalized_aspect):
            return sentence_text

    return review_text.strip()


def find_clause_containing_aspect(sentence: str, aspect: str) -> str:
    """Narrow mixed sentences to the clause that contains the target aspect."""
    normalized_aspect = normalize_text(aspect)
    clauses = split_into_clauses(sentence)

    for clause in clauses:
        if contains_aspect(clause, normalized_aspect):
            return clause.strip()

    return sentence.strip()


def split_into_clauses(sentence: str) -> list[str]:
    """Split on common contrast boundaries without losing reusable simplicity."""
    doc = get_nlp_model()(sentence)
    clauses: list[str] = []
    current_tokens: list[str] = []

    for token in doc:
        if token.lower_ in CLAUSE_BOUNDARIES:
            if current_tokens:
                clauses.append(" ".join(current_tokens).strip())
                current_tokens = []
            continue

        current_tokens.append(token.text)

    if current_tokens:
        clauses.append(" ".join(current_tokens).strip())

    return [clause for clause in clauses if clause]


def contains_aspect(text: str, normalized_aspect: str) -> bool:
    """Check whether a normalized aspect phrase appears in a text span."""
    normalized_text = normalize_text(text)
    return f" {normalized_aspect} " in f" {normalized_text} "


def normalize_text(text: str) -> str:
    """Normalize text for simple aspect matching."""
    doc = get_nlp_model()(text)
    terms = [
        token.lemma_.lower()
        for token in doc
        if token.is_alpha and not token.is_space
    ]
    return " ".join(terms)
