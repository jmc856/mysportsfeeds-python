# msf_wrapper
Python wrapper for MySportsFeed API

####Instructions
Set API credentials in `config/config.ini`

    [Authentication]
    username: your_username
    password: your_password

Create configuration object. 

`config = MsfLib(version="1.0")`

Test connection

`config.test_connection()`

Create storage method

`storage = FeedStorageMethod(config)`

Create a feed 	

    feed = Feed(config, sport="nhl", season=datetime.now().year, season_type="regular", date=datetime.now().strftime("%Y%m%d"), output_type="json")
    feed.set_store(storage)
Note: For default params, the season/sport/season_type will not always correctly align to a working feed.

Call a method to pull in data

    feed.daily_game_schedule()
This will temporarily store results in feed.store.output.  Depending on storage parameters selected, the data might be stored elsewhere.


