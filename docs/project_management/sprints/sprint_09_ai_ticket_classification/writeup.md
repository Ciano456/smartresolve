# Sprint 9 Write-Up

Sprint 9 implemented FR8, AI-assisted ticket categorisation, together with
security triage and a staff-controlled correction workflow. The feature remains
advisory: it helps staff identify the likely issue category and potentially
sensitive tickets, but it does not prevent ticket creation or replace a staff
decision.

The implementation introduced a separate issue-category taxonomy of Hardware,
Software, Network, and Access. This was intentionally kept separate from the
existing `TicketType` model because ticket type describes the support workflow,
whereas the AI category describes the technical subject of the issue. Each ticket
can have one auditable prediction record containing the suggested category,
confidence, model details, security result, matched keywords, threshold, and any
staff override.

The classifier uses TF-IDF text features from the combined ticket title and
description. Logistic Regression and Multinomial Naive Bayes are trained and
evaluated using the same features so their results can be compared fairly. A
separate Logistic Regression model handles binary security triage, supplemented
by strong phrase rules for concerns such as phishing, malware, ransomware,
credential theft, unauthorised access, and stolen devices. Routine support issues
such as a normal password reset are not treated as security incidents solely
because they contain authentication vocabulary.

Ticket creation calls the ML service after the main ticket has been saved. Missing,
corrupt, or incompatible model artifacts fail safely and leave the ticket available
for manual categorisation. Category and security inference are also isolated from
one another, so an unavailable category model does not suppress a valid security
warning. Staff can review and override a suggestion, with the correction and actor
recorded for audit purposes. Related prediction data is loaded with the ticket
querysets to avoid introducing an N+1 query problem.

## Dataset And Evaluation Approach

No suitable historical production dataset was available, so the sprint used the
synthetic-data approach approved in the project proposal. The final deterministic
development dataset contains 720 unique examples, balanced at 180 tickets per
category. It is built from 60 independently written source templates, with 15 per
category. Variations from the same source share a `template_group` so closely
related sentences cannot leak between training and validation.

Evaluation uses grouped five-fold cross-validation. Every source template appears
in validation exactly once, and every fold contains examples from all four
categories. Candidate models are selected using mean macro F1 rather than accuracy
alone, ensuring that a model cannot win by performing well only on the easiest
categories. After selection, the winning model is refitted using all development
data. The 60 tickets that informed refinement are retained separately as
`tickets_evaluation.csv`. Final evidence comes from a second 60-ticket holdout with
15 newly authored and pre-labelled tickets per category.

The training command records fold-level metrics, mean and standard deviation,
aggregate per-category results, confusion matrices, threshold candidates, holdout
errors, dependency versions, dataset hashes, and artifact hashes in
`ml/artifacts/metrics.json`. The frozen final holdout SHA-256 is
`81f6ff1e5a8b5ef75a438363dd29d85b71177d40f6d82d573a70936d7224d85b`.
Dataset validation rejects duplicate ticket text, unbalanced classes, malformed
security labels, cross-category template groups, and overlap between development,
iterative evaluation, and final holdout data.

## Challenges Faced

The main challenge was obtaining an honest estimate of generalisation from a small
synthetic dataset. The first version contained only five templates per category,
with each template repeated through filler substitutions. Its fixed validation
split held out one complete template per category. This correctly prevented direct
template leakage, but it also meant that the result depended heavily on four pieces
of unseen wording.

This weakness became visible in the Access category. Both candidate models predicted
30 of the 32 held-out Access tickets as Software. The held-out ticket described an
application that opened but denied the user's permission, while also containing the
strong Software terms "finance software" and "application". Removing those terms
during a read-only diagnostic changed both models back to Access, confirming that
Software vocabulary outweighed the valid Access indicators.

Further grouped checks showed that the problem was not limited to one unlucky
Finance example. When the password-reset template was held out, 31 of its 32
variations were also predicted as Software because password-related wording appeared
inside a Software training example. Other categories showed similar instability on
particular unseen templates. Overall validation accuracy was only 66.4% for Logistic
Regression and 68.0% for Naive Bayes, below the project's approximate 75-85% target.
The original 75% holdout result could not resolve this concern because it was based
on only 12 tickets.

The issue was addressed at the data and evaluation level rather than by adding
special-case category keywords or tuning the models against the failing validation
examples. Each category was expanded to 15 distinct templates, including carefully
labelled boundary cases. Examples now distinguish an application denying permission
(Access) from an application accepting login and then freezing (Software), and a
shared drive denying authorisation (Access) from a drive being unreachable over VPN
(Network). Shared vocabulary is retained where it occurs naturally so the task does
not become artificially easy.

The security classifier initially exposed the same limitation. Three repeated
security phrases performed perfectly during development evaluation but reached only
58.3% recall on independently worded holdout cases. Security variants were therefore
expanded to cover different realistic descriptions of phishing, ransomware,
credential theft, suspicious administration, possible breaches, malware, and lost
or stolen devices. Two holdout labels describing battery and charger safety faults
were also corrected because they were hardware risks rather than information-security
incidents. These changes were based on label meaning and coverage, not on forcing a
preferred score.

Because that 58.3% result influenced the next training dataset, those 60 tickets
could no longer support a claim of untouched final evaluation. They were renamed as
the iterative evaluation set rather than discarded. Once the implementation was
frozen, a second set of 60 tickets was independently authored and labelled. Its hash
was recorded before inference, its initial result was accepted, and no subsequent
change was made to data, labels, features, models, or threshold logic. A later
deterministic rerun verified reproducibility after the hash checks were added.

