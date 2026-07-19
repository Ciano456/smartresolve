# Sprint 9 Checklist

## Scaffolding Review

- [x] Existing untracked ML scaffolding reviewed and useful structure retained.
- [x] Wrong taxonomy and Dublin/Cork sample data replaced without deleting
      unrelated user work.

## Data Model

- [x] `ml.TicketCategoryPrediction` model added (one-to-one with `Ticket`).
- [x] Migration created and applied locally (left uncommitted for review).
- [x] `tickets/models.py` left unchanged.

## Dataset

- [x] Generator rewritten for Hardware/Software/Network/Access categories.
- [x] Naas/Carlow used instead of Dublin/Cork.
- [x] Natural cross-category ambiguity included without targeting a score.
- [x] Security-relevant phrasing woven across all categories with a ground
      truth `is_security_related` column (~15-20% of rows).
- [x] `template_group` prevents generator-template leakage across splits.
- [x] Development data expanded to 15 independent templates per category.
- [x] Iterative 60-ticket evaluation set retained separately from final evidence.
- [x] Frozen final holdout contains 15 newly authored tickets per category.
- [x] Final holdout hash recorded before its initial frozen evaluation.
- [x] Approved dataset hash manifest enforced before training or inference.
- [x] `ml/data/tickets_dataset.csv` regenerated and ready for review.

## Security Triage

- [x] `ml/security_keywords.py` keyword/phrase list + `keyword_match()`.
- [x] Binary security classifier trained on `is_security_related`.
- [x] Recall-favouring threshold selected on validation data and justified.
- [x] Benign password-reset/account-lockout phrases do not trigger a flag alone.

## Model Training

- [x] Logistic Regression category pipeline.
- [x] Naive Bayes category pipeline.
- [x] `train_classifiers` management command compares both, picks the
      better macro-F1 model, saves it as the production artifact.
- [x] Grouped five-fold cross-validation evaluates every template exactly once.
- [x] Fold means, standard deviations, aggregate per-class metrics, and ROC-AUC
      are recorded for reproducible evaluation.
- [x] Full comparison, confusion matrices, and misclassified examples
      written to `ml/artifacts/metrics.json`.
- [x] Iterative evaluation and frozen holdout metrics recorded under separate keys.
- [x] Model and threshold selected without using the final holdout.
- [x] Mean cross-validation and final holdout accuracy reported honestly against
      the 75-85% target, including Hardware and security-recall weaknesses.
- [x] `ml/artifacts/*.joblib` gitignored; `metrics.json` ready for review.
- [x] Artifact hashes and dependency versions recorded.
- [x] Railway build deterministically creates both model artifacts.

## Integration

- [x] `ml/predictor.py` with graceful "unavailable" fallback (no
      exceptions).
- [x] Ticket creation stores a prediction when available.
- [x] Inference, corrupt-artifact, and persistence failures degrade safely.
- [x] Staff can view and override the suggested category.
- [x] Override is audit-logged via `admin_portal.audit.record_audit_log`.
- [x] Security-flagged tickets are visibly highlighted for staff/admins.
- [x] Filter for security-flagged tickets on the staff/admin ticket list.
- [x] Prediction queries avoid N+1 access.
- [x] AI paths and optional threshold override use environment-backed Django
      settings; the trained threshold is stored in artifact metadata.

## Tests

- [x] `ml/tests.py` covers classifier output bounds, missing-model fallback,
      corrupt-model fallback, keyword matching, fold leakage and coverage,
      dataset balance and duplicates, threshold selection, and benign phrases.
- [x] `tickets/tests.py` covers prediction-on-create, persistence failure,
      permissions, query count, and the override/audit flow.
- [x] Manual category fallback and independent security triage are tested.
- [x] Invalid and out-of-range artifact threshold metadata falls back safely.
- [x] Override category and timestamp consistency is database constrained.
- [x] All 226 tests pass in the full local suite.

## Documentation

- [x] `requirements.txt` updated (scikit-learn, joblib).
- [x] `.env.example`, settings, and deployment docs updated.
- [x] RTM FR8 row updated with real evidence.
- [x] `testing_and_evaluation.md` AI section updated to match reality.
- [x] Sprint write-up records implementation, challenges, evaluation, lessons,
      and remaining limitations.
