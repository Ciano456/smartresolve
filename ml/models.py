# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from __future__ import annotations

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q


class TicketCategoryPrediction(models.Model):
    """One row per ticket, storing whatever the AI suggested for it (FR8).

    This lives in the ml app rather than as extra columns on
    tickets.Ticket on purpose. It keeps all the AI-specific fields in one
    place, and means the tickets app's own models and migrations never
    had to be touched to add this feature. A ticket that predates this
    feature, or one the AI couldn't classify, simply has no matching row
    here (see the ai_prediction related_name below, it's optional).
    """

    CATEGORY_CHOICES = [
        ("hardware", "Hardware"),
        ("software", "Software"),
        ("network", "Network"),
        ("access", "Access"),
    ]

    # One-to-one, not a foreign key list, because a ticket only ever gets
    # classified once, when it's created. There's no need to keep a
    # history of multiple predictions per ticket.
    ticket = models.OneToOneField(
        "tickets.Ticket", on_delete=models.CASCADE, related_name="ai_prediction"
    )
    predicted_category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, blank=True
    )
    # Blank/null rather than a default of 0, because "the model wasn't
    # available so there's no confidence to show" is a real, valid state,
    # and it's not the same thing as a confidence of 0.
    confidence = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
    )
    # Which algorithm produced this suggestion (for example
    # "LogisticRegression" or "MultinomialNB") and a hash of the exact
    # model file used, so a prediction can always be traced back to
    # exactly how it was made. Useful for the report and for debugging.
    category_model_name = models.CharField(max_length=50, blank=True)
    category_model_version = models.CharField(max_length=64, blank=True)
    is_security_flagged = models.BooleanField(default=False)
    security_confidence = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
    )
    # The threshold that was actually applied when this prediction was
    # made is stored on the row itself, not just read from whatever the
    # current setting is. That way, if the threshold gets tuned later,
    # old predictions still show what rule produced them at the time.
    security_threshold = models.FloatField(
        default=0.5, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    matched_keywords = models.CharField(max_length=255, blank=True)
    # Staff can always correct the AI's guess (FR8's manual override
    # flow). This is stored separately from predicted_category rather
    # than overwriting it, so there's always a record of what the AI
    # originally said versus what a human decided was actually correct.
    # That comparison is good evidence for the report, and would also be
    # the natural starting point for retraining on real corrections
    # later on.
    staff_override_category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, blank=True
    )
    overridden_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="ticket_category_overrides",
    )
    overridden_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # These back up the field validators above at the database level.
        # Even if something bypassed Django's normal validation, for
        # example a raw database write, the database itself would still
        # refuse to store a confidence value outside 0 to 1.
        constraints = [
            models.CheckConstraint(
                condition=Q(confidence__gte=0.0, confidence__lte=1.0),
                name="ml_prediction_confidence_range",
            ),
            models.CheckConstraint(
                condition=(
                    Q(security_confidence__isnull=True)
                    | Q(security_confidence__gte=0.0, security_confidence__lte=1.0)
                ),
                name="ml_security_confidence_range",
            ),
            models.CheckConstraint(
                condition=Q(security_threshold__gte=0.0, security_threshold__lte=1.0),
                name="ml_security_threshold_range",
            ),
            models.CheckConstraint(
                condition=(
                    Q(staff_override_category="", overridden_at__isnull=True)
                    | (~Q(staff_override_category="") & Q(overridden_at__isnull=False))
                ),
                name="ml_override_category_timestamp_consistent",
            ),
        ]

    @property
    def effective_category(self) -> str:
        # Whatever the human said wins, if a human has said anything at
        # all. This is the one value the rest of the app should display
        # or filter on, so callers never have to remember to check
        # whether a prediction was overridden themselves.
        return self.staff_override_category or self.predicted_category

    @property
    def effective_category_display(self) -> str:
        return dict(self.CATEGORY_CHOICES).get(self.effective_category, "Uncategorised")

    def __str__(self) -> str:
        return f"{self.ticket.ticket_number}: {self.effective_category_display}"
