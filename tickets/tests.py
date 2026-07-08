# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from django.test import TestCase
from .models import Ticket, TicketType, TicketSystem, TicketPriority, TicketStatus, TicketComment, TicketAttachment, TicketHistory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models.deletion import ProtectedError
from django.urls import reverse
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
        
        
class TicketStaffViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
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
        self.admin_user.groups.add(self.admin_group)
        self.support_user.groups.add(self.support_staff_group)
        self.second_support_user.groups.add(self.support_staff_group)
        self.submitter_user.groups.add(self.submitter_group)
        self.ticket_type = TicketType.objects.get(code="INCIDENT")
        self.ticket_system = TicketSystem.objects.get(code="SOFTWARE")
        self.low_priority = TicketPriority.objects.get(code="LOW")
        self.ticket_priority = TicketPriority.objects.get(code="MEDIUM")
        self.high_priority = TicketPriority.objects.get(code="HIGH")
        self.open_status = TicketStatus.objects.get(code="OPEN")
        self.in_progress_status = TicketStatus.objects.get(code="IN_PROGRESS")
        self.closed_status = TicketStatus.objects.get(code="CLOSED")
        self.ticket = Ticket.objects.create(
            title="Staff status test",
            description="Ticket used for staff status update tests.",
            submitter=self.submitter_user,
            ticket_type=self.ticket_type,
            ticket_system=self.ticket_system,
            ticket_priority=self.ticket_priority,
            ticket_status=self.open_status,
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

    def test_admin_closing_ticket_sets_closed_at(self):
        # Closed statuses should trigger the model-level closed_at timestamp.
        self.client.force_login(self.admin_user)
        response = self.client.post(
            reverse("ticket_detail", args=[self.ticket.id]),
            {"ticket_status": self.closed_status.id},
        )

        self.assertRedirects(response, reverse("ticket_detail", args=[self.ticket.id]))
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.ticket_status, self.closed_status)
        self.assertIsNotNone(self.ticket.closed_at)

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


class TicketCommentVisibilityTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.submitter_group = Group.objects.create(name="Submitter")
        self.support_staff_group = Group.objects.create(name="Support Staff")
        self.submitter_user = User.objects.create_user(
            email="comment-submitter@test.com",
            password="password123",
        )
        self.support_user = User.objects.create_user(
            email="comment-support@test.com",
            password="password123",
        )
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
        
