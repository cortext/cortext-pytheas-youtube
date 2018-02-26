from flask import Blueprint
rest_module = Blueprint('rest_module', __name__, template_folder='templates')

##########################################################################
# REST
##########################################################################
@rest_module.route('/queries/', methods=['GET'])
def queries_list():
    result = mongo_curs.db.query.find({})
    json_res = json_util.dumps(
        result, sort_keys=True, indent=2, separators=(',', ': '))
    return jsonify(json.loads(json_res))


@rest_module.route('/queries/<query_id>', methods=['GET'])
def query_search(query_id):
    result = mongo_curs.db.query.find_one_or_404({'query_id': query_id})
    json_res = json_util.dumps(
        result, sort_keys=True, indent=2, separators=(',', ': '))
    return jsonify(json.loads(json_res))


@rest_module.route('/queries/<query_id>/videos/', methods=['GET'])
def videos_list_by_query(query_id):
    result = mongo_curs.db.videos.find({'query_id': query_id})
    json_res = json_util.dumps(
        result, sort_keys=True, indent=2, separators=(',', ': '))
    return jsonify(json.loads(json_res))


@rest_module.route('/videos/<video_id>', methods=['GET'])
def video_search(video_id):
    result = mongo_curs.db.videos.find({'id.videoId': video_id})
    json_res = json_util.dumps(
        result, sort_keys=True, indent=2, separators=(',', ': '))
    return jsonify(json.loads(json_res))


@rest_module.route('/videos/<video_id>/comments/', methods=['GET'])
def comments_list_by_video(video_id):
    result = mongo_curs.db.comments.find({'videoId': video_id})
    json_res = json_util.dumps(
        result, sort_keys=True, indent=2, separators=(',', ': '))
    return jsonify(json.loads(json_res))


@rest_module.route('/comments/<comment_id>', methods=['GET'])
def comment_search(comment_id):
    result = mongo_curs.db.comments.find_one_or_404(
        {'_id': ObjectId(comment_id)})
    json_res = json_util.dumps(
        result, sort_keys=True, indent=2, separators=(',', ': '))
    return jsonify(json.loads(json_res))
