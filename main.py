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
from flask import render_template
from flask import request
from flask import Response
from flask import session
from flask import send_file
from flask import redirect
from flask import url_for
# Ext lib
from flask_bootstrap import Bootstrap
from furl import furl
# local modules
from rest import rest
from oauth import oauth
from database import Database
# Main class
from user import User
from youtube import YouTube
from youtube import YouTubeTranscriptApi
from youtube import Comment
from youtube import Caption
from code_country import language_code
# from celery import Celery


#Unclassed for moment
def cleaning_each(each):
    if 'videoId' in each['id']:
        each.update({'videoId': each['id']['videoId']})
    elif 'playlistId' in each['id']:
        each.update({'playlistId': each['id']['playlistId']})
    elif 'channelId' in each['id']:
        each.update({'channelId': each['id']['channelId']})
    return each

def cleaning_ytb_input(id_video):
    if 'youtube.com/watch?v=' in id_video:
        if 'https' in id_video:
            id_video = id_video.replace(
                'https://www.youtube.com/watch?v=', '')
        else:
            id_video = id_video.replace(
                'http://www.youtube.com/watch?v=', '')
    elif 'youtube.com/channel/' in id_video:
        if 'https' in id_video:
            id_video = id_video.replace(
                'https://www.youtube.com/channel/', '')
        else:
            id_video = id_video.replace(
                'http://www.youtube.com/channel/', '')
    #elif 'youtube.com/watch?v=' in id_video:
    return id_video

def create_app():
    with open('conf/conf.json') as conf_file:
        conf_data = json.load(conf_file)
        app = Flask(__name__)
        app.register_blueprint(rest)
        app.register_blueprint(oauth)
        app.config['DATA_DIR'] = conf_data['DATA_DIR']
        app.config['PORT'] = conf_data['PORT']
        app.config['MONGO_HOST'] = conf_data['MONGO_HOST']
        app.config['MONGO_DBNAME'] = conf_data['MONGO_DBNAME']
        app.config['MONGO_PORT'] = conf_data['MONGO_PORT']
        app.config['api_key'] = conf_data['api_key']
        app.config['oauth_status'] = conf_data['oauth_status']
        Bootstrap(app)
        app.config['debug_level'] = conf_data['debug_level']
        return app

try:
    app = create_app()
    mongo_curs = Database().init_mongo(app)
    data_dir = app.config['DATA_DIR']
    # fixed this parameter until real charge management (if necessary)
    maxResults = 50
except BaseException as error:
    print('An exception occurred : {}'.format(error))

@app.before_request
def before_request():
    try:
        # entering api_key manually if exist in conf file
        if app.config['api_key']:
            session['api_key'] = app.config['api_key']
        # tricky way to get URL 404 etc. rooting as I want
        if 'access_token' not in session:
            if app.config['oauth_status'] == 'False':
                app.config['MONGO_HOST'] = 'localhost'
                session['profil'] = {
                      'roles': ['ROLE_ADMIN', 'ROLE_USER'],
                      'username': 'test_user',
                      'id': 'foo'
                      }
                r_access_bypass = json.dumps(session['profil'])
                current_user = User(mongo_curs)
                current_user.create_or_replace_user_cortext(r_access_bypass)
                return
            else:
                if request.endpoint is None:
                    return redirect(url_for('oauth.login'))
                elif 'oauth.auth' in request.endpoint:
                    return 
                elif 'oauth.grant' in request.endpoint:
                    return 
                elif 'oauth.login' not in request.endpoint:
                    return redirect(url_for('oauth.login'))
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
            id_video = cleaning_ytb_input(id_video)
            part = ', '.join(request.form.getlist('part'))
            api = YouTube(api_key=session['api_key'])
            video_result = api.get_query('videos', id=id_video, part=part)
            video_result_string = json.dumps(
                video_result, sort_keys=True, indent=2, separators=(',', ': '))
            return render_template('methods/view_results.html', result=video_result, string=video_result_string)
        else:
            return render_template('explore.html', message='api key not set')
    return render_template('explore.html')

