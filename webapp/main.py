# py dependancies
import os
import shutil
import json
import requests
import logging
from uuid import uuid4
from threading import Thread
import re
import zipfile
from io import BytesIO
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
from flask import send_file
# Ext lib
from furl import furl
# local modules
from oauth import oauth
from database import Database
# Main class
from user import User
from youtube import YouTube
from youtube import Video
from code_country import language_code


try:
    app = Flask(__name__)
    app.register_blueprint(oauth)
    app.config['LOG_DIR'] = os.environ['LOG_DIR']
    app.config['DATA_DIR'] = os.environ['DATA_DIR']

    app.config['MONGO_PORT'] = str(os.environ['MONGO_PORT'])
    app.config['REST_PORT'] = str(os.environ['REST_PORT'])
    app.config['PORT'] = str(os.environ['PORT'])
    
    app.config['MONGO_HOST'] = os.environ['MONGO_HOST']
    app.config['MONGO_DBNAME'] = os.environ['MONGO_DBNAME']
    app.config['REST_HOST'] = os.environ['REST_HOST']
    
    app.config['MONGO_URI'] = "mongodb://"+app.config['MONGO_HOST']+":"+app.config['MONGO_PORT']+"/"+app.config['MONGO_DBNAME']
    app.config['REST_URL'] = 'http://' + app.config['REST_HOST'] + ':' + app.config['REST_PORT'] + '/'
    
    app.config['api_key_test'] = os.environ['api_key_test']
    app.config['api_key'] = os.environ['api_key']
    app.config['oauth_status'] = os.environ['oauth_status']
    app.config['debug_level'] = os.environ['debug_level']
    
    mongo_curs = Database().init_mongo(app)
    data_dir = app.config['DATA_DIR']
    # fixed this parameter until real charge management (if necessary)
    maxResults = 50
except BaseException as error:
    # app.logger.debug('An exception occurred : {}'.format(error))
    print("ERROR creating app...")


if app.config['debug_level'] == 'False':
    @app.errorhandler(Exception)
    def page_not_found(error):
        app.logger.debug(error)
        return render_template('structures/error.html', error=error)


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
# Get List of vids
# landing page who will redirect respectively to each of 
# /videos-list 
# /playlist 
# /channel 
# /search
##########################################################################
@app.route('/get-data', methods=['POST', 'GET'])
def get_data():
    return render_template('get_data.html', language_code=language_code)


def allowed_file(filename):
    ALLOWED_EXTENSIONS = ['csv']
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/import_csv', methods=['POST'])
def import_csv():
    import pandas as pd
    if request.files['input_csv_channel']:
        file = request.files['input_csv_channel']
        parsed_file = pd.read_csv(file, delimiter=";")
        # key_type =  ['channel_id', 'channel_username', 'playlist_id', 'video_id', 'search_terms',]

        dataset = {
            'videos' : [],
            'channel': [],
            'search': [],
            'playlistItems': [], 
        }

        for i, value in parsed_file.iterrows():
            if value['type'] == 'videos':
                dataset['videos'].append(value['items'])
            elif value['type'] == 'channel':
                dataset['channel'].append(value['items'])
                            
            elif value['type'] == 'search':
                dataset['search'].append(value['items'])
            
            elif value['type'] == 'playlist_id':
                dataset['playlist_id'].append(value['items'])
    
        if dataset['videos']:
            payload = {
                'query': 'query_name',
                'part': 'id, snippet',
                'videos':dataset['videos'],
            }
            video(payload)
        if dataset['channel']:
            payload = {
                'query': 'query_name',
                'part': 'id, snippet',
                'channel_id':dataset['channel'],
            }
            channel(payload)
        if dataset['playlistItems']:
            payload = {
                'query': 'query_name',
                'part': 'id, snippet',
                'playlist_id':dataset['playlist_id'],
            }
            playlist(payload)
        if dataset['search']:
            payload = {
                'query': 'query_name',
                'part': 'id, snippet',
                'search':dataset['search'],
            }
            search(payload)
    return render_template('methods/download_process.html')

