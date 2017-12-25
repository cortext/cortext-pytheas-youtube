# py dependancies
import os
import shutil
import json
import requests
from uuid import uuid4
# need to recheck here later...
import datetime
import datetime as dt
import dateutil.parser as time
# Flask
from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request
from flask import Response
from flask import session
from flask import send_file
from flask import redirect
from flask import url_for
# Ext lib
from flask_bootstrap import Bootstrap
from flask_pymongo import PyMongo
from bson import json_util
from bson.objectid import ObjectId
from furl import furl
# Main class
from youtube import YouTube
from youtube import User
from youtube import Comment
from youtube import FileData
from code_country import language_code

from celery import Celery


#Unclassed for moment
def cleaning_each(each):
    if 'videoId' in each['id']:
        each.update({'videoId': each['id']['videoId']})
    elif 'playlistId' in each['id']:
        each.update({'playlistId': each['id']['playlistId']})
    elif 'channelId' in each['id']:
        each.update({'channelId': each['id']['channelId']})
    return each

def create_app():
    with open('conf/conf.json') as conf_file:
        conf_data = json.load(conf_file)
        app = Flask(__name__)
        app._static_folder = conf_data['static_folder']
        app.config['DATA_DIR'] = conf_data['DATA_DIR']
        app.config['PORT'] = conf_data['PORT']
        app.config['MONGO_HOST'] = conf_data['MONGO_HOST']
        app.config['MONGO_DBNAME'] = conf_data['MONGO_DBNAME']
        app.config['MONGO_PORT'] = conf_data['MONGO_PORT']
        app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
        app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
        # app.config['CELERY_BROKER_URL'] = conf_data['CELERY_BROKER_URL']
        # app.config['CELERY_RESULT_BACKEND'] = conf_data['CELERY_RESULT_BACKEND']
        app.config['api_key'] = conf_data['api_key']
        Bootstrap(app)
        app.config.update(TEMPLATES_AUTO_RELOAD=True)
        app.config['debug_level'] = conf_data['debug_level']
        return app

try:
    app = create_app()
    mongo_curs = PyMongo(app)
    data_dir = app.config['DATA_DIR']
    celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    
except BaseException as error:
    print('An exception occurred : {}'.format(error))


# @celery.task
# def my_background_task(delta_days, r_after):
#     for n in range(delta_days):
#         r_after_next = r_after + dt.timedelta(days=1)
#         session['request']['publishedAfter'] = r_after.isoformat()
#         session['request']['publishedBefore'] = r_after_next.isoformat()

#         # Querying
#         date_results = api.get_query(
#             'search',
#             q=session['request']['q'],
#             part=session['request']['part'],
#             language=session['request']['language'],
#             maxResults=session['request']['maxResults'],
#             publishedAfter=session['request']['publishedAfter'],
#             publishedBefore=session['request']['publishedBefore'],
#             key=session['api_key'])

#         # insert videos
#         for each in date_results['items']:
#             each.update({'query_id': str(uid)})
#             each = cleaning_each(each)
#             mongo_curs.db.videos.insert_one(each)

#         # Loop and save while results
#         if not 'nextPageToken' in date_results:
#             while 'nextPageToken' in date_results:
#                 session['request']['nextPageToken'] = date_results['nextPageToken']

#                 date_results = api.get_query(
#                     'search',
#                     q=session['request']['q'],
#                     part=session['request']['part'],
#                     language=session['request']['language'],
#                     maxResults=session['request']['maxResults'],
#                     publishedAfter=session['request']['publishedAfter'],
#                     publishedBefore=session['request']['publishedBefore'],
#                     key=session['api_key'],
#                     nextPageToken=session['request']['nextPageToken'])

#                 # insert video-info except if last result
#                 if not date_results['items']:
#                     return
#                 for each in date_results['items']:
#                     each.update({'query_id': str(uid)})
#                     if 'snippet' in each:
#                         if 'videoId' in each['id']:
#                             each['snippet'].update({'videoId': each['id']['videoId']})
#                         elif 'playlistId' in each['id']:
#                             each['snippet'].update({'playlistId' : each['id']['playlistId']})
#                     elif 'videoId' in each['id']:
#                         each.update({'videoId': each['id']['videoId']})
#                     elif 'playlistId' in each['id']:
#                         each.update({'playlistId': each['id']['playlistId']})
#                     mongo_curs.db.videos.insert_one(each)

