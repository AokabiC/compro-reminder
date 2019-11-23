import os
import tweepy
import dtwrapper


def twitter_oauth():
    try:
        auth = tweepy.OAuthHandler(
            os.environ["TWITTER_API_CONSUMER_KEY"],
            os.environ["TWITTER_API_CONSUMER_SECRET"]
        )
        auth.set_access_token(
            os.environ["TWITTER_API_TOKEN"],
            os.environ["TWITTER_API_TOKEN_SECRET"]
        )
    except KeyError:
        print("Twitter API key does not set in os.environ")
        raise
    return auth


def contests2tweetformat(contests):
    strings = []
    NAME_LENGTH = (129 - 9 * 2) // 2
    for contest in contests:
        if(len(contest.name) > NAME_LENGTH):
            contest.name = contest.name[:(NAME_LENGTH-1)] + "…"
        is_nextday = "翌" if(contest.begin.date() > dtwrapper.now().date()) else ""
        string = "[%s]%s %s" % (contest.siteinfo.acronym,
                                is_nextday + contest.begin.strftime("%H:%M"),
                                contest.name)
        strings.append(string)
    return strings


def contests2tweets(contests):
    strings = contests2tweetformat(contests)
    if(len(strings) == 0):
        return ["本日" + dtwrapper.now().strftime("%m/%d") + "はコンテストがありません."]

    tweets_num = (len(strings)+1)//2
    tweet_title = dtwrapper.now().strftime("%m/%d") + "のコンテスト予定"
    tweets = []
    for i in range(tweets_num):
        tweet = tweet_title + ("\n" if(tweets_num == 1) else "("+str(i+1)+")\n")
              # if tweets are 2 or more, insert tweet number
        for j in range(2):
            try:
                tweet += strings.pop() + "\n"
            except IndexError:
                pass
        tweets.append(tweet)
    return tweets


def tweet(contests):
    twitter_api = tweepy.API(twitter_oauth())
    for tweet in contests2tweets(contests):
        print(tweet)
        twitter_api.update_status(status=tweet)
