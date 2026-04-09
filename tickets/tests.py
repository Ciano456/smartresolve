# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from django.test import TestCase
from .models import Ticket, TicketType, TicketSystem, TicketPriority, TicketStatus, TicketComment, TicketAttachment, TicketHistory
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models.deletion import ProtectedError
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
        
        
        
