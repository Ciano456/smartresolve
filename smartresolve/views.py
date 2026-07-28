# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

import logging

from django.db import DatabaseError, connections
from django.http import HttpRequest, JsonResponse
from django.views import View

logger = logging.getLogger(__name__)


# A simple endpoint a hosting platform (Railway) can poll to check the
# app is actually up and can talk to its database, not just that the web
# server process is running.
class HealthCheckView(View):
    http_method_names = ["get", "head", "options"]

    def get(self, request: HttpRequest) -> JsonResponse:
        try:
            # A trivial query just to prove the database connection
            # actually works, not just that Django itself started up.
            with connections["default"].cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        except DatabaseError:
            logger.warning("Health check database query failed.")
            return JsonResponse({"status": "unavailable"}, status=503)

        return JsonResponse({"status": "healthy"})
