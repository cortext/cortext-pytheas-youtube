import datetime
import datetime as dt
import dateutil.parser as time
import requests
import logging
import json
import re
from logging.handlers import RotatingFileHandler
from flask import Flask, current_app
from flask import jsonify
from flask import request
from flask import session
from flask import redirect
from flask import url_for

from youtube import YouTube
from youtube import YouTubeTranscriptApi
from youtube import Comment
from youtube import Caption
from youtube import Video
from youtube import RelatedVideos

from bson import json_util
from bson.objectid import ObjectId
from database import Database

# config app
def create_worker():
    with open('./conf/conf.json') as conf_file:
        conf_data = json.load(conf_file)
        worker = Flask(__name__)
        worker.config['LOG_DIR'] = conf_data['LOG_DIR']
        worker.config['WORKER_PORT'] = str(conf_data['WORKER_PORT'])
        worker.config['MONGO_HOST'] = conf_data['MONGO_HOST']
        worker.config['MONGO_DBNAME'] = conf_data['MONGO_DBNAME']
        worker.config['MONGO_PORT'] = conf_data['MONGO_PORT']
        worker.config['MONGO_URI'] = "mongodb://"+conf_data['MONGO_HOST']+":"+str(conf_data['MONGO_PORT'])+"/"+conf_data['MONGO_DBNAME']
        worker.config['debug_level'] = conf_data['debug_level']
    return worker

#init app
try:
    worker = create_worker()
    worker.logger.debug('app is initied')
    mongo_curs = Database().init_mongo(worker)
    worker.logger.debug('mongo_curs is initiated')
    #log_dir = worker.config['LOG_DIR']
except BaseException as error:
    worker.logger.debug('An exception occurred : {}'.format(error))



@worker.route('/<user_id>/add_query/<query_id>', methods=['POST', 'GET'])
def add_query(user_id, query_id):
    param = request.get_json() 
    worker.logger.debug(param)
    common = {
        'author_id': user_id,
        'query_id': query_id,
        'part': param['part'],
        'kind' : param['kind'],
        'query' : param['query']
    }

    if param['kind'] == 'channelItems':
        common.update({ 
            'channel_id': param['channel_id'],
            'maxResults': param['maxResults'],
            'kind' : param['kind']
        })
        mongo_curs.db.queries.insert_one(
            common
        )
    elif param['kind'] == 'searchResults':
        if 'mode' in param:
            common.update({
                'q': param['query'],
                'language': param['language'],
                'maxResults': param['maxResults'],
                'order': param['order'],
                'mode' : 'advanced',
                # 'ratio' : '', 
                'publishedAfter': param['publishedAfter'],
                'publishedBefore': param['publishedBefore']
            })
        else:
            common.update({
                'q': param['query'],
                'language': param['language'],
                'maxResults': param['maxResults'],
                'order': param['order'],
            })
        mongo_curs.db.queries.insert_one(
            common
        ) 
    elif param['kind'] == 'videos':
        common['name_query'] = param['query']
        mongo_curs.db.queries.insert_one(
            common
        )

    elif param['kind'] == 'playlistItems': 
        common.update({
            'playlist_id': param['playlist_id'],
            'maxResults': param['maxResults'],
        })
        mongo_curs.db.queries.insert_one(
            common
        )

    return 'POST query finished'


