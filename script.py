import datetime
import pytz
import dtwrapper
from contestsite import AtCoder, TopCoder, Codeforces, CSAcademy, yukicoder, LeetCode
import twitterutil


# AWS lambda
def lambda_handler(event, context):
    _now = datetime.datetime.now().astimezone(pytz.timezone("Asia/Tokyo"))
    dtwrapper.now(_now.replace(hour=8, minute=0, second=0, microsecond=0))
    contest_sites = (AtCoder(),
                     TopCoder(),
                     Codeforces(),
                     CSAcademy(),
                     yukicoder(),
                     LeetCode())
    contests = []
    for site in contest_sites:
        contests.extend(site.get_contestdata())
    contests.sort(key=lambda x: x.begin, reverse=True)
    twitterutil.tweet(contests)


if __name__ == '__main__':
    lambda_handler(None, None)
