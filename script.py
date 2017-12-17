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
    html = urlopen("https://atcoder.jp/?lang=ja")
    bs_obj = BeautifulSoup(html, "html.parser")
    table = bs_obj.find_all("table", class_="table table-default table-striped table-hover table-condensed")[1]
    rows = table.find_all("tr")
    del rows[0]

    contest_list = []
    contest_acronym = "[AC]"
    # contest = [contest_dt(開始時間), contest_name(コンテスト名)]
    for row in rows:
        contest = []
        for cell in row.find_all("td"):
            text = cell.get_text()
            contest.append(text)
        contest.insert(1, contest_acronym)
        contest[0] = parse(contest[0]).astimezone(pytz.timezone('Asia/Tokyo'))
        # ツイート有効期間内か判定(08:00~翌07:59)
        dt_diff = contest[0] - now_dt
        if(dt_diff.days != 0):
            continue
        contest_list.append(contest)
    return contest_list


# Googleカレンダーからコンテストデータを取得
def getContestDatafromCal(now_dt):
    contest_list = []

    now_dt = now_dt.replace(hour=8, minute=0, second=0, microsecond=0)
    dt_from = now_dt.isoformat(timespec='microseconds')
    dt_to = (now_dt + datetime.timedelta(hours=23, minutes=59, seconds=59)).isoformat()
    # 競プロのコンテストであると決定する文字列リスト
    # いずれかが含まれていればprint対象に含める
    procon_strs = ["Round", "SRM", "Cup", "ontest", "CODE", "Camp", "コンテスト", "ICPC"]
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
    contest_acronyms = ["[Cf]", "[TCO]", "[yuki]", "[CSA]", "[etc.]"]
    # GoogleカレンダーAPIを利用可能にする
    service = googleCalAPI()
    # 各カレンダーについてAPI実行
    for (calendar_id, contest_acronym) in zip(calendar_ids, contest_acronyms):
        events_results = service.events().list(
            calendarId=calendar_id,
            timeMin=dt_from,
            timeMax=dt_to,
            maxResults=5,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        # API結果から値を取り出す
        events = events_results.get('items', [])
        for event in events:
            try:
                contest_dt = parse(event["start"]["dateTime"]).astimezone(pytz.timezone('Asia/Tokyo'))
                contest_name = event["summary"]
            except KeyError:
                continue
            else:
                # 競プロのコンテストかどうか判定
                is_procon = False
                for string in procon_strs:
                    if(string in contest_name):
                        is_procon = True
                        break
                if(not is_procon):
                    continue
                contest_list.append([contest_dt, contest_acronym, contest_name])
        return contest_list


# ツイート文字列のリストを生成
def generateTweet(contest_list, now_dt):
    tweets = []
    tweet_num = (len(contest_list)+1)//2
    if(tweet_num == 0):
        return ["本日" + now_dt.strftime("%m/%d") + "はコンテストがありません."]

    # 時系列順にソート
    contest_list.sort(key=lambda x: x[0])
    NAME_LENGTH = (129 - 9 * 2) // 2
    for i in range(tweet_num):
        # ツイートが別れる場合(3コンテスト以上), 番号を表示
        tweet_count = ""
        if(tweet_num >= 2):
            tweet_count = "(" + (i+1) + ")"
        tweet = now_dt.strftime("%m/%d") + "のコンテスト予定" + tweet_count + "\n"
        for j in range(min(2, len(contest_list))):
            contest_dt, contest_acronym, contest_name = contest_list.pop()
            # コンテスト情報が長すぎる場合カット
            if(len(contest_name) > NAME_LENGTH):
                contest_name = contest_name[:(NAME_LENGTH - 1)] + "…"
            # 翌日のコンテストの場合
            is_nextday = ""
            if(contest_dt.date() != now_dt.date()):
                is_nextday = "翌"
            tweet += " %s%s %s\n" % (contest_acronym,
                                     is_nextday + contest_dt.strftime("%H:%M"),
                                     contest_name)
        tweets.append(tweet)
    return tweets


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
