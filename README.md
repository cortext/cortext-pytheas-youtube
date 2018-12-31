# YoutubeExplorer

**Disclaimer** : _understand this is WIP_


## Intended goal
- Explore youtube from a "data point of view"
- Download requested data as a comprehensible way
- Make data analyzable by CORTEXT platform

## Feature
- Explore video and videos from query, playlist or channel
- Get Comments, captions and metrics from video list
- Download data as JSON

## Build on
- Requests/Mongodb : build data
- Flask/Jinja : front/back
- Docker : deployment

## Install

You can use Docker for an agnostic deployment (it will need a well installed Docker) or launch it diretcly with Python (but will need to get all requirements : Python3, Mongodb)

- ***docker service (with docker-compose)*** :
``` bash
docker-compose up 
```
Then after all is correctly built and verifying it's running stop it for :
``` bash
docker-compose start
```
- ***python environment*** :

For this variant please be sure 
``` bash
cd cortext-pytheas-youtube
virtualenv env3 -p python3
source ./env3/bin/activate
```
Then from two terminal and for each ./main.py and rest/rest.py (since new branch Rest has his own app):
``` bash
pip install -R requirements.txt
python main.py
```

### Other requirements :
#### Configuration files 

- Capitalized keys are required to work
- lower case for debug purpose

**conf/conf.json**
``` json
{
    "DATA_DIR": "data/",
    "PORT": 8080,
    "REDIRECT_URI": "http://localhost:8080/auth",
    "GRANT_HOST_URL": "https://auth.cortext.net",
    
    "MONGO_HOST": "mongo",
    "MONGO_DBNAME": "youtube",
    "MONGO_PORT": 27017,
    
    "REST_HOST": "rest",
    "REST_PORT": 5002,
    
    "api_key": "",
    "oauth_status": "True",
    "debug_level": "False"
}
```

**rest/conf/conf.json**
``` json
{
    "LOG_DIR": "log/",
    "PORT": 5002,
    "MONGO_HOST": "localhost",
    "MONGO_DBNAME": "youtube",
    "MONGO_PORT": 27017
}
```

#### API Key from Google :
  1. Obtain an api key from Google and activate the **YoutubeDataAPI** from [console.developers.google.com](https://console.developers.google.com/apis/api/youtube)
  2. Put api key in Pytheas web interface or in persistant inside config file
  3. Start exploration


## Limitations
- Youtube results (api & browser) from search can only provide ~500 results (but you can get more video list by channel, playlist, arbitraty list of videos or even horodated search query)
- Automatic captions cannot be totally retrieved via API (need to trick with xml request and also with undocumented frontend Youtube API...)
- Comments gets only one sub-level

## Good to know
- Search is list of video
- Playlist is list from video
- Author/Channel are different

## Very basic rest implemented
- /queries/
- /queries/***query_id***
- /queries/***query_id***/videos/
- /videos/***video_id***
- /videos/***video_id***/comments/
- /comments/***comment_id***
- /captions/***caption_id***


## Next to do
- multiThreaded // parallele // queuding (CELERY again ?)
- continue refactoring : meaning dynamic and self function
- integrate errorhandler directly from flask
- Integrate api openSpec
- Continue to integrate methods (see about network of reccommandation mainly)
- ...
