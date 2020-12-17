import datetime
from dateutil.parser import parse
import dtwrapper
import pytz
from google.oauth2 import service_account
import apiclient
from contestdata import ContestData

_service = None


def api_auth():
    global _service
    if(not _service is None):
        return _service
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    # follow https://developers.google.com/identity/protocols/oauth2/service-account
    # then get service account's credentials.
    SERVICE_ACCOUNT_FILE = 'google_services.json'
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    _service = apiclient.discovery.build(
        "calendar", "v3", credentials=credentials)
    return _service


def get_contestdata(siteinfo):
    start = dtwrapper.now()
    duration = datetime.timedelta(days=20)

    dt_from = start.isoformat(timespec='microseconds')
    dt_to = (start+duration).isoformat()
    service = api_auth()
    try:
        events_data = service.events().list(
            calendarId=siteinfo.googlecal_id,
            timeMin=dt_from,
            timeMax=dt_to,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
    except apiclient.errors.HttpError as err:
        print(err)
        return []

    events = events_data.get('items', [])

    contests = []
    for event in events:
        try:
            contest_name = event["summary"]
            contest_begin = parse(event["start"]["dateTime"]).astimezone(
                pytz.timezone('Asia/Tokyo'))
            contest_end = parse(event["end"]["dateTime"]).astimezone(
                pytz.timezone('Asia/Tokyo'))
            contest_duration = contest_end - contest_begin
            contest = ContestData(contest_name,
                                  siteinfo,
                                  contest_begin,
                                  contest_duration)
        except KeyError:
            continue
        else:
            if(contest.is_valid(dtwrapper.now())):
                contests.append(contest)
    return contests
