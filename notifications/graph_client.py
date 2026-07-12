# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from __future__ import annotations

import json
import logging
import socket
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib import parse, request, error

from django.conf import settings

from .exceptions import GraphConfigurationError, GraphDeliveryError

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class GraphSendResult:
    message_id: str = ""


class GraphClient:
    REQUEST_TIMEOUT_SECONDS = 10
    _cached_token: str = ""
    _cached_expires_at: datetime | None = None

    def __init__(self) -> None:
        self.tenant_id = settings.GRAPH_TENANT_ID
        self.client_id = settings.GRAPH_CLIENT_ID
        self.client_secret = settings.GRAPH_CLIENT_SECRET
        self.sender_user = settings.GRAPH_SENDER_USER
        self.scope = settings.GRAPH_SCOPE
        self.token_url = settings.GRAPH_TOKEN_URL
        self.send_mail_url = settings.GRAPH_SEND_MAIL_URL

    def _validate_config(self) -> None:
        missing = [
            name
            for name, value in (
                ("GRAPH_TENANT_ID", self.tenant_id),
                ("GRAPH_CLIENT_ID", self.client_id),
                ("GRAPH_CLIENT_SECRET", self.client_secret),
                ("GRAPH_SENDER_USER", self.sender_user),
            )
            if not value
        ]
        if missing:
            raise GraphConfigurationError(
                f"Missing Microsoft Graph configuration: {', '.join(missing)}"
            )

    def _token_is_valid(self) -> bool:
        return bool(
            self._cached_token
            and self._cached_expires_at
            and datetime.now(timezone.utc) < self._cached_expires_at
        )

    def _build_token_request(self) -> request.Request:
        form_data = parse.urlencode(
            {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": self.scope,
                "grant_type": "client_credentials",
            }
        ).encode("utf-8")

        return request.Request(
            self.token_url,
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )

    def _build_mail_request(self, access_token: str, message: dict[str, Any]) -> request.Request:
        return request.Request(
            self.send_mail_url,
            data=json.dumps(message).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

    def _request_token(self) -> str:
        self._validate_config()
        if self._token_is_valid():
            return self._cached_token

        try:
            with request.urlopen(
                self._build_token_request(),
                timeout=self.REQUEST_TIMEOUT_SECONDS,
            ) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="ignore")
            raise GraphDeliveryError(
                f"Microsoft Graph token request failed with status {exc.code}: {body}"
            ) from exc
        except (error.URLError, TimeoutError, socket.timeout) as exc:
            raise GraphDeliveryError("Unable to acquire Microsoft Graph token.") from exc

        access_token = payload.get("access_token", "")
        expires_in = int(payload.get("expires_in", 3599))
        if not access_token:
            raise GraphDeliveryError("Microsoft Graph token response did not include an access token.")

        self._cached_token = access_token
        self._cached_expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=max(expires_in - 60, 0)
        )
        return access_token

    def send_mail(
        self,
        *,
        recipient_email: str,
        subject: str,
        text_body: str,
        html_body: str = "",
    ) -> GraphSendResult:
        access_token = self._request_token()
        message: dict[str, Any] = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML" if html_body else "Text",
                    "content": html_body or text_body,
                },
                "toRecipients": [{"emailAddress": {"address": recipient_email}}],
            },
            "saveToSentItems": False,
        }

        try:
            with request.urlopen(
                self._build_mail_request(access_token, message),
                timeout=self.REQUEST_TIMEOUT_SECONDS,
            ) as response:
                response.read()
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="ignore")
            raise GraphDeliveryError(
                f"Microsoft Graph mail send failed with status {exc.code}: {body}"
            ) from exc
        except (error.URLError, TimeoutError, socket.timeout) as exc:
            raise GraphDeliveryError("Microsoft Graph mail send failed due to network error.") from exc

        logger.debug("Graph sendMail accepted for %s", recipient_email)
        return GraphSendResult()
