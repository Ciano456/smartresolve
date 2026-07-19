# Sprint 9 - AI-Assisted Ticket Categorisation And Security Triage (FR8)

## Status Of Prior Scaffolding

An earlier draft created `ml/classifier.py`, `ml/data/generate_dataset.py`, a
singular `train_classifier` command, and `ml/data/tickets_dataset.csv`.
That draft predicted the wrong taxonomy (it reused `tickets.TicketType`:
Incident / Service Request / Access Request) and used Dublin/Cork as sample
locations. Treat those untracked files as recoverable scaffolding: inspect and
retain any reusable structure, then replace only the behaviour and generated
data that conflict with this approved design.

## Goal

Implement FR8 ("AI-Assisted Ticket Categorisation") and the related
security-triage behaviour described in the Technical Report and Project
Proposal, as an assistive suggestion layered on top of ticket creation -
never a hard gate. Produce real, defensible evaluation evidence (accuracy,
precision, recall, F1, confusion matrices, a two-model comparison, and error
analysis) that the Testing and Evaluation sections of the report can cite
directly.

## Architecture

- Keep ML concerns inside the existing `ml` Django app: models hold auditable
  prediction records, classifier modules handle training/inference, and a
  service coordinates prediction persistence.
- Keep ticket views thin: they call the service after ticket creation and use
  a permission-protected class-based view for staff overrides.
- Keep `tickets.TicketType` unchanged because it describes workflow type, not
  the report's AI issue-category taxonomy.
- Add one database model and one migration; no destructive schema change or
  third-party hosted AI service is required.
- Add `scikit-learn` and `joblib`; use PostgreSQL/Django constraints and
  environment-backed settings already established by the project.

## Files

Created:

- A generated `ml` migration (exact sequence number determined by Django)
- `ml/security_keywords.py`
- `ml/predictor.py`
- `ml/services.py`
- `ml/management/commands/train_classifiers.py`
- `ml/data/tickets_holdout.csv`
- `ml/data/tickets_evaluation.csv`
- `ml/data/dataset_hashes.json`
- `ml/artifacts/metrics.json`

Modified:

- `ml/models.py` (replace the tracked placeholder with the prediction model)
- `ml/classifier.py`
- `ml/data/generate_dataset.py`
- `ml/data/tickets_dataset.csv`
- `ml/tests.py`
- `tickets/views.py`, `tickets/urls.py`, `tickets/tests.py`
- Relevant staff ticket list/detail templates
- `smartresolve/settings/base.py`, `.env.example`, `.gitignore`
- `requirements.txt`, `build.sh`, and relevant deployment documentation
- `docs/project_management/requirements_traceability_matrix.md`
- `docs/project_management/testing_and_evaluation.md`

The exact template and settings paths must be confirmed against the repository
before implementation; do not create parallel files when an established file
already owns that responsibility.

## What The Report Actually Commits To (source of truth)

Quoted/paraphrased from `Technical Report - Requirement Spec.docx` and
`docs/Updated_Project_Proposal_Secure_IT_Support_Portal.docx`:

- FR8 use case: ticket submitted -> system preprocesses text -> model
  predicts most likely category -> system "applies or suggests" the
  category -> staff can manually override (A1) -> if the model is
  unavailable, the system falls back to manual categorisation (E1) -> the
  ticket ends up with a usable category either way.
- Categories are IT issue types: "hardware, software, access, and network
  issues" - this is a different taxonomy from the existing
  `tickets.TicketType` lookup (Incident / Service Request / Access
  Request), which is a workflow type, not an issue category. Do not reuse
  `TicketType`.
- Security triage is a second, related behaviour: "the system will use
  keyword-based rules and AI-assisted classification to help identify
  tickets that mention issues such as phishing, malware, suspicious
  emails, account lockouts, password resets, or unauthorised access."
  Flagged + high-priority tickets are "highlighted for administrator
  review." Triage is a rules+model combination, not a separate deep
  system.
- Two models are named explicitly for comparison: "Models such as Logistic
  Regression and Naive Bayes will be tested to compare performance."
- Named evaluation target: "assessed against a target accuracy range of
  approximately 75-85 percent on test data."
