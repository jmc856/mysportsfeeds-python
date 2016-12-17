import ConfigParser
import requests
from datetime import datetime
from dateutil.parser import parse


class MsfPull:

    def __init__(self):
        config = ConfigParser.ConfigParser()
        config.read("config/config.ini")
        self.base_url = "https://www.mysportsfeeds.com/api/feed/pull/"
        self.username = config.get("Authentication", "username")
        self.password = config.get("Authentication", "password")
        self.params = {"Accept-Encoding": "gzip"}

    def connection(self):
        date = datetime.now().year
        url = "https://www.mysportsfeeds.com/api/feed/pull/nfl/{date}-regular/latest_updates.{format}&force=True".format(
                                                                                                            date=date,
                                                                                                            format="json")
        r = requests.get(url, auth=(self.username, self.password), params={})

        if r.status_code == 200:
            print "connection ok with status code: {code}".format(code=r.status_code)
        else:
            print "connection failed with status code: {code}".format(code=r.status_code)


class Feed(MsfPull):
    def __init__(self):
        MsfPull.__init__(self)
        self.output = None

    def check_input(self, sport, date=datetime.now().strftime("%Y%m%d")):
        sports = ("nba", "nfl", "mlb", "nhl")
        if sport not in sports:
            raise AssertionError("Apply valid sport, accepts: {}".format(", ".join(x for x in sports)))

        try:
            date = parse(date).strftime("%Y%m%d")
        except:
            raise TypeError("Incorrect date format")

        return sport, date

    def make_call(self, base_url, url):
        r = requests.get(base_url+url, auth=(self.username, self.password), params=self.params)
        if r.status_code == 200:
            return r.json()

        elif r.status_code == 304:
            # Pull from stored file
            pass
        else:
            print ("API call failed with error: {error}".format(error=r.status_code))

    def cum_player_stats(self, sport, season, date, output="json"):
        sport, date = self.check_input(sport, date)
        self.url_ext = "{sport}/{season}-regular/daily_game_schedule.{format}?fordate={date}".format(sport=sport,
                                                                                                     season=season,
                                                                                                     format=output,
                                                                                                     date=date)
        self.output = self.make_call(self.base_url, self.url_ext)

    def full_game_schd(self):
        self.url_ext = ""

    def daily_game_schd(self):
        self.url_ext = ""

    def daily_player_stats(self):
        self.url_ext = ""

    def scoreboard(self):
        self.url_ext = ""

    def play_by_play(self):
        self.url_ext = ""

    def boxscore(self):
        self.url_ext = ""

    def roster(self):
        self.url_ext = ""

    def active(self):
        self.url_ext = ""

    def overall_standings(self):
        self.url_ext = ""

    def conf_standings(self):
        self.url_ext = ""

    def division_standings(self):
        self.url_ext = ""

    def playoff_standings(self):
        self.url_ext = ""

    def player_injuries(self):
        self.url_ext = ""

    def latest_updates(self):
        self.url_ext = ""


class save(MsfPull):

    def __init__(self):
        MsfPull.__init__(self)
        self.storage = self.config.get("storage", "location")