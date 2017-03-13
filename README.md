# YoutubeExplorer

**Disclaimer** : _understand this is WIP.

## Intended goal
- Explore youtube from a "data point of view"
- Download requested data as a comprehensible way

### Build with
- Python
- Flask/Jinja
- Mongodb

### Install

Copy/paste instructions on linux with python3 installed :

    git clone https://github.com/cortext/youtube-explorer.git

    virutalenv -p /usr/bin/python3 env

    source bin/activate/env

    pip -r install requirements.txt

    python main.py

##### Work as webapp :
1. Obtain an api key from Google and activate the **YoutubeDataAPI** from [console.developers.google.com](https://console.developers.google.com/apis/api/youtube)
2. Explore video info individualy and look for what you might be interested
3. Unzoom and request a query as a list of vidéo
4. Export and aggregate information

#### Limitations
- Youtube results (api & browser) can only provide ~500 results
- Automatic captions cannot be retrieved via API.
- Response from comments included as 'replies' if existing
- for moment response aer simultaneusly saved as file and MongoDb

#### Good to know
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
- Adding day/day querying methods
- Enhanced db methods (notably access, insert, erase, manage more manageable)
- Integrate api openSpec
- Improve, optimize and reduce code
