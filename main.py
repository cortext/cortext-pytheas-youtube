## main.py
import os
import shutil
import json
import requests
from uuid import uuid4

# Main class
from youtube import YouTube
from youtube import FileData
from youtube import Mongo
from code_country import language_code

# flask
from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request
from flask import session
from flask import send_file
from flask import redirect
from flask import url_for

# ext lib
from flask_bootstrap import Bootstrap
from flask_pymongo import PyMongo
from bson import json_util
from bson.objectid import ObjectId
from furl import furl

from pprint import pprint

def create_app():
    app = Flask(__name__)
    app.config.update(
        TEMPLATES_AUTO_RELOAD=True
    )
    app.config['MONGO_DBNAME'] = 'youtube'
    app._static_folder = 'static/'
    Bootstrap(app)
    return app

app = create_app()
mongo_curs = PyMongo(app)
data_dir = 'data/'


@app.before_request
def set_client_session():
    with open('conf/conf-dev.json') as data_file:
        data = json.load(data_file)
    session['api_key'] = data['session']['api_key']


@app.route('/')
def home():
    return render_template('home.html')

##########################################################################
# Csv (plus need to add json)
##########################################################################
@app.route('/getCSV')  # this is a job for GET, not POST
def getCSV(data):

    return send_file('outputs/Adjacency.csv',
                     mimetype='text/csv',
                     attachment_filename='Adjacency.csv',
                     as_attachment=True)

##########################################################################
# REST
##########################################################################
@app.route('/queries/', methods=['GET'])
def queries_list():
    result = mongo_curs.db.query.find({})
    json_res = json_util.dumps(
        result, sort_keys=True, indent=2, separators=(',', ': '))
    return jsonify(json.loads(json_res))

@app.route('/queries/<query_id>', methods=['GET'])
def query_search(query_id):
    result = mongo_curs.db.query.find_one_or_404({'query_id': query_id})
    json_res = json_util.dumps(
        result, sort_keys=True, indent=2, separators=(',', ': '))
    return jsonify(json.loads(json_res))

@app.route('/queries/<query_id>/videos/', methods=['GET'])
def videos_list_by_query(query_id):
    result = mongo_curs.db.videos.find({'query_id': query_id})
    json_res = json_util.dumps(
        result, sort_keys=True, indent=2, separators=(',', ': '))
    return jsonify(json.loads(json_res))

@app.route('/videos/<video_id>', methods=['GET'])
def video_search(video_id):
    result = mongo_curs.db.videos.find({'id.videoId': video_id})
    json_res = json_util.dumps(
        result, sort_keys=True, indent=2, separators=(',', ': '))
    return jsonify(json.loads(json_res))

@app.route('/videos/<video_id>/comments/', methods=['GET'])
def comments_list_by_video(video_id):
    result = mongo_curs.db.comments.find({'videoId': video_id})
    json_res = json_util.dumps(
        result, sort_keys=True, indent=2, separators=(',', ': '))
    return jsonify(json.loads(json_res))

@app.route('/comments/<comment_id>', methods=['GET'])
def comment_search(comment_id):
    result = mongo_curs.db.comments.find_one_or_404({'_id': ObjectId(comment_id)})
    json_res = json_util.dumps(
        result, sort_keys=True, indent=2, separators=(',', ': '))
    return jsonify(json.loads(json_res))


##########################################################################
# Browse
##########################################################################
@app.route('/browse', methods=['GET'])
def browse():
    return render_template('browse.html')

@app.route('/video_info', methods=['POST'])
def video_info():
    if request.method == 'POST':
        if 'api_key' in session:
            id_video = request.form.get('unique_id_video')
            if 'youtube.com/watch?v=' in id_video:
                if 'https' in id_video:
                    id_video = id_video.replace(
                        'https://www.youtube.com/watch?v=', '')
                else:
                    id_video = id_video.replace(
                        'http://www.youtube.com/watch?v=', '')
            part = ', '.join(request.form.getlist('part'))
            api_key = session['api_key']
            api = YouTube(api_key=api_key)
            video_result = api.get_query('videos', id=id_video, part=part)
            video_result_string = json.dumps(
                video_result, sort_keys=True, indent=2, separators=(',', ': '))
            return render_template('results.html', result=video_result, string=video_result_string)
        else:
            return render_template('browse.html', message='api key not set')
    return render_template('browse.html')

