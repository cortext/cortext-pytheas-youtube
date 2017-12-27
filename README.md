# YoutubeExplorer

**Disclaimer** : _understand this is WIP_


## Intended goal
- Explore youtube from a "data point of view"
- Download requested data as a comprehensible way

### Build with
- Python
- Flask/Jinja
- Mongodb
- Docker

### Install
Launch it as docker service (with docker-compose)

##### Work as webapp :
1. Obtain an api key from Google and activate the **YoutubeDataAPI** from [console.developers.google.com](https://console.developers.google.com/apis/api/youtube)
2. Explore video/channel/playlist individualy and look for what you might be interested
3. Download them
4. Export and aggregate information (eg. comments)

#### Limitations
- Youtube results (api & browser) can only provide ~500 results
- Automatic captions cannot be retrieved via API (need to trick with xml request).
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


#### Next to do
- Queuded requested videos
- multiThreaded // parallele
- clearly separate front/back
- change framework ?
- Integrate api openSpec
