# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from __future__ import annotations

import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from .exceptions import GraphConfigurationError, GraphDeliveryError
from .graph_client import GraphClient, GraphSendResult
from .models import NotificationEvent
from .services import NotificationService


class DummyGraphClient:
    def __init__(
        self,
        result: GraphSendResult | None = None,
        error: Exception | None = None,
    ) -> None:
        self.result = result or GraphSendResult(message_id="message-123")
        self.error = error
        self.calls: list[dict[str, str]] = []

    def send_mail(
        self,
        *,
        recipient_email: str,
        subject: str,
        text_body: str,
        html_body: str = "",
    ) -> GraphSendResult:
        self.calls.append(
            {
                "recipient_email": recipient_email,
                "subject": subject,
                "text_body": text_body,
                "html_body": html_body,
            }
        )
        if self.error:
            raise self.error
        return self.result


class NotificationEventModelTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            email="sender@test.com",
            password="testpass123",
        )

    def test_notification_event_string_representation(self) -> None:
        event = NotificationEvent.objects.create(
            event_type=NotificationEvent.EventType.GENERIC,
            recipient_email="recipient@test.com",
            subject="Subject",
            text_body="Body",
            created_by=self.user,
        )

        self.assertIn("recipient@test.com", str(event))
        self.assertEqual(event.delivery_status, NotificationEvent.DeliveryStatus.SKIPPED)


class NotificationServiceTests(TestCase):
    SUBJECT_TEMPLATE = "notifications/emails/subject.txt"
    TEXT_TEMPLATE = "notifications/emails/body.txt"
    HTML_TEMPLATE = "notifications/emails/generic_notification.html"

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            email="sender@test.com",
            password="testpass123",
        )
        GraphClient._cached_token = ""
        GraphClient._cached_expires_at = None

    def test_send_notification_records_success(self) -> None:
        service = NotificationService(client=DummyGraphClient())

        event = service.send_notification(
            event_type=NotificationEvent.EventType.TICKET_CREATED,
            recipient_email="recipient@test.com",
            subject_template=self.SUBJECT_TEMPLATE,
            text_template=self.TEXT_TEMPLATE,
            html_template=self.HTML_TEMPLATE,
            context={
                "subject": "Ticket created",
                "recipient_name": "Alex",
                "body": "Your ticket has been created.",
            },
            created_by_id=self.user.id,
        )

        event.refresh_from_db()
        self.assertEqual(event.delivery_status, NotificationEvent.DeliveryStatus.SENT)
        self.assertEqual(event.provider_message_id, "message-123")
        self.assertEqual(event.created_by_id, self.user.id)
        self.assertEqual(event.subject, "Ticket created")
        self.assertIn("Your ticket has been created.", event.text_body)

    def test_send_notification_records_delivery_failure(self) -> None:
        service = NotificationService(client=DummyGraphClient(error=GraphDeliveryError("boom")))

        event = service.send_notification(
            event_type=NotificationEvent.EventType.TICKET_UPDATED,
            recipient_email="recipient@test.com",
            subject_template=self.SUBJECT_TEMPLATE,
            text_template=self.TEXT_TEMPLATE,
            context={
                "subject": "Ticket updated",
                "recipient_name": "Alex",
                "body": "Your ticket has been updated.",
            },
            created_by_id=self.user.id,
        )

        event.refresh_from_db()
        self.assertEqual(event.delivery_status, NotificationEvent.DeliveryStatus.FAILED)
        self.assertIn("boom", event.error_message)
        self.assertEqual(event.created_by_id, self.user.id)

    def test_send_notification_records_config_failure(self) -> None:
        service = NotificationService(client=DummyGraphClient(error=GraphConfigurationError("missing config")))

        event = service.send_notification(
            event_type=NotificationEvent.EventType.TICKET_UPDATED,
            recipient_email="recipient@test.com",
            subject_template=self.SUBJECT_TEMPLATE,
            text_template=self.TEXT_TEMPLATE,
            context={
                "subject": "Ticket updated",
                "recipient_name": "Alex",
                "body": "Your ticket has been updated.",
            },
            created_by_id=self.user.id,
        )

        event.refresh_from_db()
        self.assertEqual(event.delivery_status, NotificationEvent.DeliveryStatus.FAILED)
        self.assertIn("missing config", event.error_message)


@override_settings(
    GRAPH_TENANT_ID="tenant-id",
    GRAPH_CLIENT_ID="client-id",
    GRAPH_CLIENT_SECRET="client-secret",
    GRAPH_SENDER_USER="sender@test.com",
    GRAPH_TOKEN_URL="https://example.com/token",
    GRAPH_SEND_MAIL_URL="https://example.com/sendMail",
)
class GraphClientTests(TestCase):
    def setUp(self) -> None:
        GraphClient._cached_token = ""
        GraphClient._cached_expires_at = None

    def test_validate_config_raises_for_missing_settings(self) -> None:
        with override_settings(
            GRAPH_TENANT_ID="",
            GRAPH_CLIENT_ID="client-id",
            GRAPH_CLIENT_SECRET="client-secret",
            GRAPH_SENDER_USER="sender@test.com",
            GRAPH_TOKEN_URL="",
            GRAPH_SEND_MAIL_URL="",
        ):
            client = GraphClient()
            with self.assertRaises(GraphConfigurationError):
                client.send_mail(
                    recipient_email="recipient@test.com",
                    subject="Subject",
                    text_body="Body",
                )

    def test_send_mail_requests_token_and_send_mail(self) -> None:
        class DummyResponse:
            def __init__(self, payload: dict[str, object]) -> None:
                self.payload = payload

            def __enter__(self) -> "DummyResponse":
                return self

            def __exit__(self, exc_type, exc, tb) -> None:
                return None

            def read(self) -> bytes:
                return json.dumps(self.payload).encode("utf-8")

        responses = [
            DummyResponse({"access_token": "token-123", "expires_in": 3600}),
            DummyResponse({}),
        ]

        def fake_urlopen(*args, **kwargs):
            return responses.pop(0)

        client = GraphClient()
        with patch("notifications.graph_client.request.urlopen", side_effect=fake_urlopen) as mocked_urlopen:
            result = client.send_mail(
                recipient_email="recipient@test.com",
                subject="Subject",
                text_body="Body",
            )

        self.assertEqual(result.message_id, "")
        self.assertEqual(mocked_urlopen.call_count, 2)

    def test_send_mail_wraps_timeout_errors(self) -> None:
        def fake_urlopen(*args, **kwargs):
            raise TimeoutError("timed out")

        client = GraphClient()
        with patch("notifications.graph_client.request.urlopen", side_effect=fake_urlopen):
            with self.assertRaises(GraphDeliveryError):
                client.send_mail(
                    recipient_email="recipient@test.com",
                    subject="Subject",
                    text_body="Body",
                )
