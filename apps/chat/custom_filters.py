import pytz
from pytz import timezone
from datetime import datetime
# import tzlocal 
from fastapi import Request
from . views import templates

def threadsdatetimefilter(value, format="%I:%M %p"):
    tzname = current_user.tzname
    tz = pytz.timezone(tzname) # timezone you want to convert to from UTC

    utc = pytz.timezone('UTC')
    current_date = utc.localize(datetime.utcnow(), is_dst=None).astimezone(pytz.utc)
    current_date = current_date.astimezone(tz)

    local_dt = value.astimezone(tz)
    new_dt = local_dt.strftime(format)
    if current_date.date() == local_dt.date():
        new_dt = local_dt.strftime('%H:%M')
    elif current_date.day - local_dt.day == 1 and current_date.month == local_dt.month and current_date.year == local_dt.year:
        new_dt = 'yesterday'
    else:
        new_dt = local_dt.strftime('%d/%m/%Y')

    return new_dt

def dms_datetimefilter(date):
    tzname = current_user.tzname
    tz = pytz.timezone(tzname) # timezone you want to convert to from UTC

    # Get current local time of user and date object in local time
    utc = pytz.timezone('UTC')
    current_date = utc.localize(datetime.utcnow(), is_dst=None).astimezone(pytz.utc)
    current_date = current_date.astimezone(tz)
    
    date_obj = date.astimezone(tz)

    new_dt = date_obj
    if current_date.date() == date_obj.date():
        new_dt = 'Today'
    elif current_date.day - date_obj.day == 1 and current_date.month == date_obj.month and current_date.year == date_obj.year:
        new_dt = 'Yesterday'
    else:
        new_dt = date_obj.strftime('%d/%m/%Y')
    return new_dt

def unread_messages_count(messages, other_user_id):
    count = messages.filter_by(sender_id=other_user_id, is_read=False).count()
    return count

templates.env.filters["threadsdatetimefilter"] = threadsdatetimefilter
templates.env.filters["dms_datetimefilter"] = dms_datetimefilter
templates.env.filters["unread_messages_count"] = unread_messages_count

