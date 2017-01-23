import os
import csv
import ConfigParser
import requests
from datetime import datetime
import simplejson as json
from dateutil.parser import parse


class MsfLib:
    def __init__(self, version):
        config = ConfigParser.ConfigParser()
        config.read("config/config.ini")
        self.auth = (config.get("Authentication", "username"), config.get("Authentication", "password"))
        self.params = {"accept-encoding": "gzip", "force": "false"}
        self.store_location = config.get("FileStore", "location")

        with open("config/api_version_params.json") as f:
            data = json.loads(f.read())
            if version in data.keys():
                self.version = version
                self.version_inputs = data[version]
            else:
                raise KeyError("This version is not supported.  Supported version: {}".format(", ".join(x for x in data.keys())))

    def test_connection(self, output="json"):
        sports = self.version_inputs["sports"]
        try:
            for sport in sports:
                url = "https://www.mysportsfeeds.com/api/feed/pull/{sport}/latest/latest_updates.{format}&force=True".format(
                                                                                                                    sport=sport,
                                                                                                                    format=output)
                r = requests.get(url, auth=self.auth, params={})

                if r.status_code == 200:
                    print "connection ok with status code: {code}".format(code=r.status_code)
                    return

            raise Warning("connection failed with status code: {code}".format(code=r.status_code))

        except requests.exceptions.RequestException as e:
            raise Warning("Failed due to error: {error}".format(error=e))


class FeedStorageMethod:
    def __init__(self, config, method="standard"):
        self.location = config.store_location
        self.output = None

        version_inputs = config.version_inputs

        if method not in version_inputs["storage"]:
            raise AssertionError("Could not interpret feed output format")
        self.method = method


class BaseFeed:
    def __init__(self, config=None, storage=None):
        self.sport = ""
        self.season = ""
        self.season_type = ""
        self.output_type = ""
        self.base_url = ""
        self.url_ext = ""
        self.extension = ""
        self.date = ""
        self.store = storage
        self.config = config

    def make_base_url(self):
        season = self.parse_season_type(self.season, self.season_type)
        self.base_url = "https://www.mysportsfeeds.com/api/feed/pull/{sport}/{season}".format(sport=self.sport,
                                                                                              season=season)
        return self.base_url

    def parse_season_type(self, season, season_type):
        if season.lower() not in self.config.version_inputs["season_type_generic"]:
            season = "{year}-{type}".format(year=season, type=season_type)

        return season.lower()

    @staticmethod
    def check_date(date):
        try:
            date = parse(date).strftime("%Y%m%d")
        except:
            raise TypeError("Incorrect date format")

        return date

    def check_season(self):
        raise_error = True
        if self.season in self.config.version_inputs["season_type_generic"]:
            raise_error = False
        try:
            year = int(self.season)
            if year <= datetime.now().year:
                raise_error = False

        except ValueError:
            years = self.season.split("-")
            if len(years) == 2:
                try:
                    year1 = int(years[0])
                    year2 = int(years[1])
                    if year2 - year1 == 1:
                        raise_error = False
                except ValueError:
                    pass

        if raise_error:
            raise AttributeError("Incorrect format for season parameter")

    def check_season_type(self):
        season_type = self.config.version_inputs["season_type"]
        if self.season_type.lower() not in season_type:
            raise AttributeError("Apply valid season_type, accepts: {}".format(", ".join(x for x in season_type)))

    def check_sport(self):
        sports = self.config.version_inputs["sports"]
        if self.sport.lower() not in sports:
            raise AttributeError("Apply valid sport, accepts: {}".format(", ".join(x for x in sports)))

    def make_output_filename(self):
        season = self.parse_season_type(self.season, self.season_type)

        s = ""
        for param in self.config.version_inputs["optional_params"]:
            if self.config.params.get(param):
                s += "-" + str(self.config.params.get(param))

        filename = "{sport}-{feed}-{date}-{season}{s}.{output_type}".format(sport=self.sport.lower(), feed=self.extension,
                                                                            date=self.config.params["fordate"],
                                                                            season=season, s=s,
                                                                            output_type=self.output_type)
        return filename

    def make_call(self, base_url, url):
        try:
            r = requests.get(base_url+url, auth=self.config.auth, params=self.config.params)
            self.status_last = r.status_code

            if r.status_code == 200:
                if not self.store:
                    raise AssertionError("You need to set feed store method.  Use feed.set_store()")
                self.save_feed(r)

            elif r.status_code == 304:
                print "Data has not changed since last call"
                filename = self.make_output_filename()

                with open(self.store.location + filename) as f:
                    if self.output_type == "json":
                        data = json.load(f)
                    elif self.output_type == "xml":
                        data = str(f.readlines()[0])
                    else:
                        data = f.read().splitlines()

                self.store.output = data

            else:
                raise Warning("API call failed with error: {error}".format(error=r.status_code))

        except requests.exceptions.RequestException as e:
            raise Warning("Failed due to error: {error}".format(error=e))

    def save_feed(self, response):
        # Save to memory regardless of selected method
        if self.output_type.lower() == "json":
            self.store.output = response.json()
        elif self.output_type.lower() == "xml":
            self.store.output = response.text
        elif self.output_type.lower() == "csv":
            self.store.output = response.content.split('\n')
        else:
                raise AssertionError("Requested output type incorrect.  Check self.output_type")

        if self.store.method == "standard":
            if not os.path.isdir("results"):
                os.mkdir("results")

            filename = self.make_output_filename()

            with open(self.store.location + filename, "w") as outfile:
                if isinstance(self.store.output, dict):  # This is JSON
                    json.dump(self.store.output, outfile)

                elif isinstance(self.store.output, unicode):  # This is xml
                    outfile.write(self.store.output.encode("u tf-8"))

                elif isinstance(self.store.output, list):  # This is csv
                    writer = csv.writer(outfile)
                    for row in self.store.output:
                        writer.writerow([row])

                else:
                    raise AssertionError("Could not interpret feed output format")

        elif self.store.method == "memory":
            pass  # Data already stored in store.output

        else:
            pass

    def add_params(self, data):
        if isinstance(data, dict):
            for key, value in data.items():
                if data.get(key):
                    self.config.params[key.lower()] = value.lower()
        else:
            raise TypeError("Must add parameters as a dictionary")

    def remove_params(self, data):
        for param in data:
            self.config.params.pop(param, None)

    def toggle_force(self):
        if self.config.params['force'] == 'false':
            self.config.params['force'] = 'true'
        else:
            self.config.params['force'] = 'false'

        return self.config.params['force']


