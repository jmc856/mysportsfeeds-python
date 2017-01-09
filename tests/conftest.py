import pytest
from api import MsfLib, BaseFeed, Feed


@pytest.fixture(scope="module")
def config():
    return MsfLib(version="1.0")


@pytest.fixture(scope="module")
def base():
    config = MsfLib(version="1.0")
    base_ = BaseFeed()
    base_.config = config
    return base_


@pytest.fixture(scope="module")
def feed():
    config = MsfLib(version="1.0")
    feed_ = Feed(config)
    return feed_