- Data sourcing is pre-approved in the proposal: "If real historical
  ticket data is not available, sample data will be created... No real
  personal or sensitive organisational data will be used in the submitted
  project." The live database has only 3 placeholder tickets, so synthetic
  data is the correct and already-justified choice.

## Design Decisions Made (do not re-litigate without reason)

1. **Category taxonomy**: `Hardware`, `Software`, `Network`, `Access` (4
   classes). Stored as a `CharField` with choices on a new model - not a
   new lookup table, and not a change to `tickets.TicketType`.
2. **New model lives in the `ml` app**, not `tickets`, to avoid touching
   the tickets app's existing migration history: `ml.TicketCategoryPrediction`,
   a one-to-one record per ticket holding the prediction, confidence,
   security flag, and any staff correction. See schema below.
3. **Security triage is informational, not authoritative.** The AI/keyword
   layer sets `is_security_flagged` and the UI highlights the ticket for
   admin review. It does **not** silently change `ticket_priority` -
   consistent with FR8's own "manual override" alternate flow and with
   keeping a human in the loop for security decisions.
4. **Measure accuracy; never engineer the answer.** The report's 75-85% range
   is an evaluation target, not a score to manufacture. Dataset examples must
   be realistic and include naturally ambiguous tickets, but data generation,
   model selection, and threshold selection must not be changed merely to
   force the final score into that range. Report and explain the observed
   result honestly, including a result above or below the target.
5. **Locations used in generated ticket text**: Naas office and Carlow
   office (not Dublin/Cork).
6. **Graceful degradation is mandatory**: if no trained model artifact
   exists, ticket creation must still work with no error, no prediction
   shown, and no exception raised, matching FR8's E1 exceptional flow.
7. **No template leakage**: generated examples from the same base template
   must share a `template_group` and remain in the same cross-validation fold.
   Any set used to guide refinement becomes an iterative evaluation set. A separately
   authored and pre-hashed balanced holdout must be used for final evaluation.
8. **Configuration boundary**: artifact paths are read from environment-backed
   Django settings. The validation-selected threshold ships as artifact
   metadata and may be explicitly overridden through the environment. Staff
   may override a prediction in the app, but cannot change global model
   configuration from the UI.

## Schema Changes

New file `ml/models.py` (replacing the placeholder header-only file):

```python
CATEGORY_CHOICES = [
    ("hardware", "Hardware"),
    ("software", "Software"),
    ("network", "Network"),
    ("access", "Access"),
]

class TicketCategoryPrediction(models.Model):
    ticket = models.OneToOneField(
        "tickets.Ticket", on_delete=models.CASCADE, related_name="ai_prediction"
    )
    predicted_category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    confidence = models.FloatField()
    category_model_name = models.CharField(max_length=50)   # e.g. "logistic_regression"
    category_model_version = models.CharField(max_length=50)  # e.g. training date/hash

    is_security_flagged = models.BooleanField(default=False)
    security_confidence = models.FloatField(null=True, blank=True)
    matched_keywords = models.CharField(max_length=255, blank=True)

    staff_override_category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, blank=True
    )
    overridden_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    overridden_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def effective_category(self):
        return self.staff_override_category or self.predicted_category
```

Add `MinValueValidator(0.0)` and `MaxValueValidator(1.0)` to confidence
fields and database check constraints for the same bounds. Store a stable
artifact hash/version and the configured security threshold with each
prediction so results remain auditable after retraining. Validate override
state so `overridden_by` and `overridden_at` are populated together with an
override category.

Run `python manage.py makemigrations ml` after this. This is the only
schema change required; `tickets/models.py` is untouched.

## Dataset Generation (`ml/data/generate_dataset.py`, full rewrite)

Target size: ~150-180 examples per category (600-720 rows total), plus
security-relevant phrasing woven across all four categories (not a 5th
category - security-relevant tickets still belong to Hardware/Software/
Network/Access, they are just *also* flagged), so the security classifier
learns that the flag is category-independent.

Method: hand-authored sentence templates + filler substitution per
category (same combinatorial technique as the first draft, expanded).
Requirements for this rewrite:

- **Fillers**: replace `LOCATIONS` with Naas office / Carlow office
  variants (e.g. "the Naas office", "the Carlow office", "the Naas site",
  "our Carlow branch"). Keep system/app/device/department fillers, expand
  where useful.
