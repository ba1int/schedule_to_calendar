import unittest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from processor import process_messages

class TestProcessor(unittest.TestCase):
    def setUp(self):
        """Set up mock services for testing"""
        self.gmail_service = Mock()
        self.calendar_service = Mock()
        self.calendar_id = 'test_calendar_id'
        
    @patch('processor.get_email_content')
    @patch('processor.parse_schedule_email')
    @patch('processor.get_existing_event')
    @patch('processor.create_event')
    def test_process_new_shift(self, mock_create, mock_get_existing, mock_parse, mock_get_email):
        """Test adding a new shift to the calendar"""
        # Setup
        messages = [{'id': 'msg1'}]
        mock_get_email.return_value = '<html>email content</html>'
        mock_parse.return_value = [{
            'start': datetime(2025, 11, 27, 11, 40),
            'end': datetime(2025, 11, 27, 22, 0),
            'summary': 'Work at McDonald\'s',
            'description': 'Wednesday: 12:00-22:00'
        }]
        mock_get_existing.return_value = None  # No existing event
        
        # Execute
        added, updated, deleted = process_messages(
            self.gmail_service, 
            self.calendar_service, 
            self.calendar_id, 
            messages
        )
        
        # Assert
        self.assertEqual(added, 1)
        self.assertEqual(updated, 0)
        self.assertEqual(deleted, 0)
        mock_create.assert_called_once()
        
    @patch('processor.get_email_content')
    @patch('processor.parse_schedule_email')
    @patch('processor.get_existing_event')
    @patch('processor.update_event')
    def test_process_updated_shift(self, mock_update, mock_get_existing, mock_parse, mock_get_email):
        """Test updating an existing shift with new time"""
        # Setup
        messages = [{'id': 'msg1'}]
        mock_get_email.return_value = '<html>email content</html>'
        mock_parse.return_value = [{
            'start': datetime(2025, 11, 27, 11, 40),
            'end': datetime(2025, 11, 27, 22, 0),
            'summary': 'Work at McDonald\'s',
            'description': 'Wednesday: 12:00-22:00'
        }]
        mock_get_existing.return_value = {'id': 'event123'}  # Existing event found
        
        # Execute
        added, updated, deleted = process_messages(
            self.gmail_service, 
            self.calendar_service, 
            self.calendar_id, 
            messages
        )
        
        # Assert
        self.assertEqual(added, 0)
        self.assertEqual(updated, 1)
        self.assertEqual(deleted, 0)
        mock_update.assert_called_once()
        
    @patch('processor.get_email_content')
    @patch('processor.parse_schedule_email')
    @patch('processor.get_existing_event')
    @patch('processor.create_event')
    @patch('processor.get_events_in_range')
    @patch('processor.delete_event')
    def test_process_deleted_shift(self, mock_delete, mock_get_range, mock_create, 
                                   mock_get_existing, mock_parse, mock_get_email):
        """Test deleting a shift that was removed from the schedule"""
        # Setup
        messages = [{'id': 'msg1'}]
        mock_get_email.return_value = '<html>email content</html>'
        
        # Email only has shift on Nov 27
        mock_parse.return_value = [{
            'start': datetime(2025, 11, 27, 11, 40),
            'end': datetime(2025, 11, 27, 22, 0),
            'summary': 'Work at McDonald\'s',
            'description': 'Wednesday: 12:00-22:00'
        }]
        mock_get_existing.return_value = None  # No existing event on Nov 27
        
        # Calendar has events on both Nov 27 and Nov 28
        mock_get_range.return_value = [
            {
                'id': 'event_nov27',
                'start': {'dateTime': '2025-11-27T11:40:00+01:00'},
                'summary': 'Work at McDonald\'s'
            },
            {
                'id': 'event_nov28',
                'start': {'dateTime': '2025-11-28T11:40:00+01:00'},
                'summary': 'Work at McDonald\'s'
            }
        ]
        
        # Execute
        added, updated, deleted = process_messages(
            self.gmail_service, 
            self.calendar_service, 
            self.calendar_id, 
            messages
        )
        
        # Assert
        self.assertEqual(added, 1)  # Nov 27 added
        self.assertEqual(updated, 0)
        self.assertEqual(deleted, 1)  # Nov 28 deleted
        mock_delete.assert_called_once()
        
    @patch('processor.get_email_content')
    @patch('processor.parse_schedule_email')
    def test_process_empty_email(self, mock_parse, mock_get_email):
        """Test processing an email with no schedule data"""
        # Setup
        messages = [{'id': 'msg1'}]
        mock_get_email.return_value = '<html>no schedule here</html>'
        mock_parse.return_value = []  # No events parsed
        
        # Execute
        added, updated, deleted = process_messages(
            self.gmail_service, 
            self.calendar_service, 
            self.calendar_id, 
            messages
        )
        
        # Assert
        self.assertEqual(added, 0)
        self.assertEqual(updated, 0)
        self.assertEqual(deleted, 0)
        
    @patch('processor.get_email_content')
    @patch('processor.parse_schedule_email')
    @patch('processor.get_existing_event')
    @patch('processor.create_event')
    @patch('processor.get_events_in_range')
    def test_process_multiple_shifts(self, mock_get_range, mock_create, 
                                     mock_get_existing, mock_parse, mock_get_email):
        """Test processing multiple shifts in one email"""
        # Setup
        messages = [{'id': 'msg1'}]
        mock_get_email.return_value = '<html>email content</html>'
        mock_parse.return_value = [
            {
                'start': datetime(2025, 11, 27, 11, 40),
                'end': datetime(2025, 11, 27, 22, 0),
                'summary': 'Work at McDonald\'s',
                'description': 'Wednesday: 12:00-22:00'
            },
            {
                'start': datetime(2025, 11, 28, 15, 40),
                'end': datetime(2025, 11, 28, 23, 0),
                'summary': 'Work at McDonald\'s',
                'description': 'Thursday: 16:00-23:00'
            }
        ]
        mock_get_existing.return_value = None
        mock_get_range.return_value = []
        
        # Execute
        added, updated, deleted = process_messages(
            self.gmail_service, 
            self.calendar_service, 
            self.calendar_id, 
            messages
        )
        
        # Assert
        self.assertEqual(added, 2)
        self.assertEqual(updated, 0)
        self.assertEqual(deleted, 0)
        self.assertEqual(mock_create.call_count, 2)

if __name__ == '__main__':
    unittest.main()