@app.route('/videos-list', methods=['POST'])
def video(payload=None):
    if request.method == 'POST':
        if not 'api_key' in session:
            return render_template('config.html', message='api key not set')
        query_id = str(uuid4())
        user_id = session['profil']['id']
        query_name = str(request.form.get('name_query'))
        part = ', '.join(request.form.getlist('part'))

        # come from input_csv
        if payload:
            query_name = payload['query']
            part = payload['part']
            list_videos = payload['videos']
            list_videos = [ YouTube.cleaning_video(x) for x in list_videos ]
        else:
            list_videos = request.form.get('list_videos').splitlines()
            list_videos = [ YouTube.cleaning_video(x) for x in list_videos ]

        param = {
            'query_id':query_id,
            'query': query_name,
            'part': part,
            'api_key' : session['api_key'],
            'kind': 'videosList',
            'videos':list_videos,
        }
        r_query = requests.post("http://restapp:" + app.config['REST_PORT'] + "/" + user_id + "/add_query/" + query_id, json=param)
        
        def send_request():  
            requests.post("http://restapp:" + app.config['REST_PORT'] + "/" + user_id + "/query/" + query_id + "/add_video/videos", json=param)
        Thread(target=send_request).start()
    return render_template('methods/download_process.html')


@app.route('/playlist', methods=['POST'])
def playlist():
    if request.method == 'POST':
        if not 'api_key' in session:
            return render_template('explore.html', message='api key not set')

        user_id = session['profil']['id']
        query_id = str(uuid4())
        list_playlist = request.form.getlist('list_url_id')        
        query_name = str(request.form.get('query_name'))
        part = ', '.join(request.form.getlist('part'))
        param = {
            'author_id': session['profil']['id'],
            'api_key' : session['api_key'],
            'query_id': query_id,
            'query': query_name,
            'playlist_id': list_playlist,
            'part': part,
            'maxResults': maxResults,
            'kind': 'playlistItems',
        }

        r_query = requests.post("http://restapp:" + app.config['REST_PORT'] + "/" + user_id + "/add_query/" + query_id, json=param)
        
        def send_request():
            requests.post("http://restapp:" + app.config['REST_PORT'] + "/" + user_id + "/query/" + query_id + "/add_video/playlist", json=param)
        Thread(target=send_request).start()

    return render_template('methods/download_process.html')


@app.route('/channel', methods=['POST'])
def channel():
    if request.method == 'POST':
        if not 'api_key' in session:
            return render_template('explore.html', message='api key not set')
        
        user_id = session['profil']['id']
        query_id = str(uuid4())
        query_name = str(request.form.get('query_name'))
        part = ', '.join(request.form.getlist('part'))
        list_channel_username = [YouTube.cleaning_channel(username_or_id) for username_or_id in request.form.getlist('list_username') ]
        list_channel_id = [ YouTube.cleaning_channel(username_or_id) for username_or_id in request.form.getlist('list_id') ]
        list_channel = list_channel_username + list_channel_id
        list_channel_id = list_channel_id[0].splitlines()
        
        param = {
            'author_id': session['profil']['id'],
            'api_key' : session['api_key'],
            'query_id': query_id,
            'query': query_name,
            'channel_id': list_channel_id,
            'channel_username': list_channel_username,
            'part': part,
            'maxResults': maxResults,
            'kind' : 'channelItems',
        }

        r_query = requests.post("http://restapp:" + app.config['REST_PORT'] + "/" + user_id + "/add_query/" + query_id, json=param)

        def send_request():
            requests.post("http://restapp:" + app.config['REST_PORT'] + "/" + user_id + "/query/" + query_id + "/add_video/channel", json=param)
        Thread(target=send_request).start()
        

    return render_template('methods/download_process.html')



