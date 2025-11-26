import sys
import os
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from gmail_service import get_gmail_service, search_schedule_emails
from calendar_service import get_calendar_service, get_or_create_calendar
from processor import process_messages

def main():
    start_time = datetime.now()
    print("=" * 60)
    print(f"Schedule Backfill Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    print("Authenticating with Google Services...")
    try:
        gmail_service = get_gmail_service()
        calendar_service = get_calendar_service()
        
        # Get calendar ID from environment variable or create/find by name
        calendar_id = os.environ.get('CALENDAR_ID')
        if calendar_id:
            print(f"Using calendar ID from CALENDAR_ID env var: {calendar_id}")
        else:
            calendar_name = os.environ.get('CALENDAR_NAME', 'Work Schedule')
            calendar_id = get_or_create_calendar(calendar_service, calendar_name)
            print(f"Using calendar: {calendar_name} (ID: {calendar_id})")
        
    except Exception as e:
        print(f"Authentication failed: {e}")
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        print("=" * 60)
        print(f"Finished (with errors): {end_time.strftime('%Y-%m-%d %H:%M:%S')} (Duration: {duration:.2f}s)")
        print("=" * 60)
        return

    print("Searching for ALL schedule emails (this might take a while)...")
    # Search all time, no limits
    messages = search_schedule_emails(gmail_service, max_results=None, newer_than=None)
    
    if not messages:
        print("No schedule emails found.")
    else:
        # Process from oldest to newest to ensure correct history
        messages.reverse()
        
        added, updated, deleted = process_messages(gmail_service, calendar_service, calendar_id, messages)
        print(f"\nDone! Added: {added}, Updated: {updated}, Deleted: {deleted}")
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    print("=" * 60)
    print(f"Finished successfully: {end_time.strftime('%Y-%m-%d %H:%M:%S')} (Duration: {duration:.2f}s)")
    print("=" * 60)

if __name__ == '__main__':
    main()
