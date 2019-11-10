import datetime
from contestsiteinfo import ContestSiteInfo

class ContestData():
    """Data structure of contest information."""

    def __init__(self,
                 name: str,
                 siteinfo: ContestSiteInfo,
                 begin: datetime.datetime=datetime.datetime.min,
                 duration: datetime.timedelta=datetime.timedelta(hours=1)):
        self.name = name
        self.siteinfo = siteinfo
        self.begin = begin
        self.duration = duration

    def __repr__(self):
        return "({}, {}, {}, {})".format(
            self.name, self.siteinfo.name, str(self.begin), str(self.duration))

    def is_valid(self,
                 startfrom: datetime.datetime):
        diff = self.begin - startfrom
        if(diff.days < 0 or diff.days >= 1):
            return False
        if(self.duration > datetime.timedelta(hours=12)):
            return False
        return True