#         # finally increment next after day
#         r_after += dt.timedelta(days=1)
#     return 

@app.before_request
def before_request():
    try:
        # session['api_key'] = app.config['api_key']
        if 'access_token' not in session and request.endpoint != 'login':
            if 'auth' in request.endpoint:
                return auth()
            elif 'grant' in request.endpoint:
                return grant()            
            return redirect(url_for('login'))
    except BaseException as e:
        print(e)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('structures/error.html', error=error)

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
# Explore  
##########################################################################
@app.route('/explore', methods=['GET'])
def browse():
    return render_template('explore.html')

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
            api = YouTube(api_key=session['api_key'])
            video_result = api.get_query('videos', id=id_video, part=part)
            print(video_result)
            video_result_string = json.dumps(
                video_result, sort_keys=True, indent=2, separators=(',', ': '))
            return render_template('actions/view_results.html', result=video_result, string=video_result_string)
        else:
            return render_template('explore.html', message='api key not set')
    return render_template('explore.html')

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
                return render_template('explore/channel_info.html', message='YoutubeAPI cannot retrieve user (different from channel)...')
            part = ', '.join(request.form.getlist('part'))
            api = YouTube(api_key=session['api_key'])
            channel_result = api.get_query(
                'channels', id=id_channel, part=part)
            channel_result_string = json.dumps(
                channel_result, sort_keys=True, indent=2, separators=(',', ': '))
            return render_template('actions/view_results.html', result=channel_result, string=channel_result_string)
        else:
            return render_template('explore.html', message='api key not set')
    return render_template('explore.html')

@app.route('/playlist_info', methods=['POST'])
def playlist_info():
    if request.method == 'POST':
        if 'api_key' in session:
            id_playlist = request.form.get('unique_id_playlist')
            if 'youtube.com/watch?v=' in id_playlist:
                f = furl(id_playlist)
                id_playlist = f.args['list']
            part = ', '.join(request.form.getlist('part'))
            api = YouTube(api_key=session['api_key'])
            playlist_info = api.get_query(
                'playlists', id=id_playlist, part=part)
            playlist_info_string = json.dumps(
                playlist_info, sort_keys=True, indent=2, separators=(',', ': '))
            return render_template('actions/view_results.html', result=playlist_info, string=playlist_info_string)
        else:
            return render_template('explore.html', message='api key not set')
    return render_template('explore.html')


##########################################################################
# Download
##########################################################################
@app.route('/explore', methods=['GET'])
def explore():
    return render_template('explore.html')



@app.route('/video', methods=['POST', 'GET'])
def video():
    if request.method == 'POST':
        session['request'] = {
            'q': request.form.get('query'),
            'part': ', '.join(request.form.getlist('part')),
            'language': request.form.get('language'),
            'maxResults': request.form.get('maxResults'),
            'ranking': request.form.get('ranking')
        }
        search_results = YouTube.get_search(
            session['api_key'], session['request']
        )
        
        previous_token = search_results['nextPageToken']
        
        search_results_string = json.dumps(
            search_results, sort_keys=True, indent=4, separators=(',', ': ')
        )

        return redirect(url_for('manage'))

        # video_result = YouTube.get_video(
        #     session['api_key'], session['request'])
        # video_results_string = json.dumps(
        #     video_result, sort_keys=True, indent=4, separators=(',', ': '))
        # return render_template('actions/view_results.html', video_result=video_result, string=video_results_string)

    return render_template('download/video.html')


