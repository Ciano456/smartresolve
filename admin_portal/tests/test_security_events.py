# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from __future__ import annotations

from django.test import RequestFactory, TestCase, override_settings

from admin_portal.audit import record_audit_log
from admin_portal.models import AuditLog
from admin_portal.security import get_client_ip, security_ticket_severity


class ClientIPTests(TestCase):
    # Covers get_client_ip and record_audit_log's IP capture, including
    # the TRUST_PROXY_HEADERS setting deciding whether a forwarded
    # header is trusted or ignored.
    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_remote_address_is_used_by_default(self):
        request = self.factory.get("/", REMOTE_ADDR="192.0.2.20")
        self.assertEqual(get_client_ip(request), "192.0.2.20")

    @override_settings(TRUST_PROXY_HEADERS=True)
    def test_trusted_forwarded_address_is_used(self):
        request = self.factory.get(
            "/",
            REMOTE_ADDR="10.0.0.5",
            HTTP_X_FORWARDED_FOR="2001:db8::10, 10.0.0.5",
        )
        self.assertEqual(get_client_ip(request), "2001:db8::10")

    @override_settings(TRUST_PROXY_HEADERS=False)
    def test_untrusted_forwarded_address_is_ignored(self):
        request = self.factory.get(
            "/",
            REMOTE_ADDR="192.0.2.21",
            HTTP_X_FORWARDED_FOR="198.51.100.99",
        )
        self.assertEqual(get_client_ip(request), "192.0.2.21")

    @override_settings(TRUST_PROXY_HEADERS=True)
    def test_malformed_forwarded_address_falls_back(self):
        request = self.factory.get(
            "/",
            REMOTE_ADDR="192.0.2.22",
            HTTP_X_FORWARDED_FOR="not-an-address",
        )
        self.assertEqual(get_client_ip(request), "192.0.2.22")

    def test_audit_writer_captures_ip_and_security_defaults(self):
        request = self.factory.post("/login/", REMOTE_ADDR="203.0.113.7")
        record_audit_log(
            actor=None,
            action=AuditLog.ACTION_LOGIN_RATE_LIMITED,
            target_type="User",
            target_id=None,
            target_repr="person@example.com",
            message="Login limit reached.",
            request=request,
        )
        event = AuditLog.objects.get()
        self.assertEqual(str(event.ip_address), "203.0.113.7")
        self.assertEqual(event.severity, AuditLog.SEVERITY_HIGH)
        self.assertTrue(event.flagged)


class SecurityPolicyTests(TestCase):
    # Covers security_ticket_severity, checking keyword matches win over
    # a plain confidence score, and that a decent confidence score alone
    # is still enough to raise the severity.
    def test_critical_keyword_sets_critical_severity(self):
        self.assertEqual(
            security_ticket_severity("ransomware, phishing", 0.4),
            AuditLog.SEVERITY_CRITICAL,
        )

    def test_model_only_signal_sets_medium_severity(self):
        self.assertEqual(
            security_ticket_severity("", 0.7),
            AuditLog.SEVERITY_MEDIUM,
        )

    def test_high_confidence_model_signal_sets_high_severity(self):
        self.assertEqual(
            security_ticket_severity("", 0.9),
            AuditLog.SEVERITY_HIGH,
        )
