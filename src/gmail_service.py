from googleapiclient.discovery import build
from auth import get_credentials
import base64

def get_gmail_service():
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)
    return service

def search_schedule_emails(service, sender="mymenu-support@ext.mcdonalds.com", max_results=None, newer_than=None):
    """
    Searches for emails from the specified sender with relevant subjects.
    Args:
        max_results: Max number of emails to return. If None, returns all.
        newer_than: Time filter (e.g., '2m'). If None, searches all time.
    """
    query = f'from:{sender} subject:("Beosztásod megváltozott" OR "Új beosztásod")'
    
    if newer_than:
        query += f' newer_than:{newer_than}'
    
    messages = []
    page_token = None
    
    while True:
        # If max_results is set and small (like 10), we can just pass it to API if we don't loop.
        # But if we want robust "get all", we loop.
        
        kwargs = {'userId': 'me', 'q': query, 'pageToken': page_token}
        if max_results and not page_token:
             # Only apply maxResults to the first call if we just want a few
             # But if max_results is large, this logic is tricky.
             # For our use case: main.py wants 10, backfill wants ALL.
             if max_results <= 500:
                 kwargs['maxResults'] = max_results
        
        results = service.users().messages().list(**kwargs).execute()
        batch = results.get('messages', [])
        messages.extend(batch)
        
        if max_results and len(messages) >= max_results:
            messages = messages[:max_results]
            break
            
        page_token = results.get('nextPageToken')
        if not page_token:
            break
            
    return messages

def get_email_content(service, msg_id):
    """
    Retrieves the body of the email.
    """
    message = service.users().messages().get(userId='me', id=msg_id).execute()
    payload = message['payload']
    
    # The body might be in 'body' or in 'parts'
    if 'parts' in payload:
        parts = payload['parts']
        data = parts[0]['body']['data']
    else:
        data = payload['body']['data']
        
    data = data.replace("-", "+").replace("_", "/")
    decoded_data = base64.b64decode(data)
    
    return decoded_data.decode('utf-8')
