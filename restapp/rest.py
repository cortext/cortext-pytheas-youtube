import os
import logging
import json
import requests
from logging.handlers import RotatingFileHandler
from flask import Flask, current_app
from flask import jsonify
from flask import request
from flask import session
from flask import redirect
from flask import url_for
from bson import json_util
from bson.objectid import ObjectId
from database import Database

#init app
try:
    rest = Flask(__name__)
    rest.config['debug_level'] = os.environ['debug_level']
    rest.config['LOG_DIR'] = os.environ['LOG_DIR']
    
    rest.config['REST_PORT'] = str(os.environ['REST_PORT'])
    rest.config['WORKER_PORT'] = str(os.environ['WORKER_PORT'])
    rest.config['MONGO_PORT'] = os.environ['MONGO_PORT']
    
    rest.config['MONGO_HOST'] = os.environ['MONGO_HOST']
    rest.config['MONGO_DBNAME'] = os.environ['MONGO_DBNAME']
    rest.logger.debug('app is initied')

    rest.logger.debug(rest.config)

    mongo_curs = Database().init_mongo(rest)
    rest.logger.debug('mongo_curs is initiated')
except BaseException as error:
    rest.logger.debug('An exception occurred : {}'.format(error))


#################
# WORKER 
class YouTube():
    #api_key = None
    #access_token = None
    #api_base_url = 'https://www.googleapis.com/youtube/v3/'
    #part = None

    def __init__(self, api_key, access_token=None, api_url=None ,part=None):
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
            rest.logger.info('try_request success on ' +  url)
            rest.logger.debug('kwargs are ' + str(kwargs))
        except requests.exceptions.RequestException as e:
            rest.logger.warning('try_request failed on ' + url)
            rest.logger.warning('error is : ' + str(e))
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


@rest.route('/get_one_video', methods=['POST'])
def get_one_video():
    rest.logger.debug('HET ')
    rest.logger.debug(request.form.get('id_video'))
    rest.logger.debug()

    api = YouTube(api_key=request.form['key'])
    video_result = api.get_query('videos', id=request.form['id_video'], part=request.form['part'])
    
    rest.logger.debug(video_result)
    return 'DONE'

##########################################################################
# REST GET
##########################################################################
# all queries 
@rest.route('/queries/', methods=['GET'])
def all_queries_list():
    result = mongo_curs.db.queries.find({})
    json_res = json_util.dumps(
        result, sort_keys=True, indent=2, separators=(',', ': '))
    rest.logger.info(
        'try_request success on {url} for *wildcard'.format(url=request.endpoint))
    return jsonify(json.loads(json_res))

# all videos 
@rest.route('/queries/videos/', methods=['GET'])
def all_videos_list():
    result = mongo_curs.db.videos.find({})
    json_res = json_util.dumps(
        result, sort_keys=True, indent=2, separators=(',', ': '))
    rest.logger.info(
        'try_request success on {url} for *wildcard'.format(url=request.endpoint))
    return jsonify(json.loads(json_res))

# all comments 
@rest.route('/queries/comments/', methods=['GET'])
def all_comments_list():
    result = mongo_curs.db.comments.find({})
    json_res = json_util.dumps(
        result, sort_keys=True, indent=2, separators=(',', ': '))
    rest.logger.info(
        'try_request success on {url} for *wildcard'.format(url=request.endpoint))
    return jsonify(json.loads(json_res))

# all captions
@rest.route('/queries/captions/', methods=['GET'])
def all_captions_list():
    result = mongo_curs.db.captions.find({})
    json_res = json_util.dumps(
        result, sort_keys=True, indent=2, separators=(',', ': '))
    rest.logger.info(
        'try_request success on {url} for *wildcard'.format(url=request.endpoint))
    return jsonify(json.loads(json_res))

##########################################################################
# REST view by users
##########################################################################
# all queries by user
@rest.route('/<user_id>/queries/', methods=['GET'])
def queries_list(user_id):
    result = mongo_curs.db.queries.find({'author_id': user_id})
    json_res = json_util.dumps(
        result, sort_keys=True, indent=2, separators=(',', ': '))
    rest.logger.info(
        'try_request success on {url} for {user_id}'.format(url=request.endpoint, user_id=user_id))
    return jsonify(json.loads(json_res))

# one query by user
@rest.route('/<user_id>/queries/<query_id>', methods=['GET'])
def query_search(user_id, query_id):
    result = mongo_curs.db.queries.find_one_or_404({'query_id': query_id, 
        'author_id' : user_id})
    json_res = json_util.dumps(
        result, sort_keys=True, indent=2, separators=(',', ': '))
    rest.logger.info(
        'try_request success on {url} for {user_id}'.format(url=request.endpoint, user_id=user_id))
    return jsonify(json.loads(json_res))

