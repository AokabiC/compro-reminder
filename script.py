# coding: utf-8
import datetime
from dateutil.parser import parse
import pytz
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials
import apiclient
import json
import tweepy


# Twitter OAuth認証
def Twitter_OAuth():
    authFile = open("Twitter_auth.json")
    authList = json.load(authFile)
    authFile.close()
    auth = tweepy.OAuthHandler(authList["consumer_key"], authList["consumer_secret"])
    auth.set_access_token(authList["token"], authList["token_secret"])
    return auth


# Google API認証
def GoogleCalAPI():
    client_secret_file = 'Google_calAPI.json'
    scopes = ['https://www.googleapis.com/auth/calendar.readonly']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(client_secret_file, scopes=scopes)
    http_auth = credentials.authorize(Http())
    service = apiclient.discovery.build("calendar", "v3", http=http_auth, cache_discovery=False)
    return service


# Googleカレンダーからコンテストデータを取得
def getContestDatafromAPI(Nowdt):
    _events_formatted = []

    # コンテスト情報が載ったGoogleカレンダー
    calendar_id = [
        # AtCoder
        "atcoder.jp_gqd1dqpjbld3mhfm4q07e4rops@group.calendar.google.com",
        # Codeforces
        "br1o1n70iqgrrbc875vcehacjg@group.calendar.google.com",
        # TopCoder
        "appirio.com_bhga3musitat85mhdrng9035jg@group.calendar.google.com",
        # yukicoder
        "albqnro5hkurj3sqgb9r0d0v3eqrjdif@import.calendar.google.com",
        # CS Academy
        "csacademy.com_9i5d2d1kredb9k886ee9geb1tc@group.calendar.google.com"
    ]
    contest_acronym = ["[AC]", "[Cf]", "[TCO]", "[yuki]", "[CSA]"]
    # 競プロのコンテストであると決定する文字列リスト
    # いずれかが含まれていればprint対象に含める
    ComproConString = ["AtCoder", "Round", "SRM", "Cup", "contest"]
    dtfrom = Nowdt.isoformat() + "T00:00:00.000000Z"
    dtto = (Nowdt + datetime.timedelta(days=1)).isoformat() + "T00:00:00.000000Z"

    # GoogleカレンダーAPIを利用可能にする
    service = GoogleCalAPI()
    # 各カレンダーについてAPI実行
    for (_calendarId, _contestAcronym) in zip(calendar_id, contest_acronym):
        events_results = service.events().list(
            calendarId=_calendarId,
            timeMin=dtfrom,
            timeMax=dtto,
            maxResults=5,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        # API結果から値を取り出す
        events = events_results.get('items', [])
        for event in events:
            try:
                _dt = parse(event["start"]["dateTime"]).astimezone(pytz.timezone('Asia/Tokyo'))
                _summary = event["summary"]
                # 競プロのコンテストかどうか判定
                isComproCon = False
                for st in ComproConString:
                    if(st in _summary):
                        isComproCon = True
                        break
                if(not isComproCon): continue
                # ツイート有効期間内か判定(08:00~翌07:59)
                dtDiff = _dt - datetime.datetime.combine(Nowdt, datetime.time(8)).astimezone(pytz.timezone('Asia/Tokyo'))
                if(dtDiff.days != 0): continue
                _isNextDay = ""
                if(dtDiff.seconds >= 57600): _isNextDay = "翌"
                # コンテスト情報が長すぎる場合カット
                if(len(_summary) > 33):
                    _summary = _summary[:31] + "…"
                _events_formatted.append([_dt, _isNextDay, _contestAcronym, _summary])
            except KeyError:
                continue
    # 時系列順にソート
    _events_formatted.sort(key=lambda x: x[0])
    return _events_formatted


# ツイート文字列のリストを生成
def generateTweet(_events_formatted, Nowdt):
    tweets = [Nowdt.strftime("%m/%d") + "のコンテスト予定"]
    tweetsNum = 0
    tweet_contestinfo = ""
    for _dt, _isNextDay, _contestAcronym, _summary in _events_formatted:
        if(len(tweet_contestinfo) <= 85):
            tweet_contestinfo += " %s%s %s\n" % (_contestAcronym, _isNextDay + _dt.strftime("%H:%M"), _summary)
        else:
            tweets[tweetsNum] += "(" + str(tweetsNum+1) + ")\n" + tweet_contestinfo
            tweetsNum += 1
            tweets.append(Nowdt.strftime("%m/%d") + "のコンテスト予定")
            tweet_contestinfo = " %s%s %s\n" % (_contestAcronym, _dt.strftime("%H:%M"), _summary)
    if(tweet_contestinfo == ""):
        return []
    elif(tweetsNum):
        tweets[tweetsNum] += "(" + str(tweetsNum+1) + ")\n" + tweet_contestinfo
    else:
        tweets[tweetsNum] += "\n" + tweet_contestinfo
    return tweets


# AWS lambda
def lambda_handler(event, context):
    Nowdt = datetime.date.today()
    Twitter_api = tweepy.API(Twitter_OAuth())
    tweets = generateTweet(getContestDatafromAPI(Nowdt), Nowdt)
    if(tweets):
        for tweet in tweets:
            print(tweet)
            Twitter_api.update_status(status=tweet)


if __name__ == '__main__':
    lambda_handler(None, None)
