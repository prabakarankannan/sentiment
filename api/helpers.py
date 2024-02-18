from datetime import datetime
import pytz
from django.utils import timezone
from django.conf import settings


def convert_to_unix_datetime(datetime_str):
    # Define the input datetime string

    # Create a datetime object from the string, assuming it's in the given timezone
    datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S%z")

    # Convert the datetime object to a Unix timestamp (integer value)
    unix_timestamp = int(datetime_obj.timestamp())

    return unix_timestamp


def human_format(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])


def datetime_to_hour(datetime_str):
    # Parse the datetime string
    dt = datetime.fromisoformat(datetime_str)

    # Format it as "HH:MM AM/PM"
    # formatted_datetime = dt.strftime("%I:%M %p")

    # Format it as "Month Day, Year HH:MM AM/PM"
    formatted_datetime = dt.strftime("%B %d %I:%M %p")

    return formatted_datetime


def get_current_time():
    # Get the current time in UTC
    now_utc = timezone.now()

    # Set the Indian timezone
    indian_timezone = timezone.get_current_timezone()  # or timezone.pytz.timezone('Asia/Kolkata')

    # Convert the UTC time to Indian timezone
    now_indian = now_utc.astimezone(indian_timezone)

    return now_indian