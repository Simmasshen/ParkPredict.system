from datetime import datetime, timedelta

def get_current_timestamp():
    """Returns current time in ISO format for DB entries."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def format_for_display(dt_string):
    """Converts DB timestamp to a readable format (e.g., Jan 01, 10:30 AM)."""
    dt = datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S")
    return dt.strftime("%b %d, %I:%M %p")

def calculate_duration_hours(start_time, end_time=None):
    """
    Calculates total hours parked. 
    Useful for analytics and billing.
    """
    fmt = "%Y-%m-%d %H:%M:%S"
    start = datetime.strptime(start_time, fmt)
    end = datetime.strptime(end_time, fmt) if end_time else datetime.now()
    
    duration = end - start
    return round(duration.total_seconds() / 3600, 2)

def is_peak_hour():
    """
    Returns True if current time is during typical peak parking hours.
    Used by the recommendation_service for surge pricing or availability alerts.
    """
    now = datetime.now()
    # Assuming peak is 8 AM - 10 AM and 5 PM - 7 PM
    peak_windows = [(8, 10), (17, 19)]
    return any(start <= now.hour <= end for start, end in peak_windows)

def get_day_type():
    """Returns 'Weekday' or 'Weekend' for analytics grouping."""
    return "Weekend" if datetime.now().weekday() >= 5 else "Weekday"