@app.route('/channel_info', methods=['POST'])
def channel_info():
    if request.method == 'POST':
        if 'api_key' in session:
            id_channel = request.form.get('unique_id_channel')
            id_channel = cleaning_ytb_input(id_channel)
            if 'youtube.com/user/' in id_channel:
                return render_template('explore/channel_info.html', message='YoutubeAPI cannot retrieve user (different from channel)...')
            part = ', '.join(request.form.getlist('part'))
            api = YouTube(api_key=session['api_key'])
            channel_result = api.get_query(
                'channels', id=id_channel, part=part)
            channel_result_string = json.dumps(
                channel_result, sort_keys=True, indent=2, separators=(',', ': '))
            return render_template('methods/view_results.html', result=channel_result, string=channel_result_string)
        else:
            return render_template('explore.html', message='api key not set')
    return render_template('explore.html')

@app.route('/playlist_info', methods=['POST'])
def playlist_info():
    if request.method == 'POST':
        if 'api_key' in session:
            id_playlist = request.form.get('unique_id_playlist')
            # remember to make same as for cleanning_ytb
            if 'youtube.com/watch?v=' in id_playlist:
                f = furl(id_playlist)
                id_playlist = f.args['list']
            part = ', '.join(request.form.getlist('part'))
            api = YouTube(api_key=session['api_key'])
            playlist_info = api.get_query(
                'playlists', id=id_playlist, part=part)
            playlist_info_string = json.dumps(
                playlist_info, sort_keys=True, indent=2, separators=(',', ': '))
            return render_template('methods/view_results.html', result=playlist_info, string=playlist_info_string)
        else:
            return render_template('explore.html', message='api key not set')
    return render_template('explore.html')


##########################################################################
# Download
##########################################################################
@app.route('/videos-list', methods=['POST', 'GET'])
def video():
    if request.method == 'POST':
        if 'api_key' in session:
            api = YouTube(api_key=session['api_key'])
            session['counter'] = 0
            list_videos = request.form.get('list_videos')
            list_videos = list_videos.splitlines()
            list_videos = [ cleaning_ytb_input(x) for x in list_videos]

            list_results = {'items': [] }
            for id_video in list_videos:
                part = ', '.join(request.form.getlist('part'))                
                video_result = api.get_query('videos', id=id_video, part=part)
                list_results['items'].append(video_result['items'][0])

            session['request'] = {
                'list_videos': list_videos,
                'name_query': str(request.form.get('name_query')),
                'part': ', '.join(request.form.getlist('part'))
            }

            if 'nextPageToken' in list_results:
                previous_token = list_results['nextPageToken']
            
            list_results_string = json.dumps(
                list_results, sort_keys=True, indent=4, separators=(',', ': ')
            )
            return render_template('methods/view_results.html', results=list_results, string=list_results_string,  counter=session['counter'])
        else:
            return render_template('methods/view_results.html', message='api key not set')
    return render_template('download/videos_list.html')

@app.route('/playlist', methods=['POST', 'GET'])
def playlist():
    if request.method == 'POST':
        id_playlist = cleaning_ytb_input(request.form.get('id'))
        session['counter'] = 0
        session['request'] = {
            'part': ', '.join(request.form.getlist('part')),
            'playlistId': id_playlist,
            'maxResults': maxResults
        }

        playlist_results = YouTube.get_playlist(
            session['api_key'], session['request'])
        results_string = json.dumps(
            playlist_results, sort_keys=True, indent=4, separators=(',', ': '))

        return render_template('methods/view_results.html', results=playlist_results, string=results_string, counter=session['counter'])

    # Go to next page
    elif request.method == 'GET' and request.args.get('nextPageToken'):
        session['counter'] += 1
        pageToken = request.args.get('nextPageToken')
        session['pageToken'] = pageToken
        playlist_results = YouTube.get_channel(
            session['api_key'], session['request'])
        results_string = json.dumps(
            playlist_results, sort_keys=True, indent=2, separators=(',', ': ')
        )
        return render_template('methods/view_results.html', results=playlist_results, string=results_string, counter=session['counter'])
    return render_template('download/playlist.html')

