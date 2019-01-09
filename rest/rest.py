import logging
import json
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

# config app
def create_rest_app():
    with open('./conf/conf.json') as conf_file:
        conf_data = json.load(conf_file)
        rest = Flask(__name__)
        rest.config['LOG_DIR'] = conf_data['LOG_DIR']
        rest.config['REST_PORT'] = conf_data['REST_PORT']
        rest.config['MONGO_HOST'] = conf_data['MONGO_HOST']
        rest.config['MONGO_DBNAME'] = conf_data['MONGO_DBNAME']
        rest.config['MONGO_PORT'] = conf_data['MONGO_PORT']
        rest.config['MONGO_URI'] = "mongodb://"+conf_data['MONGO_HOST']+":"+str(conf_data['MONGO_PORT'])+"/"+conf_data['MONGO_DBNAME']
        rest.config['debug_level'] = conf_data['debug_level']
    return rest

#init app
try:
    rest = create_rest_app()
    rest.logger.debug('app is initied')
    mongo_curs = Database().init_mongo(rest)
    rest.logger.debug('mongo_curs is initiated')
    #log_dir = rest.config['LOG_DIR']
except BaseException as error:
    logger.debug('An exception occurred : {}'.format(error))


# all queries 
@rest.route('/', methods=['GET'])
def hello():
    return 'hello'


##########################################################################
# REST view - all
##########################################################################
# all queries 
@rest.route('/queries/', methods=['GET'])
def all_queries_list():
    result = mongo_curs.db.query.find({})
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
    result = mongo_curs.db.query.find({'author_id': user_id})
    json_res = json_util.dumps(
        result, sort_keys=True, indent=2, separators=(',', ': '))
    rest.logger.info(
        'try_request success on {url} for {user_id}'.format(url=request.endpoint, user_id=user_id))
    return jsonify(json.loads(json_res))

# one query by user
@rest.route('/<user_id>/queries/<query_id>', methods=['GET'])
def query_search(user_id, query_id):
    result = mongo_curs.db.query.find_one_or_404({'query_id': query_id})
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
#     result = mongo_curs.db.query.find({'author_id': user_id})
#     json_res = json_util.dumps(
#         result, sort_keys=True, indent=2, separators=(',', ': '))
#     logger.info(
#         'try_request success on {url} for {user_id}'.format(url=request.endpoint, user_id=user_id))
#     return jsonify(json.loads(json_res))

##########################################################################
# REST POST
##########################################################################

# run app
if __name__ == '__main__':
    # config logger (prefering builtin flask logger)
    formatter = logging.Formatter('%(filename)s ## [%(asctime)s] %(levelname)s == "%(message)s"', datefmt='%Y/%b/%d %H:%M:%S')
    handler = RotatingFileHandler('activity.log', maxBytes=10000, backupCount=1)
    handler.setFormatter(formatter)
    #logger = logging.getLogger(__name__)
    rest.logger.setLevel(logging.DEBUG)
    rest.logger.addHandler(handler)
    rest.run(debug=rest.config['debug_level'], host='0.0.0.0', port=rest.config['REST_PORT'], threaded=True )