##########################################################################
# Playlist
##########################################################################
@app.route('/playlist', methods=['POST', 'GET'])
def playlist():
    # if request.method == 'POST':
    #     session['request'] = {
    #         'part': ', '.join(request.form.getlist('part')),
    #         'channelId': request.form.get('id'),
    #         # 'forUsername': ', '.join(request.form.getlist('forUsername')),
    #         # 'categoryId': request.form.get('categoryId'),
    #         'maxResults': request.form.get('maxResults')
    #     }

    #     channel_results = YouTube.get_channel(
    #         session['api_key'], session['request'])
    #     channel_results_string = json.dumps(
    #         channel_results, sort_keys=True, indent=4, separators=(',', ': '))
    #     return render_template('actions/view_results.html', search_results=channel_results, string=channel_results_string, counter=session['counter'])

    # # Go to next page
    # elif request.method == 'GET' and request.args.get('nextPageToken'):
    #     session['counter'] += 1
    #     pageToken = request.args.get('nextPageToken')
    #     session['pageToken'] = pageToken
    #     channel_results = YouTube.get_channel(
    #         session['api_key'], session['request'])
    #     results_string = json.dumps(
    #         channel_results, sort_keys=True, indent=2, separators=(',', ': ')
    #     )
    #     return render_template('actions/view_results.html', search_results=channel_results, string=results_string, counter=session['counter'])
    return render_template('download/playlist.html')


##########################################################################
# Author/Channel
# https://stackoverflow.com/questions/17698040/youtube-api-v3-where-can-i-find-a-list-of-each-videocategoryid
##########################################################################
@app.route('/channel', methods=['POST', 'GET'])
def channel():
    if request.method == 'POST':
        session['counter'] = 0
        session['request'] = {
            'part': ', '.join(request.form.getlist('part')),
            'channelId': request.form.get('id'),
            # 'forUsername': ', '.join(request.form.getlist('forUsername')),
            # 'categoryId': request.form.get('categoryId'),
            'maxResults': request.form.get('maxResults')
        }

        channel_results = YouTube.get_channel(
            session['api_key'], session['request'])
        channel_results_string = json.dumps(
            channel_results, sort_keys=True, indent=4, separators=(',', ': '))
        return render_template('actions/view_results.html', search_results=channel_results, string=channel_results_string, counter=session['counter'])

    # Go to next page
    elif request.method == 'GET' and request.args.get('nextPageToken'):
        session['counter'] += 1
        pageToken = request.args.get('nextPageToken')
        session['pageToken'] = pageToken
        channel_results = YouTube.get_channel(
            session['api_key'], session['request'])
        results_string = json.dumps(
            channel_results, sort_keys=True, indent=2, separators=(',', ': ')
        )
        return render_template('actions/view_results.html', search_results=channel_results, string=results_string, counter=session['counter'])
    return render_template('download/channel.html', language_code=language_code)