@worker.route('/<user_id>/query/<query_id>/add_video/<query_type>', methods=['POST', 'GET'])
def add_video(user_id, query_id, query_type):
    param = request.get_json()
    uid = param['query_id']
    query_id = param['query_id']
    query = param['query'] 
    api_key = param['api_key']
    api = YouTube(api_key=api_key)  
    maxResults = 50

    ###############################
    ## RESULTS FOR channel
    ###############################
    if query_type == 'channel':
        # looking for IDs & usernames
        # username need to retrieve ID first
        if param['channel_username']: 
            # HAVE TO PUT ALL OF THIS IN A method FUNCT()
            ######################################
            param_query = param.copy() 
            rm_list = ['query','query_id','author_id','channel_id','channel_username']
            [param_query.pop(key) for key in rm_list] 

            channel_usernames = re.sub("\r", "", param['channel_username'][0])
            channel_usernames = re.sub("\n", "", channel_usernames)
            channel_usernames = channel_usernames.split(',')        
            for channel_username in channel_usernames:
                param_query['forUsername'] = channel_username 

                find_channel_id = api.get_query(
                    'channels',
                    **param_query 
                )
                ########################################################
                if find_channel_id['items'] : 
                    param['query'] = query  
                    param['query_id'] = uid
                    param['channel_id'] += str(', ' + find_channel_id['items'][0]['id']) 
                    api.get_channel_videos(mongo_curs, find_channel_id['items'][0]['id'], param)
        
        # then for ID 
        if param['channel_id']:
            channel_ids = re.sub("\r", "", param['channel_id'][0])
            channel_ids = re.sub("\n", "", channel_ids)
            channel_ids = channel_ids.split(',')
            for channel_id in channel_ids:
                api.get_channel_videos(mongo_curs, channel_id, param)
        
        # finally add metrics for query in json
        count_videos = int(mongo_curs.db.videos.find({'query_id': query_id}).count())
        mongo_curs.db.queries.update_one(
            { 'query_id': query_id },
            { '$set': {'count_videos': count_videos } }
        )

    ###############################
    ## RESULTS FOR searchResults ##
    ###############################
    elif query_type == 'search': 
        
        if 'mode' in param:
            if param['language'] == 'None':
                del param['language']

            # Parse date time from form
            d_start = datetime.datetime.strptime(
                param['publishedAfter'], "%Y-%m-%dT%H:%M:%SZ")
            d_end = datetime.datetime.strptime(
                param['publishedBefore'], "%Y-%m-%dT%H:%M:%SZ")
            
            r_after = time.parse(param['publishedAfter'])
            r_before = time.parse(param['publishedBefore']) 

            delta = r_before - r_after
            delta_days = delta.days + 1

            param_query = {
                'q': param['query'],
                'part': param['part'],
                'relevenceLanguage': param['language'],
                'maxResults': param['maxResults'],
                'order': param['order'],
            } 

            ## Then iterate for each days 
            for n in range(delta.days + 1):
                worker.logger.debug(str(n))
                # increment one day later to get a one-day period
                r_after_next = r_after + dt.timedelta(days=1)
                st_point = r_after.isoformat()
                ed_point = r_after_next.isoformat()

                # Querying
                date_results = api.get_query(
                    'search',
                    **param_query,
                    publishedAfter = st_point,
                    publishedBefore = ed_point,
                )

                # saving
                for each in date_results['items']:
                    each.update({'query_id': query_id})
                    each = YouTube.cleaning_each(each)
                    mongo_curs.db.videos.insert_one(each)

                # loop
                while 'nextPageToken' in date_results and len(date_results['items']) != 0:
                    date_results = api.get_query(
                        'search',
                        **param_query,
                        publishedAfter = st_point,
                        publishedBefore = ed_point,
                        pageToken = date_results['nextPageToken']
                    )
                    if date_results['items']: 
                        for each in date_results['items']:
                            each.update({'query_id': query_id})
                            each = YouTube.cleaning_each(each) 
                            mongo_curs.db.videos.insert_one(each)
                    else:
                        break
                
                # finally increment next after day
                r_after += dt.timedelta(days=1)

        else:
            search_results = api.get_query(
                'search',
                q = param['query'],
                part = param['part'],
                language = param['language'],
                maxResults=param['maxResults'],
                order = param['order']
            )

            # insert videos 
            for each in search_results['items']:
                each.update({'query_id': uid})
                each = YouTube.cleaning_each(each)
                mongo_curs.db.videos.insert_one(each)

            ## Loop and save
            while 'nextPageToken' in search_results:
                search_results = api.get_query(
                    'search',
                    q=param['query'],
                    part=param['part'],
                    language=param['language'],
                    maxResults=param['maxResults'],
                    order=param['order'],
                    pageToken=search_results['nextPageToken']
                )
                if search_results['items']:
                    # insert video-info
                    for each in search_results['items']:
                        each.update({'query_id': uid})
                        each = YouTube.cleaning_each(each)
                        mongo_curs.db.videos.insert_one(each)    
                else:
                    # add metrics for query in json
                    count_videos = int(mongo_curs.db.videos.find({'query_id': uid}).count())
                    mongo_curs.db.queries.update_one(
                        { 'query_id': uid },
                        { '$set': {'count_videos': count_videos } }
                    )
                    break            

        count_videos = int(mongo_curs.db.videos.find({'query_id': uid}).count())
        mongo_curs.db.queries.update_one(
            { 'query_id': uid },
            { '$set': {'count_videos': count_videos } }
        )

    ###############################
    ## RESULTS FOR SET OF videosList
    ###############################
    elif query_type == 'video':
        for each in param['list_videos']:
            id_video = each
            video_result = api.get_query('videos', id=id_video, part=param['part'])
            video_result = video_result['items'][0]
            video_result.update({'query_id': uid})
            
            mongo_curs.db.videos.insert_one(video_result)

        count_videos = int(mongo_curs.db.videos.find({'query_id': uid}).count())
        mongo_curs.db.queries.update_one(
            { 'query_id': uid },
            { '$set': {'count_videos': count_videos } } 
        )

    ###############################
    ## RESULTS FOR PLAYLISTITEM
    ###############################
    elif query_type == 'playlist':
        for playlist_id in param['playlist_id']: 
            param.update({'playlist_id' : playlist_id})
            # call request
            playlist_results = api.get_playlist(mongo_curs, param)
                
        # add metrics for query in json
        count_videos = int(mongo_curs.db.videos.find({'query_id': query_id}).count())
        mongo_curs.db.queries.update_one(
            { 'query_id': query_id },
            { '$set': {'count_videos': count_videos } }
        )        



    return 'videos added'





