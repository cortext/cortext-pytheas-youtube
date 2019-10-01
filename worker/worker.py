import requests
import logging
import json
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


@worker.route('/<user_id>/add_queries/<query_id>/', methods=['POST', 'GET'])
def add_query(user_id, query_id): 
    param = request.get_json()
    uid = param['uid']
    part = param['part']
    list_videos = param['list_videos']
    name_query = param['name_query']

    worker.logger.debug(param)
    api_key = param['api_key']

    mongo_curs.db.queries.insert_one(
        {
            'author_id': user_id,
            'query_id': uid,
            'query': name_query,
            'part': part,
        }
    )

    list_results = {'items': [] }
    for id_video in list_videos:
        api = YouTube(api_key=api_key)
        video_result = api.get_query('videos', id=id_video, part=part)       

        try:
            list_results['items'].append(video_result['items'][0])
        except error as err:
            worker.logger.debug(err)
            continue

    # this is because not same organizing inside youtube class
    for each in list_results['items']:
        each.update({'query_id': uid})
        if 'id' in each:
            each.update({'videoId': each['id']})
        elif 'snippet' in each:
            if 'videoId' in each['id']:
                each.update({'videoId': each['id']['videoId']})
            elif 'playlistId' in each['id']:
                each.update({'playlistId' : each['id']['playlistId']})
        elif 'videoId' in each['id']:
            each.update({'videoId': each['id']['videoId']})
        elif 'playlistId' in each['id']:
            each.update({'playlistId': each['id']['playlistId']})
        mongo_curs.db.videos.insert_one(each)

    count_videos = int(mongo_curs.db.videos.find({'query_id': uid}).count())
    mongo_curs.db.queries.update_one(
        { 'query_id': uid },
        { '$set': {'count_videos': count_videos } }
    )

    return 'POST REQUEST IS RECEIVED'



@worker.route('/<user_id>/add_captions/<query_id>/', methods=['POST', 'GET'])
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



@worker.route('/<user_id>/add_comments/<query_id>/', methods=['POST', 'GET'])
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



@worker.route('/<user_id>/add_related/<query_id>/', methods=['POST', 'GET'])
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
                    each.update({'videoId': id_video})
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
    handler = RotatingFileHandler('activity.log', maxBytes=10000, backupCount=1)
    handler.setFormatter(formatter)
    #logger = logging.getLogger(__name__)
    worker.logger.setLevel(logging.DEBUG)
    worker.logger.addHandler(handler)
    worker.run(debug=worker.config['debug_level'], host='0.0.0.0', port=worker.config['WORKER_PORT'], threaded=True )
