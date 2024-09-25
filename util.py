from datetime import datetime
from typing import Any


def ms_to_hhmm(ms):
    dt = datetime.fromtimestamp(ms / 1000.0)
    return dt.strftime('%I:%M %p')


def seconds_to_hmm(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours}:{minutes:02d}"


def calendar_has_events_on_day(events: dict[str, Any], day: datetime) -> bool:
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        start_date = datetime.strptime(start[:10], '%Y-%m-%d').date()
        if start_date == day:
            return True

    return False