- **Natural ambiguity**: include realistic cross-category examples without
  targeting a predetermined error rate:
  - Hardware/Network overlap: e.g. "no internet connection because the
    router light is off" (physical device fault + connectivity symptom).
  - Software/Access overlap: e.g. "can't log into the finance software"
    (is this a software bug or an access/permissions problem?).
  - Hardware/Software overlap: e.g. "application won't open since the
    update" (could be a device issue or an application issue).
  - Network/Access overlap: e.g. "can't reach the shared drive over VPN"
    (connectivity vs permissions).
  Label these by whichever category a human IT triager would most
  reasonably pick, but expect and accept that the model will sometimes
  disagree - that disagreement is exactly what should be discussed in the
  Evaluation section's error analysis.
- **Security-relevant examples**: for roughly 15-20% of rows across all
  four categories, insert phrasing drawn from the keyword list below (see
  Security Triage section) into an otherwise normal ticket of that
  category, and mark a ground-truth `is_security_related` boolean column.
  Example: a "Software" ticket that says "I think this update prompt is
  fake, it's asking for my password and looks like phishing" - category
  stays Software, `is_security_related` = True.
- **Output**: `ml/data/tickets_dataset.csv` with columns `title,
  description, category, is_security_related, template_group`. Keep the generator
  deterministic (`random.seed(42)`) so results are reproducible for the
  report.
- **Evaluation sets**: retain refinement examples in
  `ml/data/tickets_evaluation.csv`. Create `ml/data/tickets_holdout.csv` from
  separately authored examples that do not reuse generator templates. Record its
  hash before inference and do not use its results to change features, models,
  labels, or thresholds.
- Print a per-category and per-flag count summary when run, same as the
  first draft did, so the class balance is visible immediately.

## Security Triage (`ml/security_keywords.py`, new file)

A plain keyword/phrase list (case-insensitive substring or word-boundary
regex match), grouped for readability, covering at minimum: phishing,
suspicious email, suspicious attachment, malware, virus, ransomware,
spoofed/spoofing, compromised, breach, unauthorised access, unauthorized
access, account locked / locked out, stolen device, lost device, fraud,
scam, credential theft. Expose a function:

```python
def keyword_match(text: str) -> list[str]:
    """Return the list of matched keywords/phrases, empty if none."""
```

Combine with a second, small binary classifier (same TF-IDF + Logistic
Regression approach, trained on the `is_security_related` column) rather
than relying on keywords alone, to satisfy the report's explicit
"keyword-based rules and AI-assisted classification" combination. Final
flag logic:

```
is_security_flagged = bool(keyword_match(text)) or (security_model_confidence >= SECURITY_THRESHOLD)
```

Store the validation-selected threshold in the security artifact and allow an
optional `AI_SECURITY_THRESHOLD` environment override through Django settings.
Choose the artifact value to favour recall while recording the precision cost.
Do not tune it on the final holdout. A false negative is
more costly than a false positive for triage, but ordinary password resets or
account lockouts must not be flagged solely because those benign phrases
appear; require suspicious context, a model score above threshold, or a
stronger rule match.

## Model Training (`ml/classifier.py` full rewrite + `ml/management/commands/train_classifiers.py` full rewrite, renamed from the singular `train_classifier.py`)

`ml/classifier.py` should define two small wrapper classes following the
same pattern as the first draft (`build_pipeline`, `load`, `save`,
`predict`), but this time:

1. **Category pipeline(s)**: build both a `TfidfVectorizer +
   LogisticRegression(class_weight="balanced", max_iter=1000)` pipeline
   and a `TfidfVectorizer + MultinomialNB()` pipeline. Use identical
   vectorizer settings (`ngram_range=(1,2)`, `stop_words="english"`,
   `min_df=2`, `max_features=5000`) for a fair comparison. Note:
   `MultinomialNB` requires non-negative features, which raw TF-IDF
   already satisfies, so no extra handling is needed.
2. **Security pipeline**: one `TfidfVectorizer + LogisticRegression`
   binary classifier on `is_security_related`.

`ml/management/commands/train_classifiers.py` should:

- Load `ml/data/tickets_dataset.csv`.
- Grouped five-fold cross-validation using `template_group`, balanced by
  category, plus the separately authored untouched holdout set for final reporting.