# list of videos by queries
@rest.route('/<user_id>/queries/<query_id>/videos/', methods=['GET'])
def videos_list_by_query(user_id, query_id):
    result = mongo_curs.db.videos.find({'query_id': query_id})
    json_res = json_util.dumps(
        result, sort_keys=True, indent=2, separators=(',', ': '))
    rest.logger.info(
        'try_request success on {url} for {user_id}'.format(url=request.endpoint, user_id=user_id))
    return jsonify(json.loads(json_res))

# list of comments by queries
@rest.route('/<user_id>/queries/<query_id>/comments/', methods=['GET'])
def comments_list_by_query(user_id, query_id):
    result = mongo_curs.db.comments.find({'query_id': query_id})
    json_res = json_util.dumps(
        result, sort_keys=True, indent=2, separators=(',', ': '))
    rest.logger.info(
        'try_request success on {url} for {user_id}'.format(url=request.endpoint, user_id=user_id))
    return jsonify(json.loads(json_res))

# list of captions by queries
@rest.route('/<user_id>/queries/<query_id>/captions/', methods=['GET'])
def captions_list_by_query(user_id, query_id):
    result = mongo_curs.db.captions.find({'query_id': query_id})
    json_res = json_util.dumps(
        result, sort_keys=True, indent=2, separators=(',', ': '))
    rest.logger.info(
        'try_request success on {url} for {user_id}'.format(url=request.endpoint, user_id=user_id))
    return jsonify(json.loads(json_res))





# list of related Videos by queries
@rest.route('/<user_id>/queries/<query_id>/related/', methods=['GET'])
def related_list_by_query(user_id, query_id):
    result = mongo_curs.db.relatedVideos.find({'query_id': query_id})
    json_res = json_util.dumps(
        result, sort_keys=True, indent=2, separators=(',', ': '))
    rest.logger.info(
        'try_request success on {url} for {user_id}'.format(url=request.endpoint, user_id=user_id))
    return jsonify(json.loads(json_res))






## by VIDEOS
@rest.route('/<user_id>/videos/<video_id>', methods=['GET'])
def video_search(user_id, video_id):
    result = mongo_curs.db.videos.find({'id.videoId': video_id})
    json_res = json_util.dumps(
        result, sort_keys=True, indent=2, separators=(',', ': '))
    rest.logger.info(
        'try_request success on {url} for {user_id}'.format(url=request.endpoint, user_id=user_id))
    return jsonify(json.loads(json_res))

@rest.route('/<user_id>/videos/<video_id>/comments/', methods=['GET'])
def comments_list_by_video(user_id, video_id):
    result = mongo_curs.db.comments.find({'videoId': video_id})
    json_res = json_util.dumps(
        result, sort_keys=True, indent=2, separators=(',', ': '))
    rest.logger.info(
        'try_request success on {url} for {user_id}'.format(url=request.endpoint, user_id=user_id))
    return jsonify(json.loads(json_res))

## by comments
@rest.route('/<user_id>/comments/<comment_id>', methods=['GET'])
def comment_search(user_id, comment_id):
    result = mongo_curs.db.comments.find_one_or_404(
        {'_id': ObjectId(comment_id)})
    json_res = json_util.dumps(
        result, sort_keys=True, indent=2, separators=(',', ': '))
    rest.logger.info(
        'try_request success on {url} for {user_id}'.format(url=request.endpoint, user_id=user_id))
    return jsonify(json.loads(json_res))

## by captions
@rest.route('/<user_id>/captions/<caption_id>', methods=['GET'])
def caption_search(user_id, caption_id):
    result = mongo_curs.db.captions.find_one_or_404(
        {'_id': ObjectId(caption_id)})
    json_res = json_util.dumps(
        result, sort_keys=True, indent=2, separators=(',', ': '))
    rest.logger.info(
        'try_request success on {url} for {user_id}'.format(url=request.endpoint, user_id=user_id))
    return jsonify(json.loads(json_res))


##########################################################################
# REST DEL
##########################################################################
# all queries by user
# @rest.route('/<user_id>/queries/', methods=['DELETE'])
# def queries_list(user_id):
#     result = mongo_curs.db.queries.find({'author_id': user_id})
#     json_res = json_util.dumps(
#         result, sort_keys=True, indent=2, separators=(',', ': '))
#     logger.info(
#         'try_request success on {url} for {user_id}'.format(url=request.endpoint, user_id=user_id))
#     return jsonify(json.loads(json_res))




