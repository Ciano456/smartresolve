# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

"""
Shared wrapper around scikit-learn for both FR8 models: the ticket
category classifier (hardware/software/network/access) and the security
triage classifier (is this ticket security-related, yes or no).

Both models work the same way underneath, TF-IDF features going into a
classifier, so instead of writing two nearly identical classes there is
one TextClassifier here and two factory methods for the two algorithms
named in the report, Logistic Regression and Naive Bayes. Keeping the
loading, saving and predicting logic in one place also means the
"no model available" fallback only has to be written once.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ClassifierPrediction:
    """One prediction result: the winning label, its confidence, and the
    scores for every class, not just the top one."""

    label: str
    confidence: float
    scores: dict[str, float]


class TextClassifier:
    """Thin wrapper around a scikit-learn Pipeline (vectoriser plus model).

    Kept generic rather than hard coding category logic or security logic
    into separate classes, so the same class trains, loads and predicts
    for both FR8 models. Only the labels they were trained on are
    different.
    """

    def __init__(
        self, pipeline: Any = None, metadata: dict[str, Any] | None = None
    ) -> None:
        self.pipeline = pipeline
        # Small extra facts about how the model was trained, for example
        # which algorithm won the comparison or the chosen security
        # threshold, get saved alongside the model so the rest of the app
        # can read them back instead of hard coding assumptions.
        self.metadata = metadata or {}

    @staticmethod
    def combine_text(title: str, description: str) -> str:
        # The classifier only works on one block of text, so the title
        # and description get joined into a single string before
        # anything is vectorised. This needs to match exactly between
        # training and prediction, so it lives in one place instead of
        # being copied everywhere it's needed.
        return f"{title.strip()} {description.strip()}".strip()

    @staticmethod
    def _vectorizer() -> Any:
        # TF-IDF turns the ticket text into numbers the model can learn
        # from, giving more weight to words that are distinctive for a
        # ticket and less weight to words that show up in nearly every
        # ticket, like "the" or "please". ngram_range=(1, 2) also lets it
        # pick up short two word phrases such as "no internet", not just
        # single words, which helps with IT support language. min_df=2
        # ignores any word that only shows up in a single ticket, since
        # that's usually just noise rather than something worth learning.
        from sklearn.feature_extraction.text import TfidfVectorizer

        return TfidfVectorizer(
            stop_words="english", ngram_range=(1, 2), min_df=2, max_features=5000
        )

    @classmethod
    def build_logistic_pipeline(cls) -> Any:
        # Logistic Regression, the first model the report says will be
        # compared. class_weight="balanced" matters here because there's
        # no guarantee the dataset has exactly even numbers of each
        # category, so this stops the model from just favouring whichever
        # class happens to have more examples.
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import Pipeline

        return Pipeline(
            [
                ("tfidf", cls._vectorizer()),
                (
                    "classifier",
                    LogisticRegression(
                        class_weight="balanced", max_iter=1000, random_state=42
                    ),
                ),
            ]
        )

    @classmethod
    def build_naive_bayes_pipeline(cls) -> Any:
        # Naive Bayes, the second model named in the report. It's an
        # older, simpler technique that assumes each word contributes
        # independently to the prediction. That assumption is usually
        # wrong in real language, but it still tends to do well on text
        # classification, which is exactly why it's worth comparing
        # against Logistic Regression instead of assuming the newer model
        # automatically wins.
        from sklearn.naive_bayes import MultinomialNB
        from sklearn.pipeline import Pipeline

        return Pipeline([("tfidf", cls._vectorizer()), ("classifier", MultinomialNB())])

    def predict(self, title: str, description: str) -> ClassifierPrediction:
        if self.pipeline is None:
            raise RuntimeError("Classifier is not loaded.")
        probabilities = self.pipeline.predict_proba(
            [self.combine_text(title, description)]
        )[0]
        # predict_proba gives a probability for every class the model
        # knows about, not just the winner. Keeping all of them means the
        # UI can show something like "78% Hardware, 15% Software" instead
        # of just a single guess with no sense of how confident the model
        # actually was.
        scores = {
            str(label): float(score)
            for label, score in zip(self.pipeline.classes_, probabilities)
        }
        label = max(scores, key=scores.get)
        return ClassifierPrediction(label, scores[label], scores)

    @classmethod
    def load(cls, path: Path) -> "TextClassifier":
        # joblib is the standard way to save and load scikit-learn
        # models. It handles the numpy arrays inside a fitted pipeline a
        # lot better than plain pickle would. If loading fails, whether
        # the file is missing or corrupt, that error is left to bubble up
        # so the caller in predictor.py can decide how to fall back.
        # This class doesn't try to hide failures itself.
        import joblib

        artifact = joblib.load(path)
        if isinstance(artifact, dict) and "pipeline" in artifact:
            return cls(artifact["pipeline"], artifact.get("metadata"))
        return cls(artifact)

    def save(self, path: Path, metadata: dict[str, Any] | None = None) -> None:
        import joblib

        path.parent.mkdir(parents=True, exist_ok=True)
        # Saved as a small dict rather than just the raw pipeline, so the
        # metadata (which algorithm was picked, or the trained security
        # threshold) travels with the model file itself instead of being
        # tracked somewhere separate.
        joblib.dump(
            {"pipeline": self.pipeline, "metadata": metadata or self.metadata},
            path,
        )


# Both FR8 models are really just a TextClassifier trained on different
# labels. These aliases just make the calling code easier to read, for
# example "load the SecurityClassifier", without needing a second class
# that would basically be a copy of this one.
TicketCategoryClassifier = TextClassifier
SecurityClassifier = TextClassifier
