from gmail_service import get_email_content
from email_parser import parse_schedule_email
from calendar_service import get_existing_event, create_event, update_event

def process_messages(gmail_service, calendar_service, calendar_id, messages):
    """
    Processes a list of Gmail messages, parses them, and updates the calendar.
    Returns a tuple (added_count, updated_count).
    """
    added = 0
    updated = 0
    
    total = len(messages)
    print(f"Processing {total} emails...")
    
    for i, msg in enumerate(messages):
        print(f"[{i+1}/{total}] Processing email ID: {msg['id']}")
        try:
            content = get_email_content(gmail_service, msg['id'])
            events = parse_schedule_email(content)
            
            if not events:
                continue
                
            for event in events:
                existing_event = get_existing_event(calendar_service, calendar_id, event['start'], event['end'], event['summary'])
                
                if existing_event:
                    # Update it
                    update_event(calendar_service, calendar_id, existing_event['id'], event)
                    updated += 1
                else:
                    create_event(calendar_service, calendar_id, event)
                    print(f"    Added: {event['start']} - {event['summary']}")
                    added += 1
                    
        except Exception as e:
            print(f"  Error processing email {msg['id']}: {e}")
            
    return added, updated
