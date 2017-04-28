import requests
import json
import os
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
        print('========')
        if self.access_token:
            kwargs['access_token'] = self.access_token
        else:
            kwargs['key'] = self.api_key
        if 'part' not in kwargs:
            kwargs['part'] = self.part
        kwargs = json.dumps(kwargs)
        kwargs = json.loads(kwargs)
        print(endpoint)
        print(kwargs)
        return self.try_request(kwargs, endpoint)

    def get_search(api_key, session):
        # IF advanced
        # search_results = api.get_query(
        #     'search',
        #     q=session['request']['query'],
        #     part=session['request']['part'],
        #     language=session['request']['language'],
        #     maxResults=session['request']['maxResults'],
        #     ranking=session['request']['ranking'],
        #     publishedAfter=session['request']['st_point'],
        #     publishedBefore=session['request']['ed_point']
        # )
        search_results = YouTube(api_key).get_query(
            'search',
            q=session['q'],
            part=session['part'],
            language=session['language'],
            maxResults=session['maxResults'],
            ranking=session['ranking']
        )
        return search_results

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

    def get_day_by_day(self, session):
        api_key = self.api_key
        print('get_day_by_day')
        print('-------------')
        pprint(session)
        print('-------------')

        date_results = self.get_query(
            'search',
            part=session['part'],
            maxResults=session['maxResults'],
            publishedAfter=session['publishedAfter'],
            publishedBefore=session['publishedBefore']
        )

        import datetime as dt

        # def daterange(start_date, end_date):
        #     for n in range(int((end_date - start_date).days)):
        #         yield start_date + timedelta(n)
        #
        # start_date = date(2013, 1, 1)
        # end_date = date(2015, 6, 2)
        # for single_date in daterange(session['publishedAfter'], session['publishedBefore'],):
        #     print (single_date.strftime("%Y-%m-%d"))


        # date = datetime.datetime(2003,8,1,12,4,5)
        # for i in range(5):
        #     date += datetime.timedelta(days=1)
        #     print(type(date))
        print(session['publishedBefore'])
        print(type(session['publishedBefore']))

        print('##################')

        import dateutil.parser
        r = dateutil.parser.parse(session['publishedBefore'])
        print(r)
        # r = dt.datetime.strptime(session['publishedBefore'], '%Y-%m-%d %H:%M:%S')
        # print(r)
        #
        # d1 = dt.datetime(int(session['publishedAfter']))
        # d2 = dt.datetime(int(session['publishedBefore']))
        # delta = date(d2) - date(d1)
        # print(delta)


        pprint(date_results)
        return

    # def get_comments(self, id_video):
    #     # Get list of video from list of vid (search)
    #     return
    #
    # def get_captions(self, endpoint, **kwargs):
    #     return

    @staticmethod
    def response(response):
        pprint(response)
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

    def list_mongo(query_name, mongo_curs):
        print(query_name)

    # def update_mongo(mongo_curs):
    #     # update video-info
    #     for each in search_results['items']:
    #         each.update({'query_id': str(uid)})
    #         mongo_curs.db.videos.insert_one(each)
    #     return


##########################################################################
# Comments  OLD
##########################################################################
# class Comments:
#     def clean_and_save_comment_by_comment(path, data):
#         i = 0
#         path = './data/' + path
#
#         # Exception dont know why also (non presence of textOriginal and empty
#         # textDisplay)
#         if data['snippet']['topLevelComment'].get('textDisplay') == '':
#             return
#
#         # if ['replies'] exist iterate over all comments
#         if data.get('replies'):
#             for y in data['replies']['comments']:
#
#                 # Seems sometimes text or replies dont exist... deleted ?
#                 # Censor ? (same as before)
#                 if y['snippet'].get('textOriginal') == None:
#                     return
#
#                 # from json to alt_json
#                 alt_data = {}
#                 alt_data['id_comment'] = y['id']
#                 # add parent
#                 alt_data['id_parent'] = data['snippet']['topLevelComment']['id']
#                 alt_data['kind'] = y['kind']
#                 alt_data['videoId'] = y['snippet']['videoId']
#                 alt_data['authorChannelId'] = y['snippet']['authorChannelId']['value']
#                 alt_data['authorChannelUrl'] = y['snippet']['authorChannelUrl']
#                 alt_data['authorDisplayName'] = y['snippet']['authorDisplayName']
#                 alt_data['likeCount'] = y['snippet']['likeCount']
#                 alt_data['publishedAt'] = y['snippet']['publishedAt']
#                 alt_data['updatedAt'] = y['snippet']['updatedAt']
#                 alt_data['textDisplay'] = y['snippet']['textDisplay']
#                 alt_data['textOriginal'] = y['snippet']['textOriginal']
#
#                 # iter and save
#                 i += 1
#                 out_file = open(path + 'alt_' + str(i) + '_comment.json', 'w')
#                 json.dump(alt_data, out_file, indent=4)
#                 out_file.close()
#         else:
#             # correct errors
#             if data['snippet']['totalReplyCount'] >= 1:
#                 data['snippet']['totalReplyCount'] = 0
#
#         # same process as before but for parent comment...
#         alt_data = {}
#         alt_data['id_comment'] = data['snippet']['topLevelComment']['id']
#         alt_data['kind'] = data['snippet']['topLevelComment']['kind']
#         alt_data['videoId'] = data['snippet']['topLevelComment']['snippet']['videoId']
#         alt_data['totalReplyCount'] = data['snippet']['totalReplyCount']
#         alt_data['authorChannelId'] = data['snippet']['topLevelComment']['snippet']['authorChannelId']['value']
#         alt_data['authorChannelUrl'] = data['snippet']['topLevelComment']['snippet']['authorChannelUrl']
#         alt_data['authorDisplayName'] = data['snippet']['topLevelComment']['snippet']['authorDisplayName']
#         alt_data['likeCount'] = data['snippet']['topLevelComment']['snippet']['likeCount']
#         alt_data['publishedAt'] = data['snippet']['topLevelComment']['snippet']['publishedAt']
#         alt_data['updatedAt'] = data['snippet']['topLevelComment']['snippet']['updatedAt']
#         alt_data['textDisplay'] = data['snippet']['topLevelComment']['snippet']['textDisplay']
#         alt_data['textOriginal'] = data['snippet']['topLevelComment']['snippet']['textOriginal']
#
#         # save parent
#         i += 1
#         out_file = open(path + 'alt_' + str(i) + '_comment.json', 'w')
#         json.dump(alt_data, out_file, indent=4)
#         out_file.close()