@app.route('/channel_info', methods=['POST'])
def channel_info():
    if request.method == 'POST':
        if 'api_key' in session:
            id_channel = request.form.get('unique_id_channel')
            if 'youtube.com/channel/' in id_channel:
                if 'https' in id_channel:
                    id_channel = id_channel.replace(
                        'https://www.youtube.com/channel/', '')
                else:
                    id_channel = id_channel.replace(
                        'http://www.youtube.com/channel/', '')
            elif 'youtube.com/user/' in id_channel:
                return render_template('channel_info.html', message='YoutubeAPI cannot retrieve user (different from channel)...')
            part = ', '.join(request.form.getlist('part'))
            api_key = session['api_key']
            api = YouTube(api_key=api_key)
            channel_result = api.get_query(
                'channels', id=id_channel, part=part)
            channel_result_string = json.dumps(
                channel_result, sort_keys=True, indent=2, separators=(',', ': '))
            return render_template('results.html', result=channel_result, string=channel_result_string)
        else:
            return render_template('browse.html', message='api key not set')
    return render_template('browse.html')

@app.route('/playlist_info', methods=['POST'])
def playlist_info():
    if request.method == 'POST':
        if 'api_key' in session:
            id_playlist = request.form.get('unique_id_playlist')
            if 'youtube.com/watch?v=' in id_playlist:
                f = furl(id_playlist)
                id_playlist = f.args['list']
            part = ', '.join(request.form.getlist('part'))
            api_key = session['api_key']
            api = YouTube(api_key=api_key)
            playlist_info = api.get_query(
                'playlists', id=id_playlist, part=part)
            playlist_info_string = json.dumps(
                playlist_info, sort_keys=True, indent=2, separators=(',', ': '))
            return render_template('results.html', result=playlist_info, string=playlist_info_string)
        else:
            return render_template('browse.html', message='api key not set')
    return render_template('browse.html')

##########################################################################
# Search
##########################################################################
@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        session['counter'] = 0
        if 'api_key' in session:
            if request.form.get('advanced'):
                st_point = request.form.get('startpoint') + 'T00:00:00Z'
                ed_point = request.form.get('endpoint') + 'T00:00:00Z'
                import datetime
                d_start = datetime.datetime.strptime( st_point, "%Y-%m-%dT%H:%M:%SZ" )
                d_end   = datetime.datetime.strptime( ed_point, "%Y-%m-%dT%H:%M:%SZ" )
                # use in session
                session['request'] = {
                    'q': request.form.get('query'),
                    'part': ', '.join(request.form.getlist('part')),
                    'language': request.form.get('language'),
                    'maxResults': request.form.get('maxResults'),
                    'ranking': request.form.get('ranking'),
                    'publishedAfter': st_point,
                    'publishedBefore': ed_point
                }
                # build & request
                # search_results = YouTube.get_search(session['api_key'], session['request'])
                print(d_start ,d_end)
                print('-------------')
                date_results = YouTube(session['api_key']).get_day_by_day(session['request'])

                # if 'nextPageToken' in search_results:
                #     previous_token = search_results['nextPageToken']
                # else:
                #     previous_token = ''
                results_string = json.dumps(
                    date_results, sort_keys=True, indent=4, separators=(',', ': '))
                return render_template('results.html', search_results=date_results, string=results_string, counter=session['counter'], prev='previous_token')
            else:
                session['request'] = {
                    'q': request.form.get('query'),
                    'part': ', '.join(request.form.getlist('part')),
                    'language': request.form.get('language'),
                    'maxResults': request.form.get('maxResults'),
                    'ranking': request.form.get('ranking')
                }
                search_results = YouTube.get_search(session['api_key'], session['request'])
                previous_token = search_results['nextPageToken']
                search_results_string = json.dumps(
                    search_results, sort_keys=True, indent=4, separators=(',', ': '))
                return render_template('results.html', search_results=search_results, string=search_results_string, counter=session['counter'], prev=previous_token)

        else:
            return render_template('search.html', message='api key not set')
    # Go to next page
    elif request.method == 'GET' and request.args.get('nextPageToken'):
        session['counter'] += 1
        pageToken = request.args.get('nextPageToken')
        search_results = YouTube.get_search(session['api_key'], session['request'])
        search_results_string = json.dumps(
            search_results, sort_keys=True, indent=2, separators=(',', ': '))
        return render_template('results.html', search_results=search_results, string=search_results_string, counter=session['counter'], prev=pageToken)
    return render_template('search.html', language_code=language_code)


