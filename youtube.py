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

# FILE HANDLER LOGGER (not implemented again)
# from logging.handlers import RotatingFileHandler
# # création d'un handler qui va rediriger une écriture du log vers
# # un fichier en mode 'append', avec 1 backup et une taille max de 1Mo
# file_handler = RotatingFileHandler('activity.log', 'a', 1000000, 1)
# # on lui met le niveau sur DEBUG, on lui dit qu'il doit utiliser le formateur
# # créé précédement et on ajoute ce handler au logger
# file_handler.setLevel(logging.DEBUG)
# # création d'un formateur qui va ajouter le temps, le niveau
# # de chaque message quand on écrira un message dans le log
# formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
# file_handler.setFormatter(formatter)
# logger.addHandler(file_handler)


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
            logger.info('try_request success on ' +  url)
            logger.debug('kwargs are ' + str(kwargs))
        except requests.exceptions.RequestException as e:
            logger.warning('try_request failed on ' + url)
            logger.warning('error is : ' + e)
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

    # TODO
    def get_playlist(api_key, session):
        playlist_results = YouTube(api_key).get_query(
            'playlistItems',
            playlistId=session['playlistId'],
            part=session['part'],
            maxResults=session['maxResults']
        )
        return playlist_results

    def verify_error(api_key, result_query):
        if not 'error' in result_query:
            return result_query
        else:
            logger.errors('Reason of error is : ' + commentThread['error']['errors'][0]['reason'])
            return commentThread['error']

    @staticmethod
    def response(response):
        return response.json()

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
            logger.debug('get video : ', current_video['id_video'])
        except BaseException as e:
            logger.error('video not found : ', e)
        return

    def get_one_query_videos(self):
        try:
            current_videos = self.db.videos.find({ 'query_id': self.query_id})
            logger.debug('get one query videos : ', current_user['query_id'])
        except BaseException as e:
            logger.error('one query videos not found : ', e)
        return

    def view_one_video(self):
        return str(current_video)

    def view_query_videos(self):
        return str(current_video)    

    # def update(self, dataUser):
    #     user_update = self.db.users.update_one(
    #       { 'id_pytheas' : self.id_pytheas },
    #       { '$set': { 'username': dataUser['username']} }
    #     )
    #     return user_update

    # def add_metrics_for_each(self, list_video):
    #     for each in list_video:
    #         print(each)
    #         # if 'youtube#video' in result['kind']:
    #             # print(results['kind'])
    #     return

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

    def create_if_not_exist(self, id_video):
        id_query = self.id_query
        try:
            current_caption = self.db.captions.find_one_or_404(
                { '$and':[{ 'id_query': id_query }, { 'id_video': id_video }] }
            )
        except BaseException as e:
            self.create_captions(id_video)
            logger.warning(
                str('comment not found or error. Log is here : ') + str(e) + str(type(e))
            )
        return

    def create_comment_for_each(self, commentThread):
        if not 'error' in commentThread:
            nb_comment = 0
            for each in commentThread['items']:
                nb_comment += 1
                
                snippet = each['snippet']['topLevelComment']['snippet']
                if 'authorChannelId' in snippet:
                    snippet['authorChannelId'] = snippet['authorChannelId']['value']
                else:
                    snippet['authorChannelId'] = 'cortext_pytheas_unknown_author#' + each['id']
                
                topCommentIntegrated = {
                    'id' : each['id'],
                    'query_id' : self.query_id,
                    'isPublic': each['snippet']['isPublic'],
                    'canReply': each['snippet']['canReply'],
                    'totalReplyCount': each['snippet']['totalReplyCount'],
                    'videoId' : each['snippet']['videoId'],
                    'snippet': snippet,
                    'is_top_level_comment': 'true',
                }
                self.db.comments.insert_one(topCommentIntegrated)
                
                if 'replies' in each:
                    for child in each['replies']['comments']:
                        nb_comment += 1
                        snippet = child['snippet']
                        if 'authorChannelId' in snippet:
                            snippet['authorChannelId'] = snippet['authorChannelId']['value']
                        else:
                            snippet['authorChannelId'] = 'cortext_pytheas_unknown_author#' + each['id']

                        CommentIntegrated = {
                            'id' : child['id'],
                            'query_id' : self.query_id,
                            'videoId' : child['snippet']['videoId'],
                            'snippet': snippet,
                            'is_top_level_comment': 'false'
                        }
                        self.db.comments.insert_one(CommentIntegrated)
            logger.debug('total nb comment for this request = ' + str(nb_comment))

        else:
            logger.error(commentThread['error'])
            logger.error('reason of error is : ' + ['errors'][0]['reason'])
            return

        return

    # def add_stats_for_each(self, list_video):
    #     #Youtube.verify_error(list_video)
    #     # part = 'statistics'
    #     for each in list_video:
    #         print(each)
    #         #video_result = api.get_query('videos', id=id_video, part=part)
    #         #pprint.print(video_result)

    #         if 'youtube#video' in result['kind']:
    #             print(results['kind'])
    #             # self.db.videos.update_one(
    #             #   { '' : self.id_pytheas },
    #             #   { '$set': { 'username': dataUser['username']} }
    #             # )
    #     return

##########################################################################
# Captions
# rename in aggregate class (because of list of videos)
##########################################################################
class Caption():
    # https://github.com/jdepoix/youtube-transcript-api
    # use an undocumentad part of the api youtube (web client api)
    
    def __init__(self, mongo_curs, id_query):
        self.db = mongo_curs.db
        self.id_query = id_query

    # def verify_caption(self, id_video):
    #     captions_result = self.Youtube.get_query(
    #         'captions',
    #         videoId=id_video,
    #         part='id, snippet'
    #     )
    #     # Check if error (eg unactivated captions)
    #     if 'error' in captions_result:
    #         print(captions_result['error']
    #               ['errors'][0]['reason'])
    #     if not captions_result['items']:
    #         print('empty captions')
    #     # get different captions language
    #     for key, val in captions_result.items():
    #         if key == 'items':
    #             for item in val:
    #                 lang_caption = item['snippet']['language']
    #                 track_kind = item['snippet']['trackKind']
    #                 current_captions = Caption(mongo_curs, id_query)
    #                 current_captions.create_captions(id_video)
    #     return

    def create_captions(self, id_video):
        transcript = YouTubeTranscriptApi().get_transcript(id_video)
        self.db.captions.insert_one({
            'id_query' : self.id_query,
            'id_video' : id_video,
            'captions' : transcript,
        })

    def create_if_not_exist(self, id_video):
        id_query = self.id_query
        try:
            current_caption = self.db.captions.find_one_or_404(
                { '$and':[{ 'id_query': id_query }, { 'id_video': id_video }] }
            )
        except BaseException as e:
            self.create_captions(id_video)
            logger.warning(
                str('Caption not found or error. Log is here : ') + str(e) + str(type(e))
            ) 
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