# YoutubeExplorer

**Disclaimer** : _understand this is WIP.

## Intended goal

- Explore youtube from a "data point of view"
- Download requested data as a comprehensible way

### How ?

Work as webapp on python, flask, request, mongodb :
1. Obtain an api key from Google and activate the **YoutubeDataAPI** from [console.developers.google.com](https://console.developers.google.com/apis/api/youtube)
2. Explore video info individualy and look for what you might be interested
3. Unzoom and request a query as a list of vidéo
4. Export and aggregate information

#### Limitations
- Youtube results (api & browser) can only provide ~500 results
- Automatic captions seems to cannot be retrieve via API.
- Response from comments included as 'replies' if existing
- Playlist is different from video

#### Working functionnality
- Request individual video
- Request and download youtube query
- Enhanced data with captions download (if explicitly existing)
- Enhanced data with comments (including responses to comment) download

#### Next to do
- Restfull (at least basics)
- Improve, optimize and reduce code
- Enhanced db methods
- Integrate api openSpec
- ...