##########################################################################
# Author/Channel
# https://stackoverflow.com/questions/17698040/youtube-api-v3-where-can-i-find-a-list-of-each-videocategoryid
##########################################################################
@app.route('/channel', methods=['POST', 'GET'])
def channel():
    if request.method == 'POST':
        session['counter'] = 0
        if 'api_key' in session:
            session['request'] = {
                'part': ', '.join(request.form.getlist('part')),
                'id': request.form.get('id'),
                'forUsername': ', '.join(request.form.getlist('forUsername')),
                'categoryId': request.form.get('categoryId'),
                'maxResults': request.form.get('maxResults')
            }
            channel_results = YouTube.get_channel(session['api_key'], session['request'])
            channel_results_string = json.dumps(
                channel_results, sort_keys=True, indent=4, separators=(',', ': '))
            return render_template('results.html', search_results=channel_results, string=channel_results_string, counter=session['counter'])
        else:
            return render_template('search.html', message='api key not set')
    # Go to next page
    elif request.method == 'GET' and request.args.get('nextPageToken'):
        session['counter'] += 1
        pageToken = request.args.get('nextPageToken')
        session['pageToken'] = pageToken
        channel_results = YouTube.get_channel(session['api_key'], session['request'])
        results_string = json.dumps(
            search_results, sort_keys=True, indent=2, separators=(',', ': ')
        )
        return render_template('results.html', search_results=channel_results, string=results_string, counter=session['counter'])
    return render_template('query/channel.html', language_code=language_code)

# ##########################################################################
# # Partial videos
# ##########################################################################
# @app.route('/partial_videos', methods=['POST', 'GET'])
# def partial_videos():
#     if request.method == 'POST':
#         session['counter'] = 0
#         if 'api_key' in session:
#             session['request'] = {
#                 'query': request.form.get('query'),
#                 'part': ', '.join(request.form.getlist('part')),
#                 'categoryId': request.form.get('categoryId'),
#                 'maxResults': request.form.get('maxResults')
#             }
#             # then build request
#             api = YouTube(api_key=session['api_key'])
#             search_results = api.get_query(
#                 'channels',
#                 q=session['request']['query'],
#                 part=session['request']['part'],
#                 categoryId=session['request']['categoryId'],
#                 maxResults=session['request']['maxResults']
#             )
#             previous_token = search_results['nextPageToken']
#             search_results_string = json.dumps(
#                 search_results, sort_keys=True, indent=4, separators=(',', ': '))
#             return render_template('results.html', search_results=search_results, string=search_results_string, counter=session['counter'], prev=previous_token)
#         else:
#             return render_template('search.html', message='api key not set')
#     # Go to next page
#     elif request.method == 'GET' and request.args.get('nextPageToken'):
#         session['counter'] += 1
#         pageToken = request.args.get('nextPageToken')
#         api = YouTube(api_key=session['api_key'])
#         search_results = api.get_query(
#             'channels',
#             q=session['request']['query'],
#             part=session['request']['part'],
#             categoryId=session['request']['categoryId'],
#             maxResults=session['request']['maxResults'],
#             pageToken=pageToken
#         )
#         search_results_string = json.dumps(
#             search_results, sort_keys=True, indent=2, separators=(',', ': '))
#         return render_template('results.html', search_results=search_results, string=search_results_string, counter=session['counter'], prev=pageToken)
#     return render_template('query/partial_videos.html', language_code=language_code)
#
# ##########################################################################
# # Playlist items
# ##########################################################################
# @app.route('/playlist', methods=['POST', 'GET'])
# def playlist():
#     if request.method == 'POST':
#         session['counter'] = 0
#         if 'api_key' in session:
#             session['request'] = {
#                 'query': request.form.get('query'),
#                 'part': ', '.join(request.form.getlist('part')),
#                 'categoryId': request.form.get('categoryId'),
#                 'maxResults': request.form.get('maxResults')
#             }
#             # then build request
#             api = YouTube(api_key=session['api_key'])
#             search_results = api.get_query(
#                 'channels',
#                 q=session['request']['query'],
#                 part=session['request']['part'],
#                 categoryId=session['request']['categoryId'],
#                 maxResults=session['request']['maxResults']
#             )
#             previous_token = search_results['nextPageToken']
#             search_results_string = json.dumps(
#                 search_results, sort_keys=True, indent=4, separators=(',', ': '))
#             return render_template('results.html', search_results=search_results, string=search_results_string, counter=session['counter'], prev=previous_token)
#         else:
#             return render_template('search.html', message='api key not set')
#     # Go to next page
#     elif request.method == 'GET' and request.args.get('nextPageToken'):
#         session['counter'] += 1
#         pageToken = request.args.get('nextPageToken')
#         api = YouTube(api_key=session['api_key'])
#         search_results = api.get_query(
#             'channels',
#             q=session['request']['query'],
#             part=session['request']['part'],
#             categoryId=session['request']['categoryId'],
#             maxResults=session['request']['maxResults'],
#             pageToken=pageToken
#         )
#         search_results_string = json.dumps(
#             search_results, sort_keys=True, indent=2, separators=(',', ': '))
#         return render_template('results.html', search_results=search_results, string=search_results_string, counter=session['counter'], prev=pageToken)
#     return render_template('query/playlist_items.html', language_code=language_code)

