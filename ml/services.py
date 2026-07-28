# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

"""
Connects a saved Ticket to the AI predictor: runs the prediction and
saves it as a TicketCategoryPrediction row, or does nothing if anything
along the way isn't available. This is the only function tickets/views.py
needs to call. It doesn't need to know or care whether the AI feature is
working, half working, or hasn't been trained at all.
"""

from __future__ import annotations

import logging

from django.db import DatabaseError

from tickets.models import Ticket

from .models import TicketCategoryPrediction
from .predictor import predict_for_ticket

logger = logging.getLogger(__name__)

# Read once from the model's own choices so this can never drift out of
# sync with what TicketCategoryPrediction actually accepts. If a category
# is ever added or renamed on the model, this set updates itself.
VALID_CATEGORIES = {
    value for value, _label in TicketCategoryPrediction.CATEGORY_CHOICES
}


def create_prediction_for_ticket(ticket: Ticket) -> TicketCategoryPrediction | None:
    """Called right after a ticket is saved. Returns the new prediction
    row, or None if nothing could be saved. Callers should treat None as
    "no suggestion this time", not as an error to show the user."""
    try:
        result = predict_for_ticket(ticket.title, ticket.description)
    except Exception:
        # predict_for_ticket already catches its own failures, but this
        # is a second safety net in case something unexpected slips
        # through. Ticket creation should survive no matter what happens
        # on the AI side.
        logger.exception("AI inference failed for ticket %s.", ticket.pk)
        return None
    if not result.available:
        return None
    if result.category and result.category not in VALID_CATEGORIES:
        # This would only happen if a trained model on disk came from an
        # older or different version of the taxonomy, for example someone
        # accidentally loading a model trained on a different label set.
        # Refusing to save an unrecognised category protects the database
        # instead of silently storing something that doesn't match the
        # choices.
        logger.error(
            "AI model returned unsupported category %r for ticket %s.",
            result.category,
            ticket.pk,
        )
        return None
    try:
        return TicketCategoryPrediction.objects.create(
            ticket=ticket,
            predicted_category=result.category,
            # Confidence only makes sense if a category was actually
            # predicted. If only the security triage side is available,
            # for example the category model is down but the keyword
            # rules still fired, there is no category confidence to
            # store.
            confidence=result.confidence if result.category_available else None,
            category_model_name=result.category_model_name,
            category_model_version=result.category_model_version,
            is_security_flagged=result.is_security_flagged,
            security_confidence=result.security_confidence,
            security_threshold=result.security_threshold,
            matched_keywords=", ".join(result.matched_keywords)[:255],
        )
    except DatabaseError:
        # Covers things like the database being briefly unreachable. The
        # ticket itself is already saved by this point, so a failure here
        # just means it goes without an AI suggestion instead of the
        # whole request failing.
        logger.exception("Failed to persist AI prediction for ticket %s.", ticket.pk)
        return None
