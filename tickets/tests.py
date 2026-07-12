# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase, override_settings
from .models import Ticket, TicketType, TicketSystem, TicketPriority, TicketStatus, TicketComment, TicketAttachment, TicketHistory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models.deletion import ProtectedError
from django.urls import reverse
from django.utils import timezone

from .forms import TicketAttachmentForm
from . import notifications as ticket_notifications
from notifications.models import NotificationEvent


class TicketModelTest(TestCase):
    def setUp(self):
        # Set up a user for testing ticket creation
        User = get_user_model()
        self.user = User.objects.create_user(email='testuser@gmail.com', password='testpass')

        # Set up lookup data for testing
        self.ticket_type = TicketType.objects.get(code="INCIDENT") 
        self.ticket_system = TicketSystem.objects.get(code="SOFTWARE")  
        self.ticket_priority = TicketPriority.objects.get(code="MEDIUM")  
        self.ticket_status = TicketStatus.objects.get(code="OPEN") 

    def test_ticket_creation(self):
        # Test creating a ticket and checking its attributes
        ticket = Ticket.objects.create(
            title="Test Ticket",
            description="This is a test ticket.",
            submitter=self.user,
            ticket_type = self.ticket_type,
            ticket_system = self.ticket_system,
            ticket_priority = self.ticket_priority,
            ticket_status = self.ticket_status, 
        )
        self.assertEqual(ticket.title, "Test Ticket")
        self.assertEqual(ticket.submitter, self.user)
        self.assertEqual(ticket.ticket_type, self.ticket_type)
        self.assertIsNotNone(ticket.ticket_number)  # Ensure ticket number is generated

    def test_ticket_number_generation(self):
        Ticket.objects.create(
            title="Test Ticket 1",
            description="This is the first test ticket.",
            submitter=self.user,
            ticket_type = self.ticket_type,
            ticket_system = self.ticket_system,
            ticket_priority = self.ticket_priority,
            ticket_status = self.ticket_status, 
        )
        self.assertIsNotNone(Ticket.objects.first().ticket_number)  # Ensure ticket number is generated
        

    def test_ticket_status_transitions(self):
        # Test changing the status of a ticket and ensuring it behaves as expected
        ticket_status = Ticket.objects.create(
            title="Test Ticket 2",
            description="This is the second test ticket.",
            submitter=self.user,
            ticket_type = self.ticket_type,
            ticket_system = self.ticket_system,
            ticket_priority = self.ticket_priority,
            ticket_status = self.ticket_status, 
        )
        in_progress_status = TicketStatus.objects.get(code="IN_PROGRESS")
        ticket_status.ticket_status = in_progress_status
        ticket_status.save()
        self.assertEqual(ticket_status.ticket_status, in_progress_status)  # Check if status is updated correctly

    def test_ticket_assignment(self):
        # Test assigning a ticket to a user and checking the assigned_to field
        assignee = self.user
        ticket_assignment = Ticket.objects.create(
            title="Test Ticket 3",
            description="This is the third test ticket.",
            submitter=self.user,
            assigned_to=assignee,
            ticket_type = self.ticket_type,
            ticket_system = self.ticket_system,
            ticket_priority = self.ticket_priority,
            ticket_status = self.ticket_status, 
        )
        self.assertEqual(ticket_assignment.assigned_to, assignee)

    def test_ticket_closure(self):
        # Test closing a ticket and ensuring the status is updated to closed
        ticket = Ticket.objects.create(
            title="Test Ticket 4",
            description="This is the fourth test ticket.",
            submitter=self.user,
            ticket_type = self.ticket_type,
            ticket_system = self.ticket_system,
            ticket_priority = self.ticket_priority,
            ticket_status = self.ticket_status, 
        )
        closed_status = TicketStatus.objects.get(code="CLOSED")
        ticket.ticket_status = closed_status
        ticket.save()
        self.assertEqual(ticket.ticket_status, closed_status)
        self.assertIsNotNone(ticket.closed_at)  # Ensure closed_at is set when ticket is closed

    def test_ticket_priority(self):
        # Test setting a priority for a ticket and ensuring it is stored correctly
        ticket_priority = Ticket.objects.create(
            title="Test Ticket 5",
            description="This is the fifth test ticket.",
            submitter=self.user,
            ticket_type = self.ticket_type,
            ticket_system = self.ticket_system,
            ticket_priority = self.ticket_priority,
            ticket_status = self.ticket_status,
        )
        low_priority = TicketPriority.objects.get(code="LOW")
        ticket_priority.ticket_priority = low_priority
        ticket_priority.save()
        self.assertEqual(ticket_priority.ticket_priority, low_priority)

    def test_ticket_str_method(self):
        # Test the __str__ method of the Ticket model to ensure it returns the expected string representation
        ticket = Ticket.objects.create(
            title="Test Ticket 6",
            description="This is the sixth test ticket.",
            submitter=self.user,
            ticket_type = self.ticket_type,
            ticket_system = self.ticket_system,
            ticket_priority = self.ticket_priority,
            ticket_status = self.ticket_status,
        )
        self.assertTrue(str(ticket).startswith(ticket.ticket_number))  # Ensure string representation starts with ticket number

    def test_delete_ticket(self):
        # Test deleting a ticket and ensuring it is removed from the database
        ticket = Ticket.objects.create(
            title="Test Ticket 7",
            description="This is the seventh test ticket.",
            submitter=self.user,
            ticket_type = self.ticket_type,
            ticket_system = self.ticket_system,
            ticket_priority = self.ticket_priority,
            ticket_status = self.ticket_status,
        )
        ticket_id = ticket.id
        ticket.delete()
        self.assertFalse(Ticket.objects.filter(id=ticket_id).exists())

    def test_set_null_on_user_deletion(self):
        # Test that assigned_to is set to null when the assigned user is deleted
        assignee = get_user_model().objects.create_user(
            email='assignee@gmail.com',
            password='testpass',
        )
        ticket = Ticket.objects.create(
            title="Test Ticket 8",
            description="This is the eighth test ticket.",
            submitter=self.user,
            assigned_to=assignee,
            ticket_type = self.ticket_type,
            ticket_system = self.ticket_system,
            ticket_priority = self.ticket_priority,
            ticket_status = self.ticket_status,
        )
        assignee.delete()
        ticket.refresh_from_db()
        self.assertIsNone(ticket.assigned_to)

    def test_protect_on_submitter_deletion(self):
        # Test that deleting the submitter raises an error due to PROTECT on_delete behavior
        submitter = self.user
        ticket = Ticket.objects.create(
            title="Test Ticket 9",
            description="This is the ninth test ticket.",
            submitter=submitter,
            ticket_type = self.ticket_type,
            ticket_system = self.ticket_system,
            ticket_priority = self.ticket_priority,
            ticket_status = self.ticket_status,
        )
        with self.assertRaises(ProtectedError):
            submitter.delete()
        self.assertTrue(Ticket.objects.filter(id=ticket.id).exists())

    def test_set_null_on_comment_author_deletion(self):
        author = get_user_model().objects.create_user(
            email='author@gmail.com',
            password='testpass',
        )
        comment = TicketComment.objects.create(
            ticket=Ticket.objects.create(
                title="Test Ticket 9A",
                description="Comment author null test.",
                submitter=self.user,
                ticket_type=self.ticket_type,
                ticket_system=self.ticket_system,
                ticket_priority=self.ticket_priority,
                ticket_status=self.ticket_status,
            ),
            author=author,
            body="Test comment body.",
        )

        author.delete()
        comment.refresh_from_db()
        self.assertIsNone(comment.author)

    def test_set_null_on_attachment_uploader_deletion(self):
        uploader = get_user_model().objects.create_user(
            email='uploader@gmail.com',
            password='testpass',
        )
        simple_file = SimpleUploadedFile("uploader-test.txt", b"file_content", content_type="text/plain")
        ticket = Ticket.objects.create(
            title="Test Ticket 9B",
            description="Attachment uploader null test.",
            submitter=self.user,
            ticket_type=self.ticket_type,
            ticket_system=self.ticket_system,
            ticket_priority=self.ticket_priority,
            ticket_status=self.ticket_status,
        )
        attachment = TicketAttachment.objects.create(
            ticket=ticket,
            uploaded_by=uploader,
            file=simple_file,
            original_filename="uploader-test.txt",
        )

        uploader.delete()
        attachment.refresh_from_db()
        self.assertIsNone(attachment.uploaded_by)
        
    def test_cascade_on_ticket_deletion(self):
        # Test that deleting a ticket also deletes related comments, attachments, and history entries due to CASCADE on_delete behavior
        simple_file = SimpleUploadedFile("testfile.txt", b"file_content", content_type="text/plain")
        ticket = Ticket.objects.create(
            title="Test Ticket 10",
            description="This is the tenth test ticket.",
            submitter=self.user,
            ticket_type=self.ticket_type,
            ticket_system = self.ticket_system,
            ticket_priority = self.ticket_priority,
            ticket_status = self.ticket_status,
        )
        ticket_comment = TicketComment.objects.create(ticket=ticket, author=self.user, body="This is a comment for the tenth test ticket.")
        ticket_attachment = TicketAttachment.objects.create(ticket=ticket, uploaded_by=self.user, file=simple_file, original_filename="testfile.txt")
        ticket_history = TicketHistory.objects.create(ticket=ticket, changed_by=self.user, change_type="Status Change", field_name="ticket_status", old_value=self.ticket_status.name, new_value=self.ticket_status.name)

        ticket.delete()
        self.assertFalse(Ticket.objects.filter(id=ticket.id).exists())
        self.assertFalse(TicketComment.objects.filter(id=ticket_comment.id).exists())
        self.assertFalse(TicketAttachment.objects.filter(id=ticket_attachment.id).exists())
        self.assertFalse(TicketHistory.objects.filter(id=ticket_history.id).exists())
        
        
