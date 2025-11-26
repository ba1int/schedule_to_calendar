import unittest
from unittest.mock import Mock, patch
from datetime import datetime
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from calendar_service import get_events_in_range, delete_event

class TestCalendarService(unittest.TestCase):
    def setUp(self):
        """Set up mock service for testing"""
        self.service = Mock()
        self.calendar_id = 'test_calendar_id'
        # Mock environment variable
        self.env_patcher = patch.dict('os.environ', {'EVENT_SUMMARY': 'Work at McDonald\'s'})
        self.env_patcher.start()
        
    def tearDown(self):
        self.env_patcher.stop()
        
    def test_get_events_in_range(self):
        """Test querying events in a date range"""
        # Setup
        start_date = datetime(2025, 11, 27)
        end_date = datetime(2025, 11, 30)
        
        # Mock API response
        self.service.events().list().execute.return_value = {
            'items': [
                {
                    'id': 'event1',
                    'summary': 'Work at McDonald\'s',
                    'start': {'dateTime': '2025-11-27T11:40:00+01:00'}
                },
                {
                    'id': 'event2',
                    'summary': 'Work at McDonald\'s',
                    'start': {'dateTime': '2025-11-28T15:40:00+01:00'}
                },
                {
                    'id': 'event3',
                    'summary': 'Other Event',
                    'start': {'dateTime': '2025-11-28T10:00:00+01:00'}
                }
            ]
        }
        
        # Execute
        events = get_events_in_range(self.service, self.calendar_id, start_date, end_date)
        
        # Assert
        self.assertEqual(len(events), 2)  # Only the "Work at McDonald's" events
        self.assertEqual(events[0]['id'], 'event1')
        self.assertEqual(events[1]['id'], 'event2')
        
    def test_get_events_in_range_empty(self):
        """Test querying events when none exist"""
        # Setup
        start_date = datetime(2025, 11, 27)
        end_date = datetime(2025, 11, 30)
        
        # Mock empty response
        self.service.events().list().execute.return_value = {'items': []}
        
        # Execute
        events = get_events_in_range(self.service, self.calendar_id, start_date, end_date)
        
        # Assert
        self.assertEqual(len(events), 0)
        
    def test_delete_event(self):
        """Test deleting an event"""
        # Setup
        event_id = 'event123'
        
        # Mock delete
        self.service.events().delete().execute.return_value = {}
        
        # Execute
        with patch('builtins.print'):  # Suppress print output
            delete_event(self.service, self.calendar_id, event_id)
        
        # Assert - check that execute was called
        self.service.events().delete().execute.assert_called_once()
        
    def test_get_events_filters_by_summary(self):
        """Test that get_events_in_range filters by summary correctly"""
        # Setup
        start_date = datetime(2025, 11, 27)
        end_date = datetime(2025, 11, 30)
        
        # Mock API response with different summaries
        self.service.events().list().execute.return_value = {
            'items': [
                {'id': 'event1', 'summary': 'Work at McDonald\'s'},
                {'id': 'event2', 'summary': 'Doctor Appointment'},
                {'id': 'event3', 'summary': 'Work at McDonald\'s'},
                {'id': 'event4', 'summary': 'Meeting'},
            ]
        }
        
        # Execute
        events = get_events_in_range(
            self.service, 
            self.calendar_id, 
            start_date, 
            end_date,
            summary='Work at McDonald\'s'
        )
        
        # Assert - should only get the two work events
        self.assertEqual(len(events), 2)
        for event in events:
            self.assertEqual(event['summary'], 'Work at McDonald\'s')

if __name__ == '__main__':
    unittest.main()
