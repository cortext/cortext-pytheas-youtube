import requests
import json
import os
import datetime as dt
import dateutil.parser as time
import logging
import re
from uuid import uuid4
from xml.etree import ElementTree
from html_unescaping import unescape
# see https://github.com/jdepoix/youtube-transcript-api/blob/master/src/transcript_api.py
data_dir = 'data/'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Console handler
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
# format
formatter = logging.Formatter('%(filename)s ## [%(asctime)s] -- %(levelname)s == "%(message)s"')
stream_handler.setFormatter(formatter)
# add handler
logger.addHandler(stream_handler)


class Methods():
    ###Append Function
    def AppendCaption(EntryFile):
        data = json.load(EntryFile)
        lst = []
        print(len(data))
        for i in range(len(data)):
            text = ''
            if(data[i]['captions']):
                for j in range(len(data[i]['captions'])):
                    caption = data[i]['captions'][j]['text']
                    regex = re.search('(\[[a-zA-Z])',caption)
                    print(regex)
                    if(regex):
                        print('There is a sound or action')
                    else: 
                        text+=str(caption)
                        text+=' '
                print(text)
                results_json = {
                'query_id':data[i]['query_id'],
                'videoId':data[i]['videoId'],
                'text': text
                }
                lst.append(results_json)
                
            else:
                print('There is no captions')
        return json.dumps(lst,sort_keys=True, indent=4, separators=(',', ': '))


    def AppendTranslate(EntryFile,Lang):
        data = json.load(EntryFile)
        lst = []
        print(len(data))
        for i in range(len(data)):
            text = ''
            if(data[i]['captions']):
                for j in range(len(data[i]['captions'])):
                    caption = data[i]['captions'][j]['text']
                    regex = re.search('(\[[a-zA-Z])',caption)
                    if(regex):
                        print('There is a sound')
                    else: 
                        print(type(caption))
                        print(caption)
                        src = 'en'
                        try:
                            src = detect(caption)
                            print(src)
                        except:
                            pass
                        translator= Translator(to_lang=Lang,from_lang=src)
                        translation = translator.translate(caption)
                        print(translation)
                        text+=str(caption)
                        text+=' '
                print(text)
                results_json = {
                'query_id':data[i]['query_id'],
                'videoId':data[i]['videoId'],
                'text': text,
                'translatedText': translation
                }
                lst.append(results_json)
            
            else:
                print('There is no captions')

        return json.dump(lst,OutputFile,sort_keys=True, indent=4, separators=(',', ': '))


##########################################################################
# Youtube Data Api request
# used to make all http request to Youtube Data Api
##########################################################################
class YouTube():
    #api_key = None
    #access_token = None
    #api_base_url = 'https://www.googleapis.com/youtube/v3/'
    #part = None

    def __init__(self, api_key, access_token=None, api_url=None, part=None, type_part=None):
        self.api_key = api_key
        self.access_token = access_token
        self.api_base_url = 'https://www.googleapis.com/youtube/v3/'
        if part:
            self.part = part
        if type_part:
            self.type_part = type_part
        if api_url:
            self.api_url = api_url

    # make req
    def try_request(self, kwargs, endpoint):
        url = self.api_base_url + endpoint
        try:
            req = requests.get(url, kwargs)
            logger.info('try_request success on ' +  url)
            logger.debug('kwargs are ' + str(kwargs))
        except requests.exceptions.RequestException as e:
            logger.warning('try_request failed on ' + url)
            logger.warning('error is : ' + str(e))
        logger.debug(self.response(req))    
        return self.response(req)

    # prepare request with same obligatory param
    def get_query(self, endpoint, **kwargs):
        if self.access_token:
            kwargs['access_token'] = self.access_token
        else:
            kwargs['key'] = self.api_key
        if 'part' not in kwargs:
            kwargs['part'] = self.part
        # need integration of dynamic part choose
        # if 'type_part' in kwargs:
        #     kwargs['type'] = self.type_part
        kwargs = json.dumps(kwargs)
        kwargs = json.loads(kwargs)
        return self.try_request(kwargs, endpoint)

    def verify_error(api_key, result_query):
        if not 'error' in result_query:
            return result_query
        else:
            logger.errors('Reason of error is : ' + commentThread['error']['errors'][0]['reason'])
            return commentThread['error']

    # Unclassed for moment
    # is for clean data from Youtube
    def cleaning_each(each):
        if 'videoId' in each['id']:
            each.update({'videoId': each['id']['videoId']})
        elif 'playlistId' in each['id']:
            each.update({'playlistId': each['id']['playlistId']})
        elif 'channelId' in each['id']:
            each.update({'channelId': each['id']['channelId']})
        return each
        
    # Unclassed for moment
    def cleaning_video(id_video):
        if 'youtube.com/watch?v=' in id_video:
            if 'https' in id_video:
                id_video = id_video.replace(
                    'https://www.youtube.com/watch?v=', '')
            else:
                id_video = id_video.replace(
                    'http://www.youtube.com/watch?v=', '')
        return id_video

    # cleaning_channel is for cleaning input url from user usage
    def cleaning_channel(id_channel_or_user):
        try:
            if 'https' in id_channel_or_user:
                id_channel_or_user = id_channel_or_user.replace(
                    'https://www.youtube.com', '')
            elif 'http':
                id_channel_or_user = id_channel_or_user.replace(
                    'http://www.youtube.com', '')

            if '/channel/' in id_channel_or_user:
                id_channel_or_user = id_channel_or_user.replace(
                    '/channel/', '')

            if '/c/' in id_channel_or_user:
                id_channel_or_user = id_channel_or_user.replace(
                    '/c/', '')

            if '/user/' in id_channel_or_user:
                id_channel_or_user = id_channel_or_user.replace(
                    '/user/', '')
        except Exception as e:
            logger.debug('Unexpected error on cleaning_channel :' + str(e))

        return id_channel_or_user

    @staticmethod
    def response(response):
        return response.json()

##########################################################################
# Video
# rename in aggregate class (because of list of videos)
##########################################################################
class Video():
    # to complete
    video_fields = ['_id','videoId','query_id','kind', 'part']
    snippet_fields = ['']
    stats_fields = ['']

    def __init__(self, mongo_curs, video_id=None, query_id=None, api_key=None):
        self.db = mongo_curs.db
        if video_id:
            self.id_video = id_video
        if query_id:
            self.query_id = query_id
        if api_key:
            self.api_key = api_key
            self.api = YouTube(api_key=api_key)

    def add_stats_for_each_entry(self, query_id):
        try:        
            current_videos = self.db.videos.find({ 'query_id': query_id})
            for video in current_videos:
                id_video = video['id']
                stat_result = self.api.get_query('videos', id=id_video, part='id,statistics')
                
                logger.error(stat_result)
                logger.error(id_video)
                logger.error(query_id)

                # add new stats
                self.db.videos.update_one(
                    {   
                        '$and':
                            [{ 'videoId': id_video },
                            { 'query_id': query_id }] 
                         
                    },{ 
                        '$set': {
                            'statistics': stat_result['items'][0]['statistics']
                        }
                    }, upsert=False
                )

            # add new part
            # seems like $concat method didnt work with pymongo and update method (cf. $set)
            # have to make two call to db...
            part_value = self.db.queries.find_one_or_404({ 'query_id': query_id})
            self.db.queries.update_one(
                {
                    'query_id': query_id
                },{
                    '$set': {
                        'part': part_value['part'] + ", statistics",                             
                    } 
                }, upsert=False
            )

        except BaseException as e:
            logger.error('add_stats_for_each_entry get an error : ', str(e))
            return e
        return

    def delete():
        return