@override_settings(IT_SUPPORT_EMAIL="itsupport@test.com")
class TicketStaffViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.notification_send_patcher = patch(
            "tickets.notifications.NotificationService.send_notification",
            autospec=True,
            return_value=None,
        )
        self.notification_send_patcher.start()
        self.addCleanup(self.notification_send_patcher.stop)
        self.admin_group = Group.objects.create(name="Admin")
        self.submitter_group = Group.objects.create(name="Submitter")
        self.support_staff_group = Group.objects.create(name="Support Staff")
        self.admin_user = User.objects.create_user(
            email="admin-ticket@test.com",
            password="password123",
        )
        self.support_user = User.objects.create_user(
            email="support-ticket@test.com",
            password="password123",
        )
        self.second_support_user = User.objects.create_user(
            email="second-support-ticket@test.com",
            password="password123",
        )
        self.submitter_user = User.objects.create_user(
            email="submitter-ticket@test.com",
            password="password123",
        )
        self.other_submitter_user = User.objects.create_user(
            email="other-submitter-ticket@test.com",
            password="password123",
        )
        self.admin_user.groups.add(self.admin_group)
        self.support_user.groups.add(self.support_staff_group)
        self.second_support_user.groups.add(self.support_staff_group)
        self.submitter_user.groups.add(self.submitter_group)
        self.other_submitter_user.groups.add(self.submitter_group)
        self.ticket_type = TicketType.objects.get(code="INCIDENT")
        self.service_type = TicketType.objects.get(code="SERVICE")
        self.ticket_system = TicketSystem.objects.get(code="SOFTWARE")
        self.network_system = TicketSystem.objects.get(code="NETWORK")
        self.hardware_system = TicketSystem.objects.get(code="HARDWARE")
        self.low_priority = TicketPriority.objects.get(code="LOW")
        self.ticket_priority = TicketPriority.objects.get(code="MEDIUM")
        self.high_priority = TicketPriority.objects.get(code="HIGH")
        self.open_status = TicketStatus.objects.get(code="OPEN")
        self.in_progress_status = TicketStatus.objects.get(code="IN_PROGRESS")
        self.closed_status = TicketStatus.objects.get(code="CLOSED")
        self.cancelled_status = TicketStatus.objects.get(code="CANCELLED")
        self.ticket = Ticket.objects.create(
            title="Staff status test",
            description="Ticket used for staff status update tests.",
            submitter=self.submitter_user,
            ticket_type=self.ticket_type,
            ticket_system=self.ticket_system,
            ticket_priority=self.ticket_priority,
            ticket_status=self.open_status,
        )

    def _create_queue_ticket(
        self,
        title,
        submitter=None,
        assigned_to=None,
        ticket_type=None,
        ticket_system=None,
        ticket_priority=None,
        ticket_status=None,
    ):
        return Ticket.objects.create(
            title=title,
            description=f"{title} description.",
            submitter=submitter or self.submitter_user,
            assigned_to=assigned_to,
            ticket_type=ticket_type or self.ticket_type,
            ticket_system=ticket_system or self.ticket_system,
            ticket_priority=ticket_priority or self.ticket_priority,
            ticket_status=ticket_status or self.open_status,
        )

    def test_support_staff_can_update_ticket_status(self):
        # Support staff need to move tickets through the operational workflow.
        self.client.force_login(self.support_user)
        response = self.client.post(
            reverse("ticket_detail", args=[self.ticket.id]),
            {"ticket_status": self.in_progress_status.id},
        )

        self.assertRedirects(response, reverse("ticket_detail", args=[self.ticket.id]))
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.ticket_status, self.in_progress_status)
        self.assertTrue(
            TicketHistory.objects.filter(
                ticket=self.ticket,
                changed_by=self.support_user,
                change_type="STATUS_CHANGED",
                field_name="ticket_status",
                old_value="Open",
                new_value="In Progress",
            ).exists()
        )

    def test_closed_status_requires_dedicated_resolve_action(self):
        self.client.force_login(self.admin_user)
        response = self.client.post(
            reverse("ticket_detail", args=[self.ticket.id]),
            {"ticket_status": self.closed_status.id},
        )

        self.assertEqual(response.status_code, 400)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.ticket_status, self.open_status)
        self.assertIsNone(self.ticket.closed_at)
        self.assertContains(
            response,
            "Select a valid ticket status.",
            status_code=400,
        )

    def test_cancelled_status_requires_dedicated_cancel_action(self):
        self.client.force_login(self.admin_user)
        response = self.client.post(
            reverse("ticket_detail", args=[self.ticket.id]),
            {"ticket_status": self.cancelled_status.id},
        )

        self.assertEqual(response.status_code, 400)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.ticket_status, self.open_status)
        self.assertIsNone(self.ticket.closed_at)
        self.assertContains(
            response,
            "Select a valid ticket status.",
            status_code=400,
        )

    def test_support_staff_can_resolve_ticket_with_summary(self):
        self.client.force_login(self.support_user)
        response = self.client.post(
            reverse("ticket_resolve", args=[self.ticket.id]),
            {"resolution_summary": "Resolved by clearing cached credentials."},
        )

        self.assertRedirects(response, reverse("ticket_detail", args=[self.ticket.id]))
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.ticket_status, self.closed_status)
        self.assertEqual(
            self.ticket.resolution_summary,
            "Resolved by clearing cached credentials.",
        )
        self.assertEqual(self.ticket.cancellation_reason, "")
        self.assertIsNotNone(self.ticket.closed_at)
        self.assertFalse(
            TicketComment.objects.filter(
                ticket=self.ticket,
                body="Resolved by clearing cached credentials.",
            ).exists()
        )
        self.assertTrue(
            TicketHistory.objects.filter(
                ticket=self.ticket,
                changed_by=self.support_user,
                change_type="RESOLVED",
                field_name="ticket_status",
                old_value="Open",
                new_value="Closed",
            ).exists()
        )

    def test_blank_resolution_summary_is_rejected(self):
        self.client.force_login(self.support_user)
        response = self.client.post(
            reverse("ticket_resolve", args=[self.ticket.id]),
            {"resolution_summary": ""},
        )

        self.assertEqual(response.status_code, 400)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.ticket_status, self.open_status)
        self.assertEqual(self.ticket.resolution_summary, "")
        self.assertFalse(
            TicketHistory.objects.filter(
                ticket=self.ticket,
                change_type="RESOLVED",
            ).exists()
        )

    def test_submitter_cannot_resolve_ticket(self):
        self.client.force_login(self.submitter_user)
        response = self.client.post(
            reverse("ticket_resolve", args=[self.ticket.id]),
            {"resolution_summary": "Submitter should not resolve this."},
        )

        self.assertRedirects(response, reverse("profile"))
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.ticket_status, self.open_status)
        self.assertEqual(self.ticket.resolution_summary, "")
        self.assertFalse(TicketHistory.objects.filter(ticket=self.ticket).exists())

    def test_closed_ticket_cannot_be_resolved_again(self):
        self.ticket.ticket_status = self.closed_status
        self.ticket.resolution_summary = "Already resolved."
        self.ticket.save()

        self.client.force_login(self.support_user)
        response = self.client.post(
            reverse("ticket_resolve", args=[self.ticket.id]),
            {"resolution_summary": "Duplicate resolution."},
        )

        self.assertEqual(response.status_code, 400)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.resolution_summary, "Already resolved.")
        self.assertFalse(
            TicketHistory.objects.filter(
                ticket=self.ticket,
                change_type="RESOLVED",
            ).exists()
        )

    def test_admin_can_cancel_ticket_with_reason(self):
        self.client.force_login(self.admin_user)
        response = self.client.post(
            reverse("ticket_cancel", args=[self.ticket.id]),
            {"cancellation_reason": "Duplicate request raised by mistake."},
        )

        self.assertRedirects(response, reverse("ticket_detail", args=[self.ticket.id]))
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.ticket_status, self.cancelled_status)
        self.assertEqual(
            self.ticket.cancellation_reason,
            "Duplicate request raised by mistake.",
        )
        self.assertEqual(self.ticket.resolution_summary, "")
        self.assertIsNotNone(self.ticket.closed_at)
        self.assertFalse(
            TicketComment.objects.filter(
                ticket=self.ticket,
                body="Ticket cancelled: Duplicate request raised by mistake.",
            ).exists()
        )
        self.assertTrue(
            TicketHistory.objects.filter(
                ticket=self.ticket,
                changed_by=self.admin_user,
                change_type="CANCELLED",
                field_name="ticket_status",
                old_value="Open",
                new_value="Cancelled",
            ).exists()
        )

    def test_blank_cancellation_reason_is_rejected(self):
        self.client.force_login(self.support_user)
        response = self.client.post(
            reverse("ticket_cancel", args=[self.ticket.id]),
            {"cancellation_reason": ""},
        )

        self.assertEqual(response.status_code, 400)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.ticket_status, self.open_status)
        self.assertEqual(self.ticket.cancellation_reason, "")
        self.assertFalse(
            TicketHistory.objects.filter(
                ticket=self.ticket,
                change_type="CANCELLED",
            ).exists()
        )

    def test_submitter_cannot_cancel_ticket(self):
        self.client.force_login(self.submitter_user)
        response = self.client.post(
            reverse("ticket_cancel", args=[self.ticket.id]),
            {"cancellation_reason": "Submitter should not cancel this."},
        )

        self.assertRedirects(response, reverse("profile"))
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.ticket_status, self.open_status)
        self.assertEqual(self.ticket.cancellation_reason, "")
        self.assertFalse(TicketHistory.objects.filter(ticket=self.ticket).exists())

    def test_closed_ticket_cannot_be_cancelled_again(self):
        self.ticket.ticket_status = self.cancelled_status
        self.ticket.cancellation_reason = "Already cancelled."
        self.ticket.save()

        self.client.force_login(self.support_user)
        response = self.client.post(
            reverse("ticket_cancel", args=[self.ticket.id]),
            {"cancellation_reason": "Duplicate cancellation."},
        )

        self.assertEqual(response.status_code, 400)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.cancellation_reason, "Already cancelled.")
        self.assertFalse(
            TicketHistory.objects.filter(
                ticket=self.ticket,
                change_type="CANCELLED",
            ).exists()
        )

    def test_resolve_and_cancel_get_redirect_to_ticket_detail(self):
        self.client.force_login(self.support_user)

        resolve_response = self.client.get(
            reverse("ticket_resolve", args=[self.ticket.id])
        )
        cancel_response = self.client.get(
            reverse("ticket_cancel", args=[self.ticket.id])
        )

        self.assertRedirects(resolve_response, reverse("ticket_detail", args=[self.ticket.id]))
        self.assertRedirects(cancel_response, reverse("ticket_detail", args=[self.ticket.id]))

    def test_submitter_cannot_update_ticket_status_from_staff_view(self):
        # Submitters must not be able to use the staff ticket detail POST endpoint.
        self.client.force_login(self.submitter_user)
        response = self.client.post(
            reverse("ticket_detail", args=[self.ticket.id]),
            {"ticket_status": self.closed_status.id},
        )

        self.assertRedirects(response, reverse("profile"))
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.ticket_status, self.open_status)
        self.assertFalse(TicketHistory.objects.filter(ticket=self.ticket).exists())

    def test_invalid_status_update_is_rejected(self):
        # Invalid status ids should return an error and leave the ticket unchanged.
        self.client.force_login(self.support_user)
        response = self.client.post(
            reverse("ticket_detail", args=[self.ticket.id]),
            {"ticket_status": 999999},
        )

        self.assertEqual(response.status_code, 400)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.ticket_status, self.open_status)
        self.assertContains(response, "Select a valid ticket status.", status_code=400)
        self.assertFalse(TicketHistory.objects.filter(ticket=self.ticket).exists())

    def test_staff_ticket_detail_shows_comments_and_attachments(self):
        # Staff detail view should show related ticket discussion and uploaded files.
        simple_file = SimpleUploadedFile(
            "staff-detail.txt",
            b"file_content",
            content_type="text/plain",
        )
        TicketComment.objects.create(
            ticket=self.ticket,
            author=self.submitter_user,
            body="Visible staff comment.",
        )
        TicketAttachment.objects.create(
            ticket=self.ticket,
            uploaded_by=self.submitter_user,
            file=simple_file,
            original_filename="staff-detail.txt",
        )
        other_ticket = Ticket.objects.create(
            title="Other ticket",
            description="Other ticket description.",
            submitter=self.submitter_user,
            ticket_type=self.ticket_type,
            ticket_system=self.ticket_system,
            ticket_priority=self.ticket_priority,
            ticket_status=self.open_status,
        )
        TicketComment.objects.create(
            ticket=other_ticket,
            author=self.submitter_user,
            body="Hidden other ticket comment.",
        )

        self.client.force_login(self.support_user)
        response = self.client.get(reverse("ticket_detail", args=[self.ticket.id]))

        self.assertContains(response, "Visible staff comment.")
        self.assertContains(response, "staff-detail.txt")
        self.assertNotContains(response, "Hidden other ticket comment.")

    def test_staff_ticket_detail_shows_ticket_history(self):
        TicketHistory.objects.create(
            ticket=self.ticket,
            changed_by=self.support_user,
            change_type="STATUS_CHANGED",
            field_name="ticket_status",
            old_value="Open",
            new_value="In Progress",
        )

        self.client.force_login(self.support_user)
        response = self.client.get(reverse("ticket_detail", args=[self.ticket.id]))

        self.assertContains(response, "Ticket History")
        self.assertContains(response, "STATUS_CHANGED")
        self.assertContains(response, "Changed by support-ticket@test.com")
        self.assertContains(response, "Field: ticket_status")
        self.assertContains(response, "Open")
        self.assertContains(response, "In Progress")

    def test_staff_ticket_history_is_ordered_newest_first(self):
        TicketHistory.objects.create(
            ticket=self.ticket,
            changed_by=self.support_user,
            change_type="STATUS_CHANGED",
            field_name="ticket_status",
            old_value="Open",
            new_value="Older history entry",
        )
        TicketHistory.objects.create(
            ticket=self.ticket,
            changed_by=self.support_user,
            change_type="PRIORITY_CHANGED",
            field_name="ticket_priority",
            old_value="Medium",
            new_value="Newer history entry",
        )

        self.client.force_login(self.support_user)
        response = self.client.get(reverse("ticket_detail", args=[self.ticket.id]))
        content = response.content.decode()

        self.assertLess(
            content.index("Newer history entry"),
            content.index("Older history entry"),
        )

    def test_staff_ticket_detail_shows_empty_history_state(self):
        self.client.force_login(self.support_user)
        response = self.client.get(reverse("ticket_detail", args=[self.ticket.id]))

        self.assertContains(response, "Ticket History")
        self.assertContains(response, "No ticket history yet.")

    def test_submitter_ticket_detail_does_not_show_staff_history_section(self):
        TicketHistory.objects.create(
            ticket=self.ticket,
            changed_by=self.support_user,
            change_type="STATUS_CHANGED",
            field_name="ticket_status",
            old_value="Open",
            new_value="In Progress",
        )

        self.client.force_login(self.submitter_user)
        response = self.client.get(reverse("my_ticket_detail", args=[self.ticket.id]))

        self.assertNotContains(response, "Ticket History")
        self.assertNotContains(response, "STATUS_CHANGED")

    def test_staff_ticket_queue_filters_by_status(self):
        closed_ticket = self._create_queue_ticket(
            "Closed queue filter ticket",
            ticket_status=self.closed_status,
        )

        self.client.force_login(self.support_user)
        response = self.client.get(
            reverse("ticket_list"),
            {"status": self.closed_status.id},
        )

        self.assertContains(response, closed_ticket.title)
        self.assertNotContains(response, self.ticket.title)

    def test_staff_ticket_queue_filters_by_priority(self):
        high_priority_ticket = self._create_queue_ticket(
            "High priority queue filter ticket",
            ticket_priority=self.high_priority,
        )

        self.client.force_login(self.support_user)
        response = self.client.get(
            reverse("ticket_list"),
            {"priority": self.high_priority.id},
        )

        self.assertContains(response, high_priority_ticket.title)
        self.assertNotContains(response, self.ticket.title)

    def test_staff_ticket_queue_filters_by_type_and_system(self):
        matching_ticket = self._create_queue_ticket(
            "Service network queue filter ticket",
            ticket_type=self.service_type,
            ticket_system=self.network_system,
        )
        self._create_queue_ticket(
            "Service hardware hidden ticket",
            ticket_type=self.service_type,
            ticket_system=self.hardware_system,
        )

        self.client.force_login(self.support_user)
        response = self.client.get(
            reverse("ticket_list"),
            {
                "type": self.service_type.id,
                "system": self.network_system.id,
            },
        )

        self.assertContains(response, matching_ticket.title)
        self.assertNotContains(response, "Service hardware hidden ticket")
        self.assertNotContains(response, self.ticket.title)

    def test_staff_ticket_queue_filters_by_submitter(self):
        other_submitter_ticket = self._create_queue_ticket(
            "Other submitter queue filter ticket",
            submitter=self.other_submitter_user,
        )

        self.client.force_login(self.support_user)
        response = self.client.get(
            reverse("ticket_list"),
            {"submitter": self.other_submitter_user.id},
        )

        self.assertContains(response, other_submitter_ticket.title)
        self.assertNotContains(response, self.ticket.title)

    def test_staff_ticket_queue_filters_by_assigned_user(self):
        assigned_ticket = self._create_queue_ticket(
            "Assigned queue filter ticket",
            assigned_to=self.second_support_user,
        )

        self.client.force_login(self.support_user)
        response = self.client.get(
            reverse("ticket_list"),
            {"assigned_to": self.second_support_user.id},
        )

        self.assertContains(response, assigned_ticket.title)
        self.assertNotContains(response, self.ticket.title)

    def test_staff_ticket_queue_filters_by_created_date_range(self):
        old_ticket = self._create_queue_ticket("Old queue filter ticket")
        new_ticket = self._create_queue_ticket("New queue filter ticket")
        old_date = timezone.now() - timedelta(days=5)
        new_date = timezone.now()
        Ticket.objects.filter(id=old_ticket.id).update(created_at=old_date)
        Ticket.objects.filter(id=new_ticket.id).update(created_at=new_date)

        self.client.force_login(self.support_user)
        response = self.client.get(
            reverse("ticket_list"),
            {"created_from": timezone.localdate().isoformat()},
        )

        self.assertContains(response, new_ticket.title)
        self.assertNotContains(response, old_ticket.title)

    def test_staff_ticket_queue_is_paginated_and_preserves_filters(self):
        for index in range(26):
            self._create_queue_ticket(
                f"High priority paginated ticket {index:02d}",
                ticket_priority=self.high_priority,
            )

        self.client.force_login(self.support_user)
        response = self.client.get(
            reverse("ticket_list"),
            {"priority": self.high_priority.id},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Page 1 of 2")
        self.assertContains(
            response,
            f"?priority={self.high_priority.id}&page=2",
            html=False,
        )
        self.assertEqual(response.context["page_obj"].paginator.count, 26)
        self.assertEqual(len(response.context["tickets"]), 25)

        second_page_response = self.client.get(
            reverse("ticket_list"),
            {
                "priority": self.high_priority.id,
                "page": 2,
            },
        )

        self.assertContains(second_page_response, "Page 2 of 2")
        self.assertEqual(len(second_page_response.context["tickets"]), 1)

    def test_staff_ticket_queue_ignores_invalid_filters(self):
        self.client.force_login(self.support_user)
        response = self.client.get(
            reverse("ticket_list"),
            {
                "status": "invalid",
                "priority": "999999",
                "created_from": "not-a-date",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.ticket.title)

    def test_submitter_cannot_access_staff_ticket_queue(self):
        self.client.force_login(self.submitter_user)
        response = self.client.get(reverse("ticket_list"))

        self.assertRedirects(response, reverse("profile"))

    def test_staff_ticket_detail_shows_assignment_form(self):
        self.client.force_login(self.support_user)
        response = self.client.get(reverse("ticket_detail", args=[self.ticket.id]))

        self.assertContains(
            response,
            reverse("ticket_assignment_update", args=[self.ticket.id]),
        )
        self.assertContains(response, "support-ticket@test.com")
        self.assertContains(response, "second-support-ticket@test.com")

    def test_staff_ticket_detail_shows_priority_form(self):
        self.client.force_login(self.support_user)
        response = self.client.get(reverse("ticket_detail", args=[self.ticket.id]))

        self.assertContains(
            response,
            reverse("ticket_priority_update", args=[self.ticket.id]),
        )
        self.assertContains(response, "Low")
        self.assertContains(response, "Medium")
        self.assertContains(response, "High")

    def test_support_staff_can_assign_ticket_to_support_staff(self):
        self.client.force_login(self.support_user)
        response = self.client.post(
            reverse("ticket_assignment_update", args=[self.ticket.id]),
            {"assigned_to": self.second_support_user.id},
        )

        self.assertRedirects(response, reverse("ticket_detail", args=[self.ticket.id]))
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.assigned_to, self.second_support_user)
        self.assertTrue(
            TicketHistory.objects.filter(
                ticket=self.ticket,
                changed_by=self.support_user,
                change_type="ASSIGNMENT_CHANGED",
                field_name="assigned_to",
                old_value="Unassigned",
                new_value="second-support-ticket@test.com",
            ).exists()
        )

    def test_admin_can_assign_ticket_to_support_staff(self):
        self.client.force_login(self.admin_user)
        response = self.client.post(
            reverse("ticket_assignment_update", args=[self.ticket.id]),
            {"assigned_to": self.support_user.id},
        )

        self.assertRedirects(response, reverse("ticket_detail", args=[self.ticket.id]))
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.assigned_to, self.support_user)

    def test_support_staff_can_unassign_ticket(self):
        self.ticket.assigned_to = self.support_user
        self.ticket.save()

        self.client.force_login(self.support_user)
        response = self.client.post(
            reverse("ticket_assignment_update", args=[self.ticket.id]),
            {"assigned_to": ""},
        )

        self.assertRedirects(response, reverse("ticket_detail", args=[self.ticket.id]))
        self.ticket.refresh_from_db()
        self.assertIsNone(self.ticket.assigned_to)
        self.assertTrue(
            TicketHistory.objects.filter(
                ticket=self.ticket,
                changed_by=self.support_user,
                change_type="ASSIGNMENT_CHANGED",
                field_name="assigned_to",
                old_value="support-ticket@test.com",
                new_value="Unassigned",
            ).exists()
        )

    def test_submitter_cannot_assign_ticket_from_staff_endpoint(self):
        self.client.force_login(self.submitter_user)
        response = self.client.post(
            reverse("ticket_assignment_update", args=[self.ticket.id]),
            {"assigned_to": self.support_user.id},
        )

        self.assertRedirects(response, reverse("profile"))
        self.ticket.refresh_from_db()
        self.assertIsNone(self.ticket.assigned_to)
        self.assertFalse(TicketHistory.objects.filter(ticket=self.ticket).exists())

    def test_submitter_cannot_be_selected_as_assignee(self):
        self.client.force_login(self.support_user)
        response = self.client.post(
            reverse("ticket_assignment_update", args=[self.ticket.id]),
            {"assigned_to": self.submitter_user.id},
        )

        self.assertEqual(response.status_code, 400)
        self.ticket.refresh_from_db()
        self.assertIsNone(self.ticket.assigned_to)
        self.assertFalse(TicketHistory.objects.filter(ticket=self.ticket).exists())

    def test_same_assignment_does_not_create_duplicate_history(self):
        self.ticket.assigned_to = self.support_user
        self.ticket.save()

        self.client.force_login(self.support_user)
        response = self.client.post(
            reverse("ticket_assignment_update", args=[self.ticket.id]),
            {"assigned_to": self.support_user.id},
        )

        self.assertRedirects(response, reverse("ticket_detail", args=[self.ticket.id]))
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.assigned_to, self.support_user)
        self.assertFalse(
            TicketHistory.objects.filter(
                ticket=self.ticket,
                change_type="ASSIGNMENT_CHANGED",
            ).exists()
        )

    def test_assignment_get_redirects_to_ticket_detail(self):
        self.client.force_login(self.support_user)
        response = self.client.get(
            reverse("ticket_assignment_update", args=[self.ticket.id])
        )

        self.assertRedirects(response, reverse("ticket_detail", args=[self.ticket.id]))

    def test_support_staff_can_update_ticket_priority(self):
        self.client.force_login(self.support_user)
        response = self.client.post(
            reverse("ticket_priority_update", args=[self.ticket.id]),
            {"ticket_priority": self.high_priority.id},
        )

        self.assertRedirects(response, reverse("ticket_detail", args=[self.ticket.id]))
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.ticket_priority, self.high_priority)
        self.assertTrue(
            TicketHistory.objects.filter(
                ticket=self.ticket,
                changed_by=self.support_user,
                change_type="PRIORITY_CHANGED",
                field_name="ticket_priority",
                old_value="Medium",
                new_value="High",
            ).exists()
        )

    def test_admin_can_update_ticket_priority(self):
        self.client.force_login(self.admin_user)
        response = self.client.post(
            reverse("ticket_priority_update", args=[self.ticket.id]),
            {"ticket_priority": self.low_priority.id},
        )

        self.assertRedirects(response, reverse("ticket_detail", args=[self.ticket.id]))
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.ticket_priority, self.low_priority)

    def test_submitter_cannot_update_ticket_priority(self):
        self.client.force_login(self.submitter_user)
        response = self.client.post(
            reverse("ticket_priority_update", args=[self.ticket.id]),
            {"ticket_priority": self.high_priority.id},
        )

        self.assertRedirects(response, reverse("profile"))
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.ticket_priority, self.ticket_priority)
        self.assertFalse(TicketHistory.objects.filter(ticket=self.ticket).exists())

    def test_invalid_priority_update_is_rejected(self):
        self.client.force_login(self.support_user)
        response = self.client.post(
            reverse("ticket_priority_update", args=[self.ticket.id]),
            {"ticket_priority": 999999},
        )

        self.assertEqual(response.status_code, 400)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.ticket_priority, self.ticket_priority)
        self.assertFalse(TicketHistory.objects.filter(ticket=self.ticket).exists())

    def test_same_priority_does_not_create_duplicate_history(self):
        self.client.force_login(self.support_user)
        response = self.client.post(
            reverse("ticket_priority_update", args=[self.ticket.id]),
            {"ticket_priority": self.ticket_priority.id},
        )

        self.assertRedirects(response, reverse("ticket_detail", args=[self.ticket.id]))
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.ticket_priority, self.ticket_priority)
        self.assertFalse(
            TicketHistory.objects.filter(
                ticket=self.ticket,
                change_type="PRIORITY_CHANGED",
            ).exists()
        )

    def test_priority_get_redirects_to_ticket_detail(self):
        self.client.force_login(self.support_user)
        response = self.client.get(
            reverse("ticket_priority_update", args=[self.ticket.id])
        )

        self.assertRedirects(response, reverse("ticket_detail", args=[self.ticket.id]))

    def test_ticket_create_triggers_notification_helper(self):
        self.client.force_login(self.submitter_user)
        with patch("tickets.views.ticket_notifications.notify_ticket_created") as notify_created:
            response = self.client.post(
                reverse("ticket_create"),
                {
                    "title": "Notification create test",
                    "description": "Testing ticket creation notifications.",
                    "ticket_priority": self.ticket_priority.id,
                    "ticket_system": self.ticket_system.id,
                    "ticket_type": self.ticket_type.id,
                },
            )

        created_ticket = Ticket.objects.get(title="Notification create test")
        self.assertRedirects(
            response,
            reverse("my_ticket_detail", args=[created_ticket.id]),
        )
        notify_created.assert_called_once_with(
            created_ticket,
            created_by_id=self.submitter_user.id,
        )

    def test_ticket_assignment_triggers_notification_helper(self):
        self.client.force_login(self.support_user)
        with patch("tickets.views.ticket_notifications.notify_ticket_assigned") as notify_assigned:
            response = self.client.post(
                reverse("ticket_assignment_update", args=[self.ticket.id]),
                {"assigned_to": self.second_support_user.id},
            )

        self.assertRedirects(response, reverse("ticket_detail", args=[self.ticket.id]))
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.assigned_to, self.second_support_user)
        notify_assigned.assert_called_once_with(
            self.ticket,
            created_by_id=self.support_user.id,
        )

    def test_status_change_triggers_notification_helper(self):
        self.client.force_login(self.support_user)
        with patch("tickets.views.ticket_notifications.notify_ticket_status_changed") as notify_status_changed:
            response = self.client.post(
                reverse("ticket_detail", args=[self.ticket.id]),
                {"ticket_status": self.in_progress_status.id},
            )

        self.assertRedirects(response, reverse("ticket_detail", args=[self.ticket.id]))
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.ticket_status, self.in_progress_status)
        notify_status_changed.assert_called_once()
        self.assertEqual(
            notify_status_changed.call_args.kwargs["previous_status_name"],
            "Open",
        )
        self.assertEqual(
            notify_status_changed.call_args.kwargs["created_by_id"],
            self.support_user.id,
        )

    def test_public_staff_comment_triggers_notification_helper(self):
        self.client.force_login(self.support_user)
        with patch("tickets.views.ticket_notifications.notify_public_comment") as notify_public_comment:
            response = self.client.post(
                reverse("staff_comment_create", args=[self.ticket.id]),
                {
                    "body": "Public reply from staff.",
                },
            )

        self.assertRedirects(response, reverse("ticket_detail", args=[self.ticket.id]))
        comment = TicketComment.objects.get(
            ticket=self.ticket,
            author=self.support_user,
            body="Public reply from staff.",
        )
        notify_public_comment.assert_called_once()
        self.assertEqual(notify_public_comment.call_args.kwargs["comment"].id, comment.id)
        self.assertEqual(
            notify_public_comment.call_args.kwargs["created_by_id"],
            self.support_user.id,
        )

    def test_internal_staff_comment_does_not_trigger_public_notification(self):
        self.client.force_login(self.support_user)
        with patch("tickets.views.ticket_notifications.notify_public_comment") as notify_public_comment:
            response = self.client.post(
                reverse("staff_comment_create", args=[self.ticket.id]),
                {
                    "body": "Internal note only.",
                    "is_internal": "on",
                },
            )

        self.assertRedirects(response, reverse("ticket_detail", args=[self.ticket.id]))
        self.assertTrue(
            TicketComment.objects.filter(
                ticket=self.ticket,
                author=self.support_user,
                body="Internal note only.",
                is_internal=True,
            ).exists()
        )
        notify_public_comment.assert_not_called()

    def test_resolve_triggers_notification_helper(self):
        self.client.force_login(self.support_user)
        with patch("tickets.views.ticket_notifications.notify_ticket_resolved") as notify_resolved:
            response = self.client.post(
                reverse("ticket_resolve", args=[self.ticket.id]),
                {"resolution_summary": "Resolved after updating the account."},
            )

        self.assertRedirects(response, reverse("ticket_detail", args=[self.ticket.id]))
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.ticket_status, self.closed_status)
        notify_resolved.assert_called_once_with(
            self.ticket,
            created_by_id=self.support_user.id,
        )

    def test_cancel_triggers_notification_helper(self):
        self.client.force_login(self.admin_user)
        with patch("tickets.views.ticket_notifications.notify_ticket_cancelled") as notify_cancelled:
            response = self.client.post(
                reverse("ticket_cancel", args=[self.ticket.id]),
                {"cancellation_reason": "Request duplicated elsewhere."},
            )

        self.assertRedirects(response, reverse("ticket_detail", args=[self.ticket.id]))
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.ticket_status, self.cancelled_status)
        notify_cancelled.assert_called_once_with(
            self.ticket,
            created_by_id=self.admin_user.id,
        )


