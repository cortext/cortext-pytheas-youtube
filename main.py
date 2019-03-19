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
from flask import jsonify
# Ext lib
# from flask_bootstrap import Bootstrap
from furl import furl
# local modules
from oauth import oauth
from database import Database
# Main class
from user import User
from youtube import YouTube
from youtube import YouTubeTranscriptApi
from youtube import Comment
from youtube import Caption
from youtube import Video
from code_country import language_code
# from celery import Celery

def create_app():
    with open('conf/conf.json') as conf_file:
        conf_data = json.load(conf_file)
        app = Flask(__name__)
        app.register_blueprint(oauth)
        app.config['DATA_DIR'] = conf_data['DATA_DIR']
        app.config['PORT'] = conf_data['PORT']
        app.config['MONGO_HOST'] = conf_data['MONGO_HOST']
        app.config['MONGO_DBNAME'] = conf_data['MONGO_DBNAME']
        app.config['MONGO_PORT'] = conf_data['MONGO_PORT']
        app.config['MONGO_URI'] = "mongodb://mongod:"+str(conf_data['MONGO_PORT'])+"/"+conf_data['MONGO_DBNAME']
        app.config['REST_URL'] = 'http://' + conf_data['REST_HOST'] + ':' + str(conf_data['REST_PORT']) + '/'
        app.config['api_key_test'] = conf_data['api_key_test']
        app.config['api_key'] = conf_data['api_key']
        app.config['oauth_status'] = conf_data['oauth_status']
        app.config['debug_level'] = conf_data['debug_level']
    return app

try:
    app = create_app()
    mongo_curs = Database().init_mongo(app)
    data_dir = app.config['DATA_DIR']
    # fixed this parameter until real charge management (if necessary)
    maxResults = 50
except BaseException as error:
    app.logger.debug('An exception occurred : {}'.format(error))

@app.before_request
def before_request():
    try:
        # entering api_key manually if exist in conf file
        if app.config['api_key']:
            session['api_key'] = app.config['api_key']
        # tricky way to get URL 404 etc. rooting as I want
        if 'access_token' not in session:
            # and here to bypass oauth for debug purpose
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
        # else nothing let continue  
    except BaseException as e:
        app.logger.debug(e)


if app.config['debug_level'] == 'False':
    @app.errorhandler(Exception)
    def page_not_found(error):
        app.logger.debug(error)
        return render_template('structures/error.html', error=error)


@app.route('/')
def home():
    user_info = session['profil']
    if 'api_key' in session:
        api_key = session['api_key']
    else:
        return render_template('home.html', user_info=user_info)
    return render_template('home.html', user_info=user_info, api_key=api_key)

##########################################################################
# Explore  
##########################################################################
@app.route('/explore', methods=['GET'])
def browse():
    return render_template('explore.html')

@app.route('/video_info', methods=['POST'])
def video_info():
    if request.method == 'POST':
        # specific for 'try it' on /
        # since it is my own api_key used for now...
        if request.form.get('api_key_test') is not None:
            api_key = app.config['api_key_test']
        elif 'api_key' in session:
            api_key = session['api_key']
        else:
            return render_template('explore.html', message="""
                <h4><strong class="text-danger">You can try Pytheas but to go further you will need to get an api_key from Google services
                <br>Please go to <a href="./config" class="btn btn-primary btn-lg active" role="button" aria-pressed="true">Config</a> and follow guidelines</strong></h4>
                """)

        id_video = request.form.get('unique_id_video')
        id_video = YouTube.cleaning_video(id_video)
        part = ', '.join(request.form.getlist('part'))
        api = YouTube(api_key=api_key)
        video_result = api.get_query('videos', id=id_video, part=part)
        video_result_string = json.dumps(
            video_result, sort_keys=True, indent=2, separators=(',', ': '))
        return render_template('methods/view_results.html', result=video_result, string=video_result_string)
    return render_template('explore.html')

