# coding: utf-8
import datetime
from dateutil.parser import parse
import pytz
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials
import apiclient
import json
import tweepy
from bs4 import BeautifulSoup
from urllib.request import urlopen
import models

# Twitter OAuth認証
def twitterOAuth():
    auth_file = open("Twitter_auth.json")
    auth_list = json.load(auth_file)
    auth_file.close()
    auth = tweepy.OAuthHandler(auth_list["consumer_key"], auth_list["consumer_secret"])
    auth.set_access_token(auth_list["token"], auth_list["token_secret"])
    return auth


# Google API認証
def googleCalAPI():
    client_secret_file = 'Google_calAPI.json'
    scopes = ['https://www.googleapis.com/auth/calendar.readonly']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(client_secret_file, scopes=scopes)
    http_auth = credentials.authorize(Http())
    service = apiclient.discovery.build("calendar", "v3", http=http_auth, cache_discovery=False)
    return service


# Webサイトから直接スクレイピング
def scrapeContestData(now_dt):
    # AtCoder
    html = urlopen("https://beta.atcoder.jp/contests/")
    bs_obj = BeautifulSoup(html, "html.parser")
    table = bs_obj.find_all("table", class_="table table-default table-striped table-hover table-condensed")[1]
    rows = table.find_all("tr")
    del rows[0]

    # contest = [contest_dt(開始時間), contest_name(コンテスト名)]
    for row in rows:
        contest_data = [cell.get_text() for cell in row.find_all("td")]
        contest = models.ContestData(contest_data[1],
                                     models.ContestSite.AtCoder,
                                     parse(contest_data[0]+"+09:00").astimezone(pytz.timezone('Asia/Tokyo'))
        # ツイート有効期間内か判定(08:00~翌07:59)
        dt_diff = contest[0] - now_dt
        if(dt_diff.days < 0 or dt_diff.days >= 1):
            continue
        contest_list.append(contest)
    return contest_list


# Googleカレンダーからコンテストデータを取得
def getContestDatafromCal(now_dt):
    contest_list = []

    now_dt = now_dt.replace(hour=8, minute=0, second=0, microsecond=0)
    dt_from = now_dt.isoformat(timespec='microseconds')
    dt_to = (now_dt + datetime.timedelta(days=1)).isoformat()
    # コンテスト情報が載ったGoogleカレンダー
    calendar_ids = [
        # AtCoder(スクレイピングに変更)
        # "atcoder.jp_gqd1dqpjbld3mhfm4q07e4rops@group.calendar.google.com",
        # Codeforces
        "br1o1n70iqgrrbc875vcehacjg@group.calendar.google.com",
        # TopCoder
        "appirio.com_bhga3musitat85mhdrng9035jg@group.calendar.google.com",
        # yukicoder
        "albqnro5hkurj3sqgb9r0d0v3eqrjdif@import.calendar.google.com",
        # CS Academy
        "8e3hcf3piim0pt3ibh4vfuh8rs@group.calendar.google.com",
        # Others
        "9oq67ntb3j77hnlem9tds02og0@group.calendar.google.com"
    ]
    # GoogleカレンダーAPIを利用可能にする
    service = googleCalAPI()
    # 各カレンダーについてAPI実行
    


# AWS lambda
def lambda_handler(event, context):
    now_dt = datetime.datetime.today().astimezone(pytz.timezone("Asia/Tokyo"))
    twitter_api = tweepy.API(twitterOAuth())
    tweets = generateTweet(scrapeContestData(now_dt)+getContestDatafromCal(now_dt), now_dt)
    for tweet in tweets:
        print(tweet)
        twitter_api.update_status(status=tweet)


if __name__ == '__main__':
    lambda_handler(None, None)
