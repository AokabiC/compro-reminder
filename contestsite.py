import datetime
from dateutil.parser import parse
import pytz
import dtwrapper
from urllib.request import urlopen
from bs4 import BeautifulSoup
import googlecalutil
from contestsiteinfo import ContestSiteInfo
from contestdata import ContestData


# superclass
class ContestSite():
    def __init__(self,
                name: str,
                acronym: str,
                googlecal_id: str):
        self.siteinfo = ContestSiteInfo(
            name,
            acronym,
            googlecal_id)

    def get_contestdata(self):
        raise NotImplementedError()


# Contest Sites
class AtCoder(ContestSite):
    def __init__(self):
        super().__init__(
            "AtCoder",
            "AC",
            ""   #atcoder.jp_gqd1dqpjbld3mhfm4q07e4rops@group.calendar.google.com
        )

    def get_contestdata(self):
        html = urlopen("https://beta.atcoder.jp/contests/")
        bs_obj = BeautifulSoup(html, "html.parser")
        table = bs_obj.find_all("table", class_="table table-default table-striped table-hover table-condensed table-bordered small")[1]
        rows = table.find_all("tr")
        del rows[0]

        contests = []
        for row in rows:
            # contest_data = [start, contestname, duration, rated]
            contest_data = [cell.get_text() for cell in row.find_all("td")]

            contest_name = contest_data[1]
            contest_begin = parse(contest_data[0]).astimezone(pytz.timezone('Asia/Tokyo'))
            contest_duration = dtwrapper.str2timedelta(contest_data[2])
            contest = ContestData(contest_name,
                                  self.siteinfo,
                                  contest_begin,
                                  contest_duration)
            if(not contest.is_valid(dtwrapper.now())):
                continue
            contests.append(contest)
        return contests


class TopCoder(ContestSite):
    def __init__(self):
        super().__init__(
            "TopCoder",
            "TC",
            "appirio.com_bhga3musitat85mhdrng9035jg@group.calendar.google.com"
        )
    
    def get_contestdata(self):
        return googlecalutil.get_contestdata(self.siteinfo)


class Codeforces(ContestSite):
    def __init__(self):
        super().__init__(
            "Codeforces",
            "Cf",
            "br1o1n70iqgrrbc875vcehacjg@group.calendar.google.com"
        )
    
    def get_contestdata(self):
        return googlecalutil.get_contestdata(self.siteinfo)


class CSAcademy(ContestSite):
    def __init__(self):
        super().__init__(
            "CSAcademy",
            "CSA",
            "8e3hcf3piim0pt3ibh4vfuh8rs@group.calendar.google.com"
        )
    
    def get_contestdata(self):
        return googlecalutil.get_contestdata(self.siteinfo)


class yukicoder(ContestSite):
    def __init__(self):
        super().__init__(
            "yukicoder",
            "ykc",
            "albqnro5hkurj3sqgb9r0d0v3eqrjdif@import.calendar.google.com"
        )
    
    def get_contestdata(self):
        return googlecalutil.get_contestdata(self.siteinfo)


class LeetCode(ContestSite):
    def __init__(self):
        super().__init__(
            "LeetCode",
            "LC",
            "tlvovsip3t3045rnkq0rt7d77c@group.calendar.google.com"
        )

    def get_contestdata(self):
        return googlecalutil.get_contestdata(self.siteinfo)