@app.route('/channel_info', methods=['POST'])
def channel_info():
    if request.method == 'POST':
        if 'api_key' in session:
            id_channel = request.form.get('unique_id_channel')
            id_username = request.form.get('unique_user_channel')
            part = ', '.join(request.form.getlist('part'))
            api = YouTube(api_key=session['api_key'])

            if 'youtube.com/channel/' in id_channel:
                id_channel = YouTube.cleaning_channel(id_channel)
                channel_result = api.get_query(
                'channels',  id=id_channel, part=part)
            elif id_username != '':
                id_username = YouTube.cleaning_channel(id_username)
                channel_result = api.get_query(
                    'channels', forUsername=id_username, part=part)
            else:
                channel_result = api.get_query(
                'channels',  id=id_channel, part=part)

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
# start Download
##########################################################################
@app.route('/get-data', methods=['POST', 'GET'])
def get_data():
    return render_template('get_data.html', language_code=language_code)

@app.route('/videos-list', methods=['POST'])
def video():
    if request.method == 'POST':
        uid = str(uuid4())
        if 'api_key' in session:
            api = YouTube(api_key=session['api_key'])
            
            list_videos = request.form.get('list_videos')
            list_videos = list_videos.splitlines()
            list_videos = [ YouTube.cleaning_video(x) for x in list_videos ]
            
            list_results = {'items': [] }

            for id_video in list_videos:
                part = ', '.join(request.form.getlist('part'))                
                video_result = api.get_query('videos', id=id_video, part=part)
                list_results['items'].append(video_result['items'][0])

            name_query = str(request.form.get('name_query'))
            mongo_curs.db.queries.insert_one(
                {
                    'author_id': session['profil']['id'],
                    'query_id': uid,
                    'query': name_query,
                    'part': part,
                }
            )

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

        else:
            return render_template('explore.html', message='api key not set')
    return redirect(url_for('manage'))

@app.route('/playlist', methods=['POST'])
def playlist():
    if request.method == 'POST':
        if not 'api_key' in session:
            return render_template('explore.html', message='api key not set')

        query_id = str(uuid4())
        list_playlist = request.form.getlist('list_url')        
        query_name = str(request.form.get('query_name'))
        part = ', '.join(request.form.getlist('part'))
        param = {
            'part': part,
            'maxResults': maxResults,
            'query_id' : query_id,
            'query': query_name
        }

        # insert query
        mongo_curs.db.queries.insert_one(
            {   
                'author_id': session['profil']['id'],
                'query_id': query_id,
                'query': query_name,
                'playlist_id': list_playlist,
                'part': part,
                'maxResults': maxResults,
            }
        )

        for playlist_id in list_playlist:
            param.update({'playlist_id' : playlist_id})
            
            # call request
            api = YouTube(api_key=session['api_key'])
            playlist_results = api.get_playlist(mongo_curs, param)
            
        # add metrics for query in json
        count_videos = int(mongo_curs.db.videos.find({'query_id': query_id}).count())
        mongo_curs.db.queries.update_one(
            { 'query_id': query_id },
            { '$set': {'count_videos': count_videos } }
        )

        return redirect(url_for('manage'))

@app.route('/channel', methods=['POST'])
def channel():
    if request.method == 'POST':
        if not 'api_key' in session:
            return render_template('explore.html', message='api key not set')
        query_id = str(uuid4())
        list_channel = request.form.getlist('list_url')        
        query_name = str(request.form.get('query_name'))
        part = ', '.join(request.form.getlist('part'))
        param = {
            'part': part,
            'maxResults': maxResults,
            'query_id': query_id,
            'query': query_name
        }   

        # insert query
        mongo_curs.db.queries.insert_one(
            {   
                'author_id': session['profil']['id'],
                'query_id': query_id,
                'query': query_name,
                'channel_id': list_channel,
                'part': part,
                'maxResults': maxResults,
            }
        )

        for channel_id in list_channel:
            param = {
                'part': part,
                'maxResults': maxResults,
                'query_id': query_id,
                'query': query_name
            }  
            # tricks to detect username or channel id
            # need to refact with cleaning_channel methods (also used in /explore)

            if '/channel/' in channel_id:
                channel_id = YouTube.cleaning_channel(channel_id)
                app.logger.debug('channel////////')
                param.update({'channelId' : channel_id})

            if '/c/' in channel_id:
                app.logger.debug('c///////')
                channel_id = YouTube.cleaning_channel(channel_id)
                param.update({'forUsername' : channel_id})

            if '/user/' in channel_id:
                app.logger.debug('user//////')
                channel_id = YouTube.cleaning_channel(channel_id)
                param.update({'forUsername' : channel_id})
            
            app.logger.debug(param)
            # call request
            api = YouTube(api_key=session['api_key'])
            channel_results = api.get_channel_videos(mongo_curs, param)
            
        # add metrics for query in json
        count_videos = int(mongo_curs.db.videos.find({'query_id': query_id}).count())
        mongo_curs.db.queries.update_one(
            { 'query_id': query_id },
            { '$set': {'count_videos': count_videos } }
        )

        return redirect(url_for('manage'))