##########################################################################
# processing results uesd by /search and /aggregate
##########################################################################
@app.route('/process_results')
def process_results():
    # prepare dir & files
    print(session)
    path_query = session['request']['q'] + '_' + \
        session['request']['language'] + '_' + \
        session['request']['ranking'] + '/'
    FileData.create_dir(path_query)

    # build request based on session
    session['counter'] = 0
    api = YouTube(api_key=session['api_key'])
    search_results = api.get_query(
        'search',
        q=session['request']['q'],
        part=session['request']['part'],
        language=session['request']['language'],
        maxResults=session['request']['maxResults'],
        ranking=session['request']['ranking']
    )
    # save file & meta
    name_file = str(session['counter']) + '.json'

    meta_inf = {
        'regionCode': search_results['regionCode'],
        'pageInfo': search_results['pageInfo'],
        'etag': search_results['etag'],
        'kind': search_results['kind']
    }
    meta_info_file = path_query + 'meta_info.txt'
    search_results_file = path_query + name_file
    FileData.save_json(meta_info_file, meta_inf)
    FileData.save_json(search_results_file, search_results['items'])

    # mongo Insert
    # avoid duplicates
    # mongo_curs.db.query.createIndex( { 'unique_id': 1 }, unique=True )

    # insert query
    uid = uuid4()
    mongo_curs.db.query.insert_one(
        {
            'query_id': str(uid),
            'text': session['request']['q'],
            'part': session['request']['part'],
            'language': session['request']['language'],
            'maxResults': session['request']['maxResults'],
            'ranking': session['request']['ranking'],
        }
    )
    # insert videos
    for each in search_results['items']:
        each.update({'query_id': str(uid)})
        mongo_curs.db.videos.insert_one(
            each
        )
    ## Loop and save
    while 'nextPageToken' in search_results:
        session['counter'] += 1
        name_file = str(session['counter']) + '.json'
        search_results = api.get_query(
            'search',
            q=session['request']['q'],
            part=session['request']['part'],
            language=session['request']['language'],
            maxResults=session['request']['maxResults'],
            ranking=session['request']['ranking'],
            pageToken=search_results['nextPageToken']
        )
        if not search_results['items']:
            return render_template('download_process.html', message='ok it is done')
        # save items
        search_results_file = path_query + name_file
        FileData.save_json(search_results_file, search_results['items'])

        # insert video-info
        for each in search_results['items']:
            each.update({'query_id': str(uid)})
            mongo_curs.db.videos.insert_one(each)
    return render_template('download_process.html', message='ok it is done')

