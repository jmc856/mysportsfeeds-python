import os
import ConfigParser
import requests
from datetime import datetime
import simplejson as json
from dateutil.parser import parse


class MsfPull:
    def __init__(self):
        config = ConfigParser.ConfigParser()
        config.read("config/config.ini")
        self.auth = (config.get("Authentication", "username"), config.get("Authentication", "password"))
        self.params = {"Accept-Encoding": "gzip", "force": "false"}
        self.storage = config.get("FileStore", "location")

        with open('config/feeds.json') as f:
            data = json.loads(f.read())
        self.api_vals = data
        self.sport = ''
        self.season = ''
        self.season_type = ''
        self.date = ''
        self.output = None
        self.output_type = ''
        self.base_url = ''
        self.url_ext = ''
        self.extension = ''

    def connection(self, output="json"):
        date = datetime.now().year
        url = "https://www.mysportsfeeds.com/api/feed/pull/nfl/{date}-regular/latest_updates.{format}&force=True".format(
                                                                                                                date=date,
                                                                                                                format=output)
        try:
            r = requests.get(url, auth=self.auth, params={})

            if r.status_code == 200:
                print "connection ok with status code: {code}".format(code=r.status_code)
            else:
                print "connection failed with status code: {code}".format(code=r.status_code)

        except requests.exceptions.RequestException as e:
            print "Failed due to error: {error}".format(error=e)


class SaveFeed(MsfPull):
    def __init__(self):
        MsfPull.__init__(self)

    def results_folder(self):
        if not os.path.isdir('results'):
            os.mkdir('results')

    def save_feed(self):
        filename = "{sport}-{feed}-{date}.{output_type}".format(sport=self.sport, feed=self.extension, date=self.date,
                                                                output_type=self.output_type)
        with open(self.storage + filename, 'w') as outfile:
            if isinstance(self.output, dict):
                json.dump(self.output, outfile)

            elif isinstance(self.output, unicode):
                outfile.write(self.output.encode("utf-8"))
            # TODO: Add if statement for saving csv output
            else:
                raise AssertionError("Could not interpret feed output format")


class BaseFeed(MsfPull, SaveFeed):
    def __init__(self):
        MsfPull.__init__(self)
        self.results_folder()

    def make_base_url(self):
        self.base_url = "https://www.mysportsfeeds.com/api/feed/pull/{sport}/{season}-{season_type}".format(sport=self.sport,
                                                                                                            season=self.season,
                                                                                                            season_type=self.season_type)
        return self.base_url

    def check_sport(self):
        sports = self.api_vals['sports']
        if self.sport.lower() not in sports:
            raise AssertionError("Apply valid sport, accepts: {}".format(", ".join(x for x in sports)))
    
    def check_date(self):
        try:
            date = parse(self.date).strftime("%Y%m%d")
        except:
            raise TypeError("Incorrect date format")

        return date

    def check_season_type(self):
        season_type = self.api_vals['season_type']
        if self.season_type.lower() not in season_type:
            raise AssertionError("Apply valid season_type, accepts: {}".format(", ".join(x for x in season_type)))

    def make_call(self, base_url, url):
        try:
            r = requests.get(base_url+url, auth=self.auth, params=self.params)
            self.status_last = r.status_code

            if r.status_code == 200:
                if self.output_type.lower() == "json":
                    self.output = r.json()
                elif self.output_type.lower() == "xml":
                    self.output = r.text
                elif self.output.lower() == "csv":
                    # TODO: add setting output for csv
                    pass
                else:
                    raise AssertionError("Requeted output type incorredt.  Check self.output_type")

                self.save_feed()

            elif r.status_code == 304:
                # Load data from stored file
                pass
            else:
                print ("API call failed with error: {error}".format(error=r.status_code))

        except requests.exceptions.RequestException as e:
            print "Failed due to error: {error}".format(error=e)

    def add_params(self, data):
        if isinstance(data, dict):
            data["Accept-Encoding"] = "gzip"  # Should always include this
            for key, value in data.items():
                self.params[key] = value
        else:
            print "Must add parameters as a dictionary"


class Feeds(BaseFeed):
    def __init__(self, sport='nhl', season=datetime.now().year, season_type='regular', date=datetime.now().strftime("%Y%m%d"), output_type="json"):
        BaseFeed.__init__(self)
        self.date = date
        self.sport = sport
        self.season = season
        self.season_type = season_type
        self.output_type = output_type
        self.add_params({"fordate": date})
        self.check_date()
        self.check_season_type()
        self.check_sport()

    def make_url(self, extension):
        self.extension = extension
        self.base_url = self.make_base_url()
        self.url_ext = '/' + extension + '.' + self.output_type

    def cum_player_stats(self):
        self.make_url('cumulative_player_stats')
        self.make_call(self.base_url, self.url_ext)

    def full_game_schd(self):
        self.make_url('full_game_schedule')
        self.make_call(self.base_url, self.url_ext)

    def daily_game_schedule(self):
        self.make_url('daily_game_schedule')
        self.make_call(self.base_url, self.url_ext)

    def daily_player_stats(self, player_stats="none"):
        self.add_params({"playerstats": player_stats})
        self.make_url('daily_player_stats')
        self.make_call(self.base_url, self.url_ext)

    def scoreboard(self):
        self.make_url('scoreboard')
        self.make_call(self.base_url, self.url_ext)

    def play_by_play(self, hometeam, awayteam, player_stats="none", team_stats="none"):
        self.add_params({"playerstats": player_stats,
                         "teamstats": team_stats,
                         "game-id": "{date}-{away}-{home}".format(date=self.date, away=awayteam, home=hometeam)
                         })
        self.make_url('game_playbyplay')
        self.make_call(self.base_url, self.url_ext)

    def boxscore(self, hometeam, awayteam, player_stats="none", team_stats="none"):
        self.add_params({"playerstats": player_stats,
                         "teamstats": team_stats,
                         "game-id": "{date}-{away}-{home}".format(date=self.date, away=awayteam, home=hometeam)
                         })
        self.make_url('game_boxscore')
        self.make_call(self.base_url, self.url_ext)

    def roster(self):
        self.make_url('roster_players')
        self.make_call(self.base_url, self.url_ext)

    def active(self):
        self.make_url('active_players')
        self.make_call(self.base_url, self.url_ext)

    def overall_standings(self, team_stats="none"):
        self.add_params({"teamstats": team_stats})
        self.make_url('overall_team_standings')
        self.make_call(self.base_url, self.url_ext)

    def conf_standings(self, team_stats="none"):
        self.add_params({"teamstats": team_stats})
        self.make_url('conference_team_standings')
        self.make_call(self.base_url, self.url_ext)

    def division_standings(self, team_stats="none"):
        self.add_params({"teamstats": team_stats})
        self.make_url('division_team_standings')
        self.make_call(self.base_url, self.url_ext)

    def playoff_standings(self, team_stats="none"):
        self.add_params({"teamstats": team_stats})
        self.make_url('playoff_team_standings')
        self.make_call(self.base_url, self.url_ext)

    def player_injuries(self):
        self.make_url('player_injuries')
        self.make_call(self.base_url, self.url_ext)

    def latest_updates(self):
        self.make_url('latest_updates')
        self.make_call(self.base_url, self.url_ext)
