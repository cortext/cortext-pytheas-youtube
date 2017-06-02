import requests
import json
import os
import datetime as dt
import dateutil.parser as time
from pprint import pprint

data_dir = 'data/'

##########################################################################
# Youtube Data Api
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

    # make req
    def try_request(self, kwargs, endpoint):
        url = self.api_base_url + endpoint
        try:
            req = requests.get(url, kwargs)
        except requests.exceptions.RequestException as e:
            print(e)
        return self.response(req)

    # prepare request with same obligatory param
    def get_query(self, endpoint, **kwargs):
        # print('========')
        if self.access_token:
            kwargs['access_token'] = self.access_token
        else:
            kwargs['key'] = self.api_key
        if 'part' not in kwargs:
            kwargs['part'] = self.part
        kwargs = json.dumps(kwargs)
        kwargs = json.loads(kwargs)
        # print(endpoint)
        print(kwargs)
        return self.try_request(kwargs, endpoint)

    def get_search(api_key, session):
        search_results = YouTube(api_key).get_query(
            'search',
            q=session['q'],
            part=session['part'],
            language=session['language'],
            maxResults=session['maxResults'],
            ranking=session['ranking']
        )
        return search_results

    # old
    # def get_day_by_day(self, session):
    #     api_key = self.api_key
    #     # r_before = time.parse(session['publishedBefore']).isoformat()
    #     # r_after = time.parse(session['publishedAfter'])
    #     if 'nextPageToken' in session:
    #         date_results = self.get_query(
    #             'search',
    #             q=session['q'],
    #             part=session['part'],
    #             language=session['language'],
    #             maxResults=session['maxResults'],
    #             publishedAfter=session['publishedAfter'],
    #             publishedBefore=session['publishedBefore'],
    #             nextPageToken=session['nextPageToken']
    #         )
    #     else:
    #         date_results = self.get_query(
    #             'search',
    #             q=session['q'],
    #             part=session['part'],
    #             language=session['language'],
    #             maxResults=session['maxResults'],
    #             publishedAfter=session['publishedAfter'],
    #             publishedBefore=session['publishedBefore']
    #         )
    #     return date_results

    def get_channel(api_key, session):
        if 'pageToken' in session:
            channel_results = YouTube(api_key).get_query(
                'search',
                part=session['part'],
                channelId=session['id'],
                maxResults=session['maxResults'],
                pageToken=pageToken
            )
        else:
            channel_results = YouTube(api_key).get_query(
                'search',
                part=session['part'],
                channelId=session['id'],
                maxResults=session['maxResults']
            )
        return channel_results

    @staticmethod
    def response(response):
        # pprint(response)
        return response.json()



##########################################################################
# Mongo
##########################################################################
class Mongo:
    data_db = "youtube"

    def __init__(self, mongo_curs):
        data_db = self.data_db


    # old but use it like that :
    # Mongo.insert_mongo(query_id, each, mongo_curs)
    def insert_mongo(query_id, each, mongo_curs):
        if 'replies' in each:
            each['snippet'].update(
                {'replies': each['replies']}
            )
        each['snippet'].update({'query_id': query_id})
        mongo_curs.db.comments.insert_one(
            each['snippet']
        )

    # old
    def list_mongo(query_name, mongo_curs):
        print(query_name)



##########################################################################
# I/O File/dir access (PROBABLY OBSOLETE NOW)
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