@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        if not 'api_key' in session:
            return render_template('download/search.html', message='api key not set')
        session['counter'] = 0
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
                'order': request.form.get('order'),
                'publishedAfter': st_point,
                'publishedBefore': ed_point
            }

            # insert query in mongo
            uid = str(uuid4())
            mongo_curs.db.queries.insert_one(
                {
                    'query_id': uid,
                    'author_id':session['profil']['id'],
                    'query': session['request']['q'],
                    'part': session['request']['part'],
                    'language': session['request']['language'],
                    'maxResults': maxResults,
                    'order': session['request']['order'],
                    'date_start': session['request']['publishedAfter'],
                    'date_end': session['request']['publishedBefore']
                }
            )

            # Parse date time from form
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
                    order=session['request']['order'],
                    publishedAfter=session['request']['publishedAfter'],
                    publishedBefore=session['request']['publishedBefore'])

                # check if ['items'] exist and not empty 
                # https://thispointer.com/python-how-to-check-if-a-key-exists-in-dictionary/
                #if date_results.get('items', -1) != -1:
                    # insert videos in db
                
                for each in date_results['items']:
                    each.update({'query_id': uid})
                    each = YouTube.cleaning_each(each)
                    mongo_curs.db.videos.insert_one(each)

                # while len(date_results['items']) > 0 : 
                #if not 'nextPageToken' in date_results:
                #if date_results.get('nextPageToken', -1) != -1:
                #while 'nextPageToken' in date_results:
                app.logger.debug( ' LEN ITEMSSSS ::::::=>' + str(len(date_results['items']))) 
                # if not 'nextPageToken' in date_results:
                #     while 'nextPageToken' in date_results:
                while 'nextPageToken' in date_results and len(date_results['items']) != 0:
                    date_results = api.get_query(
                        'search',
                        q = session['request']['q'],
                        part = session['request']['part'],
                        language = session['request']['language'],
                        maxResults = maxResults,
                        order = session['request']['order'],
                        publishedAfter = session['request']['publishedAfter'],
                        publishedBefore = session['request']['publishedBefore'],
                        pageToken = date_results['nextPageToken']
                        )
                    # insert video-info except if last result
                    # only if "items" not empty 
                    #if date_results.get('items', -1) != -1:
                    for each in date_results['items']:
                        each.update({'query_id': uid})
                        each = YouTube.cleaning_each(each) 
                        mongo_curs.db.videos.insert_one(each)

                # finally increment next after day
                r_after += dt.timedelta(days=1)

            count_videos = int(mongo_curs.db.videos.find({'query_id': uid}).count())
            mongo_curs.db.queries.update_one(
                { 'query_id': uid },
                { '$set': {'count_videos': count_videos } }
            )
 
            return redirect(url_for('manage'))

        # to integrate later to get global dated search (not one day/one day) 
        # elif
        #     #  request
        #     date_results = api.get_query(
        #         'search',
        #         q=session['request']['q'],
        #         part=session['request']['part'],
        #         language=session['request']['language'],
        #         maxResults=maxResults,
        #         order=session['request']['order'],
        #         publishedAfter=session['request']['publishedAfter'],
        #         publishedBefore=session['request']['publishedBefore']) 
        else:
            session['request'] = {
                'q': request.form.get('query'),
                'part': ', '.join(request.form.getlist('part')),
                'language': request.form.get('language'),
                'maxResults': maxResults,
                'order': request.form.get('order')
            }
            search_results = YouTube.get_search(
                session['api_key'], session['request'])
            previous_token = search_results['nextPageToken']
            search_results_string = json.dumps(
                search_results, sort_keys=True, indent=4, separators=(',', ': '))

            return render_template('methods/view_results.html', results=search_results, string=search_results_string, counter=session['counter'], prev=previous_token)
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
@app.route('/complete-data', methods=['POST', 'GET'])
def complete_data():
    list_queries = []

    if request.method == 'GET':
        result = requests.get(app.config['REST_URL']+ session['profil']['id'] +'/queries/')
        result = result.json()
        for doc in result:
            # add count
            # and for db compatibilty need to 
            if 'count_videos' in doc:
                doc['countVideos'] = doc['count_videos']
            else:
                doc['countVideos'] = '0'
            list_queries.append(doc)
    return render_template('complete_data.html', list_queries=list_queries)


