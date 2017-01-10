import pytest
import datetime


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


def test_add_remove_params(base):
    base.config.params = {}
    base.add_params({"random": "param"})
    assert base.config.params == {"Accept-Encoding": "gzip", "random": "param"}
    base.remove_params({"Accept-Encoding": "gzip"})
    assert base.config.params == {"random": "param"}


def test_make_call(base):
    pass


def test_storage_output():
    pass


def test_save_storage():
    pass


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

