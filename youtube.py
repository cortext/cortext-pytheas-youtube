import requests
import json
import os


data_dir = 'data/'

##########################################################################
# Youtube Data Api
# freely inspirated from github.com/rhayun/python-youtube-api
##########################################################################
class YouTube:
    api_key = None
    access_token = None
    api_base_url = 'https://www.googleapis.com/youtube/v3/'
    part = None

    def __init__(self, api_key, access_token=None, api_url=None):
        self.api_key = api_key
        self.access_token = access_token
        if api_url:
            self.api_url = api_url

    def get_search(self, endpoint, **kwargs):
        if self.access_token:
            kwargs['access_token'] = self.access_token
        else:
            kwargs['key'] = self.api_key
        if 'part' not in kwargs:
            kwargs['part'] = self.part
        kwargs = json.dumps(kwargs)
        kwargs = json.loads(kwargs)
        url = self.api_base_url + endpoint
        print(endpoint)
        print(kwargs)
        try:
            req = requests.get(url, kwargs)
        except requests.exceptions.RequestException as e:
            print(e)
        return self.response(req)

    def get_search_by_date(self, endpoint, **kwargs):
        return self.response(req)

    def get_comments(self, id_video):
        # Get list of video from list of vid (search)
        return

    def get_captions(self, endpoint, **kwargs):
        return

    @staticmethod
    def response(response):
        return response.json()

##########################################################################
# I/O File/dir access
##########################################################################
class FileData:

    def create_dir(path_query):
        # data_dir = 'data/'
        complete_path = data_dir + path_query
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            if not os.path.exists(complete_path):
                os.makedirs(complete_path)
        else:
            if not os.path.exists(complete_path):
                os.makedirs(complete_path)
        return

    def list_file(path):
        items_videoId = []
        items_playlist = []
        for json_file in os.listdir(path):
            if any(word in json_file for word in ['comments', 'captions', 'meta_info.txt']):
                continue
            path_file = path + '/' + json_file
        items_videoId = []
        with open(path_file, 'r') as json_data:
            search_data = json.load(json_data)
            for item in search_data:
                if not 'video_result' in search_data:
                    if 'videoId' in item['id']:
                        id_video = item['id']['videoId']
                        items_videoId.append(id_video)
                    elif 'playlistId'in item['id']:
                        id_playlist = item['id']['playlistId']
                        items_playlist.append(id_playlist)

        return {'items_videoId': items_videoId,
                'items_playlist': items_playlist}

    def save_json(path_file, data):
        # data_dir = self.data_dir
        data_dir = 'data/'
        with open(data_dir + path_file, 'w') as outfile:
            json.dump(data, outfile)
        return

##########################################################################
# Mongo
##########################################################################
class Mongo:
    data_db = "youtube"
    def __init__(self, mongo_curs):
        data_db = self.data_db

    def insert_mongo(query_name, each, mongo_curs):
        if 'replies' in each:
            each['snippet'].update(
                {'replies': each['replies']}
            )
        each['snippet'].update({'query_name': query_name})
        mongo_curs.db.comments.insert_one(
            each['snippet']
        )

    # def update_mongo(mongo_curs):
    #     # update video-info
    #     for each in search_results['items']:
    #         each.update({'query_id': str(uid)})
    #         mongo_curs.db.videos.insert_one(each)
    #     return



##########################################################################
# Comments
##########################################################################
class Comments:
    def clean_and_save_comment_by_comment(path, data):
        i = 0
        path = './data/' + path

        # Exception dont know why also (non presence of textOriginal and empty textDisplay)
        if data['snippet']['topLevelComment'].get('textDisplay') == '':
            return

        # if ['replies'] exist iterate over all comments
        if data.get('replies'):
            for y in data['replies']['comments']:

                # Seems sometimes text or replies dont exist... deleted ? Censor ? (same as before)
                if y['snippet'].get('textOriginal') == None:
                    return

                # from json to alt_json
                alt_data = {}
                alt_data['id_comment'] = y['id']
                # add parent
                alt_data['id_parent'] = data['snippet']['topLevelComment']['id']
                alt_data['kind'] = y['kind']
                alt_data['videoId'] = y['snippet']['videoId']
                alt_data['authorChannelId'] = y['snippet']['authorChannelId']['value']
                alt_data['authorChannelUrl'] = y['snippet']['authorChannelUrl']
                alt_data['authorDisplayName'] = y['snippet']['authorDisplayName']
                alt_data['likeCount'] = y['snippet']['likeCount']
                alt_data['publishedAt'] = y['snippet']['publishedAt']
                alt_data['updatedAt'] = y['snippet']['updatedAt']
                alt_data['textDisplay'] = y['snippet']['textDisplay']
                alt_data['textOriginal'] = y['snippet']['textOriginal']

                # iter and save
                i += 1
                out_file = open(path + 'alt_' + str(i) + '_comment.json', 'w')
                json.dump(alt_data,out_file, indent=4)
                out_file.close()
        else:
            # correct errors
            if data['snippet']['totalReplyCount'] >= 1:
                data['snippet']['totalReplyCount'] = 0

        # same process as before but for parent comment...
        alt_data = {}
        alt_data['id_comment'] = data['snippet']['topLevelComment']['id']
        alt_data['kind'] = data['snippet']['topLevelComment']['kind']
        alt_data['videoId'] = data['snippet']['topLevelComment']['snippet']['videoId']
        alt_data['totalReplyCount'] = data['snippet']['totalReplyCount']
        alt_data['authorChannelId'] = data['snippet']['topLevelComment']['snippet']['authorChannelId']['value']
        alt_data['authorChannelUrl'] = data['snippet']['topLevelComment']['snippet']['authorChannelUrl']
        alt_data['authorDisplayName'] = data['snippet']['topLevelComment']['snippet']['authorDisplayName']
        alt_data['likeCount'] = data['snippet']['topLevelComment']['snippet']['likeCount']
        alt_data['publishedAt'] = data['snippet']['topLevelComment']['snippet']['publishedAt']
        alt_data['updatedAt'] = data['snippet']['topLevelComment']['snippet']['updatedAt']
        alt_data['textDisplay'] = data['snippet']['topLevelComment']['snippet']['textDisplay']
        alt_data['textOriginal'] = data['snippet']['topLevelComment']['snippet']['textOriginal']

        #save parent
        i += 1
        out_file = open(path + 'alt_' + str(i) + '_comment.json', 'w')
        json.dump(alt_data,out_file, indent=4)
        out_file.close()
