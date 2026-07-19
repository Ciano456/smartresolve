# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

import csv
import json
import os
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.management.base import CommandError
from django.test import SimpleTestCase, TestCase, override_settings

from ml.classifier import TextClassifier
from ml.data.generate_dataset import TEMPLATES, generate_examples
from ml.management.commands.train_classifiers import (
    CATEGORY_LABELS,
    FOLD_COUNT,
    _grouped_folds,
    _select_security_threshold,
    _sha256,
    _texts,
    _validate_dataset_hashes,
    _validate_datasets,
)
from ml.models import TicketCategoryPrediction
from ml.predictor import (
    _validated_artifact_threshold,
    clear_classifier_cache,
    predict_for_ticket,
)
from ml.security_keywords import keyword_match
from ml.services import create_prediction_for_ticket
from smartresolve.settings.base import optional_probability_env_float


class SecurityKeywordTests(SimpleTestCase):
    def test_strong_security_phrases_are_matched(self):
        # Strong phrases should trigger rule-based review even without the model.
        self.assertEqual(
            keyword_match("Possible phishing email with malware"),
            ["phishing", "malware"],
        )

    def test_benign_password_reset_is_not_matched(self):
        # Routine support language must not be treated as a security incident alone.
        self.assertEqual(keyword_match("Please reset my forgotten password"), [])


class DatasetTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        data_dir = Path(__file__).parent / "data"
        with (data_dir / "tickets_dataset.csv").open(encoding="utf-8") as source:
            cls.development = list(csv.DictReader(source))
        with (data_dir / "tickets_holdout.csv").open(encoding="utf-8") as source:
            cls.holdout = list(csv.DictReader(source))
        cls.holdout_path = data_dir / "tickets_holdout.csv"
        cls.hash_manifest_path = data_dir / "dataset_hashes.json"
        with (data_dir / "tickets_evaluation.csv").open(encoding="utf-8") as source:
            cls.evaluation = list(csv.DictReader(source))

    def test_generator_has_enough_independent_templates(self):
        self.assertTrue(
            all(len(templates) >= 15 for templates in TEMPLATES.values())
        )

    def test_generated_dataset_is_deterministic(self):
        first = generate_examples(per_category=30)
        second = generate_examples(per_category=30)
        self.assertEqual(first, second)

    def test_datasets_are_balanced_unique_and_independent(self):
        _validate_datasets(self.development, self.holdout, self.evaluation)
        development_counts = Counter(
            row["category"] for row in self.development
        )
        holdout_counts = Counter(row["category"] for row in self.holdout)
        self.assertEqual(set(development_counts), set(CATEGORY_LABELS))
        self.assertEqual(len(set(development_counts.values())), 1)
        self.assertEqual(set(holdout_counts.values()), {15})
        self.assertEqual(len(_texts(self.development)), len(set(_texts(self.development))))

    def test_final_holdout_hash_is_stable_and_complete(self):
        digest = _sha256(self.holdout_path)
        self.assertEqual(
            digest,
            "81f6ff1e5a8b5ef75a438363dd29d85b71177d40f6d82d573a70936d7224d85b",
        )

    def test_dataset_hash_manifest_matches_all_approved_files(self):
        data_dir = self.holdout_path.parent
        hashes = _validate_dataset_hashes(
            self.hash_manifest_path,
            {
                "development": data_dir / "tickets_dataset.csv",
                "iterative_evaluation": data_dir / "tickets_evaluation.csv",
                "final_holdout": self.holdout_path,
            },
        )
        expected = json.loads(self.hash_manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(hashes, expected)

    def test_dataset_hash_mismatch_is_rejected(self):
        with TemporaryDirectory() as directory:
            manifest = Path(directory) / "hashes.json"
            manifest.write_text('{"final_holdout": "wrong"}', encoding="utf-8")
            with self.assertRaisesMessage(CommandError, "hash does not match"):
                _validate_dataset_hashes(
                    manifest, {"final_holdout": self.holdout_path}
                )

    def test_grouped_folds_have_no_leakage_and_cover_every_row_once(self):
        folds = _grouped_folds(self.development)
        validation_groups_seen = []
        validation_rows_seen = []
        self.assertEqual(len(folds), FOLD_COUNT)
        for training, validation, validation_groups in folds:
            training_groups = {row["template_group"] for row in training}
            self.assertTrue(training_groups.isdisjoint(validation_groups))
            self.assertEqual(
                {row["category"] for row in validation}, set(CATEGORY_LABELS)
            )
            validation_groups_seen.extend(validation_groups)
            validation_rows_seen.extend(id(row) for row in validation)
        self.assertEqual(
            len(validation_groups_seen), len(set(validation_groups_seen))
        )
        self.assertCountEqual(validation_rows_seen, [id(row) for row in self.development])

    def test_duplicate_ticket_text_is_rejected(self):
        duplicated = [*self.development, dict(self.development[0])]
        with self.assertRaisesMessage(CommandError, "duplicate ticket text"):
            _validate_datasets(duplicated, self.holdout)

    def test_threshold_selection_prioritises_required_recall(self):
        selected, _ = _select_security_threshold(
            [True, True, False, False], [0.8, 0.8, 0.1, 0.1]
        )
        self.assertGreaterEqual(selected["recall"], 0.8)
        self.assertEqual(selected["threshold"], 0.2)


class ClassifierTests(SimpleTestCase):
    def test_invalid_artifact_threshold_falls_back_safely(self):
        classifier = TextClassifier(metadata={"threshold": "invalid"})
        self.assertEqual(_validated_artifact_threshold(classifier), 0.5)

    def test_out_of_range_artifact_threshold_falls_back_safely(self):
        classifier = TextClassifier(metadata={"threshold": 1.5})
        self.assertEqual(_validated_artifact_threshold(classifier), 0.5)

    def test_prediction_has_a_valid_label_and_probability(self):
        # A real small pipeline proves the wrapper returns bounded probabilities.
        texts = [
            "broken laptop screen hardware",
            "laptop keyboard hardware fault",
            "software application crash",
            "software update error",
            "wifi network unavailable",
            "vpn network timeout",
            "access permission denied",
            "account access request",
        ]
        labels = [
            "hardware",
            "hardware",
            "software",
            "software",
            "network",
            "network",
            "access",
            "access",
        ]
        pipeline = TextClassifier.build_logistic_pipeline()
        pipeline.fit(texts, labels)

        prediction = TextClassifier(pipeline).predict(
            "VPN failure", "Network connection timed out"
        )

        self.assertIn(prediction.label, labels)
        self.assertGreaterEqual(prediction.confidence, 0.0)
        self.assertLessEqual(prediction.confidence, 1.0)

    def test_missing_model_returns_unavailable_result(self):
        # FR8 requires ticket creation to continue when artifacts are absent.
        with TemporaryDirectory() as directory:
            missing = Path(directory) / "missing.joblib"
            with override_settings(
                AI_CATEGORY_MODEL_PATH=missing,
                AI_SECURITY_MODEL_PATH=missing,
            ):
                clear_classifier_cache()
                result = predict_for_ticket("Printer fault", "Printer will not start")
        clear_classifier_cache()
        self.assertFalse(result.available)

    def test_corrupt_model_returns_unavailable_result(self):
        # Corrupt local artifacts must not interrupt the ticket workflow.
        with TemporaryDirectory() as directory:
            corrupt = Path(directory) / "corrupt.joblib"
            corrupt.write_text("not a model", encoding="utf-8")
            with override_settings(
                AI_CATEGORY_MODEL_PATH=corrupt,
                AI_SECURITY_MODEL_PATH=corrupt,
            ):
                clear_classifier_cache()
                result = predict_for_ticket("VPN problem", "Cannot connect")
        clear_classifier_cache()
        self.assertFalse(result.available)

    def test_keywords_still_flag_ticket_when_models_are_missing(self):
        # Rule-based security triage must survive category artifact failure.
        with TemporaryDirectory() as directory:
            missing = Path(directory) / "missing.joblib"
            with override_settings(
                AI_CATEGORY_MODEL_PATH=missing,
                AI_SECURITY_MODEL_PATH=missing,
                AI_SECURITY_THRESHOLD=None,
            ):
                clear_classifier_cache()
                result = predict_for_ticket(
                    "Suspicious email", "This looks like a phishing message."
                )
        clear_classifier_cache()
        self.assertTrue(result.available)
        self.assertFalse(result.category_available)
        self.assertTrue(result.is_security_flagged)
        self.assertEqual(result.category, "")

class PredictionModelTests(TestCase):
    def test_confidence_validator_rejects_out_of_range_value(self):
        # Model validation protects auditable confidence data before persistence.
        prediction = TicketCategoryPrediction(confidence=1.2, security_threshold=0.4)
        with self.assertRaises(ValidationError):
            prediction.full_clean(
                exclude=[
                    "ticket",
                    "predicted_category",
                    "category_model_name",
                    "category_model_version",
                ]
            )

    def test_unknown_category_is_not_persisted(self):
        # Incompatible artifacts must not store labels outside the model choices.
        with patch("ml.services.predict_for_ticket") as predictor:
            predictor.return_value = SimpleNamespace(
                available=True,
                category="unknown",
            )
            self.assertIsNone(
                create_prediction_for_ticket(
                    SimpleNamespace(title="", description="", pk=1)
                )
            )

    def test_override_category_requires_override_timestamp(self):
        prediction = TicketCategoryPrediction(
            staff_override_category="hardware",
            overridden_at=None,
        )
        with self.assertRaises(ValidationError):
            prediction.validate_constraints(exclude={"ticket"})


class AISettingsTests(SimpleTestCase):
    def test_invalid_threshold_configuration_is_rejected(self):
        # Invalid operational configuration should fail clearly at startup.
        with patch.dict(os.environ, {"AI_SECURITY_THRESHOLD": "invalid"}):
            with self.assertRaises(ImproperlyConfigured):
                optional_probability_env_float("AI_SECURITY_THRESHOLD")
