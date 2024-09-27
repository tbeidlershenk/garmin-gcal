from init_api import init_api
from util import calendar_has_events_on_day, ms_to_hhmm, seconds_to_hmm
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import datetime
import os
from dotenv import load_dotenv
import sys
from logger import logger

load_dotenv()
SCOPES = ['https://www.googleapis.com/auth/calendar']
email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")
calendar_id = os.getenv("CALENDAR_ID")
credentials_file = os.getenv('CREDENTIALS_FILE')
tokenstore = os.getenv("GARMINTOKENS") or "~/.garminconnect"
tokenstore_base64 = os.getenv(
    "GARMINTOKENS_BASE64") or "~/.garminconnect_base64"
api = init_api(email, password, tokenstore, tokenstore_base64)

day = datetime.date.today() if len(
    sys.argv) == 1 else datetime.datetime.strptime(sys.argv[1], '%m-%d-%Y').date()
data = api.get_sleep_data(day.isoformat())

if data['dailySleepDTO']['id'] is None:
    logger.info(f"Error: No sleep data found for {day}")
    exit(0)

start_time_ms = data['dailySleepDTO']['sleepStartTimestampGMT']
end_time_ms = data['dailySleepDTO']['sleepEndTimestampGMT']
sleep_time_seconds = data['dailySleepDTO']['sleepTimeSeconds']
deep_sleep_seconds = data['dailySleepDTO']['deepSleepSeconds']
light_sleep_seconds = data['dailySleepDTO']['lightSleepSeconds']
rem_sleep_seconds = data['dailySleepDTO']['remSleepSeconds']
awake_sleep_seconds = data['dailySleepDTO']['awakeSleepSeconds']
resting_heart_rate = data['restingHeartRate']

start_time_hr = ms_to_hhmm(start_time_ms)
end_time_hr = ms_to_hhmm(end_time_ms)
sleep_time_hr = f"Total sleep time: {seconds_to_hmm(sleep_time_seconds)} hours"
deep_sleep_hr = f"Deep sleep: {seconds_to_hmm(deep_sleep_seconds)} hours"
light_sleep_hr = f"Light sleep: {seconds_to_hmm(light_sleep_seconds)} hours"
rem_sleep_hr = f"REM sleep: {seconds_to_hmm(rem_sleep_seconds)} hours"
awake_sleep_hr = f"Awake time: {seconds_to_hmm(awake_sleep_seconds)} hours"
resting_heart_rate_hr = f"Resting heart rate: {resting_heart_rate} bpm"

try:
    # build Google Calendar service
    credentials = Credentials.from_service_account_file(
        credentials_file, scopes=SCOPES)
    service = build('calendar', 'v3', credentials=credentials)
    logger.info("Built Google Calendar service")

    # query for events on the calendar
    events_result = service.events().list(
        calendarId=calendar_id).execute()
    events = events_result.get('items', [])
    logger.info("Retrieved existing calendar events")

    # script already run for today
    if calendar_has_events_on_day(events, day):
        logger.info(f"Error: Event already exists for {day}")
        exit(0)

    event = {
        'summary': "Garmin",
        'description': f"Start Time: {start_time_hr}\nEnd Time: {end_time_hr}\n{sleep_time_hr}\n{deep_sleep_hr}\n{light_sleep_hr}\n{rem_sleep_hr}\n{awake_sleep_hr}\n{resting_heart_rate_hr}",
        'start': {
            'date': day.isoformat(),
        },
        'end': {
            'date': (day + datetime.timedelta(days=1)).isoformat(),
        },
    }

    # add the event to configured calendar
    event = service.events().insert(calendarId=calendar_id, body=event).execute()
    logger.info(f"Event created: {event.get('htmlLink')}")

except Exception as error:
    logger.info(f"Error: {error}")