@app.route('/aggregate', methods=['POST', 'GET'])
def aggregate():
    stats = {    
            'list_queries': [],
        }

    if request.method == 'GET':
        result = requests.get(app.config['REST_URL']+ session['profil']['id'] +'/queries/')
        result = result.json()
        for doc in result:
            # add count
            # and for db compatibilty need to 
            if 'count_videos' in doc:
                doc['countVideos'] = doc['count_videos']
            else:
                doc['countVideos'] = 'NA'
            stats['list_queries'].append(doc)
        
    if request.method == 'POST':
        if request.form and request.form.get('optionsRadios'):

            ## NEED TO REFACT HERE FOR CAPTIONS DATA...
            query_id = request.form.get('optionsRadios')
            options_api = request.form.getlist('api_part')
            part = ', '.join(request.form.getlist('part'))


            app.logger.debug(str(options_api))

            api_key = session['api_key']
            api = YouTube(api_key=api_key)
            # qui ont un id de type str ou un id video qui existe
            # ET un id query
            results = mongo_curs.db.videos.find(
                {
                    "$and": [
                        {"$or" : [ {"id": {"$type": "string"}}, {"id.videoId": {"$exists": "True"}} ]} ,
                        {"query_id": query_id}
                    ]
                }
            )

            list_vid = []
            # need to fix this later

            for result in results:
                if 'videoId' in result:
                    id_video = result['videoId']
                else:
                    app.logger.debug(result)
                    id_video = result['id']['videoId']

                list_vid.append(id_video)
                query_id = result['query_id']

            if 'captions' in options_api:
                # WIP
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
            
            if 'statistics' in options_api:
                # Here we will just add 'statistics' part from youtube to our videos set
                # also we have to work with unique object id instead of id_video to avoid duplicate etc.
                ressources_id = [item['_id'] for item in results]
                app.logger.debug(str(results))

                current_query = Video(mongo_curs)
                for ressource_id in ressources_id:
                    # after ressources id taking videoId
                    get_video_by_id = current_query.get_one_video(ressource_id)
                    video_result = api.get_query('videos', id=get_video_by_id['videoId'], part='statistics')
                    #call add_stats to update()
                    current_query.add_stats_for_each_entry(video_result, ressource_id)



            return redirect(url_for('manage'))

    return render_template('aggregate.html', stats=stats)

##########################################################################
# processing results uesd by /search and /aggregate
##########################################################################
@app.route('/process_results')
def process_results():
    uid = str(uuid4())
    api = YouTube(api_key=session['api_key'])
    session['counter'] = 0

    if 'q' in session['request'] :
        # build request based on session
        search_results = api.get_query(
            'search',
            q=session['request']['q'],
            part=session['request']['part'],
            language=session['request']['language'],
            maxResults=maxResults,
            order=session['request']['order']
        )

        # insert query
        mongo_curs.db.queries.insert_one(
            {
                'author_id':session['profil']['id'],
                'query_id': uid,
                'query': session['request']['q'],
                'part': session['request']['part'],
                'language': session['request']['language'],
                'maxResults': maxResults,
                'order': session['request']['order'],
            }
        )
        # insert videos
        for each in search_results['items']:
            each.update({'query_id': uid})
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
                order=session['request']['order'],
                pageToken=search_results['nextPageToken']
            )
            if not search_results['items']:
                # add metrics for query in json
                count_videos = int(mongo_curs.db.videos.find({'query_id': uid}).count())
                mongo_curs.db.queries.update_one(
                    { 'query_id': uid },
                    { '$set': {'count_videos': count_videos } }
                )
                return redirect(url_for('manage'))

            # insert video-info
            for each in search_results['items']:
                each.update({'query_id': uid})
                each = YouTube.cleaning_each(each)
                mongo_curs.db.videos.insert_one(each)

        return redirect(url_for('manage'))
    return redirect(url_for('manage'))

