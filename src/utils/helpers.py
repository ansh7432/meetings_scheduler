def format_date(date):
    """Format a date object into a string."""
    return date.strftime("%Y-%m-%d")

def format_time(time):
    """Format a time object into a string."""
    return time.strftime("%H:%M")

def parse_date(date_str):
    """Parse a date string into a date object."""
    from datetime import datetime
    return datetime.strptime(date_str, "%Y-%m-%d").date()

def parse_time(time_str):
    """Parse a time string into a time object."""
    from datetime import datetime
    return datetime.strptime(time_str, "%H:%M").time()

def is_time_slot_available(start_time, end_time, booked_slots):
    """Check if a time slot is available given booked slots."""
    for slot in booked_slots:
        if (start_time < slot[1] and end_time > slot[0]):
            return False
    return True

def suggest_time_slots(start_time, end_time, duration, booked_slots):
    """Suggest available time slots within a given range."""
    available_slots = []
    current_start = start_time

    while current_start + duration <= end_time:
        current_end = current_start + duration
        if is_time_slot_available(current_start, current_end, booked_slots):
            available_slots.append((current_start, current_end))
        current_start += duration

    return available_slots