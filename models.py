import datetime
from enum import Enum, auto


class ContestSite(Enum):
    AtCoder = auto()
    TopCoder = auto()
    Codeforces = auto()
    CSAcademy = auto()
    yukicoder = auto()
    Others = auto()


class ContestData:
    """コンテスト情報を格納するデータ構造"""
    def __init__(self,
                 name: str,
                 site: ContestSite,
                 begin: datetime.datetime=datetime.datetime.min,
                 duration: datetime.timedelta=datetime.timedelta(days=1)):
        self.name = name
        self.site = site
        self.begin = begin
        self.duration = duration

    def setDate(self,
                begin: datetime.datetime,
                end: datetime.datetime):
        self.begin = begin
        if(begin > end):
            raise ValueError
        self.end = end - begin

    __contest_acronym = {site: acronym
                         for site, acronym in zip(ContestSite, ["[AC]", "[TC]", "[Cf]", "[CSA]", "[yuki]", "[etc.]"])}

    def isVaild(self, now_dt: datetime):
        dt_diff = self.begin - now_dt
        if(dt_diff.days < 0 or dt_diff.days >= 1):
            return False
        # 時間が長過ぎるコンテストは除外
        if(self.duration > datetime.timedelta(hours=12)):
            return False
        return True

    def generateTweetStr(self, now_dt: datetime):
        if(not self.isVaild()):
            raise RuntimeError("generateTweetStr is supposed to be used only for vaild contests.")
        NAME_LENGTH = (129 - 9 * 2) // 2
        contest_name = self.name
        if(len(contest_name) > NAME_LENGTH):
            contest_name = contest_name[:(NAME_LENGTH - 1)] + "…"
        is_nextday = ""
        if(self.begin.date() != now_dt.date()):
            is_nextday = "翌"
        tweet_str = "%s%s %s" % (ContestData.__contest_acronym[self.site],
                                 is_nextday+self.begin.strftime("%H:%M"),
                                 contest_name)
        return tweet_str