##########################################################################
# Search
##########################################################################
@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        session['counter'] = 0
        if 'api_key' in session:

            api = YouTube(session['api_key'])

            # IF DATE = ONE SEARCH BY DAY
            if request.form.get('advanced'):

                # get date points & convert them
                st_point = request.form.get('startpoint') + 'T00:00:00Z'
                ed_point = request.form.get('endpoint') + 'T00:00:00Z'
                d_start = datetime.datetime.strptime(
                    st_point, "%Y-%m-%dT%H:%M:%SZ")
                d_end = datetime.datetime.strptime(
                    ed_point, "%Y-%m-%dT%H:%M:%SZ")

                # add in session
                session['request'] = {
                    'q': request.form.get('query'),
                    'part': ', '.join(request.form.getlist('part')),
                    'language': request.form.get('language'),
                    'maxResults': request.form.get('maxResults'),
                    'ranking': request.form.get('ranking'),
                    'publishedAfter': st_point,
                    'publishedBefore': ed_point
                }

                # insert query in mongo
                uid = uuid4()
                mongo_curs.db.query.insert_one(
                    {
                        'query_id': str(uid),
                        'author_id':session['profil']['id'],
                        'query': session['request']['q'],
                        'part': session['request']['part'],
                        'language': session['request']['language'],
                        'maxResults': session['request']['maxResults'],
                        'ranking': session['request']['ranking'],
                        'date_start': session['request']['publishedAfter'],
                        'date_end': session['request']['publishedBefore']
                    }
                )

                # request
                date_results = YouTube(session['api_key']).get_query(
                    'search',
                    q=session['request']['q'],
                    part=session['request']['part'],
                    language=session['request']['language'],
                    maxResults=session['request']['maxResults'],
                    publishedAfter=session['request']['publishedAfter'],
                    publishedBefore=session['request']['publishedBefore'],
                    key=session['api_key'])

                r_before = time.parse(session['request']['publishedBefore'])
                r_after = time.parse(session['request']['publishedAfter'])
                delta = r_before - r_after
                delta_days = delta.days + 1

                # # Then iterate for each days
                for n in range(delta.days + 1):
                    # increment one day later to get a one-day period
                    r_after_next = r_after + dt.timedelta(days=1)
                    session['request']['publishedAfter'] = r_after.isoformat()
                    session['request']['publishedBefore'] = r_after_next.isoformat()

                    # Querying
                    date_results = api.get_query(
                        'search',
                        q=session['request']['q'],
                        part=session['request']['part'],
                        language=session['request']['language'],
                        maxResults=session['request']['maxResults'],
                        publishedAfter=session['request']['publishedAfter'],
                        publishedBefore=session['request']['publishedBefore'],
                        key=session['api_key'])

                    # insert videos
                    for each in date_results['items']:
                        each.update({'query_id': str(uid)})
                        each = cleaning_each(each)
                        mongo_curs.db.videos.insert_one(each)

                    # Loop and save while results
                    if not 'nextPageToken' in date_results:
                        while 'nextPageToken' in date_results:
                            session['request']['nextPageToken'] = date_results['nextPageToken']

                            date_results = api.get_query(
                                'search',
                                q=session['request']['q'],
                                part=session['request']['part'],
                                language=session['request']['language'],
                                maxResults=session['request']['maxResults'],
                                publishedAfter=session['request']['publishedAfter'],
                                publishedBefore=session['request']['publishedBefore'],
                                key=session['api_key'],
                                nextPageToken=session['request']['nextPageToken'])

                            # insert video-info except if last result
                            if not date_results['items']:
                                return
                            for each in date_results['items']:
                                each.update({'query_id': str(uid)})
                                if 'snippet' in each:
                                    if 'videoId' in each['id']:
                                        each['snippet'].update({'videoId': each['id']['videoId']})
                                    elif 'playlistId' in each['id']:
                                        each['snippet'].update({'playlistId' : each['id']['playlistId']})
                                elif 'videoId' in each['id']:
                                    each.update({'videoId': each['id']['videoId']})
                                elif 'playlistId' in each['id']:
                                    each.update({'playlistId': each['id']['playlistId']})
                                mongo_curs.db.videos.insert_one(each)

                    # finally increment next after day
                    r_after += dt.timedelta(days=1)

                return redirect(url_for('manage'))

            else:
                session['request'] = {
                    'q': request.form.get('query'),
                    'part': ', '.join(request.form.getlist('part')),
                    'language': request.form.get('language'),
                    'maxResults': request.form.get('maxResults'),
                    'ranking': request.form.get('ranking')
                }
                search_results = YouTube.get_search(
                    session['api_key'], session['request'])
                previous_token = search_results['nextPageToken']
                search_results_string = json.dumps(
                    search_results, sort_keys=True, indent=4, separators=(',', ': '))
                return render_template('actions/view_results.html', search_results=search_results, string=search_results_string, counter=session['counter'], prev=previous_token)

        else:
            return render_template('download/search.html', message='api key not set')
    # Go to next page
    elif request.method == 'GET' and request.args.get('nextPageToken'):
        session['counter'] += 1
        pageToken = request.args.get('nextPageToken')
        search_results = YouTube.get_search(
            session['api_key'], session['request'])
        search_results_string = json.dumps(
            search_results, sort_keys=True, indent=2, separators=(',', ': '))
        return render_template('actions/view_results.html', search_results=search_results, string=search_results_string, counter=session['counter'], prev=pageToken)
    return render_template('download/search.html', language_code=language_code)


