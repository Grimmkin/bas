from datetime import datetime, timezone, timedelta

def convert_to_ampm(time_string):
    # Parse the string to a datetime object
    dt = datetime.fromisoformat(time_string.replace('Z', '+00:00'))

    # Format the datetime object to a string in am/pm format
    return dt.strftime('%I:%M%p')

def get_current_time():
    # Get the current time
    current_time = datetime.now()

    # Format the time to a string in am/pm format
    return current_time.strftime('%I:%M%p')

def get_formatted_time():
    current_time = datetime.now(timezone.utc)
    formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S.%f%z')
    return formatted_time

def get_iso_time():
    # Create a timezone for UTC+1
    utc_plus_one = timezone(timedelta(hours=1))

    # Get the current time in UTC+1
    current_time = datetime.now(utc_plus_one)

    # Format the time to a string
    formatted_time = current_time.isoformat()

    return formatted_time

def get_timestamp():
    # Get the current time in UTC
    current_time = datetime.now(timezone.utc)

    # Convert the current time to a timestamp
    timestamp = current_time.timestamp()

    return timestamp