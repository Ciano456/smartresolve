# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

"""Train and evaluate the FR8 category and security classifiers.

Development examples are evaluated with grouped five-fold cross-validation.
Every variation derived from one source template stays in the same fold, so a
model is always tested on wording it did not see during training. The separate
holdout is used only after the model and security threshold have been selected.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.metadata
import json
from collections import Counter
from pathlib import Path
from statistics import mean, pstdev
from typing import Any, Callable

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from ml.classifier import TextClassifier

CATEGORY_LABELS = ["access", "hardware", "network", "software"]
FOLD_COUNT = 5


def _load_rows(path: Path) -> list[dict[str, str]]:
    # Reads one of the CSV datasets in and checks straight away that the
    # columns this command actually needs are there. Better to fail here
    # with a clear message than halfway through training with a confusing
    # KeyError.
    if not path.exists():
        raise CommandError(f"Dataset not found: {path}")
    with path.open(encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    required = {
        "title",
        "description",
        "category",
        "is_security_related",
        "template_group",
    }
    if not rows or not required.issubset(rows[0]):
        raise CommandError(f"Dataset must contain: {', '.join(sorted(required))}")
    return rows


def _texts(rows: list[dict[str, str]]) -> list[str]:
    # Same combine_text used at prediction time in classifier.py, so the
    # text the model trains on is built exactly the same way as the text
    # it will see later from a real ticket.
    return [
        TextClassifier.combine_text(row["title"], row["description"]) for row in rows
    ]


def _sha256(path: Path) -> str:
    # A fingerprint of a dataset file. Used below to prove training only
    # ever runs against the reviewed, frozen copies of the data, not
    # something that got edited by accident after being checked over.
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_dataset_hashes(
    manifest_path: Path, dataset_paths: dict[str, Path]
) -> dict[str, str]:
    """Ensure evaluation runs use the reviewed and frozen dataset files."""
    # dataset_hashes.json records the sha256 of each dataset file at the
    # point they were last reviewed. If any of the three files here have
    # changed since then, even by one row, training stops instead of
    # quietly producing metrics for data nobody has actually checked.
    if not manifest_path.exists():
        raise CommandError(f"Dataset hash manifest not found: {manifest_path}")
    try:
        expected = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise CommandError("Dataset hash manifest is invalid.") from exc
    actual = {name: _sha256(path) for name, path in dataset_paths.items()}
    for name, digest in actual.items():
        if expected.get(name) != digest:
            raise CommandError(
                f"{name.replace('_', ' ').title()} hash does not match the "
                "approved dataset manifest."
            )
    return actual


def _validate_datasets(
    development: list[dict[str, str]],
    holdout: list[dict[str, str]],
    evaluation: list[dict[str, str]] | None = None,
) -> None:
    """Reject data mistakes that could invalidate the reported evaluation."""
    datasets = [("development", development), ("final holdout", holdout)]
    if evaluation is not None:
        datasets.append(("iterative evaluation", evaluation))
    # Basic sanity checks on each file on its own before comparing them
    # against each other below.
    for name, rows in datasets:
        labels = sorted({row["category"] for row in rows})
        if labels != CATEGORY_LABELS:
            raise CommandError(
                f"{name.title()} categories must be: {', '.join(CATEGORY_LABELS)}"
            )
        invalid_security = {
            row["is_security_related"]
            for row in rows
            if row["is_security_related"] not in {"True", "False"}
        }
        if invalid_security:
            raise CommandError(f"{name.title()} has invalid security labels.")
        combined = [text.casefold() for text in _texts(rows)]
        if len(combined) != len(set(combined)):
            raise CommandError(f"{name.title()} contains duplicate ticket text.")

    # The important check. None of development, the final holdout and the
    # iterative evaluation set are allowed to share a template group or
    # even just the same wording. If a template leaked across two of
    # these files, the model could end up being tested on wording it had
    # already effectively seen during training, which would make the
    # reported accuracy look better than it really is.
    for index, (left_name, left_rows) in enumerate(datasets):
        for right_name, right_rows in datasets[index + 1 :]:
            left_groups = {row["template_group"] for row in left_rows}
            right_groups = {row["template_group"] for row in right_rows}
            if left_groups & right_groups:
                raise CommandError(
                    f"{left_name.title()} and {right_name} template groups overlap."
                )
            left_texts = {text.casefold() for text in _texts(left_rows)}
            right_texts = {text.casefold() for text in _texts(right_rows)}
            if left_texts & right_texts:
                raise CommandError(
                    f"{left_name.title()} and {right_name} ticket text overlaps."
                )

    # Every template belongs to exactly one category. If this ever failed
    # it would mean two categories somehow share a template_group value,
    # which would break the group aware split further down.
    group_categories: dict[str, set[str]] = {}
    for row in development:
        group_categories.setdefault(row["template_group"], set()).add(row["category"])
    if any(len(categories) != 1 for categories in group_categories.values()):
        raise CommandError("Each template group must belong to exactly one category.")

    # Both the development set and the holdout should have an even spread
    # of categories. An unbalanced dataset would let a model score well
    # just by guessing whichever category has the most examples.
    category_counts = Counter(row["category"] for row in development)
    if len(set(category_counts.values())) != 1:
        raise CommandError("Development categories must contain equal row counts.")
    holdout_category_counts = Counter(row["category"] for row in holdout)
    if len(set(holdout_category_counts.values())) != 1:
        raise CommandError("Holdout categories must contain equal row counts.")


def _grouped_folds(
    rows: list[dict[str, str]], fold_count: int = FOLD_COUNT
) -> list[tuple[list[dict[str, str]], list[dict[str, str]], list[str]]]:
    """Return balanced folds while keeping complete template groups together."""
    # Template groups are assigned to folds round robin, per category, so
    # every fold ends up with roughly the same number of examples from
    # every category, and a whole template always lands in one fold only.
    # That second part is what stops near identical wording from showing
    # up in both the training and validation side of the same fold.
    groups_by_category = {
        category: sorted(
            {
                row["template_group"]
                for row in rows
                if row["category"] == category
            }
        )
        for category in CATEGORY_LABELS
    }
    if any(len(groups) < fold_count for groups in groups_by_category.values()):
        raise CommandError(
            f"Each category requires at least {fold_count} template groups."
        )

    folds = []
    for fold_index in range(fold_count):
        validation_groups = sorted(
            group
            for groups in groups_by_category.values()
            for index, group in enumerate(groups)
            if index % fold_count == fold_index
        )
        validation_group_set = set(validation_groups)
        training = [
            row for row in rows if row["template_group"] not in validation_group_set
        ]
        validation = [
            row for row in rows if row["template_group"] in validation_group_set
        ]
        validation_categories = {row["category"] for row in validation}
        if validation_categories != set(CATEGORY_LABELS):
            raise CommandError(f"Fold {fold_index + 1} does not contain every category.")
        folds.append((training, validation, validation_groups))
    return folds


def _metrics(
    labels: list[Any], predictions: list[Any], class_labels: list[Any]
) -> dict[str, Any]:
    # One shared helper for building a metrics dict, used for both the
    # category model and the security model, and for cross validation,
    # the holdout and the iterative evaluation set. Keeping it in one
    # place means every reported number in metrics.json was calculated
    # the exact same way.
    from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

    return {
        "accuracy": float(accuracy_score(labels, predictions)),
        "classification_report": classification_report(
            labels, predictions, labels=class_labels, output_dict=True, zero_division=0
        ),
        "confusion_matrix": confusion_matrix(
            labels, predictions, labels=class_labels
        ).tolist(),
        "labels": class_labels,
    }


def _category_cross_validation(
    folds: list[tuple[list[dict[str, str]], list[dict[str, str]], list[str]]],
    factory: Callable[[], Any],
) -> dict[str, Any]:
    # Trains a fresh pipeline on each fold's training rows and scores it
    # on that fold's validation rows, five separate times. This gives a
    # much steadier read on how well a model actually generalises than
    # judging it off a single lucky or unlucky split would.
    fold_results = []
    all_truth: list[str] = []
    all_predictions: list[str] = []
    for fold_number, (training, validation, validation_groups) in enumerate(folds, 1):
        pipeline = factory()
        pipeline.fit(_texts(training), [row["category"] for row in training])
        truth = [row["category"] for row in validation]
        predictions = pipeline.predict(_texts(validation)).tolist()
        metrics = _metrics(truth, predictions, CATEGORY_LABELS)
        fold_results.append(
            {
                "fold": fold_number,
                "validation_groups": validation_groups,
                **metrics,
            }
        )
        all_truth.extend(truth)
        all_predictions.extend(predictions)

    # Macro F1 is tracked alongside plain accuracy because accuracy alone
    # can hide a model that is quietly bad at one category, for example
    # always guessing Software whenever it is unsure. Macro F1 treats
    # every category as equally important regardless of how many rows it
    # has, so a model can't hide behind doing well on the easy categories.
    accuracies = [fold["accuracy"] for fold in fold_results]
    macro_f1_scores = [
        fold["classification_report"]["macro avg"]["f1-score"]
        for fold in fold_results
    ]
    return {
        "folds": fold_results,
        "accuracy_mean": mean(accuracies),
        "accuracy_std": pstdev(accuracies),
        "macro_f1_mean": mean(macro_f1_scores),
        "macro_f1_std": pstdev(macro_f1_scores),
        "aggregate": _metrics(all_truth, all_predictions, CATEGORY_LABELS),
    }


def _security_cross_validation(
    folds: list[tuple[list[dict[str, str]], list[dict[str, str]], list[str]]],
) -> tuple[list[bool], list[float]]:
    # Unlike the category model, the security side only ever uses
    # Logistic Regression. The report's model comparison is about ticket
    # categorisation, and the security threshold work below matters more
    # here than picking between two algorithms. What this returns is the
    # true label and the model's raw probability for every ticket across
    # all five folds, ready for the threshold search that comes next.
    truth: list[bool] = []
    probabilities: list[float] = []
    for training, validation, _ in folds:
        pipeline = TextClassifier.build_logistic_pipeline()
        pipeline.fit(
            _texts(training), [row["is_security_related"] == "True" for row in training]
        )
        positive_index = list(pipeline.classes_).index(True)
        probabilities.extend(
            pipeline.predict_proba(_texts(validation))[:, positive_index].tolist()
        )
        truth.extend(row["is_security_related"] == "True" for row in validation)
    return truth, probabilities


def _select_security_threshold(
    truth: list[bool], probabilities: list[float]
) -> tuple[dict[str, float], list[dict[str, float]]]:
    # Tries every threshold from 0.20 up to 0.80 in steps of 0.05 and
    # scores each one, rather than just picking whatever threshold gives
    # the best overall accuracy. A missed real security ticket is worse
    # than an admin briefly checking one that turns out to be nothing, so
    # thresholds that catch at least 80 percent of real security tickets
    # (recall >= 0.8) are preferred. If several thresholds clear that bar,
    # the one with the best F1 wins, and if none do, the best available
    # threshold is used anyway rather than the command failing outright.
    from sklearn.metrics import precision_recall_fscore_support

    results = []
    for threshold in (value / 100 for value in range(20, 81, 5)):
        predictions = [probability >= threshold for probability in probabilities]
        precision, recall, f1, _ = precision_recall_fscore_support(
            truth, predictions, average="binary", zero_division=0
        )
        results.append(
            {
                "threshold": threshold,
                "precision": float(precision),
                "recall": float(recall),
                "f1": float(f1),
            }
        )
    eligible = [result for result in results if result["recall"] >= 0.8]
    selected = max(
        eligible or results,
        key=lambda result: (result["f1"], result["recall"], -result["threshold"]),
    )
    return selected, results


class Command(BaseCommand):
    help = "Train and evaluate FR8 category and security classifiers."

    def add_arguments(self, parser) -> None:
        # Three dataset files plus the hash manifest that approves them.
        # development trains and cross validates the models, the
        # iterative evaluation set is a separate check used while the
        # project was being built, and holdout is only ever touched once,
        # right at the end, for the final honest numbers.
        data_dir = Path(__file__).resolve().parents[2] / "data"
        parser.add_argument("--dataset", default=str(data_dir / "tickets_dataset.csv"))
        parser.add_argument(
            "--evaluation", default=str(data_dir / "tickets_evaluation.csv")
        )
        parser.add_argument("--holdout", default=str(data_dir / "tickets_holdout.csv"))
        parser.add_argument(
            "--hash-manifest", default=str(data_dir / "dataset_hashes.json")
        )

    def handle(self, *args, **options) -> None:
        try:
            from sklearn.metrics import roc_auc_score
        except ImportError as exc:
            raise CommandError("Install scikit-learn and joblib first.") from exc

        development_path = Path(options["dataset"])
        evaluation_path = Path(options["evaluation"])
        holdout_path = Path(options["holdout"])
        # Fails fast if any dataset file has changed since it was last
        # approved, before any time is spent loading rows or training.
        dataset_hashes = _validate_dataset_hashes(
            Path(options["hash_manifest"]),
            {
                "development": development_path,
                "iterative_evaluation": evaluation_path,
                "final_holdout": holdout_path,
            },
        )
        development = _load_rows(development_path)
        evaluation = _load_rows(evaluation_path)
        holdout = _load_rows(holdout_path)
        _validate_datasets(development, holdout, evaluation)
        folds = _grouped_folds(development)

        # Compares Logistic Regression against Naive Bayes on the
        # development set, five fold cross validation, the way the report
        # says both would be tested. Whichever scores higher on macro F1
        # is the one that actually gets trained up and saved, so the
        # choice is based on real numbers rather than assuming one model
        # is better before checking.
        factories = {
            "logistic_regression": TextClassifier.build_logistic_pipeline,
            "naive_bayes": TextClassifier.build_naive_bayes_pipeline,
        }
        comparison = {
            name: _category_cross_validation(folds, factory)
            for name, factory in factories.items()
        }
        selected_name = max(
            comparison,
            key=lambda name: (
                comparison[name]["macro_f1_mean"],
                comparison[name]["accuracy_mean"],
                name,
            ),
        )
        for name, result in comparison.items():
            self.stdout.write(
                f"{name}: accuracy {result['accuracy_mean']:.3f} "
                f"(+/- {result['accuracy_std']:.3f}), macro F1 "
                f"{result['macro_f1_mean']:.3f} (+/- {result['macro_f1_std']:.3f})"
            )

        # The winning model gets refit on the whole development set,
        # every fold combined, rather than just kept from whichever fold
        # did best. Cross validation is only there to pick the model and
        # get an honest score, the model that actually gets saved and
        # used in production should learn from as much data as possible.
        category_pipeline = factories[selected_name]()
        category_pipeline.fit(
            _texts(development), [row["category"] for row in development]
        )
        holdout_truth = [row["category"] for row in holdout]
        holdout_predictions = category_pipeline.predict(_texts(holdout)).tolist()
        holdout_metrics = _metrics(
            holdout_truth, holdout_predictions, CATEGORY_LABELS
        )
        evaluation_truth = [row["category"] for row in evaluation]
        evaluation_predictions = category_pipeline.predict(_texts(evaluation)).tolist()
        evaluation_metrics = _metrics(
            evaluation_truth, evaluation_predictions, CATEGORY_LABELS
        )
        category_model_path = Path(settings.AI_CATEGORY_MODEL_PATH)
        TextClassifier(category_pipeline).save(
            category_model_path, metadata={"model_name": selected_name}
        )

        # Same idea for the security side. Cross validation picks the
        # threshold, then the final security model is refit on the full
        # development set before it gets saved.
        security_truth, security_probabilities = _security_cross_validation(folds)
        selected_threshold, threshold_results = _select_security_threshold(
            security_truth, security_probabilities
        )
        security_cv_predictions = [
            probability >= selected_threshold["threshold"]
            for probability in security_probabilities
        ]
        security_pipeline = TextClassifier.build_logistic_pipeline()
        security_pipeline.fit(
            _texts(development),
            [row["is_security_related"] == "True" for row in development],
        )
        security_model_path = Path(settings.AI_SECURITY_MODEL_PATH)
        TextClassifier(security_pipeline).save(
            security_model_path,
            metadata={"threshold": selected_threshold["threshold"]},
        )
        security_holdout_truth = [
            row["is_security_related"] == "True" for row in holdout
        ]
        positive_index = list(security_pipeline.classes_).index(True)
        security_holdout_probabilities = security_pipeline.predict_proba(
            _texts(holdout)
        )[:, positive_index]
        security_holdout_predictions = (
            security_holdout_probabilities >= selected_threshold["threshold"]
        ).tolist()
        security_evaluation_truth = [
            row["is_security_related"] == "True" for row in evaluation
        ]
        security_evaluation_probabilities = security_pipeline.predict_proba(
            _texts(evaluation)
        )[:, positive_index]
        security_evaluation_predictions = (
            security_evaluation_probabilities >= selected_threshold["threshold"]
        ).tolist()

        # A plain list of every holdout ticket the final model got wrong,
        # kept for the report. Being able to show and explain a handful
        # of real mistakes is more convincing than a single accuracy
        # number on its own.
        errors = [
            {
                "title": row["title"],
                "true": row["category"],
                "predicted": prediction,
            }
            for row, prediction in zip(holdout, holdout_predictions)
            if row["category"] != prediction
        ]
        # Everything below gets written out to metrics.json. This one
        # file is the evidence the report's evaluation section is built
        # from, so it covers the cross validation comparison, the
        # iterative evaluation results, and the final holdout numbers for
        # both models, plus the dataset hashes so it is always clear
        # exactly which data produced these numbers. roc_auc is included
        # for the security model since it summarises how well it ranks
        # security tickets above normal ones across every threshold, not
        # just the one that was chosen.
        metrics = {
            "methodology": (
                "grouped five-fold development cross-validation plus separately "
                "authored final holdout"
            ),
            "dataset": {
                "development_rows": len(development),
                "development_template_groups": len(
                    {row["template_group"] for row in development}
                ),
                "iterative_evaluation_rows": len(evaluation),
                "final_holdout_rows": len(holdout),
                "fold_count": FOLD_COUNT,
                "sha256": dataset_hashes,
            },
            "selected_category_model": selected_name,
            "category_cross_validation": comparison,
            "category_iterative_evaluation": evaluation_metrics,
            "category_holdout": holdout_metrics,
            "category_holdout_errors": errors,
            "security_cross_validation": {
                "selected_threshold_metrics": _metrics(
                    security_truth, security_cv_predictions, [False, True]
                ),
                "roc_auc": float(
                    roc_auc_score(security_truth, security_probabilities)
                ),
                "threshold_candidates": threshold_results,
            },
            "security_threshold": selected_threshold,
            "security_iterative_evaluation": {
                **_metrics(
                    security_evaluation_truth,
                    security_evaluation_predictions,
                    [False, True],
                ),
                "roc_auc": float(
                    roc_auc_score(
                        security_evaluation_truth,
                        security_evaluation_probabilities,
                    )
                ),
            },
            "security_holdout": {
                **_metrics(
                    security_holdout_truth,
                    security_holdout_predictions,
                    [False, True],
                ),
                "roc_auc": float(
                    roc_auc_score(
                        security_holdout_truth, security_holdout_probabilities
                    )
                ),
            },
            "artifacts": {},
            # Records the exact scikit-learn and joblib versions used to
            # train these models. If the models ever behave differently
            # after an upgrade, this is the first place to check.
            "dependencies": {
                "scikit-learn": importlib.metadata.version("scikit-learn"),
                "joblib": importlib.metadata.version("joblib"),
            },
        }
        # A hash of the saved model files themselves, not just the
        # datasets. predictor.py records this same hash against every
        # prediction, so any prediction can be traced back to exactly
        # which trained model file produced it.
        for name, path in {
            "category": category_model_path,
            "security": security_model_path,
        }.items():
            metrics["artifacts"][name] = {
                "filename": path.name,
                "sha256": _sha256(path),
            }
        metrics_path = category_model_path.parent / "metrics.json"
        metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
        self.stdout.write(
            self.style.SUCCESS(
                f"Selected {selected_name}; holdout accuracy "
                f"{holdout_metrics['accuracy']:.3f}"
            )
        )
        self.stdout.write(
            f"Security threshold {selected_threshold['threshold']:.2f}; "
            f"metrics: {metrics_path}"
        )