@worker.route('/<user_id>/add_captions/<query_id>', methods=['POST', 'GET'])
def add_captions(user_id, query_id): 
    current_captions = Caption(mongo_curs, query_id)
    param = request.get_json()
    api = YouTube(api_key=param['api_key'])
    
    list_vid = param['list_vid']
    for id_video in list_vid:
        current_captions.create_if_not_exist(id_video)
    
    count_captions = int(mongo_curs.db.captions.find({'query_id': query_id}).count())
    
    mongo_curs.db.queries.update_one(
        { 'query_id': query_id },
        { '$set': {'count_captions': count_captions } }
    )

    

    return 'POST REQUEST add_captions IS RECEIVED'



@worker.route('/<user_id>/add_comments/<query_id>', methods=['POST', 'GET'])
def add_comments(user_id, query_id): 
    current_comment_thread = Comment(mongo_curs, query_id)
    param = request.get_json()
    api = YouTube(api_key=param['api_key'])

    list_vid = param['list_vid']
    for id_video in list_vid:
        commentThreads_result = api.get_query(
            'commentThreads',
            videoId=id_video,
            part='id, replies, snippet')
        current_comment_thread.create_comment_for_each(commentThreads_result)
        
        ## Loop and save while there is content
        while 'nextPageToken' in commentThreads_result:
            commentThreads_result = api.get_query(
                'commentThreads',
                videoId=id_video,
                part='id, replies, snippet',
                pageToken=commentThreads_result['nextPageToken'])
            current_comment_thread.create_comment_for_each(commentThreads_result)

        count_comments = int(mongo_curs.db.comments.find({'query_id': query_id}).count())
        mongo_curs.db.queries.update_one(
            { 'query_id': query_id },
            { '$set': {'count_comments': count_comments } }
        )
    return 'POST REQUEST add_comments IS RECEIVED'



@worker.route('/<user_id>/add_related/<query_id>', methods=['POST', 'GET'])
def add_related(user_id, query_id): 
    current_relatedVideos = RelatedVideos(mongo_curs, query_id)
    param = request.get_json()
    api = YouTube(api_key=param['api_key'])

    list_vid = param['list_vid']
    for id_video in list_vid:
        search_results = api.get_query(
            'search',
            part='id,snippet',
            maxResults= 50,
            relatedToVideoId=id_video,
            type='video',
        )

        for each in search_results['items']:
            each.update({'query_id': query_id})
            each.update({'videoId': id_video})
            mongo_curs.db.relatedVideos.insert_one(each)

        ## Loop and save
        while 'nextPageToken' in search_results:
            search_results = api.get_query(
                'search',
                part='id,snippet',
                maxResults= 50,
                relatedToVideoId=id_video,
                type='video',
                pageToken=search_results['nextPageToken']
            )
            if not search_results['items']:
                return redirect(url_for('manage'))
            else:
                for each in search_results['items']:
                    each.update({'query_id': query_id})
                    each.update({'belongTo': id_video})
                    mongo_curs.db.relatedVideos.insert_one(each)
        
    # add metrics for query in json
    count_videos = int(mongo_curs.db.relatedVideos.find({'query_id': query_id}).count())
    mongo_curs.db.queries.update_one(
        { 'query_id': query_id },
        { '$set': {'count_relatedVideos': count_videos } }
    )

    # add part as indicator
    part_value = mongo_curs.db.queries.find_one_or_404({ 'query_id': query_id})
    mongo_curs.db.queries.update_one(
        {
            'query_id': query_id
        },{
            '$set': {
                'part': part_value['part'] + ", relatedVideos",                             
            } 
        }, upsert=False
    )

    return 'POST REQUEST add_related IS RECEIVED'














# run app
if __name__ == '__main__':
    # config logger (prefering builtin flask logger)
    formatter = logging.Formatter('%(filename)s ## [%(asctime)s] %(levelname)s == "%(message)s"', datefmt='%Y/%b/%d %H:%M:%S')
    handler = RotatingFileHandler('./'+ worker.config['LOG_DIR'] +'/activity.log', maxBytes=10000, backupCount=1)
    handler.setFormatter(formatter)
    #logger = logging.getLogger(__name__)
    worker.logger.setLevel(logging.DEBUG)
    worker.logger.addHandler(handler)
    worker.run(debug=worker.config['debug_level'], host='0.0.0.0', port=worker.config['WORKER_PORT'], threaded=True )
