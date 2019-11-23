import datetime
import pytz
import dtwrapper
from contestsite import AtCoder, TopCoder, Codeforces, CSAcademy, yukicoder, LeetCode, GoogleCodeJam
import os
import twitterutil
import pprint


# AWS lambda
def lambda_handler(event, context):
    event_arn = event["resources"][0]
    print("Event AWS Resource Name(ARN): " + event_arn)
    now = datetime.datetime.now().astimezone(pytz.timezone("Asia/Tokyo"))
    dtwrapper.now(now.replace(hour=8, minute=0, second=0, microsecond=0))
    contest_sites = (AtCoder(),
                     TopCoder(),
                     Codeforces(),
                     CSAcademy(),
                     yukicoder(),
                     LeetCode(),
                     GoogleCodeJam())
    contests = []
    for site in contest_sites:
        contests.extend(site.get_contestdata())
    contests.sort(key=lambda x: x.begin, reverse=True)
    pprint.pprint(contests)
    if(event_arn == os.environ["AWS_EVENT_ARN"]):
        twitterutil.tweet(contests)


if __name__ == '__main__':
    test_event = {
        "version": "0",
        "id": "89d1a02d-5ec7-412e-82f5-13505f849b41",
        "detail-type": "Scheduled Event",
        "source": "aws.events",
        "account": "123456789012",
        "time": "2016-12-30T18:44:49Z",
        "region": "us-east-1",
        "resources": [
            "arn:aws:events:us-east-1:123456789012:rule/SampleRule"
        ],
        "detail": {}
    }
    lambda_handler(test_event, None)