@app.route('/search', methods=['POST', 'GET'])
def search():
    # to integrate later to get global dated search (not only one day/one day) 
    if request.method == 'POST':
        if not 'api_key' in session:
            return render_template('download/search.html', message='api key not set')

        query_id = str(uuid4())
        api = YouTube(api_key=session['api_key'])
        user_id = session['profil']['id']
        query =  str(request.form.get('query'))
        part = ','.join(request.form.getlist('part'))
        order = str(request.form.get('order'))
        language = str(request.form.get('language'))

        param = {
                'author_id': session['profil']['id'],
                'api_key' : session['api_key'],
                'query_id': query_id,
                'query': query,
                'part': part,
                'order': order,
                'language': language,
                'maxResults': maxResults,
                'kind' : 'searchResults',
        }

        if request.form.get('advanced'):
            # get date points & convert them
            st_point = request.form.get('startpoint') + 'T00:00:00Z'
            ed_point = request.form.get('endpoint') + 'T00:00:00Z'
            param = {   
                **param,
                'mode' : 'advanced',
                'publishedAfter' : st_point,
                'publishedBefore' : ed_point,
            }
            r_query = requests.post("http://restapp:" + app.config['REST_PORT'] + "/" + user_id + "/add_query/" + query_id, json=param)

            def send_request():
                requests.post("http://restapp:" + app.config['REST_PORT'] + "/" + user_id + "/query/" + query_id + "/add_video/search", json=param)
            Thread(target=send_request).start()

        else:
            r_query = requests.post("http://restapp:" + app.config['REST_PORT'] + "/" + user_id + "/add_query/" + query_id, json=param)

            def send_request():
                requests.post("http://restapp:" + app.config['REST_PORT'] + "/" + user_id + "/query/" + query_id + "/add_video/search", json=param)
            Thread(target=send_request).start()

    return render_template('methods/download_process.html')


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
    
    if request.method == 'GET':
        stats = { 'list_queries': [], }
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
            user_id = session['profil']['id']
            query_id = request.form.get('optionsRadios')
            api_key = session['api_key']

            options_api = request.form.getlist('api_part')
            part = ', '.join(request.form.getlist('part'))
            
            param = {
                'part': part,
                'api_key' : api_key
            }
            
            if 'captions' in options_api:
                def send_request():
                    requests.post("http://restapp:" + app.config['REST_PORT'] + "/" + user_id + "/query/" + query_id + "/add_captions", json=param)
                Thread(target=send_request).start()

            if 'comments' in options_api:
                def send_request():
                    requests.post("http://restapp:" + app.config['REST_PORT'] + "/" + user_id + "/query/" + query_id + "/add_comments", json=param)
                Thread(target=send_request).start()

            if 'related' in options_api:
                def send_request():
                    requests.post("http://restapp:" + app.config['REST_PORT'] + "/" + user_id + "/query/" + query_id + "/add_related", json=param)
                Thread(target=send_request).start()

            if 'statistics' in options_api:
                # r = requests.post("http://restapp:5053/" + user_id + "/query/" + query_id + "/add_statistics", json=param)
                current_query = Video(mongo_curs, api_key=api_key)
                current_query.add_stats_for_each_entry(query_id)

            return render_template('methods/download_process.html')

    return render_template('aggregate.html', stats=stats)


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
        app.logger.debug(app.config['REST_URL'])
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

            if 'count_related' in doc:
                doc['countRelated'] = doc['count_related']
            else:
                doc['countRelated'] = 'NC'
            list_queries.append(doc)

    return render_template('manage.html', stats=list_queries)

# Delete dataset
# should be partially moved to /rest
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

@app.route('/extract_channel/<query_id>', methods=['GET'])
def extract_channel(query_id):
    # find name of query for filename download
    r_name = requests.get(app.config['REST_URL']+session['profil']['id']+'/queries/'+query_id)
    query = r_name.json()
    query_name = re.sub('[^A-Za-z0-9]+', '_', str(query['query']))
    filename = query_name + '_unique_channel'

    # extract channel mongo query
    query_result = mongo_curs.db['videos'].distinct("snippet.channelId", {'query_id': query_id})

    # zip
    # have to switch to "with opens()" forms because more safe closing file style
    in_memory = BytesIO()
    zf = zipfile.ZipFile(in_memory, mode="w", compression=zipfile.ZIP_DEFLATED)
    zf.writestr(filename + '.json', json.dumps(query_result))
    zf.close()
    in_memory.seek(0)
    data = in_memory.read()

    return Response(data,
            mimetype='application/zip',
            headers={'Content-Disposition':'attachment;filename='+filename+'.zip'})

@app.route('/extract_related/<query_id>', methods=['GET'])
def extract_related(query_id):
    # find name of query for filename download
    r_name = requests.get(app.config['REST_URL']+session['profil']['id']+'/queries/'+query_id)
    query = r_name.json()
    query_name = re.sub('[^A-Za-z0-9]+', '_', str(query['query']))
    filename = query_name + '_related_videos'

    # extract related rest query
    r = requests.get(app.config['REST_URL'] + session['profil']['id'] +'/queries/' + query_id + '/related/').json()

    in_memory = BytesIO()
    zf = zipfile.ZipFile(in_memory, mode="w", compression=zipfile.ZIP_DEFLATED)
    zf.writestr(filename + '.json', str(r))
    zf.close()
    in_memory.seek(0)
    data = in_memory.read()

    return Response(data,
            mimetype='application/zip',
            headers={'Content-Disposition':'attachment;filename='+filename+'.zip'})


