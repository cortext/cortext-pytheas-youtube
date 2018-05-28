import requests
import json
import os
import datetime as dt
import dateutil.parser as time
from pprint import pprint
from uuid import uuid4

data_dir = 'data/'

# from https://github.com/jdepoix/youtube-transcript-api/blob/master/src/transcript_api.py
from xml.etree import ElementTree
import re
import logging
import requests
from html_unescaping import unescape
logger = logging.getLogger(__name__)


##########################################################################
# Youtube Data Api request
##########################################################################
class YouTube():
    #api_key = None
    #access_token = None
    #api_base_url = 'https://www.googleapis.com/youtube/v3/'
    #part = None

    def __init__(self, api_key, access_token=None, part=None,api_url=None):
        self.api_key = api_key
        self.access_token = access_token
        self.api_base_url = 'https://www.googleapis.com/youtube/v3/'
        if part:
            self.part = part
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
        if self.access_token:
            kwargs['access_token'] = self.access_token
        else:
            kwargs['key'] = self.api_key
        if 'part' not in kwargs:
            kwargs['part'] = self.part
        kwargs = json.dumps(kwargs)
        kwargs = json.loads(kwargs)
        return self.try_request(kwargs, endpoint)

    def get_search(api_key, session):
        search_results = YouTube(api_key).get_query(
            'search',
            q=session['q'],
            part=session['part'],
            relevanceLanguage=session['language'],
            maxResults=session['maxResults'],
            ranking=session['ranking']
        )
        return search_results

    def get_channel(api_key, session):
        channel_results = YouTube(api_key).get_query(
            'search',
            channelId=session['channelId'],
            part=session['part'],
            maxResults=session['maxResults']
        )
        return channel_results

    def verify_error(api_key, result_query):
        if not 'error' in result_query:
            return result_query
        else:
            print('Reason of error is : ' + commentThread['error']['errors'][0]['reason'])
            return commentThread['error']

    @staticmethod
    def response(response):
        # print('RES = ')
        # pprint(response)
        # pprint(response.json())
        return response.json()

##########################################################################
# Query
# rename in aggregate class (because of list of videos)
##########################################################################


##########################################################################
# Video
# rename in aggregate class (because of list of videos)
##########################################################################
class Videos():
    # to complete
    video_fields = ['id','videoId','query_id','kind']
    snippet_fields = ['']
    stats_fields = ['']

    def __init__(self, mongo_curs, id=None, query_id=None):
        self.db = mongo_curs.db
        if id:
            self.id_video = id
            self.get()
        if query_id:
            self.query_id = query_id
            self.get()

    def get_one_video(self):
        try:
            current_video = self.db.videos.find_one_or_404({ 'id_video': self.id_video})
            print('get video : ', current_video['id_video'])
        except BaseException as e:
            print('video not found : ', e)
        return

    def get_one_query_videos(self):
        try:
            current_videos = self.db.videos.find({ 'query_id': self.query_id})
            print('get one query videos : ', current_user['query_id'])
        except BaseException as e:
            print('one query videos not found : ', e)
        return

    def view_one_video(self):
        return str(current_video)

    def view_query_videos(self):
        return str(current_video)    

    def create(self):
        return

    def create_or_replace_user_cortext(self, dataUser):
        dataUser = dataUser.json()
        self.username = dataUser['username']
        self.id_cortext = dataUser['id']
        
        try:
            current_user = self.db.users.find_one_or_404({ 'id_cortext': self.id_cortext})
            print('get cortext user : ', current_user['username'])
            if (current_user):
                # self.udpate(dataUser)
                self.db.users.update_one(
                  { 'id_cortext' : self.id_cortext },
                  { '$set': { 'username': dataUser['username']} }
                )
        except BaseException as e:
            print('user not found or error : ', e)
            self.create()
            return 'user not found or error : '+ str(e)
        return

    def update(self, dataUser):
        user_update = self.db.users.update_one(
          { 'id_pytheas' : self.id_pytheas },
          { '$set': { 'username': dataUser['username']} }
        )
        return user_update

    def delete():
        return