##########################################################################
# Aggregate
##########################################################################
@app.route('/aggregate', methods=['POST', 'GET'])
def aggregate():
    if os.path.exists(data_dir):
        # dir_list was used to list dir when json was only downlaod as file
        # be care to refact here
        dir_list = os.listdir(data_dir)
        db_list = mongo_curs.db.query.find({})
        db_listed = []
        for doc in db_list:
            concat_name = '_'.join([doc['text'], doc['language'], doc['ranking']])
            print(doc['query_id'])
            db_listed.append(concat_name)

        if request.method == 'POST':

            if request.form and request.form.get('del'):
                shutil.rmtree(data_dir + request.form.get('del'))
                dir_list = os.listdir(data_dir)
                return render_template('aggregate.html', dir_list=dir_list)

            if request.form and request.form.get('optionsRadios'):
                dir_to_check = request.form.get('optionsRadios')

                options_api = request.form.getlist('api_part')
                path_dir = data_dir + dir_to_check
                query_name = path_dir.replace('data/', '')

                part = ', '.join(request.form.getlist('part'))
                api_key = session['api_key']
                api = YouTube(api_key=api_key)

                # Get list of video from list of vid in dir (from /search)
                items = FileData.list_file(path_dir)
                items_videoId = items['items_videoId']
                items_playlist = items['items_playlist']
                # items_channel = items['items_channel']

                print(query_name)
                print('count of video :', len(items_videoId))
                print('count of playlist :', len(items_playlist))
                ############################
                if 'comments' in options_api:
                    path_comments = dir_to_check + '/comments/'
                    FileData.create_dir(path_comments)
                    count_total_commentThreads = 0

                    # for each video loop to comments
                    for id_video in items_videoId:
                        commentThreads_result = api.get_query(
                            'commentThreads',
                            videoId=id_video,
                            part='id, replies, snippet'
                        )
                        ## Check if error (eg unactivated comments)
                        if 'error' in commentThreads_result:
                            print(
                                commentThreads_result['error']['errors'][0]['reason']
                                )
                            continue

                        ## get OneByOne commentThreads & save json
                        for each in commentThreads_result['items']:
                            count_total_commentThreads += 1
                            print('EACH IN COMMENTS_THREADS == ', each)
                            ### insert videos into mongoDB
                            Mongo.insert_mongo(query_name, each, mongo_curs)

                            ### save file
                            each_sanitized = json.loads(
                                json_util.dumps(each['snippet'])
                            )
                            comments_file = path_comments + \
                                str(count_total_commentThreads) + '_commentThread.json'
                            FileData.save_json(comments_file, each_sanitized)
                        print(count_total_commentThreads)

                        ## Loop and save
                        while 'nextPageToken' in commentThreads_result:
                            commentThreads_result = api.get_query(
                                'commentThreads',
                                videoId=id_video,
                                part='id, replies, snippet',
                                pageToken=commentThreads_result['nextPageToken']
                            )
                            ### Check if error (eg unactivated comments)
                            if 'error' in commentThreads_result:
                                print(
                                    commentThreads_result['error']['errors'][0]['reason']
                                    )
                                continue
                            for each in commentThreads_result['items']:
                                count_total_commentThreads += 1

                                ### save file
                                each_sanitized = json.loads(
                                    json_util.dumps(each['snippet'])
                                )
                                comments_file = path_comments + \
                                    str(count_total_commentThreads) + '_commentThread.json'
                                FileData.save_json(comments_file, each_sanitized)

                                ### insert videos into mongoDB
                                Mongo.insert_mongo(query_name, each, mongo_curs)

                            print(count_total_commentThreads)
                ############################
                if 'captions' in options_api:
                    path_captions = dir_to_check + '/captions/'
                    FileData.create_dir(path_captions)
                    # for each video loop to captions
                    for id_video in items_videoId:
                        captions_result = api.get_query(
                            'captions',
                            videoId=id_video,
                            part='id, snippet'
                        )
                        # Check if error (eg unactivated captions)
                        if 'error' in captions_result:
                            print(captions_result['error']
                                  ['errors'][0]['reason'])
                            continue
                        if not captions_result['items']:
                            print('empty captions')
                            continue
                        # get different captions language
                        for key, val in captions_result.items():
                            # if not captions_result['items'] and key ==
                            # 'items':
                            if key == 'items':
                                for item in val:
                                    lang_caption = item['snippet']['language']
                                    caption_xml = 'https://www.youtube.com/api/timedtext?lang=' \
                                        + lang_caption \
                                        + '&v=' + id_video
                                    print(caption_xml)
                                    req_xml = requests.get(caption_xml)
                                    if req_xml.text:
                                        # saving cap
                                        name_file = id_video + '_' + lang_caption + '.xml'
                                        with open(data_dir + path_captions + name_file, 'w') as f:
                                            f.write(req_xml.text)

                return render_template('download_process.html', message='ok it is done')

        return render_template('aggregate.html', dir_list=db_listed)

    return render_template('aggregate.html', message='hmmm it seems to have a bug on dir_path...')