Another challenge was preserving the required human-in-the-loop behaviour when an
ML dependency fails. The predictor and service layers were designed to degrade
gracefully, and tests explicitly cover missing artifacts, corrupt artifacts,
persistence failures, unsupported labels, and independent security fallback. This
keeps the core support workflow reliable even when the optional classifier is not
available.

## Final Evaluation

Logistic Regression was selected as the category classifier. It achieved 82.5% mean
grouped cross-validation accuracy with a standard deviation of 6.9 percentage points,
and 0.815 mean macro F1 with a standard deviation of 0.076. Naive Bayes achieved
81.3% mean accuracy and 0.801 mean macro F1 on the same folds.

Across all out-of-fold Logistic Regression predictions, Access recall improved to
85.0%. Network recall was 89.4% and Software recall was 90.6%. Hardware remained the
weakest category at 65.0% recall, with physical-device reports still sometimes
confused with Network or Software symptoms. Fold accuracy ranged from 75.0% to 95.1%,
which demonstrates that performance continues to depend on the wording held out.

After refitting on all development data, the selected category model achieved 95.0%
accuracy and 0.949 macro F1 on the iterative evaluation set. These figures show the
post-refinement behaviour but are not presented as independent final evidence.

On the frozen final holdout, the category model achieved 91.7% accuracy and 0.917
macro F1. Access recall was 93.3%, Hardware and Network recall were each 86.7%, and
Software recall was 100%. Five tickets were incorrect: a laptop storage failure was
predicted as Network, a scanner sensor fault as Software, suspicious outbound traffic
as Hardware, an intermittent DNS failure as Software, and phishing-exposed
credentials as Hardware. The result was accepted without further model or dataset
changes.

The security model selected a recall-oriented threshold of 0.55 using only
out-of-fold development probabilities. It achieved 98.3% accuracy, 100% precision,
91.7% recall, and 0.957 security F1 on the iterative evaluation set. On the frozen
final holdout it achieved 90.0% accuracy, 80.0% precision, 66.7% recall, 0.727
security F1, and 0.981 ROC-AUC. Four of the 12 security-positive tickets were missed
and two normal tickets were false positives. The existing narrow keyword rules did
not change those outcomes. This weaker result is retained as the honest final
security evidence and shows that broader real-world security language remains future
work.

## Review Follow-Up

A final code and evidence review identified several hardening improvements after the
frozen evaluation was introduced. These changes did not alter the datasets, feature
configuration, selected algorithms, trained threshold, or reported outcomes.

The security threshold stored in a model artifact is now parsed and range-checked
inside the predictor's fallback boundary. Missing, non-numeric, infinite, or
out-of-range metadata falls back to 0.5 and logs a warning. This prevents a malformed
artifact from discarding an otherwise valid category result or keyword security flag,
and preserves FR8's requirement that optional AI failure must not interrupt the core
ticket workflow.

Dataset provenance is now enforced rather than merely reported. The approved SHA-256
values for development, iterative evaluation, and final holdout data are stored in
`ml/data/dataset_hashes.json`. The training command verifies every file against that
manifest before model fitting or inference and stops with a specific error if any
content has changed. Regression tests also pin the final holdout to its approved hash.
This was necessary because recalculating a file's current hash twice proves only
determinism; it does not prove that the frozen file remained unchanged.

The generated metrics report now records the iterative evaluation results under
separate `category_iterative_evaluation` and `security_iterative_evaluation` keys.
Frozen results remain under the holdout keys. This keeps the earlier 95.0% category
and 98.3% security figures reproducible without presenting them as independent final
evidence. A deterministic evidence rerun reproduced all results after the manifest
check, with no tuning or data changes between runs.

Prediction audit consistency was also tightened with a database constraint linking a
staff override category to its override timestamp. This prevents an override from
being stored without evidence of when it occurred, while retaining `SET_NULL` for the
actor if that user is later deleted. The corresponding migration and constraint test
were added.

## Verification

- Full local test suite: 226 tests passed on 19 July 2026.
- Focused ML suite: 21 tests passed after the final review fixes.
- Ruff checks passed for the generator, training command, and ML tests.
- Django system check completed with no issues.
- Generated model files match the SHA-256 hashes recorded in the metrics report.
- Migration consistency check reported no missing model changes.

## Lessons Learned And Limitations

The central lesson from this sprint was that preventing direct data leakage is
necessary but does not make a small template dataset representative. A single grouped
split exposed one real weakness, while grouped cross-validation showed how widely
performance varied across different unseen language. Per-category recall, fold
variation, and error examples provided a more useful account than one headline
accuracy figure.

The category results meet the stated accuracy target, but they remain synthetic
evaluation results rather than evidence of production performance. The independently
frozen category score of 91.7% is encouraging, while the cross-validation mean of
82.5% remains useful because it covers every development template. Hardware recall,
fold variation, and final security recall of 66.7% are known weaknesses. Future work
should use consented, anonymised support tickets, preserve grouped evaluation, freeze
new holdouts before inference, and monitor staff overrides to identify recurring
real-world classification errors.

## Current Deliverable Status

Sprint 9 implementation, automated testing, model evaluation, and supporting
documentation are complete in the current working tree and ready for review. The
feature remains deliberately assistive: staff retain control over the effective
category, security flags request review rather than automatically changing ticket
priority, and ticket submission continues when either trained artifact is unavailable.