##########################################################################
# Comment
# rename in aggregate class (because of list of videos)
##########################################################################
class Comment():
    def __init__(self, mongo_curs, query_id):
        #super(Executive, self).__init__(*args)

        self.db = mongo_curs.db
        self.query_id = query_id


    def add_stats_for_each_entry(self, list_video):
        #Youtube.verify_error(list_video)
        # part = 'statistics'
        for each in list_video:
            print(each)
            #video_result = api.get_query('videos', id=id_video, part=part)
            #pprint.print(video_result)

            if 'youtube#video' in result['kind']:
                print(results['kind'])

                # self.db.videos.update_one(
                #   { '' : self.id_pytheas },
                #   { '$set': { 'username': dataUser['username']} }
                # )
        return

    def create_comment_entry_for_each(self, commentThread):
        if not 'error' in commentThread:
            for each in commentThread['items']:
                # try:
                snippet = each['snippet']['topLevelComment']['snippet']
                if 'authorChannelId' in snippet:
                    snippet['authorChannelId'] = snippet['authorChannelId']['value']
                else:
                    snippet['authorChannelId'] = 'cortext_pytheas_unknown_author#' + each['id']
                
                self.db.comments.insert_one({
                    'id' : each['id'],
                    'query_id' : self.query_id,
                    'isPublic': each['snippet']['isPublic'],
                    'canReply': each['snippet']['canReply'],
                    'totalReplyCount': each['snippet']['totalReplyCount'],
                    'videoId' : each['snippet']['videoId'],
                    'snippet': snippet,
                    'is_top_level_comment': 'true',
                })
                
                if 'replies' in each:
                    for child in each['replies']['comments']:
                        snippet = child['snippet']
                        if 'authorChannelId' in snippet:
                            snippet['authorChannelId'] = snippet['authorChannelId']['value']
                        else:
                            snippet['authorChannelId'] = 'cortext_pytheas_unknown_author#' + each['id']
                        self.db.comments.insert_one({
                            'id' : child['id'],
                            'query_id' : self.query_id,
                            'videoId' : child['snippet']['videoId'],
                            'snippet': snippet,
                            'is_top_level_comment': 'false'
                        })
                # except Exception as e:
                #     print('error here : ' + e)
                #     pass

        else:
            print(commentThread['error'])
            return str('reason of error is : ' + commentThread['error']['errors'][0]['reason'])

        return


##########################################################################
# I/O File/dir access (PROBABLY OBSOLETE NOW EXCEPT CAPTIONS)
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



#################################################################""


class YouTubeTranscriptApi():
    class CouldNotRetrieveTranscript(Exception):
        """
        Raised if a transcript could not be retrieved.
        """

        ERROR_MESSAGE = (
            'Could not get the transcript for the video {video_url}! '
            'Most likely subtitles have been disabled by the uploader or the video is no longer '
            'available.'
        )

        def __init__(self, video_id):
            super(YouTubeTranscriptApi.CouldNotRetrieveTranscript, self).__init__(
                self.ERROR_MESSAGE.format(video_url=_TranscriptFetcher.WATCH_URL.format(video_id=video_id))
            )
            self.video_id = video_id


    @staticmethod
    def get_transcripts(video_ids, continue_after_error=False):
        """
        Retrieves the transcripts for a list of videos.
        :param video_ids: a list of youtube video ids
        :type video_ids: [str]
        :param continue_after_error: if this is set the execution won't be stopped, if an error occurs while retrieving
        one of the video transcripts
        :type continue_after_error: bool
        :return: a tuple containing a dictionary mapping video ids onto their corresponding transcripts, and a list of
        video ids, which could not be retrieved
        :rtype: ({str: [{'text': str, 'start': float, 'end': float}]}, [str]}
        """
        data = {}
        unretrievable_videos = []

        for video_id in video_ids:
            try:
                data[video_id] = YouTubeTranscriptApi.get_transcript(video_id)
            except Exception as exception:
                if not continue_after_error:
                    raise exception

                unretrievable_videos.append(video_id)

        return data, unretrievable_videos

    @staticmethod
    def get_transcript(video_id):
        """
        Retrieves the transcript for a single video.
        :param video_id: the youtube video id
        :type video_id: str
        :return: a list of dictionaries containing the 'text', 'start' and 'duration' keys
        :rtype: [{'text': str, 'start': float, 'end': float}]
        """
        try:
            return _TranscriptParser(_TranscriptFetcher(video_id).fetch()).parse()
        except Exception:
            logger.error(
                YouTubeTranscriptApi.CouldNotRetrieveTranscript.ERROR_MESSAGE.format(
                    video_url=_TranscriptFetcher.WATCH_URL.format(video_id=video_id)
                )
            )
            print(YouTubeTranscriptApi.CouldNotRetrieveTranscript(video_id))
            #raise YouTubeTranscriptApi.CouldNotRetrieveTranscript(video_id)
            


class _TranscriptFetcher():
    WATCH_URL = 'https://www.youtube.com/watch?v={video_id}'
    API_BASE_URL = 'https://www.youtube.com/api/{api_url}'

    def __init__(self, video_id):
        self.video_id = video_id

    def fetch(self):
        fetched_site = requests.get(self.WATCH_URL.format(video_id=self.video_id)).text

        timedtext_url_start = fetched_site.find('timedtext')

        return requests.get(
            self.API_BASE_URL.format(
                api_url=fetched_site[
                    timedtext_url_start:timedtext_url_start + fetched_site[timedtext_url_start:].find('"')
                ].replace(
                    '\\u0026', '&'
                ).replace(
                    '\\', ''
                )
            )
        ).text


class _TranscriptParser():
    HTML_TAG_REGEX = re.compile(r'<[^>]*>', re.IGNORECASE)

    def __init__(self, plain_data):
        self.plain_data = plain_data

    def parse(self):
        return [
            {
                'text': re.sub(self.HTML_TAG_REGEX, '', unescape(xml_element.text)),
                'start': float(xml_element.attrib['start']),
                'duration': float(xml_element.attrib['dur']),
            }
            for xml_element in ElementTree.fromstring(self.plain_data)
        ]