##########################################################################
# Documentation
##########################################################################
@app.route('/documentation', methods=['GET'])
def documentation():
    return render_template('documentation.html')

##########################################################################
# Manage
##########################################################################
@app.route('/manage', methods=['POST', 'GET'])
def manage():
    if request.method == 'GET':
        # get all query fur user
        r = requests.get(app.config['REST_URL'] + session['profil']['id'] + '/queries/')
        result = r.json()
        list_queries = []

        for doc in result:
            # verify if count
            if 'count_videos' in doc:
                doc['countVideos'] = doc['count_videos']
            else:
                doc['countVideos'] = 'NC'
            
            if 'count_comments' in doc:
                doc['countComments'] = doc['count_comments']
            else:
                doc['countComments'] = 'NC'

            if 'count_captions' in doc:
                doc['countCaptions'] = doc['count_captions']
            else:
                doc['countCaptions'] = 'NC'
            list_queries.append(doc)

        # send all as json, template will manage it
        stats = {
            'list_queries': list_queries
        }

    return render_template('manage.html', stats=stats)

##########################################################################
# Delete dataset
##########################################################################
@app.route('/delete/<query_id>', methods=['GET'])
def delete(query_id):
    # using json_util from dumping querying (see later)
    from bson import json_util

    query = mongo_curs.db.queries.find_one({'query_id': query_id})
    from_query = json.dumps(query, default=json_util.default)
    from_query = json.loads(from_query)
    
    # erase all from query
    for table in ['captions', 'comments', 'videos', 'queries']: 
        mongo_curs.db[table].remove({'query_id': query_id})

    return redirect(url_for('manage'))

##########################################################################
## View in-db human readable
# request by type_data and query_id to rest urls 
# then rendering html template
##########################################################################
@app.route('/view-<data_type>/<query_id>', methods=['POST','GET'])
def view_data_by_type(query_id, data_type):
    if data_type not in ['videos', 'comments', 'captions']:
        redirect(url_for(page_not_found))
    url = app.config['REST_URL']+ session['profil']['id'] +'/queries/' + query_id + '/' + data_type + '/'
    r = requests.get(url)
    return render_template('view.html', list_queries=r.json())

##########################################################################
# Download videos, comments set
##########################################################################
@app.route('/download/<query_type>/<query_id>', methods=['GET'])
def download_videos_by_type(query_id, query_type):
    if query_type not in ['videos', 'comments', 'captions']:
        return redirect(url_for('page_not_found'))
    from bson import json_util

    # find name of query for filename download
    r_name = requests.get(app.config['REST_URL']+session['profil']['id']+'/queries/'+query_id)
    query = r_name.json()
    query_name = str(query['query'])

    # get results
    r = requests.get(app.config['REST_URL']+session['profil']['id']+'/queries/'+query_id+'/'+query_type+'/')
    query_result = r.json()

    import re
    query_name = re.sub('[^A-Za-z0-9]+', '_', query_name)
    app.logger.debug(query_name)
    filename = {'Content-Disposition':'attachment;filename=' + query_name + '.json'}

    # send back response
    response = app.response_class(
        response=json.dumps(query_result),
        status=200,
        mimetype='application/json',
        headers=filename
    )
    return response

    
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

    app.logger.debug(api_key_validate)

    if request.method == 'POST':
        if request.form.get('api_key'):
            session['api_key'] = request.form.get('api_key')
            return redirect(url_for('home'))

    return render_template('config.html', session_data=session['profil'], message=api_key_validate)



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
    app.session_cookie_path = '/'
    app.run(debug=app.config['debug_level'], host='0.0.0.0', port=app.config['PORT'], threaded=True )
