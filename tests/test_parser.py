import unittest
from unittest.mock import patch
from datetime import datetime
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from email_parser import parse_schedule_email

class TestParser(unittest.TestCase):
    def setUp(self):
        # Mock environment variable to ensure consistent test results
        self.env_patcher = patch.dict('os.environ', {'EVENT_SUMMARY': 'Work at McDonald\'s'})
        self.env_patcher.start()
        
    def tearDown(self):
        self.env_patcher.stop()

    def test_schedule_change_html(self):
        email_text = """
<p>Kedves Bencsok Bálint!</p>
<p>Beoszt&aacute;sod megv&aacute;ltozott:</p>
<table style="float: none;" border="1" cellspacing="0" cellpadding="3">
<tbody>
<tr>
<td><strong>Nap</strong></td>
<td><strong>D&aacute;tum</strong></td>
<td><strong>Beoszt&aacute;s</strong></td>
</tr>
<tr>
<td>Hétfő</td>
<td>2025.10.27</td>
<td>PN</td>
</tr>
<tr>
<td><strong><em>Szombat</em></strong></td>
<td><strong><em>2025.11.01</em></strong></td>
<td><strong><em>10:00-22:00</em></strong></td>
</tr>
</tbody>
</table>
"""
        events = parse_schedule_email(email_text)
        self.assertEqual(len(events), 1)
        
        # Check event
        # Start time should be 10:00 - 20 mins = 09:40
        self.assertEqual(events[0]['start'], datetime(2025, 11, 1, 9, 40))
        self.assertEqual(events[0]['end'], datetime(2025, 11, 1, 22, 0))
        
    def test_new_schedule_html(self):
        email_text = """
<p>Aktu&aacute;lis beoszt&aacute;sod a k&ouml;vetkező:</p>
<table style="float: none;" border="1" cellspacing="0" cellpadding="3">
<tbody>
<tr>
<td>Csütörtök</td>
<td>2025.11.06</td>
<td>12:00-22:00</td>
</tr>
<tr>
<td>Péntek</td>
<td>2025.11.07</td>
<td>12:00-22:00</td>
</tr>
</tbody>
</table>
"""
        events = parse_schedule_email(email_text)
        self.assertEqual(len(events), 2)
        
        # Check first event
        # Start time should be 12:00 - 20 mins = 11:40
        self.assertEqual(events[0]['start'], datetime(2025, 11, 6, 11, 40))
        self.assertEqual(events[0]['end'], datetime(2025, 11, 6, 22, 0))

if __name__ == '__main__':
    unittest.main()