##########################################################################
# REST POST
##########################################################################
# add_query
@rest.route('/<user_id>/add_query/<query_id>', methods=['POST', 'GET'])
def add_query(user_id, query_id):
    rest.logger.debug(user_id)
    rest.logger.debug(query_id)
    rest.logger.debug(request.get_json())

    r = requests.post("http://worker:" + rest.config['WORKER_PORT'] + "/" + user_id + "/add_query/" + query_id, json=request.get_json())
    
    return 'POST REQUEST IS SENT'



# add_video by type of (channel, searchResults, videosList, playlistItem)
@rest.route('/<user_id>/query/<query_id>/add_video/<query_type>', methods=['POST', 'GET'])
def add_video(user_id, query_id, query_type):
    rest.logger.debug(user_id)
    rest.logger.debug(query_id)
    rest.logger.debug(query_type)

    requests.post("http://worker:" + rest.config['WORKER_PORT'] + "/" + user_id + "/query/" + query_id + "/add_video/" + query_type, json=request.get_json())
    
    return 'POST REQUEST IS SENT'


# add_comments
@rest.route('/<user_id>/query/<query_id>/add_comments', methods=['POST', 'GET'])
def add_comments(user_id, query_id):
    # first list videos from a query
    param = request.get_json() 
    results_query = requests.get("http://restapp:" + rest.config['REST_PORT'] + "/" + user_id + "/queries/" + query_id + "/videos/")
        
    list_vid = []
    for result in results_query.json():
        if 'videoId' in result:
            id_video = result['videoId']
        elif result['kind'] == 'youtube#playlistItem':
            id_video = result['snippet']['resourceId']['videoId']
        else:
            id_video = result['id']
        list_vid.append(id_video)
    # Then send job to worker 
    param['list_vid'] = list_vid
    r = requests.post("http://worker:" + rest.config['WORKER_PORT'] + "/" + user_id + "/add_comments/" + query_id, json=param)
    
    return 'POST REQUEST add_comments IS SENT'


# add_captions
@rest.route('/<user_id>/query/<query_id>/add_captions', methods=['POST', 'GET'])
def add_captions(user_id, query_id):
    # first list videos from a query
    param = request.get_json()
    results_query = requests.get("http://restapp:" + rest.config['REST_PORT'] + "/" + user_id + "/queries/" + query_id + "/videos/")
    rest.logger.debug('NIET1')

    list_vid = []
    for result in results_query.json():
        
        if 'videoId' in result:
            id_video = result['videoId']
        elif result['kind'] == 'youtube#playlistItem':
            id_video = result['snippet']['resourceId']['videoId']
        else:
            id_video = result['id']
        rest.logger.debug(id_video)
        list_vid.append(id_video)
    rest.logger.debug('NIET2')
    # Then send job to worker 
    param['list_vid'] = list_vid
    r = requests.post("http://worker:" + rest.config['WORKER_PORT'] + "/" + user_id + "/add_captions/" + query_id, json=param)
    
    return 'POST REQUEST add_captions IS SENT'



# add_related
@rest.route('/<user_id>/query/<query_id>/add_related', methods=['POST', 'GET'])
def add_related(user_id, query_id):
    rest.logger.debug(user_id)
    rest.logger.debug(query_id)

    # first list videos from a query
    param = request.get_json()
    results_query = requests.get("http://restapp:" + rest.config['REST_PORT'] + "/" + user_id + "/queries/" + query_id + "/videos/")

    list_vid = []
    for result in results_query.json():
        if 'videoId' in result:
            id_video = result['videoId']
        elif result['kind'] == 'youtube#playlistItem':
            id_video = result['snippet']['resourceId']['videoId']
        else:
            id_video = result['id']
        list_vid.append(id_video)

    # Then send job to worker
    param['list_vid'] = list_vid
    r = requests.post("http://worker:" + rest.config['WORKER_PORT'] + "/" + user_id + "/add_related/" + query_id, json=param)
    
    return 'POST REQUEST add_related IS SENT'



# run app
if __name__ == '__main__':
    # config logger (prefering builtin flask logger)
    formatter = logging.Formatter('%(filename)s ## [%(asctime)s] %(levelname)s == "%(message)s"', datefmt='%Y/%b/%d %H:%M:%S')
    handler = RotatingFileHandler('./' + rest.config['LOG_DIR'] + '/activity_rest.log', maxBytes=100000, backupCount=1)
    handler.setFormatter(formatter)
    #logger = logging.getLogger(__name__)

    rest.logger.setLevel(logging.DEBUG)
    rest.logger.addHandler(handler)

    rest.run(debug=rest.config['debug_level'], host='0.0.0.0', port=rest.config['REST_PORT'], threaded=True )