- Fit both category pipelines on the training split.
- Compare both across identical folds: accuracy, macro precision/recall/F1,
  per-class precision/recall/F1, confusion matrices, means, and standard deviations.
- Print a comparison table (Logistic Regression vs Naive Bayes) to stdout.
- Select the higher macro-F1 model as the "production" model saved to
  `ml/artifacts/category_model.joblib`; still record both models' full
  metrics in the metrics file so the report can show the comparison even
  though only one ships.
- Select the model and security threshold using out-of-fold development data, then refit
  the selected pipelines on all development data and evaluate exactly once on
  the untouched holdout.
- Separately train/evaluate the security binary classifier with group-aware
  splits and record precision, recall, F1, ROC-AUC (where defined), and the
  selected threshold; save it to `ml/artifacts/security_model.joblib`.
- Pull a handful (8-12) of misclassified test examples for the winning
  category model and write them into the metrics file verbatim (title,
  description, true label, predicted label, confidence) - this is the
  error-analysis evidence for the Evaluation section.
- Write everything to `ml/artifacts/metrics.json`: both models' full
  metrics, the comparison, the chosen production model name, the security
  classifier's metrics and chosen threshold, misclassified examples, and
  final accuracy vs the 75-85% target with a one-line pass/fail note.
- `ml/artifacts/*.joblib` should be **gitignored**. The Railway build must run
  the deterministic training command after dependencies are installed so the
  artifacts exist in the deployed image. Deployment must fail clearly if
  training fails; runtime ticket submission still retains the FR8 manual
  fallback if an artifact later becomes unavailable. Commit `metrics.json`,
  both CSV datasets, dependency versions, and artifact hashes as evidence.

## Integration Into Ticket Creation

New file `ml/predictor.py` - the inference entry point used by the ML service:

```python
def predict_for_ticket(title: str, description: str) -> PredictionResult:
    """
    Returns category, confidence, is_security_flagged, security_confidence,
    matched_keywords. Category and security availability are tracked
    independently; missing artifacts never raise into the ticket workflow.
    """
```

Use a small `ml/services.py` orchestration service from the ticket-creation
view after the `Ticket` is saved. The service calls `predict_for_ticket` and
persists `TicketCategoryPrediction` atomically where practical. Any inference
or prediction-persistence failure is logged safely and leaves the successfully
created ticket usable, matching the report's fallback flow. Load and cache
trusted local artifacts once per process; reject corrupt or incompatible
artifacts and fall back without exposing filesystem details to users.

UI (ticket detail/list templates, staff-facing):

- Ticket detail: show "Suggested category: Hardware (78% confidence)" with
  an override control for staff (a small form posting to a new
  `ticket_override_category` view that sets `staff_override_category`,
  `overridden_by`, `overridden_at`, and writes an `admin_portal` audit log
  entry - reuse the existing `record_audit_log()` helper).
- Ticket list (staff/admin view): a small warning badge on rows where
  `is_security_flagged=True`, and a filter option "Security flagged only."
- Restrict prediction visibility, override actions, and the security filter to
  support staff/administrators with explicit permission checks. Optimise list
  queries with `select_related("ai_prediction")` to avoid N+1 queries.
- If no AI category exists (model unavailable, or ticket predates this feature),
  show the manual staff category control and a clear unavailable message.

## Tests

`ml/tests.py` (currently empty, full rewrite):

- Unit tests for `TicketCategoryClassifier`/security classifier `predict()`
  output shape and bounds (confidence in [0,1], label in the 4 valid
  categories).
- `predict_for_ticket()` reports category/security availability independently
  when artifacts are missing, while preserving keyword-only security triage.
- `keyword_match()` returns matches for known phishing/malware phrases and
  an empty list for benign text.

`tickets/tests.py` additions:

- Mock `ml.predictor.predict_for_ticket` for the bulk of ticket-creation
  tests (avoid loading a real sklearn model in every test run).
- At least one integration test using a temporary real model trained once per
  test session on a small fixed sample to prove the full wiring works:
  create ticket -> prediction row exists -> override view changes
  `effective_category` and writes an audit log entry.

## Dependencies

Add to `requirements.txt`: `scikit-learn`, `joblib`. `numpy`/`scipy` will
come in as scikit-learn's own dependencies - no need to pin them
separately unless a conflict appears.