@app.route('/channel', methods=['POST', 'GET'])
def channel():
    if request.method == 'POST':
        id_channel = cleaning_ytb_input(request.form.get('id'))
        session['counter'] = 0
        session['request'] = {
            'part': ', '.join(request.form.getlist('part')),
            'channelId': id_channel,
            # 'forUsername': ', '.join(request.form.getlist('forUsername')),
            # 'categoryId': request.form.get('categoryId'),
            'maxResults': maxResults
        }

        channel_results = YouTube.get_channel(
            session['api_key'], session['request'])
        results_string = json.dumps(
            channel_results, sort_keys=True, indent=4, separators=(',', ': '))

        return render_template('methods/view_results.html', results=channel_results, string=results_string, counter=session['counter'])

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
        return render_template('methods/view_results.html', results=channel_results, string=results_string, counter=session['counter'])
    return render_template('download/channel.html', language_code=language_code)

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
                    'maxResults': maxResults,
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
                        'maxResults': maxResults,
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
                    maxResults=maxResults,
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
                        maxResults=maxResults,
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
                                maxResults=maxResults,
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
                    'maxResults': maxResults,
                    'ranking': request.form.get('ranking')
                }
                search_results = YouTube.get_search(
                    session['api_key'], session['request'])
                previous_token = search_results['nextPageToken']
                search_results_string = json.dumps(
                    search_results, sort_keys=True, indent=4, separators=(',', ': '))
                return render_template('methods/view_results.html', results=search_results, string=search_results_string, counter=session['counter'], prev=previous_token)

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
        return render_template('methods/view_results.html', results=search_results, string=search_results_string, counter=session['counter'], prev=pageToken)
    return render_template('download/search.html', language_code=language_code)



##########################################################################
# Aggregate
##########################################################################
@app.route('/aggregate', methods=['POST', 'GET'])
def aggregate():
    stats = {    
            'list_queries': [],
        }

    if request.method == 'GET':
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
            doc['countVideos'] = countVideos.count()
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
                        {"$or" : [ {"id": {"$type": "string"}}, {"videoId": {"$exists": "True"}} ]} ,
                        {"query_id": query_id}
                    ]
                }
            )

            list_vid = []
            # absolutely need to fix this later
            for result in results:
                if 'videoId' in result:
                    id_video = result['videoId']
                else:
                    id_video = result['id']

                list_vid.append(id_video)
                query_id = result['query_id']
                
                if 'captions' in options_api:
                    current_captions = Caption(mongo_curs, query_id)
                    current_captions.create_if_not_exist(id_video)

                if 'comments' in options_api:
                    current_comment_thread = Comment(mongo_curs, query_id)
                    for id_video in list_vid:
                        commentThreads_result = api.get_query(
                            'commentThreads',
                            videoId=id_video,
                            part='id, replies, snippet')
                        current_comment_thread.create_comment_for_each(commentThreads_result)
                        ## Loop and save
                        while 'nextPageToken' in commentThreads_result:
                            commentThreads_result = api.get_query(
                                'commentThreads',
                                videoId=id_video,
                                part='id, replies, snippet',
                                pageToken=commentThreads_result['nextPageToken'])
                            current_comment_thread.create_comment_for_each(commentThreads_result)
            # if 'metrics' in options_api:
            #     current_query = Comment(mongo_curs, query_id)
            #     for id_video in list_vid:
            #         print(id_video)
            #         video_result = api.get_query('videos', id=id_video, part=part)
            #         current_query.add_stats_for_each_entry(video_result)

            return render_template('methods/download_process.html', message='ok it is done')

    return render_template('aggregate.html', stats=stats)

    #return render_template('aggregate.html', message='hmmm it seems to have a bug on dir_path...')