class Feed(BaseFeed):
    def __init__(self, config=MsfLib("1.0"), sport="nhl", season="current", season_type="regular", date=datetime.now().strftime("%Y%m%d"), output_type="json"):
        BaseFeed.__init__(self)
        self.config = config
        self.sport = sport.lower()
        self.season = season.lower()
        self.season_type = season_type.lower()
        self.output_type = output_type.lower()
        self.date = self.check_date(date)
        self.add_params({"fordate": self.date})
        self.check_season()
        self.check_season_type()
        self.check_sport()

    def set_store(self, feed_storage_method):
        self.store = feed_storage_method

    def make_url(self, extension):
        self.extension = extension
        self.base_url = self.make_base_url()
        self.url_ext = "/" + extension + "." + self.output_type

    def cum_player_stats(self):
        self.make_url("cumulative_player_stats")
        self.make_call(self.base_url, self.url_ext)

    def full_game_schedule(self):
        self.remove_params(["fordate"])
        self.make_url("full_game_schedule")
        self.make_call(self.base_url, self.url_ext)
        self.add_params({"fordate": self.date})

    def daily_game_schedule(self):
        self.make_url("daily_game_schedule")
        self.make_call(self.base_url, self.url_ext)

    def daily_player_stats(self, player_stats=None):
        self.add_params({"playerstats": player_stats})
        self.make_url("daily_player_stats")
        self.make_call(self.base_url, self.url_ext)

    def scoreboard(self):
        self.make_url("scoreboard")
        self.make_call(self.base_url, self.url_ext)

    def play_by_play(self, hometeam, awayteam, player_stats=None, team_stats=None):
        self.add_params({
            "playerstats": player_stats,
            "teamstats": team_stats,
            "gameid": "{date}-{away}-{home}".format(date=self.config.params["fordate"], away=awayteam, home=hometeam)
        })
        self.make_url("game_playbyplay")
        self.make_call(self.base_url, self.url_ext)

    def boxscore(self, hometeam, awayteam, player_stats=None, team_stats=None):
        self.add_params({
            "playerstats": player_stats,
            "teamstats": team_stats,
            "gameid": "{date}-{away}-{home}".format(date=self.config.params["fordate"], away=awayteam, home=hometeam)
            })
        self.make_url("game_boxscore")
        self.make_call(self.base_url, self.url_ext)

    def roster(self):
        self.make_url("roster_players")
        self.make_call(self.base_url, self.url_ext)

    def active(self):
        self.make_url("active_players")
        self.make_call(self.base_url, self.url_ext)

    def overall_standings(self, team_stats=None):
        self.add_params({"teamstats": team_stats})
        self.make_url("overall_team_standings")
        self.make_call(self.base_url, self.url_ext)

    def conf_standings(self, team_stats=None):
        self.add_params({"teamstats": team_stats})
        self.make_url("conference_team_standings")
        self.make_call(self.base_url, self.url_ext)

    def division_standings(self, team_stats=None):
        self.add_params({"teamstats": team_stats})
        self.make_url("division_team_standings")
        self.make_call(self.base_url, self.url_ext)

    def playoff_standings(self, team_stats=None):
        self.add_params({"teamstats": team_stats})
        self.make_url("playoff_team_standings")
        self.make_call(self.base_url, self.url_ext)

    def player_injuries(self):
        self.make_url("player_injuries")
        self.make_call(self.base_url, self.url_ext)

    def latest_updates(self):
        self.make_url("latest_updates")
        self.make_call(self.base_url, self.url_ext)