##########################################################################
# Aggregate
##########################################################################
@app.route('/aggregate', methods=['POST', 'GET'])
def aggregate():
    if os.path.exists(data_dir):
        # dir_list was used to list dir when json was only downlaod as file
        # be care to refact here
        dir_list = os.listdir(data_dir)
        db_list = mongo_curs.db.query.find(
            {'author_id': session['profil']['id']}
        )
        stats = {    
            'list_queries': [],
        }
        result = mongo_curs.db.query.find(
            {'author_id': session['profil']['id']
        })
        for doc in result:
            # add basic stat for admin
            countVideos = mongo_curs.db.videos.find(
                {'query_id': doc['query_id']
            })
            countComments = mongo_curs.db.comments.find(
                {'query_id': doc['query_id']
            })
            doc['countVideos'] = countVideos.count()
            doc['countComments'] = countComments.count()
            stats['list_queries'].append(doc)

        
        
        if request.method == 'POST':
            if request.form and request.form.get('optionsRadios'):
                ## NEED TO REFACT HERE FOR CAPTIONS DATA...
                query_id = request.form.get('optionsRadios')
                options_api = request.form.getlist('api_part')
                part = ', '.join(request.form.getlist('part'))
                api_key = session['api_key']
                api = YouTube(api_key=api_key)
                results = mongo_curs.db.videos.find(
                    {
                        "$and": [
                            {"id.videoId": {"$exists": True}},
                            {"query_id": query_id}
                        ]
                    }
                )

                list_vid = []
                for result in results:
                    list_vid.append(result['id']['videoId'])

                ############################
                if 'comments' in options_api:
                    # for each video loop to comments
                    current_comment_thread = Comment(mongo_curs, query_id)

                    for id_video in list_vid:
                        commentThreads_result = api.get_query(
                            'commentThreads',
                            videoId=id_video,
                            part='id, replies, snippet')
                        current_comment_thread.create_comment_entry_for_each(commentThreads_result)

                        ## Loop and save
                        while 'nextPageToken' in commentThreads_result:
                            commentThreads_result = api.get_query(
                                'commentThreads',
                                videoId=id_video,
                                part='id, replies, snippet',
                                pageToken=commentThreads_result['nextPageToken'])
                            current_comment_thread.create_comment_entry_for_each(commentThreads_result)

                ############################
                if 'captions' in options_api:
                    path_captions = dir_to_check + '/captions/'
                    FileData.create_dir(path_captions)
                    # for each video loop to captions
                    for id_video in list_vid:
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

                return render_template('actions/download_process.html', message='ok it is done')

        return render_template('aggregate.html', stats=stats)

    return render_template('aggregate.html', message='hmmm it seems to have a bug on dir_path...')