##########################################################################
# processing results uesd by /search and /aggregate
##########################################################################
@app.route('/process_results')
def process_results():
    uid = uuid4()
    api = YouTube(api_key=session['api_key'])
    session['counter'] = 0
    #### /!\ Need to refact functions here ! /!\ ####
    # 3 cases : arbitrary list of vids OR search list OR channel list
    if 'list_videos' in session['request']:
        list_results = {'items': [] }
        
        for id_video in session['request']['list_videos']:
            part = session['request']['part']
            video_result = api.get_query('videos', id=id_video, part=part)
            list_results['items'].append(video_result['items'][0])

        mongo_curs.db.query.insert_one(
            {
                'author_id': session['profil']['id'],
                'query_id': str(uid),
                'query': session['request']['name_query'] ,
                'part': session['request']['part'],
            }
        )

        for each in list_results['items']:
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

    elif 'q' in session['request'] :
        # build request based on session
        search_results = api.get_query(
            'search',
            q=session['request']['q'],
            part=session['request']['part'],
            language=session['request']['language'],
            maxResults=maxResults,
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
                'maxResults': maxResults,
                'ranking': session['request']['ranking'],
            }
        )
        # insert videos
        for each in search_results['items']:
            each.update({'query_id': str(uid)})
            # thing is search query can provide video, an playlist id...
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
                maxResults=maxResults,
                ranking=session['request']['ranking'],
                pageToken=search_results['nextPageToken']
            )
            if not search_results['items']:
                return render_template('methods/download_process.html', message='ok it is done')

            # insert video-info
            for each in search_results['items']:
                each.update({'query_id': str(uid)})
                each = cleaning_each(each)
                mongo_curs.db.videos.insert_one(each)

    elif 'channelId' in session['request']:
        # build request based on session
        channel_results = api.get_query(
            'search',
            channelId=session['request']['channelId'],
            part=session['request']['part'],
            maxResults=maxResults
        )
        # insert query
        mongo_curs.db.query.insert_one(
            {   
                'author_id':session['profil']['id'],
                'query_id': str(uid),
                'channel_id': session['request']['channelId'],
                'part': session['request']['part'],
                'maxResults': maxResults,
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
                maxResults=maxResults,
                pageToken=channel_results['nextPageToken']
            )
            if not channel_results['items']:
                return render_template('methods/download_process.html', message='ok it is done')

            # insert video-info
            for each in channel_results['items']:
                each.update({'query_id': str(uid)})
                each = cleaning_each(each)
                mongo_curs.db.videos.insert_one(each)

    elif 'playlistId' in session['request']:
        # build request based on session
        playlist_results = api.get_query(
            'search',
            playlistId=session['request']['playlistId'],
            part=session['request']['part'],
            maxResults=maxResults
        )
        # insert query
        mongo_curs.db.query.insert_one(
            {   
                'author_id':session['profil']['id'],
                'query_id': str(uid),
                'playlist_id': session['request']['playlistId'],
                'part': session['request']['part'],
                'maxResults': maxResults,
            }
        )
        # insert videos
        for each in playlist_results['items']:
            each.update({'query_id': str(uid)})
            if 'snippet' in each:
                if 'videoId' in each['contentDetails']:
                    each['snippet'].update({'videoId': each['contentDetails']['videoId']})
                elif 'playlistId' in each['contentDetails']:
                    each['snippet'].update({'playlistId' : each['contentDetails']['playlistId']})
            elif 'videoId' in each['contentDetails']:
                each.update({'videoId': each['contentDetails']['videoId']})
            elif 'playlistId' in each['contentDetails']:
                each.update({'playlistId': each['contentDetails']['playlistId']})
            mongo_curs.db.videos.insert_one(each)
        ## Loop and save
        while 'nextPageToken' in playlist_results:
            session['counter'] += 1
            name_file = str(session['counter']) + '.json'
            playlist_results = api.get_query(
                'search',
                playlistId=session['request']['playlistId'],
                part=session['request']['part'],
                maxResults=maxResults,
                pageToken=playlist_results['nextPageToken']
            )
            if not playlist_results['items']:
                return render_template('methods/download_process.html', message='ok it is done')

            # insert video-info
            for each in playlist_results['items']:
                each.update({'query_id': str(uid)})
                each = cleaning_each(each)
                mongo_curs.db.videos.insert_one(each)

    return render_template('methods/download_process.html', message='ok it is done')


##########################################################################
# Manage
##########################################################################
@app.route('/manage', methods=['POST', 'GET'])
def manage():
    if request.method == 'GET':
        result = mongo_curs.db.query.find({
            'author_id': session['profil']['id']
        })
        list_queries = []

        for doc in result:
            doc['countVideos'] = mongo_curs.db.videos.find(
                {'query_id': doc['query_id']}).count()
            doc['countComments'] = mongo_curs.db.comments.find(
                {'query_id': doc['query_id']}).count()
            doc['countCaptions'] = mongo_curs.db.captions.find(
                {'id_query': doc['query_id']}).count()
            list_queries.append(doc)

        if 'ROLE_ADMIN' in session['profil']['roles']:
            stats = {
                'query_totalCount': mongo_curs.db.query.find({}).count(),
                'videos': mongo_curs.db.videos.find({}).count(),
                'comments': mongo_curs.db.comments.find({}).count(),            
                'list_queries': list_queries,
                'message' : 'admin roles should be able to see counted db'
            }
        else:
            videos_count = 0
            comments_count = 0
            for each in list_queries:
                videos_count += mongo_curs.db.videos.find({
                    'query_id' : each['query_id']
                }).count()
                comments_count += mongo_curs.db.comments.find({
                    'query_id' : each['query_id']
                }).count()

            stats = {
                'query_totalCount': mongo_curs.db.query.find({
                    'author_id': session['profil']['id']
                    }).count(),
                'videos': videos_count,
                'comments': comments_count,            
                'list_queries': list_queries
            }

    return render_template('manage.html', stats=stats)

##########################################################################
# View db
##########################################################################
@app.route('/view-videos/<query_id>', methods=['POST','GET'])
def view_videos(query_id):
    #34cd696a-0d24-4ba0-9351-fbe8fdd80348
    
    r = requests.get('http://127.0.01:8081/queries/' + query_id + '/videos/')
    print(r.text)
    return render_template('view.html', list_queries=r.json())

@app.route('/view-comments/<query_id>', methods=['POST','GET'])
def view_comments(query_id):
    #34cd696a-0d24-4ba0-9351-fbe8fdd80348
    
    r = requests.get('http://127.0.01:8081/queries/' + query_id + '/comments/')
    print(r.text)
    return render_template('view.html', list_queries=r.json())

@app.route('/view-captions/<query_id>', methods=['POST','GET'])
def view_captions(query_id):
    #34cd696a-0d24-4ba0-9351-fbe8fdd80348
    
    r = requests.get('http://127.0.01:8081/queries/' + query_id + '/captions/')
    print(r.text)
    return render_template('view.html', list_queries=r.json())
##########################################################################
# Export
##########################################################################
@app.route('/export', methods=['POST', 'GET'])
def export():
    if request.method == 'GET':
        result = mongo_curs.db.query.find({
            'author_id': session['profil']['id']
        })
        list_queries = []

        for doc in result:
            doc['countVideos'] = mongo_curs.db.videos.find(
                {'query_id': doc['query_id']}).count()
            doc['countComments'] = mongo_curs.db.comments.find(
                {'query_id': doc['query_id']}).count()
            doc['countCaptions'] = mongo_curs.db.captions.find(
                {'id_query': doc['query_id']}).count()
            list_queries.append(doc)

    return render_template('export.html', list_queries=list_queries)


##########################################################################
# Config
##########################################################################
@app.route('/config', methods=['POST', 'GET'])
def config():

    json_formated = json.dumps(session['profil'], indent=2) 

    if not 'api_key' in session:
       api_key_validate = 'You need an API KEY from youtube'
    else:
       api_key_validate = session['api_key']

    if request.method == 'POST':
        if request.form.get('api_key'):
            session['api_key'] = request.form.get('api_key')
            return redirect(url_for('home'))

    return render_template('config.html', session_data=json_formated, message=api_key_validate)

##########################################################################
# Reset session
##########################################################################
@app.route('/reset', methods=['GET'])
def reset():
    session.clear()
    return redirect(url_for('oauth.login'))

##########################################################################
# Start
##########################################################################
if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.secret_key = os.urandom(24)
    app.run(debug=app.config['debug_level'], host='0.0.0.0', port=app.config['PORT'], threaded=True )
