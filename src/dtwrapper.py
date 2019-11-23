import datetime
from contestdata import ContestData

__now = None

# Read-Only
# Due to the behavior of AWS Lambda, datetime.now() is callable
# only in lambda_handler().
def now(val=None):
    global __now
    if(not val is None):
        __now = val
    return __now


def str2timedelta(HHMM):
    """convert HH:MM str to datetime.timedelta obj."""
    HHMM = list(map(int, HHMM.split(":")))
    return datetime.timedelta(hours=HHMM[0], minutes=HHMM[1])