##########################################################################
# processing results uesd by /search and /aggregate
##########################################################################
@app.route('/process_results')
def process_results():
    uid = uuid4()

    if 'q' in session['request'] :
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

        # insert query
        mongo_curs.db.query.insert_one(
            {
                'author_id':session['profil']['id'],
                'query_id': str(uid),
                'query': session['request']['q'],
                'part': session['request']['part'],
                'language': session['request']['language'],
                'maxResults': session['request']['maxResults'],
                'ranking': session['request']['ranking'],
            }
        )
        # insert videos
        for each in search_results['items']:
            each.update({'query_id': str(uid)})
            if 'snippet' in each:
                if 'videoId' in each['id']:
                    each['snippet'].update({'videoId': each['id']['videoId']})
                elif 'playlistId' in each['id']:
                    each['snippet'].update({'playlistId' : each['id']['playlistId']})
            elif 'videoId' in each['id']:
                each.update({'videoId': each['id']['videoId']})
            elif 'playlistId' in each['id']:
                each.update({'playlistId': each['id']['playlistId']})
            mongo_curs.db.videos.insert_one(each)

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
                return render_template('actions/download_process.html', message='ok it is done')

            # insert video-info
            for each in search_results['items']:
                each.update({'query_id': str(uid)})
                each = cleaning_each(each)
                mongo_curs.db.videos.insert_one(each)

    elif 'channelId' in session['request']:
        # build request based on session
        session['counter'] = 0
        api = YouTube(api_key=session['api_key'])
        channel_results = api.get_query(
            'search',
            channelId=session['request']['channelId'],
            part=session['request']['part'],
            maxResults=session['request']['maxResults']
        )
        # insert query
        mongo_curs.db.query.insert_one(
            {   
                'author_id':session['profil']['id'],
                'query_id': str(uid),
                'channel_id': session['request']['channelId'],
                'part': session['request']['part'],
                'maxResults': session['request']['maxResults'],
            }
        )
        # insert videos
        for each in channel_results['items']:
            each.update({'query_id': str(uid)})
            if 'snippet' in each:
                if 'videoId' in each['id']:
                    each['snippet'].update({'videoId': each['id']['videoId']})
                elif 'playlistId' in each['id']:
                    each['snippet'].update({'playlistId' : each['id']['playlistId']})
            elif 'videoId' in each['id']:
                each.update({'videoId': each['id']['videoId']})
            elif 'playlistId' in each['id']:
                each.update({'playlistId': each['id']['playlistId']})
            mongo_curs.db.videos.insert_one(each)
        ## Loop and save
        while 'nextPageToken' in channel_results:
            session['counter'] += 1
            name_file = str(session['counter']) + '.json'
            channel_results = api.get_query(
                'search',
                channelId=session['request']['channelId'],
                part=session['request']['part'],
                maxResults=session['request']['maxResults'],
                pageToken=channel_results['nextPageToken']
            )
            if not channel_results['items']:
                return render_template('actions/download_process.html', message='ok it is done')

            # insert video-info
            for each in channel_results['items']:
                each.update({'query_id': str(uid)})
                each = cleaning_each(each)
                mongo_curs.db.videos.insert_one(each)

    return render_template('actions/download_process.html', message='ok it is done')


##########################################################################
# Config
##########################################################################
@app.route('/config', methods=['POST', 'GET'])
def config():

    profil = session['profil']
    json_filtered = {
        'name' : profil['name'],
        'institution' : profil['institution'],
        'activitydomain' : profil['activitydomain'],
        'country' : profil['country'],
        'researchdomain' : profil['researchdomain'],
        'website' : profil['website'],
        'birthdate' : profil['birthdate'],
        'username' : profil['username'],
        'email' : profil['email'],
        'last_connexion' : profil['last_connexion'],
        'description' : profil['description']
    } 

    json_formated = json.dumps(json_filtered, indent=2) 

    if not 'api_key' in session:
       api_key_validate = 'You need an API KEY from youtube'
    else:
       api_key_validate = session['api_key']

    if request.method == 'POST':
        if request.form.get('api_key'):
            session['api_key'] = request.form.get('api_key')
            return redirect(url_for('home'))

    return render_template('config.html', session_data=json_formated, api_key_validate=api_key_validate)


##########################################################################
# Manage
##########################################################################
@app.route('/manage', methods=['POST', 'GET'])
def manage():
    if os.path.exists(data_dir):
        dir_list = os.listdir(data_dir)

        stats = {
            'query_totalCount': mongo_curs.db.query.find({}).count(),
            'videos': mongo_curs.db.videos.find({}).count(),
            'comments': mongo_curs.db.comments.find({}).count(),            
            'list_queries': []
        }

        result = mongo_curs.db.query.find(
            {'author_id': session['profil']['id']
        })
        for doc in result:
            # add basic stat for admin
            countVideos = mongo_curs.db.videos.find(
                {'query_id': doc['query_id']
            })
            countComments = mongo_curs.db.comments.find(
                {'query_id': doc['query_id']
            })
            doc['countVideos'] = countVideos.count()
            doc['countComments'] = countComments.count()
            stats['list_queries'].append(doc)

        # Del Dir data
        if request.method == 'POST':
            if request.form and request.form.get('del'):
                shutil.rmtree(data_dir + request.form.get('del'))
                dir_list = os.listdir(data_dir)

    return render_template('manage.html',  dir_list=dir_list, stats=stats)