## View in-db human readable
# request by type_data and query_id to rest urls then rendering html template
@app.route('/view-<data_type>/<query_id>', methods=['POST','GET'])
def view_data_by_type(query_id, data_type):
    if data_type not in ['videos', 'comments', 'captions']:
        redirect(url_for(page_not_found))
    url = app.config['REST_URL']+ session['profil']['id'] +'/queries/' + query_id + '/' + data_type + '/'
    r = requests.get(url)

    def AppendCaption(data):
        lst = []
        n_words = 0
        for i in range(len(data)):
            text = ''
            if(data[i]['captions']):
                for j in range(len(data[i]['captions'])):
                    n_words += len(data[i]['captions'][j]['text'])
                    caption = data[i]['captions'][j]['text']
                    regex = re.search('(\[[a-zA-Z])',caption)
                    if not regex:
                        text+=str(caption)
                        text+=' '
                results_json = {
                    'query_id':data[i]['query_id'],
                    'videoId':data[i]['videoId'],
                    'text': text,
                    'countwords': n_words
                }
                lst.append(results_json)

        return lst

    if data_type == 'captions':
        query_result = AppendCaption(r.json())
    else:
        query_result = r.json()
    return render_template('view.html', list_queries=query_result)

# Download videos, comments set
@app.route('/download/<query_type>/<query_id>', methods=['GET'])
def download_videos_by_type(query_id, query_type):

    def chunkList(initialList, chunkSize):
        finalList = []
        for i in range(0, len(initialList), chunkSize):
            finalList.append(initialList[i:i+chunkSize])
        return finalList

    if query_type not in ['videos', 'comments', 'captions']:
        return redirect(url_for('page_not_found'))

    # find name of query for filename download
    r_name = requests.get(app.config['REST_URL']+session['profil']['id']+'/queries/'+query_id)
    query_name = re.sub('[^A-Za-z0-9]+', '_', str(r_name.json()['query']))
    query_type = re.sub('[^A-Za-z0-9]+', '_', query_type)
    filename = query_name + '_' + query_type

    # get results
    r = requests.get(app.config['REST_URL']+session['profil']['id']+'/queries/'+query_id+'/'+query_type+'/')

    # prepare zipping
    in_memory = BytesIO()
    zf = zipfile.ZipFile(in_memory, mode="w", compression=zipfile.ZIP_DEFLATED)
    
    if query_type == 'captions':
        data = r.json()
        chunkSize = 10
        
        n = 0
        for batch in chunkList(data, chunkSize):
            lst = []
            for entry in batch:
                text = ''
                if 'captions' in entry:
                    for caption in entry['captions']:
                        regex = re.search('(\[[a-zA-Z])', caption['text'])
                        if(regex):
                            app.logger.debug('There is a sound or action')
                            continue
                        else: 
                            text+= caption['text'] + ' '

                    results_json = {
                        'query_id':entry['query_id'],
                        'videoId':entry['videoId'],
                        'text': text
                    }
                    lst.append(results_json)                    
                else:
                    app.logger.debug('There is no captions found in db')
            query_result = json.dumps(lst,sort_keys=True, indent=2, separators=(',', ': '))            
            zf.writestr(filename + str(n) + '.json', query_result)
            n += 1

        zf.close()
        in_memory.seek(0)
        data = in_memory.read()

    else:
        query_result = r.json()
        query_result = json.dumps(query_result,sort_keys=True, indent=4, separators=(',', ': '))

        zf.writestr(filename + '.json', query_result)
        zf.close()
        in_memory.seek(0)
        data = in_memory.read()

    return Response(data,
            mimetype='application/zip',
            headers={'Content-Disposition':'attachment;filename='+filename+'.zip'})

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

    from logging.handlers import RotatingFileHandler
    # config logger (prefering builtin flask logger)
    formatter = logging.Formatter('%(filename)s ## [%(asctime)s] %(levelname)s == "%(message)s"', datefmt='%Y/%b/%d %H:%M:%S')
    handler = RotatingFileHandler('./' + app.config['LOG_DIR'] + '/activity_webapp.log', maxBytes=100000, backupCount=1)
    handler.setFormatter(formatter)
    #logger = logging.getLogger(__name__)

    app.logger.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)

    app.run(debug=app.config['debug_level'], host='0.0.0.0', port=app.config['PORT'], threaded=True )
