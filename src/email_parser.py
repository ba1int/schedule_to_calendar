import re
import os
from datetime import datetime, timedelta

def clean_html(raw_html):
    """
    Removes HTML tags from a string.
    """
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.strip()

def parse_schedule_email(email_body):
    """
    Parses the email body (HTML) to extract schedule entries.
    Returns a list of dictionaries with 'start', 'end', 'summary', 'description'.
    """
    events = []
    
    # Normalize newlines and spaces
    content = email_body.replace('\n', '')
    
    # Find all table rows
    # We look for <tr>...</tr>. Non-greedy match.
    rows = re.findall(r'<tr>(.*?)</tr>', content, re.IGNORECASE | re.DOTALL)
    
    for row in rows:
        # Extract cells <td>...</td>
        cells = re.findall(r'<td>(.*?)</td>', row, re.IGNORECASE | re.DOTALL)
        
        if len(cells) != 3:
            continue
            
        # Clean up HTML tags from cells (e.g. <strong>, <em>)
        day_name = clean_html(cells[0])
        date_str = clean_html(cells[1])
        schedule_str = clean_html(cells[2])
        
        # Skip header row
        if "Nap" in day_name or "Dátum" in date_str:
            continue
            
        # Parse Date
        # Format: 2025.11.02 (ma) -> remove (ma)
        date_str = date_str.split(' ')[0].strip()
        
        # Check for valid date format YYYY.MM.DD
        if not re.match(r'\d{4}\.\d{2}\.\d{2}', date_str):
            continue
            
        # Check Schedule
        # Ignore "PN" (Pihenőnap), "Szabi" (Holiday), "Beteg" (Sick)
        # We only care about time ranges like "12:00-22:00"
        
        time_match = re.search(r'(\d{1,2}:\d{2})-(\d{1,2}:\d{2})', schedule_str)
        if time_match:
            start_time_str = time_match.group(1)
            end_time_str = time_match.group(2)
            
            try:
                # Construct full datetime objects
                start_dt = datetime.strptime(f"{date_str} {start_time_str}", "%Y.%m.%d %H:%M")
                end_dt = datetime.strptime(f"{date_str} {end_time_str}", "%Y.%m.%d %H:%M")
                
                # Adjust start time: subtract 20 minutes
                start_dt = start_dt - timedelta(minutes=20)
                
                # Get summary from env var or default
                summary = os.environ.get('EVENT_SUMMARY', 'Work at McDonald\'s')
                
                events.append({
                    'summary': summary,
                    'start': start_dt,
                    'end': end_dt,
                    'description': f"{day_name}: {schedule_str}"
                })
            except ValueError as e:
                print(f"Error parsing date/time: {e}")
                continue
            
    return events