##########################################################################
# Download videos, comments set
##########################################################################
@app.route('/download/queries/<query_id>/videos', methods=['GET'])
def download_videos(query_id):
    query = mongo_curs.db.query.find_one({'query_id': query_id})
    result = mongo_curs.db.videos.find({'query_id': query_id})
    json_res = json_util.dumps(result, sort_keys=True, indent=2, separators=(',', ': '))    
    
    if 'query' in query:
        query_name = '_'.join(
            [query['query'], query['language'], query['ranking']])
    elif 'channel_id' in query:
        query_name = query['channel_id']
    
    response = jsonify(json.loads(json_res))
    response.headers['Content-Disposition'] = 'attachment;filename=' + \
        str(query_name) + '_videos.json'
    return response

@app.route('/download/comments/<query_id>', methods=['GET'])
def download_comments(query_id):
    query = mongo_curs.db.query.find_one({'query_id': query_id})
    from_query = json.dumps(query, default=json_util.default)
    from_query = json.loads(from_query)
    
    if 'query' in query:
        query_name = '_'.join(
            [query['query'], query['language'], query['ranking']])
    elif 'channel_id' in query:
        query_name = query['channel_id']
    
    result = mongo_curs.db.comments.find({'query_id': query_id})
    json_res = json_util.dumps(result, sort_keys=True, indent=2, separators=(',', ': '))

    response = jsonify(json.loads(json_res))
    response.headers['Content-Disposition'] = 'attachment;filename=' + \
        str(query_name) + '_comments.json'
    return response


##########################################################################
# Delete dataset
##########################################################################
@app.route('/delete/<query_id>', methods=['GET'])
def delete(query_id):
    query = mongo_curs.db.query.find_one({'query_id': query_id})
    from_query = json.dumps(query, default=json_util.default)
    from_query = json.loads(from_query)
    
    if 'query' in query:
        query_name = '_'.join(
            [query['query'], query['language'], query['ranking']])
    elif 'channel_id' in query:
        query_name = query['channel_id']

    mongo_curs.db.comments.remove({'query_name': query_name})
    mongo_curs.db.videos.remove({'query_id': query_id})
    mongo_curs.db.query.remove({'query_id': query_id})
    return redirect(url_for('manage'))


##########################################################################
# Reset session
##########################################################################
@app.route('/reset', methods=['GET'])
def reset():
    session.clear()
    return redirect(url_for('login'))


##########################################################################
# OAuth
##########################################################################
@app.route('/login')
def login():   
    return render_template('actions/login.html')

@app.route('/grant', methods=['GET'])
def grant():
    with open('conf/conf.json') as conf_file:
        conf_data = json.load(conf_file)
        grant_host_url = conf_data['grant_host_url']
        redirect_uri_conf = conf_data['redirect_uri']

    grant_url = grant_host_url + "/auth/authorize" + \
                "?response_type=code" + \
                "&state=" + str(uuid4().hex) + \
                "&client_id=pytheas" + \
                "&redirect_uri=" + redirect_uri_conf

    headers = {
        'Location': grant_url
    }

    return Response(grant_url, status=302, headers=headers)

@app.route('/auth', methods=['GET'])
def auth():
    code = str(request.args['code']) 
    state = str(request.args['state']) 

    with open('conf/conf.json') as conf_file:
        conf_data = json.load(conf_file)
        print(conf_data)
        redirect_uri_conf = conf_data['redirect_uri']
        grant_host_url = conf_data['grant_host_url']

    payload = {
      'code': code,
      'state': state,
      'client_id': 'pytheas',
      'client_secret': 'mys3cr3t',
      'redirect_uri': redirect_uri_conf,
      'grant_type': 'authorization_code'
    }

    r_grant = requests.post(grant_host_url + '/auth/grant', data=payload)
    data = r_grant.json()
    r_access = requests.get(grant_host_url + '/auth/access?access_token=' + str(data['access_token']))
    
    session['access_token'] = data['access_token']
    session['profil'] = r_access.json()

    current_user = User(mongo_curs)
    current_user.create_or_replace_user_cortext(r_access)

    return redirect(url_for('config'))

##########################################################################
# Start
##########################################################################
if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run(debug=app.config['debug_level'], host='0.0.0.0', port=app.config['PORT'], threaded=True )