@override_settings(IT_SUPPORT_EMAIL="itsupport@test.com")
class TicketNotificationRecipientTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.submitter = User.objects.create_user(
            email="recipient-submitter@test.com",
            password="password123",
        )
        self.assignee = User.objects.create_user(
            email="recipient-assignee@test.com",
            password="password123",
        )
        self.staff_author = User.objects.create_user(
            email="recipient-staff@test.com",
            password="password123",
        )
        self.ticket_type = TicketType.objects.get(code="INCIDENT")
        self.ticket_system = TicketSystem.objects.get(code="SOFTWARE")
        self.ticket_priority = TicketPriority.objects.get(code="MEDIUM")
        self.open_status = TicketStatus.objects.get(code="OPEN")
        self.in_progress_status = TicketStatus.objects.get(code="IN_PROGRESS")
        self.closed_status = TicketStatus.objects.get(code="CLOSED")

    def _create_ticket(self, *, assigned_to=None, status=None):
        return Ticket.objects.create(
            title="Recipient rule ticket",
            description="Ticket used to verify notification recipient rules.",
            submitter=self.submitter,
            assigned_to=assigned_to,
            ticket_type=self.ticket_type,
            ticket_system=self.ticket_system,
            ticket_priority=self.ticket_priority,
            ticket_status=status or self.open_status,
        )

    def _recipient_emails(self, mocked_send):
        return [call_args.kwargs["recipient_email"] for call_args in mocked_send.call_args_list]

    def test_created_ticket_notifies_assignee_and_support_inbox(self):
        ticket = self._create_ticket(assigned_to=self.assignee)

        with patch("tickets.notifications.NotificationService.send_notification") as mocked_send:
            ticket_notifications.notify_ticket_created(
                ticket,
                created_by_id=self.submitter.id,
            )

        self.assertEqual(
            self._recipient_emails(mocked_send),
            [self.assignee.email, "itsupport@test.com"],
        )
        self.assertEqual(
            mocked_send.call_args_list[0].kwargs["event_type"],
            NotificationEvent.EventType.TICKET_CREATED,
        )
        self.assertEqual(
            mocked_send.call_args_list[0].kwargs["context"]["subject"],
            f"New ticket created: {ticket.ticket_number}",
        )

    def test_created_ticket_without_assignee_notifies_support_only(self):
        ticket = self._create_ticket()

        with patch("tickets.notifications.NotificationService.send_notification") as mocked_send:
            ticket_notifications.notify_ticket_created(
                ticket,
                created_by_id=self.submitter.id,
            )

        self.assertEqual(
            self._recipient_emails(mocked_send),
            ["itsupport@test.com"],
        )

    def test_created_ticket_without_support_inbox_still_notifies_assignee(self):
        ticket = self._create_ticket(assigned_to=self.assignee)

        with override_settings(IT_SUPPORT_EMAIL=""):
            with patch("tickets.notifications.NotificationService.send_notification") as mocked_send:
                ticket_notifications.notify_ticket_created(
                    ticket,
                    created_by_id=self.submitter.id,
                )

        self.assertEqual(self._recipient_emails(mocked_send), [self.assignee.email])

    def test_assignment_notifies_assignee_only(self):
        ticket = self._create_ticket(assigned_to=self.assignee)

        with patch("tickets.notifications.NotificationService.send_notification") as mocked_send:
            ticket_notifications.notify_ticket_assigned(
                ticket,
                created_by_id=self.staff_author.id,
            )

        self.assertEqual(self._recipient_emails(mocked_send), [self.assignee.email])
        self.assertEqual(
            mocked_send.call_args_list[0].kwargs["event_type"],
            NotificationEvent.EventType.TICKET_ASSIGNED,
        )

    def test_public_comment_notifies_submitter_and_assignee(self):
        ticket = self._create_ticket(assigned_to=self.assignee)
        comment = TicketComment.objects.create(
            ticket=ticket,
            author=self.staff_author,
            body="Public update for the submitter.",
            is_internal=False,
        )

        with patch("tickets.notifications.NotificationService.send_notification") as mocked_send:
            ticket_notifications.notify_public_comment(
                ticket,
                comment=comment,
                created_by_id=self.staff_author.id,
            )

        self.assertEqual(
            self._recipient_emails(mocked_send),
            [self.submitter.email, self.assignee.email],
        )
        self.assertEqual(
            mocked_send.call_args_list[0].kwargs["event_type"],
            NotificationEvent.EventType.TICKET_COMMENTED,
        )

    def test_public_comment_skips_the_comment_author(self):
        ticket = self._create_ticket(assigned_to=self.assignee)
        comment = TicketComment.objects.create(
            ticket=ticket,
            author=self.submitter,
            body="Submitter follow-up.",
            is_internal=False,
        )

        with patch("tickets.notifications.NotificationService.send_notification") as mocked_send:
            ticket_notifications.notify_public_comment(
                ticket,
                comment=comment,
                created_by_id=self.submitter.id,
            )

        self.assertEqual(self._recipient_emails(mocked_send), [self.assignee.email])

    def test_internal_comment_does_not_send_notification(self):
        ticket = self._create_ticket(assigned_to=self.assignee)
        comment = TicketComment.objects.create(
            ticket=ticket,
            author=self.staff_author,
            body="Internal note only.",
            is_internal=True,
        )

        with patch("tickets.notifications.NotificationService.send_notification") as mocked_send:
            if not comment.is_internal:
                ticket_notifications.notify_public_comment(
                    ticket,
                    comment=comment,
                    created_by_id=self.staff_author.id,
                )

        mocked_send.assert_not_called()

    def test_resolved_notifies_support_inbox_only(self):
        ticket = self._create_ticket(status=self.in_progress_status)
        ticket.ticket_status = self.closed_status

        with patch("tickets.notifications.NotificationService.send_notification") as mocked_send:
            ticket_notifications.notify_ticket_resolved(
                ticket,
                created_by_id=self.staff_author.id,
            )

        self.assertEqual(
            self._recipient_emails(mocked_send),
            ["itsupport@test.com"],
        )

    def test_cancelled_notifies_support_inbox_only(self):
        ticket = self._create_ticket(status=self.in_progress_status)
        ticket.ticket_status = self.closed_status

        with patch("tickets.notifications.NotificationService.send_notification") as mocked_send:
            ticket_notifications.notify_ticket_cancelled(
                ticket,
                created_by_id=self.staff_author.id,
            )

        self.assertEqual(
            self._recipient_emails(mocked_send),
            ["itsupport@test.com"],
        )


class TicketAttachmentDownloadTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin_group = Group.objects.create(name="Admin")
        self.submitter_group = Group.objects.create(name="Submitter")
        self.support_staff_group = Group.objects.create(name="Support Staff")
        self.submitter_user = User.objects.create_user(
            email="attachment-owner@test.com",
            password="password123",
        )
        self.other_submitter = User.objects.create_user(
            email="attachment-other@test.com",
            password="password123",
        )
        self.support_user = User.objects.create_user(
            email="attachment-support@test.com",
            password="password123",
        )
        self.admin_user = User.objects.create_user(
            email="attachment-admin@test.com",
            password="password123",
        )
        self.submitter_user.groups.add(self.submitter_group)
        self.other_submitter.groups.add(self.submitter_group)
        self.support_user.groups.add(self.support_staff_group)
        self.admin_user.groups.add(self.admin_group)
        self.ticket_type = TicketType.objects.get(code="INCIDENT")
        self.ticket_system = TicketSystem.objects.get(code="SOFTWARE")
        self.ticket_priority = TicketPriority.objects.get(code="MEDIUM")
        self.open_status = TicketStatus.objects.get(code="OPEN")
        self.ticket = Ticket.objects.create(
            title="Attachment download test",
            description="Ticket with a protected attachment.",
            submitter=self.submitter_user,
            ticket_type=self.ticket_type,
            ticket_system=self.ticket_system,
            ticket_priority=self.ticket_priority,
            ticket_status=self.open_status,
        )
        self.attachment = TicketAttachment.objects.create(
            ticket=self.ticket,
            uploaded_by=self.submitter_user,
            file=SimpleUploadedFile(
                "protected.txt",
                b"protected file content",
                content_type="text/plain",
            ),
            original_filename="protected.txt",
        )

    def test_submitter_can_download_own_attachment(self):
        self.client.force_login(self.submitter_user)
        response = self.client.get(
            reverse("attachment_download", args=[self.attachment.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Disposition"], 'attachment; filename="protected.txt"'
        )

    def test_submitter_cannot_download_another_submitters_attachment(self):
        self.client.force_login(self.other_submitter)
        response = self.client.get(
            reverse("attachment_download", args=[self.attachment.id])
        )

        self.assertRedirects(response, reverse("profile"))

    def test_support_staff_can_download_attachment(self):
        self.client.force_login(self.support_user)
        response = self.client.get(
            reverse("attachment_download", args=[self.attachment.id])
        )

        self.assertEqual(response.status_code, 200)

    def test_admin_can_download_attachment(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(
            reverse("attachment_download", args=[self.attachment.id])
        )

        self.assertEqual(response.status_code, 200)

    def test_anonymous_user_redirects_to_login(self):
        download_url = reverse("attachment_download", args=[self.attachment.id])
        response = self.client.get(download_url)

        self.assertRedirects(response, f"{reverse('login')}?next={download_url}")

    def test_ticket_detail_uses_protected_attachment_link(self):
        self.client.force_login(self.support_user)
        response = self.client.get(reverse("ticket_detail", args=[self.ticket.id]))

        self.assertContains(
            response,
            reverse("attachment_download", args=[self.attachment.id]),
        )
        self.assertNotContains(response, self.attachment.file.url)

    def test_submitter_detail_uses_protected_attachment_link(self):
        self.client.force_login(self.submitter_user)
        response = self.client.get(reverse("my_ticket_detail", args=[self.ticket.id]))

        self.assertContains(
            response,
            reverse("attachment_download", args=[self.attachment.id]),
        )
        self.assertNotContains(response, self.attachment.file.url)

    def test_attachment_size_validation_shows_mb_limit(self):
        large_file = SimpleUploadedFile(
            "too-large.txt",
            b"x" * ((5 * 1024 * 1024) + 1),
            content_type="text/plain",
        )
        form = TicketAttachmentForm(data={}, files={"file": large_file})

        self.assertFalse(form.is_valid())
        self.assertIn("File size must be less than 5 MB", form.errors["file"])


@override_settings(IT_SUPPORT_EMAIL="itsupport@test.com")
class TicketCommentVisibilityTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.notification_send_patcher = patch(
            "tickets.notifications.NotificationService.send_notification",
            autospec=True,
            return_value=None,
        )
        self.notification_send_patcher.start()
        self.addCleanup(self.notification_send_patcher.stop)
        self.admin_group = Group.objects.create(name="Admin")
        self.submitter_group = Group.objects.create(name="Submitter")
        self.support_staff_group = Group.objects.create(name="Support Staff")
        self.admin_user = User.objects.create_user(
            email="comment-admin@test.com",
            password="password123",
        )
        self.submitter_user = User.objects.create_user(
            email="comment-submitter@test.com",
            password="password123",
        )
        self.support_user = User.objects.create_user(
            email="comment-support@test.com",
            password="password123",
        )
        self.admin_user.groups.add(self.admin_group)
        self.submitter_user.groups.add(self.submitter_group)
        self.support_user.groups.add(self.support_staff_group)
        self.ticket_type = TicketType.objects.get(code="INCIDENT")
        self.ticket_system = TicketSystem.objects.get(code="SOFTWARE")
        self.ticket_priority = TicketPriority.objects.get(code="MEDIUM")
        self.open_status = TicketStatus.objects.get(code="OPEN")
        self.ticket = Ticket.objects.create(
            title="Comment visibility test",
            description="Ticket used for comment visibility tests.",
            submitter=self.submitter_user,
            ticket_type=self.ticket_type,
            ticket_system=self.ticket_system,
            ticket_priority=self.ticket_priority,
            ticket_status=self.open_status,
        )

    def test_submitter_sees_public_staff_comment_and_not_internal_note(self):
        TicketComment.objects.create(
            ticket=self.ticket,
            author=self.support_user,
            body="Public support reply.",
            is_internal=False,
        )
        TicketComment.objects.create(
            ticket=self.ticket,
            author=self.support_user,
            body="Internal support note.",
            is_internal=True,
        )

        self.client.force_login(self.submitter_user)
        response = self.client.get(
            reverse("my_ticket_detail", args=[self.ticket.id])
        )

        self.assertContains(response, "Public support reply.")
        self.assertNotContains(response, "Internal support note.")

    def test_staff_sees_public_and_internal_comments(self):
        TicketComment.objects.create(
            ticket=self.ticket,
            author=self.support_user,
            body="Public support reply.",
            is_internal=False,
        )
        TicketComment.objects.create(
            ticket=self.ticket,
            author=self.support_user,
            body="Internal support note.",
            is_internal=True,
        )

        self.client.force_login(self.support_user)
        response = self.client.get(reverse("ticket_detail", args=[self.ticket.id]))

        self.assertContains(response, "Public support reply.")
        self.assertContains(response, "Internal support note.")
        self.assertContains(response, "Internal")

    def test_staff_can_create_internal_comment(self):
        self.client.force_login(self.support_user)
        response = self.client.post(
            reverse("staff_comment_create", args=[self.ticket.id]),
            {
                "body": "Internal triage note.",
                "is_internal": "on",
            },
        )

        self.assertRedirects(
            response,
            reverse("ticket_detail", args=[self.ticket.id]),
        )
        self.assertTrue(
            TicketComment.objects.filter(
                ticket=self.ticket,
                author=self.support_user,
                body="Internal triage note.",
                is_internal=True,
            ).exists()
        )

    def test_submitter_cannot_use_staff_comment_endpoint(self):
        self.client.force_login(self.submitter_user)
        response = self.client.post(
            reverse("staff_comment_create", args=[self.ticket.id]),
            {
                "body": "I should not be able to post here.",
                "is_internal": "on",
            },
        )

        self.assertRedirects(response, reverse("profile"))
        self.assertFalse(
            TicketComment.objects.filter(
                ticket=self.ticket,
                body="I should not be able to post here.",
            ).exists()
        )

    def test_submitter_created_comment_is_public(self):
        self.client.force_login(self.submitter_user)
        response = self.client.post(
            reverse("comment_create", args=[self.ticket.id]),
            {"body": "Submitter follow-up."},
        )

        self.assertRedirects(
            response,
            reverse("my_ticket_detail", args=[self.ticket.id]),
        )
        comment = TicketComment.objects.get(
            ticket=self.ticket,
            author=self.submitter_user,
            body="Submitter follow-up.",
        )
        self.assertFalse(comment.is_internal)

    def test_staff_can_create_resolution_note(self):
        self.client.force_login(self.support_user)
        response = self.client.post(
            reverse("ticket_resolution_note_create", args=[self.ticket.id]),
            {"body": "Resolved after clearing the user's cached credentials."},
        )

        self.assertRedirects(
            response,
            reverse("ticket_detail", args=[self.ticket.id]),
        )
        note = TicketComment.objects.get(
            ticket=self.ticket,
            author=self.support_user,
            body="Resolved after clearing the user's cached credentials.",
        )
        self.assertFalse(note.is_internal)
        self.assertTrue(
            TicketHistory.objects.filter(
                ticket=self.ticket,
                changed_by=self.support_user,
                change_type="RESOLUTION_NOTE_ADDED",
                field_name="comments",
                new_value="Resolution note added",
            ).exists()
        )

    def test_admin_can_create_resolution_note(self):
        self.client.force_login(self.admin_user)
        response = self.client.post(
            reverse("ticket_resolution_note_create", args=[self.ticket.id]),
            {"body": "Admin added final resolution details."},
        )

        self.assertRedirects(
            response,
            reverse("ticket_detail", args=[self.ticket.id]),
        )
        self.assertTrue(
            TicketComment.objects.filter(
                ticket=self.ticket,
                author=self.admin_user,
                body="Admin added final resolution details.",
                is_internal=False,
            ).exists()
        )

    def test_submitter_cannot_create_resolution_note(self):
        self.client.force_login(self.submitter_user)
        response = self.client.post(
            reverse("ticket_resolution_note_create", args=[self.ticket.id]),
            {"body": "Submitter should not add resolution notes."},
        )

        self.assertRedirects(response, reverse("profile"))
        self.assertFalse(
            TicketComment.objects.filter(
                ticket=self.ticket,
                body="Submitter should not add resolution notes.",
            ).exists()
        )

    def test_resolution_note_is_visible_to_submitter(self):
        TicketComment.objects.create(
            ticket=self.ticket,
            author=self.support_user,
            body="Public resolution note for submitter.",
            is_internal=False,
        )

        self.client.force_login(self.submitter_user)
        response = self.client.get(reverse("my_ticket_detail", args=[self.ticket.id]))

        self.assertContains(response, "Public resolution note for submitter.")

    def test_resolution_summary_is_visible_to_submitter(self):
        self.ticket.resolution_summary = "Resolved by resetting the account lockout."
        self.ticket.save()

        self.client.force_login(self.submitter_user)
        response = self.client.get(reverse("my_ticket_detail", args=[self.ticket.id]))

        self.assertContains(response, "Resolution Summary")
        self.assertContains(response, "Resolved by resetting the account lockout.")

    def test_cancellation_reason_is_visible_to_submitter(self):
        self.ticket.cancellation_reason = "Request cancelled because access is no longer needed."
        self.ticket.save()

        self.client.force_login(self.submitter_user)
        response = self.client.get(reverse("my_ticket_detail", args=[self.ticket.id]))

        self.assertContains(response, "Cancellation Reason")
        self.assertContains(
            response,
            "Request cancelled because access is no longer needed.",
        )

    def test_blank_resolution_note_is_rejected(self):
        self.client.force_login(self.support_user)
        response = self.client.post(
            reverse("ticket_resolution_note_create", args=[self.ticket.id]),
            {"body": ""},
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(
            TicketComment.objects.filter(
                ticket=self.ticket,
                author=self.support_user,
            ).exists()
        )
        self.assertFalse(
            TicketHistory.objects.filter(
                ticket=self.ticket,
                change_type="RESOLUTION_NOTE_ADDED",
            ).exists()
        )

    def test_resolution_note_get_redirects_to_ticket_detail(self):
        self.client.force_login(self.support_user)
        response = self.client.get(
            reverse("ticket_resolution_note_create", args=[self.ticket.id])
        )

        self.assertRedirects(response, reverse("ticket_detail", args=[self.ticket.id]))


class TicketSubmitterViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.submitter_group = Group.objects.create(name="Submitter")
        self.submitter_user = User.objects.create_user(
            email="submitter-list@test.com",
            password="password123",
        )
        self.other_submitter = User.objects.create_user(
            email="other-submitter-list@test.com",
            password="password123",
        )
        self.submitter_user.groups.add(self.submitter_group)
        self.other_submitter.groups.add(self.submitter_group)
        self.ticket_type = TicketType.objects.get(code="INCIDENT")
        self.ticket_system = TicketSystem.objects.get(code="SOFTWARE")
        self.ticket_priority = TicketPriority.objects.get(code="MEDIUM")
        self.open_status = TicketStatus.objects.get(code="OPEN")

    def test_my_tickets_only_shows_logged_in_submitters_tickets(self):
        # Submitters must not see tickets submitted by other users in their list.
        own_ticket = Ticket.objects.create(
            title="Own visible ticket",
            description="This ticket belongs to the logged-in submitter.",
            submitter=self.submitter_user,
            ticket_type=self.ticket_type,
            ticket_system=self.ticket_system,
            ticket_priority=self.ticket_priority,
            ticket_status=self.open_status,
        )
        other_ticket = Ticket.objects.create(
            title="Other hidden ticket",
            description="This ticket belongs to another submitter.",
            submitter=self.other_submitter,
            ticket_type=self.ticket_type,
            ticket_system=self.ticket_system,
            ticket_priority=self.ticket_priority,
            ticket_status=self.open_status,
        )

        self.client.force_login(self.submitter_user)
        response = self.client.get(reverse("my_tickets"))

        self.assertContains(response, own_ticket.ticket_number)
        self.assertContains(response, own_ticket.title)
        self.assertNotContains(response, other_ticket.ticket_number)
        self.assertNotContains(response, other_ticket.title)
        
