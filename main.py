import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from gmail_service import get_gmail_service, search_schedule_emails
from calendar_service import get_calendar_service, get_or_create_calendar
from processor import process_messages

def main():
    print("Authenticating with Google Services...")
    try:
        gmail_service = get_gmail_service()
        calendar_service = get_calendar_service()
        
        # Get or create the dedicated calendar
        calendar_id = get_or_create_calendar(calendar_service, "Work Schedule")
        print(f"Using calendar: Work Schedule (ID: {calendar_id})")
        
    except Exception as e:
        print(f"Authentication/Setup failed: {e}")
        print("Please ensure you have 'credentials.json' in the project root.")
        return

    print("Searching for recent schedule emails...")
    # Search last 2 months, max 10 results
    messages = search_schedule_emails(gmail_service, max_results=10, newer_than='2m')
    
    if not messages:
        print("No schedule emails found.")
        return
        
    added, updated = process_messages(gmail_service, calendar_service, calendar_id, messages)
            
    print(f"\nDone! Added: {added}, Updated: {updated}")

if __name__ == '__main__':
    main()
