from gmail_service import get_email_content
from email_parser import parse_schedule_email
from calendar_service import get_existing_event, get_events_in_range, create_event, update_event, delete_event

def process_messages(gmail_service, calendar_service, calendar_id, messages):
    """
    Processes a list of Gmail messages, parses them, and updates the calendar.
    Also deletes calendar events that are no longer in the schedule.
    Returns a tuple (added_count, updated_count, deleted_count).
    """
    added = 0
    updated = 0
    deleted = 0
    
    total = len(messages)
    print(f"Processing {total} emails...")
    
    for i, msg in enumerate(messages):
        print(f"[{i+1}/{total}] Processing email ID: {msg['id']}")
        try:
            content = get_email_content(gmail_service, msg['id'])
            events = parse_schedule_email(content)
            
            if not events:
                continue
            
            # Track which dates are in this email's schedule
            event_dates = set()
            
            for event in events:
                event_dates.add(event['start'].date())
                existing_event = get_existing_event(calendar_service, calendar_id, event['start'], event['end'], event['summary'])
                
                if existing_event:
                    # Update it
                    update_event(calendar_service, calendar_id, existing_event['id'], event)
                    updated += 1
                else:
                    create_event(calendar_service, calendar_id, event)
                    print(f"    Added: {event['start']} - {event['summary']}")
                    added += 1
            
            # Check for deletions: get the date range covered by this email
            if event_dates:
                min_date = min(event_dates)
                max_date = max(event_dates)
                
                # Get all calendar events in this date range
                calendar_events = get_events_in_range(
                    calendar_service, 
                    calendar_id, 
                    min_date, 
                    max_date,
                    events[0]['summary']  # Use the summary from parsed events
                )
                
                # Delete events that are in the calendar but not in the email
                for cal_event in calendar_events:
                    # Extract the date from the calendar event
                    from datetime import datetime
                    event_start = datetime.fromisoformat(cal_event['start']['dateTime'].replace('Z', '+00:00'))
                    event_date = event_start.date()
                    
                    if event_date not in event_dates:
                        print(f"    Deleting removed shift on {event_date}")
                        delete_event(calendar_service, calendar_id, cal_event['id'])
                        deleted += 1
                    
        except Exception as e:
            print(f"  Error processing email {msg['id']}: {e}")
            
    return added, updated, deleted
