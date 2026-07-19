# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

"""
The "keyword-based rules" half of FR8's security triage, kept separate
from the ML model on purpose. A plain word or phrase check has two big
advantages over relying on the model alone. It still works even if the
security model fails to load, and it's completely explainable. If a
ticket gets flagged because of a keyword, the exact phrase that triggered
it is known and can be shown to an admin, instead of just an opaque model
confidence score.
"""

from __future__ import annotations

import re

# Each pattern is kept narrow and uses \b word boundaries so it only
# matches whole words or phrases, not random substrings inside other
# words. This matters. See the "benign password reset" test in
# ml/tests.py, which checks that ordinary support language like "reset my
# forgotten password" does not get treated as a security incident just
# because it shares a word with phrases like "credential theft". Being
# too aggressive here would flood admins with false alarms and make the
# whole triage feature useless.
SECURITY_PATTERNS = {
    "phishing": r"\bphish(?:ing)?\b",
    "suspicious email": r"\bsuspicious (?:email|message)\b",
    "suspicious attachment": r"\bsuspicious attachment\b",
    "malware": r"\bmalware\b",
    "virus": r"\bvirus\b",
    "ransomware": r"\bransomware\b",
    "spoofing": r"\bspoof(?:ed|ing)?\b",
    "compromised": r"\bcompromis(?:e|ed)\b",
    "breach": r"\b(?:data )?breach\b",
    "unauthorised access": r"\bunauthori[sz]ed access\b",
    "stolen device": r"\bstolen (?:device|laptop|phone)\b",
    "lost device": r"\blost (?:device|laptop|phone)\b",
    "fraud": r"\bfraud(?:ulent)?\b",
    "scam": r"\bscam\b",
    "credential theft": r"\b(?:credential theft|stolen credentials)\b",
}


def keyword_match(text: str) -> list[str]:
    """Return every strong security phrase found in the given text
    (title and description combined). An empty list means the keyword
    rules found nothing suspicious, but that's not the final answer on
    its own. predictor.py also checks the ML model's opinion before
    deciding whether to flag the ticket."""
    return [
        label
        for label, pattern in SECURITY_PATTERNS.items()
        if re.search(pattern, text, flags=re.IGNORECASE)
    ]
