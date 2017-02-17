import requests
import json
import os
# from bson import ObjectId





# this class is freely inspirated from github.com/rhayun/python-youtube-api
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
        url = self.api_base_url+endpoint
        # print(kwargs)
        try:
            req = requests.get(url, kwargs)
        except requests.exceptions.RequestException as e:
            print(e)
        return self.response(req)


    def get_comments(self, id_video):
        # Get list of video from list of vid (search)


        # print(len(items_videoId))
        ###################################
        # if 'comments' in options_api:
        #     path_comments = path_dir + '/comments/'
        #     if not os.path.exists(path_comments):
        #         os.makedirs(path_comments)
        #     print(path_comments)
        #     i = 0
        #     # for each video loop to comments
        #     for id_video in items_videoId:
        #         commentThreads_result = api.get_search(
        #             'commentThreads',
        #             videoId=id_video,
        #             part='id, replies, snippet'
        #         )
        #         # Check if error (eg unactivated comments)
        #         if 'error' in commentThreads_result:
        #             disabled_comments = commentThreads_result['error']['errors'][0]['reason']
        #             if 'commentsDisabled' in disabled_comments:
        #                 continue
        #         # get OneByOne commentThreads & save json
        #         for key, val in commentThreads_result.items():
        #             if key == 'items':
        #                 for item in val:
        #                     with open(path_comments + str(i) + '_commentThread.json', 'w') as td:
        #                         json.dump(item, td)
        #                         i += 1
        #         # Loop and save
        #         while 'nextPageToken' in commentThreads_result:
        #             commentThreads_result = api.get_search(
        #                 'commentThreads',
        #                 videoId=id_video,
        #                 part='id, replies, snippet',
        #                 pageToken=commentThreads_result['nextPageToken']
        #             )
        #             for key, val in commentThreads_result.items():
        #                 if key == 'items':
        #                     for item in val:
        #                         with open(path_comments + str(i) + '_commentThread.json', 'w') as td:
        #                             json.dump(item, td)
        #                             i += 1
        return

        #/* Alternative approach with new built in paginateResults function */
        #
        # // Same Params as before
        # params = {
        #     'q': 'Android',
        #     'type': 'video',
        #     'part': 'id, snippet',
        #     'maxResults': 50
        # }
        #
        # // an array to store page tokens so we can go back and forth
        # page_tokens = {}
        #
        # // make inital search
        # search = youtube.paginate_results(params, None)
        #
        # // store token
        # page_tokens.append(search['info']['nextPageToken'])
        #
        # // go to next page in result
        # search = youtube.paginate_results(params, page_tokens[0])
        #
        # // store token
        # pageTokens.append(search['info']['nextPageToken'])
        #
        # // go to next page in result
        # search = youtube.paginate_results(params, page_tokens[1])
        #
        # // store token
        # pageTokens.append(search['info']['nextPageToken'])
        #
        # // go back a page
        # search = youtube.paginate_results(params, page_tokens[0])
        #
        # // add results key with info parameter set
        # print search['results']

    def get_captions(self, endpoint, **kwargs):
        return

    @staticmethod
    def response(response):
        return response.json()


class IO:
    data_dir = "data/"

    def __init__(self):
        data_dir = self.data_dir

    def create_dir(self, path_query):
        data_dir = self.data_dir
        complete_path = data_dir + path_query
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            if not os.path.exists(complete_path):
                os.makedirs(complete_path)
        else:
            if not os.path.exists(complete_path):
                os.makedirs(complete_path)
        return


    def save_json(self, path_file, data):
        data_dir = self.data_dir
        with open(data_dir + path_file, 'w') as outfile:
            json.dump(data, outfile)
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
                if not 'video_result' in search_data :
                    if 'videoId' in item['id']:
                        id_video = item['id']['videoId']
                        items_videoId.append(id_video)
                    elif 'playlistId'in item['id']:
                        id_playlist = item['id']['playlistId']
                        items_playlist.append(id_playlist)

        return {'items_videoId'  : items_videoId,
                'items_playlist' : items_playlist}

    def process(path):
        return


class Mongo:
    data_db = "youtube"

    def __init__(self):
        data_db = self.data_db

    def insert_mongo():
        # insert video-info
        for each in search_results['items']:
            each.update({'query_id' : str(uid)})
            ytb_db.videos.insert_one(each)
        return

    def update_mongo():
        # update video-info
        for each in search_results['items']:
            each.update({'query_id' : str(uid)})
            ytb_db.videos.insert_one(each)
        return





# class JSONEncoder(json.JSONEncoder):
#     def default(self, o):
#         if isinstance(o, ObjectId):
#             return str(o)
#         return json.JSONEncoder.default(self, o)
# JSONEncoder().encode(analytics)
