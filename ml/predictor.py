# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

"""
The one entry point the rest of the app should use for FR8 predictions.

Anything that can go wrong with the AI feature, missing model files,
corrupt files, a model throwing an unexpected error, gets caught in here
and turned into a plain "not available" result instead of an exception.
That's on purpose. Ticket creation should never break just because the
optional AI suggestion couldn't run (see FR8's exceptional flow E1 in the
report, the system falls back to manual categorisation). Callers like
ml/services.py never need their own try/except around this.
"""

from __future__ import annotations

import hashlib
import logging
import math
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from django.conf import settings

from .classifier import TextClassifier
from .security_keywords import keyword_match

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PredictionResult:
    """Everything the rest of the app might want to know about one
    prediction attempt, packaged together so callers get one object back
    instead of several loose return values."""

    available: bool
    category_available: bool = False
    category: str = ""
    confidence: float = 0.0
    category_model_name: str = ""
    category_model_version: str = ""
    is_security_flagged: bool = False
    security_confidence: float | None = None
    security_threshold: float = 0.5
    matched_keywords: tuple[str, ...] = ()


@lru_cache(maxsize=4)
def _load_classifier(path_value: str) -> TextClassifier:
    # Loading a joblib model from disk takes a bit of time, and this
    # function runs on every single ticket created, so the loaded model
    # is kept in memory for the life of the process instead of being
    # re-read from disk each time. lru_cache is keyed on the path string,
    # so if the setting ever points somewhere new it just caches a new
    # entry instead of serving a stale model.
    return TextClassifier.load(Path(path_value))


@lru_cache(maxsize=4)
def _artifact_hash(path_value: str) -> str:
    # A short fingerprint of the exact model file used. Stored alongside
    # each prediction so it's always possible to prove which trained
    # model produced which suggestion. Useful for the report and for
    # debugging if the model gets retrained later.
    return hashlib.sha256(Path(path_value).read_bytes()).hexdigest()


def clear_classifier_cache() -> None:
    # Mainly needed by the test suite, which swaps AI_CATEGORY_MODEL_PATH
    # and AI_SECURITY_MODEL_PATH between tests and needs the cache
    # cleared out so each test actually loads its own temp model instead
    # of reusing whatever was cached from an earlier test.
    _load_classifier.cache_clear()
    _artifact_hash.cache_clear()


def _validated_artifact_threshold(classifier: TextClassifier | None) -> float:
    """Return a safe artifact threshold, falling back for invalid metadata."""
    if classifier is None:
        return 0.5
    raw_threshold = classifier.metadata.get("threshold", 0.5)
    try:
        threshold = float(raw_threshold)
    except (TypeError, ValueError):
        logger.warning("AI security artifact has an invalid threshold; using 0.5.")
        return 0.5
    if not math.isfinite(threshold) or not 0.0 <= threshold <= 1.0:
        logger.warning("AI security artifact threshold is out of range; using 0.5.")
        return 0.5
    return threshold


def predict_for_ticket(title: str, description: str) -> PredictionResult:
    """Run both FR8 models against a ticket's text and combine the
    results.

    Two independent things happen here, and either one can fail without
    taking the other down with it. First, the category model guesses
    Hardware, Software, Network or Access. Second, the security triage
    layer decides if the ticket looks security-related, using keyword
    rules and the security model together, the way the report describes.
    """
    category_path = Path(settings.AI_CATEGORY_MODEL_PATH)
    security_path = Path(settings.AI_SECURITY_MODEL_PATH)
    try:
        category_classifier = _load_classifier(str(category_path))
        category = category_classifier.predict(title, description)
    except FileNotFoundError:
        # No trained model exists yet, for example on a fresh checkout
        # before anyone has run train_classifiers. This is expected, not
        # a bug. The ticket still gets created, just without a suggested
        # category.
        logger.warning("AI category model is unavailable at the configured path.")
        category_classifier = None
        category = None
    except Exception:
        # Anything else, a corrupt file or an incompatible scikit-learn
        # version after an upgrade for example, gets logged for later but
        # is still treated as "no suggestion this time" rather than
        # crashing the ticket form.
        logger.exception("AI category model could not be loaded or used.")
        category_classifier = None
        category = None

    # Keyword rules run no matter whether the ML models are working or
    # not. This is the "keyword-based rules" half of the report's
    # "keyword-based rules and AI-assisted classification" combination,
    # and it's cheap enough to always run even if the model layer is
    # down.
    matches = tuple(keyword_match(f"{title} {description}"))
    security_confidence: float | None = None
    security_classifier: TextClassifier | None = None
    try:
        security_classifier = _load_classifier(str(security_path))
        security_prediction = security_classifier.predict(title, description)
        # The security model's classes are True/False, is this
        # security-related, but depending on how the labels were stored
        # during training they might come back as the strings "True" or
        # "1" rather than real Python booleans, so both are checked here
        # to be safe.
        security_confidence = security_prediction.scores.get("True")
        if security_confidence is None:
            security_confidence = security_prediction.scores.get("1", 0.0)
    except FileNotFoundError:
        logger.warning("AI security model is unavailable; using strong keyword rules.")
    except Exception:
        logger.exception(
            "AI security model could not be loaded; using strong keyword rules."
        )

    # The threshold above which the security model's confidence counts as
    # "flag this ticket" was chosen during training to favour recall (see
    # train_classifiers.py) and is saved inside the model file itself, so
    # it always travels with the model it was tuned for. An operator can
    # still override it with the AI_SECURITY_THRESHOLD environment
    # variable without retraining anything, in case the default ever
    # needs adjusting once the system is live.
    artifact_threshold = _validated_artifact_threshold(security_classifier)
    threshold = (
        settings.AI_SECURITY_THRESHOLD
        if settings.AI_SECURITY_THRESHOLD is not None
        else artifact_threshold
    )
    category_available = category_classifier is not None and category is not None
    # Triage still counts as "available" even if the security model
    # itself failed to load, as long as the keyword rules found
    # something. A ticket that mentions "phishing" should still get
    # flagged even on a day the ML side is broken.
    triage_available = security_classifier is not None or bool(matches)
    return PredictionResult(
        available=category_available or triage_available,
        category_available=category_available,
        category=category.label if category else "",
        confidence=category.confidence if category else 0.0,
        category_model_name=(
            type(category_classifier.pipeline.named_steps["classifier"]).__name__
            if category_classifier
            else ""
        ),
        category_model_version=(
            _artifact_hash(str(category_path)) if category_classifier else ""
        ),
        # Flagged if either the keyword rules found a strong phrase or
        # the model's confidence cleared the threshold. Matching either
        # signal on its own is enough, since missing a real security
        # ticket is worse than an admin briefly checking one that turns
        # out to be nothing.
        is_security_flagged=bool(matches)
        or bool(security_confidence is not None and security_confidence >= threshold),
        security_confidence=security_confidence,
        security_threshold=threshold,
        matched_keywords=matches,
    )