##########################################################################
# Config
##########################################################################
@app.route('/config', methods=['POST', 'GET'])
def config():
    if os.path.exists(data_dir):
        dir_list = os.listdir(data_dir)
        if request.method == 'POST':
            if request.form and request.form.get('del'):
                shutil.rmtree(data_dir + request.form.get('del'))
                dir_list = os.listdir(data_dir)

    if request.method == 'POST':
        if request.form.get('api_key'):
            session['api_key'] = request.form.get('api_key')

    return render_template('config.html',  dir_list=dir_list)

##########################################################################
# Manage
##########################################################################
@app.route('/manage', methods=['POST', 'GET'])
def manage():
    if os.path.exists(data_dir):
        dir_list = os.listdir(data_dir)

        stats = {
            'query_totalCount' : mongo_curs.db.query.find({}).count(),
            'videos' : mongo_curs.db.videos.find({}).count(),
            'comments' : mongo_curs.db.comments.find({}).count(),
            'list_queries' : []
        }

        result = mongo_curs.db.query.find({})
        for doc in result:
            # add basic stat for admin
            countVideos = mongo_curs.db.videos.find({ 'query_id': doc['query_id']})
            # need to refact for comments table...
            concat_name = '_'.join([doc['text'], doc['language'], doc['ranking']])
            countComments = mongo_curs.db.comments.find({ 'query_name': concat_name})
            doc['countVideos'] = countVideos.count()
            doc['countComments'] = countComments.count()
            stats['list_queries'].append(doc)

        #Del Dir data
        if request.method == 'POST':
            if request.form and request.form.get('del'):
                shutil.rmtree(data_dir + request.form.get('del'))
                dir_list = os.listdir(data_dir)

    return render_template('manage.html',  dir_list=dir_list, stats=stats)


##########################################################################
# Download videos, comments set
##########################################################################
@app.route('/download/videos/<query_id>', methods=['GET'])
def download_videos(query_id):
    result = mongo_curs.db.query.find_one({'query_id': query_id})
    result = mongo_curs.db.videos.find({'query_id': query_id})
    json_res = json_util.dumps(
        result, sort_keys=True, indent=2, separators=(',', ': ')
    )
    response = jsonify(json.loads(json_res))
    response.headers['Content-Disposition'] = 'attachment;filename=' + str(result['text']) + '.json'
    return response

@app.route('/download/comments/<query_id>', methods=['GET'])
def download_comments(query_id):
    query = mongo_curs.db.query.find_one({'query_id': query_id})
    from_query = json.dumps(query, default=json_util.default)
    from_query = json.loads(from_query)
    query_name = '_'.join([from_query['text'], from_query['language'], from_query['ranking']])

    result = mongo_curs.db.comments.find({'query_name': query_name})
    json_res = json_util.dumps(
        result, sort_keys=True, indent=2, separators=(',', ': ')
    )
    response = jsonify(json.loads(json_res))
    response.headers['Content-Disposition'] = 'attachment;filename=' + str(query_name) + '_comments.json'
    return response


##########################################################################
# Delete dataset
##########################################################################
@app.route('/delete/<query_id>', methods=['GET'])
def delete(query_id):
    # del comments
    query = mongo_curs.db.query.find_one({'query_id': query_id})
    from_query = json.dumps(query, default=json_util.default)
    from_query = json.loads(from_query)
    query_name = '_'.join([from_query['text'], from_query['language'], from_query['ranking']])
    mongo_curs.db.comments.remove({'query_name': query_name})
    # del videos
    mongo_curs.db.videos.remove({'query_id': query_id})
    # del query
    mongo_curs.db.query.remove({'query_id': query_id})
    return redirect(url_for('manage'))

##########################################################################
# Reset session
##########################################################################
@app.route('/reset', methods=['POST'])
def reset():
    if session['api_key']:
        session.clear()
    return render_template('config.html')


##########################################################################
# Start
##########################################################################
if __name__ == '__main__':
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    app.secret_key = os.urandom(24)
    app.run(debug=True,host='0.0.0.0')
