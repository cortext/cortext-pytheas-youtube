import json
from flask import Blueprint
from flask import Flask, current_app
from flask import jsonify
from flask import request
from flask import session
from flask import redirect
from flask import url_for
from database import Database
from bson import json_util
from bson.objectid import ObjectId

rest = Blueprint('rest', __name__,)
app = Flask(__name__)

with app.app_context():
    current_app = app
    mongo_curs = Database().init_mongo(app)

## HAVE TO INTEGRATE LOGGER HERE..


##########################################################################
# REST view
##########################################################################
@rest.route('/queries/', methods=['GET'])
def queries_list():
    result = mongo_curs.db.query.find({})
    json_res = json_util.dumps(
        result, sort_keys=True, indent=2, separators=(',', ': '))
    return jsonify(json.loads(json_res))

@rest.route('/queries/<query_id>', methods=['GET'])
def query_search(query_id):
    result = mongo_curs.db.query.find_one_or_404({'query_id': query_id})
    json_res = json_util.dumps(
        result, sort_keys=True, indent=2, separators=(',', ': '))
    return jsonify(json.loads(json_res))

@rest.route('/queries/<query_id>/videos/', methods=['GET'])
def videos_list_by_query(query_id):
    result = mongo_curs.db.videos.find({'query_id': query_id})
    json_res = json_util.dumps(
        result, sort_keys=True, indent=2, separators=(',', ': '))
    return jsonify(json.loads(json_res))

@rest.route('/queries/<query_id>/comments/', methods=['GET'])
def comments_list_by_query(query_id):
    result = mongo_curs.db.comments.find({'query_id': query_id})
    json_res = json_util.dumps(
        result, sort_keys=True, indent=2, separators=(',', ': '))
    return jsonify(json.loads(json_res))

@rest.route('/queries/<query_id>/captions/', methods=['GET'])
def captions_list_by_query(query_id):
    result = mongo_curs.db.captions.find({'query_id': query_id})
    json_res = json_util.dumps(
        result, sort_keys=True, indent=2, separators=(',', ': '))
    return jsonify(json.loads(json_res))

@rest.route('/videos/<video_id>', methods=['GET'])
def video_search(video_id):
    result = mongo_curs.db.videos.find({'id.videoId': video_id})
    json_res = json_util.dumps(
        result, sort_keys=True, indent=2, separators=(',', ': '))
    return jsonify(json.loads(json_res))

@rest.route('/videos/<video_id>/comments/', methods=['GET'])
def comments_list_by_video(video_id):
    result = mongo_curs.db.comments.find({'videoId': video_id})
    json_res = json_util.dumps(
        result, sort_keys=True, indent=2, separators=(',', ': '))
    return jsonify(json.loads(json_res))

@rest.route('/comments/<comment_id>', methods=['GET'])
def comment_search(comment_id):
    result = mongo_curs.db.comments.find_one_or_404(
        {'_id': ObjectId(comment_id)})
    json_res = json_util.dumps(
        result, sort_keys=True, indent=2, separators=(',', ': '))
    return jsonify(json.loads(json_res))

@rest.route('/captions/<caption_id>', methods=['GET'])
def caption_search(caption_id):
    result = mongo_curs.db.captions.find_one_or_404(
        {'_id': ObjectId(caption_id)})
    json_res = json_util.dumps(
        result, sort_keys=True, indent=2, separators=(',', ': '))
    return jsonify(json.loads(json_res))

##########################################################################
# Download videos, comments set
##########################################################################
## future work to get dynamically repetitive methods access data. 
## Could be possibly apply on others data side of code.
# but warn because will need to identify query_type in url
# and also rename ontolgogy for query_type based between videos (as lists of videos by query) and others (see below)
# also have to download filename as utf8 (and have to see better process about downloading files...)
@rest.route('/download/<query_type>/<query_id>', methods=['GET'])
def download_videos_by_type(query_id, query_type):
    if query_type not in ['comments', 'captions']:
        # need to fix later. There is 404 function in @app
        from flask import render_template
        return render_template('structures/error.html', error='error')

    query = mongo_curs.db.query.find_one({'query_id': query_id})    
    
    if 'query' in query:
        if not 'ranking' in query: 
            query_name = str(query['query'])
        else:
            query_name = '_'.join([query['query'], query['language'], query['ranking']])
    elif 'channel_id' in query:
        query_name = query['channel_id']
    
    query_name = str(query_name.encode('utf8'))
    query_type_filename = (str(query_type))
    result = mongo_curs.db[query_type].find({'query_id': query_id})
    json_res = json_util.dumps(result, sort_keys=True, indent=2, separators=(',', ': '))

    response = jsonify(json.loads(json_res))
    response.headers['Content-Disposition'] = 'attachment;filename=' + \
        query_name + '_'+ query_type +'.json'
    return response

# old style hard query_type fro /queries/videos...
@rest.route('/download/queries/<query_id>/videos', methods=['GET'])
def download_videos(query_id):
    query = mongo_curs.db.query.find_one({'query_id': query_id})    
    
    if 'query' in query:
        if not 'ranking' in query: 
            query_name = str(query['query'])
        else:
            query_name = '_'.join([query['query'], query['language'], query['ranking']])
    elif 'channel_id' in query:
        query_name = query['channel_id']
    query_name = str(query_name.encode('utf8'))

    result = mongo_curs.db.videos.find({'query_id': query_id})
    json_res = json_util.dumps(result, sort_keys=True, indent=2, separators=(',', ': '))

    response = jsonify(json.loads(json_res))
    response.headers['Content-Disposition'] = 'attachment;filename=' + \
        query_name + '_videos.json'
    return response



##########################################################################
# Delete dataset
##########################################################################
@rest.route('/delete/<query_id>', methods=['GET'])
def delete(query_id):
    query = mongo_curs.db.query.find_one({'query_id': query_id})
    from_query = json.dumps(query, default=json_util.default)
    from_query = json.loads(from_query)
    
    mongo_curs.db.comments.remove({'query_name': query_id})
    mongo_curs.db.videos.remove({'query_id': query_id})
    mongo_curs.db.query.remove({'query_id': query_id})
    return redirect(url_for('manage'))