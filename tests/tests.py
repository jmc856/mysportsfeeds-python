import pytest
import datetime
import simplejson as json
from api import MsfLib, Feed


def test_versions():
    with open("config/api_version_params.json") as f:
        data = json.loads(f.read())
        for version in data.keys():
            assert MsfLib(version)

    with pytest.raises(KeyError):
        MsfLib("0.1")


def test_auth(config):
    assert config.auth is not None
    assert config.params is not None
    assert config.store_location is not None


def test_connection(config):
    config.test_connection()

    with pytest.raises(Warning):
        config.auth = ("fake", "credentials")
        config.test_connection()


def test_make_baseurl1(base):
    base.season = "2012-2013"
    base.sport = "nfl"
    base.season_type = "regular"
    assert base.make_base_url() == "https://www.mysportsfeeds.com/api/feed/pull/nfl/2012-2013-regular"


def test_make_baseurl2(base):
    base.season = "latest"
    base.sport = "mlb"
    base.season_type = "regular"
    assert base.make_base_url() == "https://www.mysportsfeeds.com/api/feed/pull/mlb/latest"


def test_make_output_file_name(config):
    feed = Feed(config, sport="NBA", season="current", season_type="regular", date="20150101", output_type="csv")
    feed.make_url("daily_game_schedule")
    player_stats = None
    team_stats = None
    awayteam = "ATL"
    hometeam = "PHL"
    feed.add_params({"playerstats": player_stats,
                     "teamstats": team_stats,
                     "gameid": "{date}-{away}-{home}".format(date=feed.config.params["fordate"], away=awayteam, home=hometeam)
                     })

    assert feed.make_output_filename() == "nba-daily_game_schedule-20150101-current-20150101-atl-phl.csv"


def test_add_remove_params(base):
    base.add_params({"random": "param"})
    assert base.config.params == {"accept-encoding": "gzip", "force": "false", "random": "param", }
    base.remove_params({"accept-encoding": "gzip"})
    assert base.config.params == {"force": "false", "random": "param"}
    base.toggle_force()
    assert base.config.params == {"force": "true", "random": "param"}


def test_parse_season_type(base):
    assert base.parse_season_type(season="LatesT", season_type="should not matter") == "latest"
    assert base.parse_season_type(season="2014", season_type="regular") == "2014-regular"
    assert base.parse_season_type(season="2015-2016", season_type="plaYoffs") == "2015-2016-playoffs"


def test_date_check(base):
    base.season = "2011-2012"
    base.check_season()

    with pytest.raises(AttributeError):
        base.season = "2014-2013"
        base.check_season()

    with pytest.raises(AttributeError):
        base.season = "guzz-2015"
        base.check_season()

    with pytest.raises(AttributeError):
        date1 = str(datetime.now().year + 1)
        date2 = str(datetime.now().year + 2)
        base.season = "{date1}-{date2}".format(date1=date1, date2=date2)
        base.check_season()


def test_check_sport(base):
    base.sport = "nbA"
    base.check_sport()

    with pytest.raises(AttributeError):
        base.sport = "not a sport"
        base.check_sport()


def test_check_season_type(base):
    base.season_type = "reGuLar"
    base.check_season_type()

    with pytest.raises(AttributeError):
        base.season_type = "playoffs"
        base.check_season_type()


def test_make_call(base):
    pass


def test_storage_output():
    pass


def test_save_storage():
    pass

#TODO: Add tests for storing and loading from storage