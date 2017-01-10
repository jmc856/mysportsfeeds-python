# MySportsFeeds Wrapper - Python
![alt](https://pbs.twimg.com/profile_images/779390458892001280/aFHAsc24.jpg)

#####Python wrapper for MySportsFeeds API
##Instructions

Clone repo
    
    $ git clone https://github.com/jmc856/mysportsfeeds-python.git

Set API credentials 

    $ cd mysportsfeeds-python
    $ nano config/config.ini
    
If you haven't signed up for API access, do so here [https://www.mysportsfeeds.com/index.php/register/](https://www.mysportsfeeds.com/index.php/register/)
    
Change `config.ini` to include your username & login from MySportsFeeds.com 
 
    [Authentication]
    username: <your_username>
    password: <your_password>

Set storage location of API feeds (default is `results/`)

    [FileStore]
    location <your results location>
    
Install requirements and run tests

    $ make build

##Usage

Create configuration object with API version as input parameter

    config = MsfLib(version="1.0")

Test connection at any time with:

    config.test_connection()

Create storage method

    storage = FeedStorageMethod(config)

Create a feed 	

    feed = Feed(config, sport="nhl", season="current", season_type="regular", date=datetime.now().strftime("%Y%m%d"), output_type="json")
 
 Note: For default params, the season/sport/season_type will not always correctly align to a working feed.  Although, `season="current"` or `season="latest"`**should** always pull a working feed.
    
    feed.set_store(storage)


This will temporarily store results in feed.store.output.  Depending on storage parameters selected, the data may be stored in `<your results location>`.