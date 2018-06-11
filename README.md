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

### Build on
- Requests/Mongodb : build data
- Flask/Jinja : templating
- Docker : deployment

### Install
You could either launch it from root dir :
- as docker service (with docker-compose)
- as a python environment  like this
``` bash
cd cortext-pytheas-youtube
virtualenv env3 -p python3
source ./env3/bin/activate
pip install -R requirements.txt
python main.py
```

#### Work as webapp :

**On top of this in order to get fully functionnal Pytheas you will need to get :**
- A functionnal mongodb :
  - configure it via **conf/conf.json**
- an API Key from Google :
  1. Obtain an api key from Google and activate the **YoutubeDataAPI** from [console.developers.google.com](https://console.developers.google.com/apis/api/youtube)
  2. Put api key in Pytheas (/config)
  3. Start exploration

#### Limitations
- Youtube results (api & browser) from search can only provide ~500 results (but you can get more video list by channel, playlist, arbitraty list of videos or even horodated search query)
- Automatic captions cannot be totally retrieved via API (need to trick with xml request and also with undocumented frontend Youtube API...)
- Comments gets only one sub-level

#### Good to know
- Search is list of video
- Playlist is list from video
- Author/Channel are different


#### Very basic rest implemented
- /queries/
- /queries/***query_id***
- /queries/***query_id***/videos/
- /videos/***video_id***
- /videos/***video_id***/comments/
- /comments/***comment_id***
- /captions/***caption_id***

#### Next to do
- Queuded requested videos in order to clearly separate back/front(CELERY ?)
- multiThreaded // parallele (CELERY again ?)
- continue refactoring
- Integrate api openSpec
- make captions data integrable by CORTEXT
- Continue to integrate methods
- ...
