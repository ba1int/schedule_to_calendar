from googleapiclient.discovery import build
from auth import get_credentials
from datetime import timedelta
from dateutil import tz

def get_calendar_service():
    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)
    return service

def get_or_create_calendar(service, calendar_name='Work Schedule'):
    """
    Returns the ID of the calendar with the given name.
    If it doesn't exist, creates it.
    """
    # List all calendars
    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            if calendar_list_entry['summary'] == calendar_name:
                return calendar_list_entry['id']
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break
            
    # If not found, create it
    calendar = {
        'summary': calendar_name,
        'timeZone': 'Europe/Budapest'
    }
    created_calendar = service.calendars().insert(body=calendar).execute()
    return created_calendar['id']

def get_existing_event(service, calendar_id, start_time, end_time, summary='Work at McDonald\'s'):
    """
    Checks if an event with the same summary exists on the same day.
    Returns the event object if found, None otherwise.
    """
    # Ensure start_time and end_time are timezone aware (Budapest)
    budapest_tz = tz.gettz('Europe/Budapest')
    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=budapest_tz)
    if end_time.tzinfo is None:
        end_time = end_time.replace(tzinfo=budapest_tz)
        
    # We want to check the whole day to find if there was a previous schedule
    # Construct start and end of the day for the query
    day_start = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = start_time.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    time_min = day_start.astimezone(tz.UTC).isoformat().replace('+00:00', 'Z')
    time_max = day_end.astimezone(tz.UTC).isoformat().replace('+00:00', 'Z')
    
    events_result = service.events().list(calendarId=calendar_id, timeMin=time_min,
                                        timeMax=time_max, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    for event in events:
        if event['summary'] == summary:
            return event
            
    return None

def get_events_in_range(service, calendar_id, start_date, end_date, summary='Work at McDonald\'s'):
    """
    Gets all events with the given summary within a date range.
    Returns a list of event objects.
    """
    from datetime import datetime
    budapest_tz = tz.gettz('Europe/Budapest')
    
    # Convert date to datetime if needed
    if not isinstance(start_date, datetime):
        start_date = datetime.combine(start_date, datetime.min.time())
    if not isinstance(end_date, datetime):
        end_date = datetime.combine(end_date, datetime.max.time())
    
    # Ensure dates are timezone aware
    if start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=budapest_tz)
    if end_date.tzinfo is None:
        end_date = end_date.replace(tzinfo=budapest_tz)
    
    # Set to start and end of days
    day_start = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    time_min = day_start.astimezone(tz.UTC).isoformat().replace('+00:00', 'Z')
    time_max = day_end.astimezone(tz.UTC).isoformat().replace('+00:00', 'Z')
    
    events_result = service.events().list(calendarId=calendar_id, timeMin=time_min,
                                        timeMax=time_max, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    
    # Filter by summary
    return [event for event in events if event.get('summary') == summary]

def delete_event(service, calendar_id, event_id):
    """
    Deletes a calendar event.
    """
    service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
    print(f"Event deleted: {event_id}")

def update_event(service, calendar_id, event_id, event_data):
    """
    Updates an existing calendar event.
    """
    start_dt = event_data['start']
    end_dt = event_data['end']
    
    # Ensure timezone awareness
    budapest_tz = tz.gettz('Europe/Budapest')
    if start_dt.tzinfo is None:
        start_dt = start_dt.replace(tzinfo=budapest_tz)
    if end_dt.tzinfo is None:
        end_dt = end_dt.replace(tzinfo=budapest_tz)

    event = {
        'summary': event_data['summary'],
        'description': event_data['description'],
        'start': {
            'dateTime': start_dt.isoformat(),
            'timeZone': 'Europe/Budapest',
        },
        'end': {
            'dateTime': end_dt.isoformat(),
            'timeZone': 'Europe/Budapest',
        },
    }
    
    updated_event = service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()
    print(f"Event updated: {updated_event.get('htmlLink')}")
    return updated_event

def create_event(service, calendar_id, event_data):
    """
    Creates a calendar event.
    event_data: {'summary': str, 'start': datetime, 'end': datetime, 'description': str}
    """
    start_dt = event_data['start']
    end_dt = event_data['end']
    
    # Ensure timezone awareness
    budapest_tz = tz.gettz('Europe/Budapest')
    if start_dt.tzinfo is None:
        start_dt = start_dt.replace(tzinfo=budapest_tz)
    if end_dt.tzinfo is None:
        end_dt = end_dt.replace(tzinfo=budapest_tz)

    event = {
        'summary': event_data['summary'],
        'description': event_data['description'],
        'start': {
            'dateTime': start_dt.isoformat(),
            'timeZone': 'Europe/Budapest',
        },
        'end': {
            'dateTime': end_dt.isoformat(),
            'timeZone': 'Europe/Budapest',
        },
    }
    
    event = service.events().insert(calendarId=calendar_id, body=event).execute()
    print(f"Event created: {event.get('htmlLink')}")
    return event