Add settings backed by environment variables for category/security artifact
paths and an optional `AI_SECURITY_THRESHOLD` override, with safe documented
behaviour in `.env.example`. No secrets are involved and no model configuration
is exposed through the application UI.

## Risks And Edge Cases

- Synthetic-template leakage could overstate performance; group-aware splitting
  and an independently authored holdout mitigate it.
- A missing, corrupt, incompatible, or maliciously replaced joblib artifact
  must never break ticket submission. Load only locally generated artifacts,
  verify the recorded hash/version, log the failure, and use manual fallback.
- Security triage can create harmful false reassurance. It remains advisory,
  visibly supports staff review, and reports both false negatives and false
  positives.
- Confidence values and override metadata can become inconsistent; validators,
  database constraints, and model tests enforce valid state.
- Ticket lists can introduce N+1 prediction queries; use `select_related` and a
  query-count regression test.
- Training during deployment adds build time and can fail if dependencies or
  data drift. Pin compatible versions, keep generation deterministic, and make
  build failure explicit.
- Prediction persistence can fail after the ticket is created. The service must
  preserve the ticket, log the AI failure safely, and allow manual handling.

## Open Questions

- The repository instructions say not to commit migrations, but the new model
  cannot be deployed reproducibly without its schema migration. Before
  implementation, confirm whether this project migration should be committed as
  a necessary exception.

The Technical Report is otherwise authoritative for FR numbering and scope;
global configuration belongs in environment-backed Django settings, while
individual prediction overrides belong in the staff application workflow.

## Definition Of Done

- [x] Existing scaffold reviewed, conflicting behaviour/data replaced, and the
      obsolete singular training-command alias removed.
- [x] `ml/models.py` has `TicketCategoryPrediction`; migration created and
      applied.
- [x] Development and independently authored holdout datasets ready for review with
      balanced-enough classes, Naas/Carlow locations, natural ambiguity,
      `is_security_related`, provenance, and template groups documented.
- [x] `python manage.py train_classifiers` runs cleanly, prints a Logistic
      Regression vs Naive Bayes comparison, and writes
      `ml/artifacts/metrics.json` + both `.joblib` files.
- [x] Final holdout accuracy is reported honestly and explained relative to
      the 75-85% target; no data or model choice is altered to force the score.
- [x] Security classifier metrics recorded with the recall-favouring
      threshold justified in `metrics.json`.
- [x] Ticket creation calls `predict_for_ticket` and stores a
      `TicketCategoryPrediction` when available; creation never fails when
      the model is missing.
- [x] Staff can see and override the suggested category from the ticket
      detail page; override is audit-logged.
- [x] Security-flagged tickets are visibly highlighted for staff/admins.
- [x] `ml/tests.py` and `tickets/tests.py` contain focused ML and integration
      tests covering the new integration points.
- [x] `requirements.txt` updated.
- [x] `.env.example`, Django settings, and Railway build documentation define
      artifact paths, threshold configuration, and deterministic training.
- [x] `docs/project_management/requirements_traceability_matrix.md` FR8
      row updated with real evidence (file paths + test names).
- [x] `docs/project_management/testing_and_evaluation.md` AI section
      updated to reflect that classification is now implemented, evidenced,
      and evaluated (replacing the current "not implemented" wording).

## Suggested Implementation Order

1. Review the untracked `ml/` scaffold, retain reusable structure, and replace
   only the parts that conflict with this plan.
2. `ml/models.py` + migration.
3. `ml/security_keywords.py`.
4. Rewrite dataset generation, add template groups and the independently
   authored holdout, then validate schema, balance, duplicates, and provenance.
5. `ml/classifier.py` rewrite (both category pipelines + security
   pipeline wrappers).
6. Rewrite `train_classifiers`; select models/thresholds on validation data,
   refit on development data, evaluate once on the holdout, and report the
   result honestly against the target.
7. `ml/predictor.py`.
8. Wire into `tickets/views.py` (create + a new override view) and
   templates.
9. `ml/tests.py` + `tickets/tests.py` additions; run the full suite.
10. Update dependencies, environment/settings documentation, Railway artifact
    generation, the RTM, and `testing_and_evaluation.md`.
