"""
Time utility functions for WAffy Dashboard.
"""

import re
from datetime import datetime, timedelta

def convert_relative_time_to_date(time_str):
    """
    Convert relative time expressions like 'tomorrow', 'next week', etc. to actual dates
    
    Args:
        time_str: String containing relative time expression
        
    Returns:
        Formatted date string in the format 'YYYY-MM-DD HH:MM' or the original string if no conversion possible
    """
    if not time_str:
        return time_str
        
    now = datetime.now()
    time_str = time_str.lower().strip()
    
    # Handle common relative time expressions
    if time_str == 'today':
        return now.strftime('%Y-%m-%d %H:%M')
    elif time_str == 'tomorrow':
        return (now + timedelta(days=1)).strftime('%Y-%m-%d %H:%M')
    elif time_str == 'day after tomorrow':
        return (now + timedelta(days=2)).strftime('%Y-%m-%d %H:%M')
    elif 'next week' in time_str:
        return (now + timedelta(days=7)).strftime('%Y-%m-%d %H:%M')
    elif 'next month' in time_str:
        # Approximate next month as 30 days
        return (now + timedelta(days=30)).strftime('%Y-%m-%d %H:%M')
    
    # Handle 'in X days/hours/minutes'
    in_match = re.search(r'in (\d+) (day|days|hour|hours|minute|minutes)', time_str)
    if in_match:
        amount = int(in_match.group(1))
        unit = in_match.group(2)
        
        if 'day' in unit:
            return (now + timedelta(days=amount)).strftime('%Y-%m-%d %H:%M')
        elif 'hour' in unit:
            return (now + timedelta(hours=amount)).strftime('%Y-%m-%d %H:%M')
        elif 'minute' in unit:
            return (now + timedelta(minutes=amount)).strftime('%Y-%m-%d %H:%M')
    
    # Handle specific time today (e.g., '5pm', '17:00')
    time_match = re.search(r'(\d{1,2})(:|\s)?(\d{2})?(\s)?(am|pm)?', time_str)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(3) or 0)
        ampm = time_match.group(5)
        
        if ampm == 'pm' and hour < 12:
            hour += 12
        elif ampm == 'am' and hour == 12:
            hour = 0
            
        today = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        return today.strftime('%Y-%m-%d %H:%M')
    
    # If no conversion was possible, return the original string
    return time_str
