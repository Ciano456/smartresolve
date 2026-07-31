# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from collections.abc import Callable

from django.http import HttpRequest, HttpResponse
from django.utils.cache import patch_cache_control


class AuthenticatedNoStoreMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        user = getattr(request, "user", None)
        is_authenticated = bool(user and user.is_authenticated)
        response = self.get_response(request)

        if is_authenticated:
            # After logout the session is gone, but a browser can still
            # redraw the last page from its own cache when Back is pressed.
            # These headers tell it not to keep authenticated pages around.
            patch_cache_control(
                response,
                no_cache=True,
                no_store=True,
                must_revalidate=True,
                private=True,
            )

        return response
