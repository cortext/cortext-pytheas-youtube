# main.py
import os
import shutil
import json
import requests
import pprint as pp

from uuid import uuid4
from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request
from flask import session
from flask_bootstrap import Bootstrap
from flask_pymongo import PyMongo
from bson import json_util

from youtube import YouTube
from youtube import IO

def create_app():
    app = Flask(__name__)
    app.config.update(
        TEMPLATES_AUTO_RELOAD = True
    )
    app.config['MONGO_DBNAME'] = 'youtube'
    Bootstrap(app)
    return app

app = create_app()
mongo = PyMongo(app)
data_dir = 'data/'

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/video_info', methods = ['POST', 'GET'])
def video_info():
    if request.method == 'POST':
        if 'api_key' in session:
            id_video = request.form.get('unique_id_video')
            if 'youtube.com/watch?v=' in id_video:
                if 'https':
                    id_video = id_video.replace('https://www.youtube.com/watch?v=', '')
                else:
                    id_video = id_video.replace('http://www.youtube.com/watch?v=', '')
            print(id_video)
            part = ', '.join(request.form.getlist('part'))
            api_key = session['api_key']
            api = YouTube(api_key=api_key)
            video_result = api.get_search('videos', id=id_video, part=part)
            video_result_string = json.dumps(video_result, sort_keys = True, indent = 2, separators = (',', ': '))
            return render_template('results.html', result=video_result, string=video_result_string)
        else:
            return render_template('video_info.html', message='api key not set')
    return render_template('video_info.html')


@app.route('/channel_info', methods = ['POST', 'GET'])
def channel_info():
    if request.method == 'POST':
        if 'api_key' in session:
            id_channel = request.form.get('unique_id_channel')
            if 'youtube.com/user/' in id_channel:
                if 'https':
                    id_channel = id_channel.replace('https://www.youtube.com/user/', '')
                else:
                    id_channel = id_channel.replace('http://www.youtube.com/user/', '')
            print(id_channel)
            part = ', '.join(request.form.getlist('part'))
            api_key = session['api_key']
            api = YouTube(api_key=api_key)
            channel_result = api.get_search('channels', forUsername=id_channel, part=part)
            channel_result_string = json.dumps(channel_result, sort_keys = True, indent = 2, separators = (',', ': '))
            print(channel_result_string)
            return render_template('results.html', result=channel_result, string=channel_result_string)
            # return jsonify(channel_result)
        else:
            return render_template('channel_info.html', message='api key not set')
    return render_template('channel_info.html')


@app.route('/playlist_info', methods = ['POST', 'GET'])
def playlist_info():
    if request.method == 'POST':
        if 'api_key' in session:
            id_playlist = request.form.get('unique_id_playlist')
            # if 'youtube.com/watch?v=' in id_playlist:
            #     if 'https':
            #         id_playlist = id_playlist.replace('https://www.youtube.com/watch?v=', '')
            #     else:
            #         id_playlist = id_playlist.replace('http://www.youtube.com/watch?v=', '')
            print(id_playlist)
            part = ', '.join(request.form.getlist('part'))
            api_key = session['api_key']
            api = YouTube(api_key=api_key)
            playlist_info = api.get_search('playlists', id=id_playlist, part=part)
            pp.pprint(playlist_info)
            playlist_info_string = json.dumps(playlist_info, sort_keys = True, indent = 2, separators = (',', ': '))
            return render_template('results.html', result=playlist_info, string=playlist_info_string)
        else:
            return render_template('playlist_info.html', message='api key not set')
    return render_template('playlist_info.html')


@app.route('/search', methods = ['POST', 'GET'])
def search():
    if request.method == 'POST':
        session['counter'] = 0
        if 'api_key' in session:
            ## build query in session
            session['request'] = {
                'query':request.form.get('query'),
                'part':', '.join(request.form.getlist('part')),
                'language':request.form.get('language'),
                'maxResults':request.form.get('maxResults'),
                'ranking': request.form.get('ranking')
            }
            ## build request
            api = YouTube(api_key=session['api_key'])
            search_results = api.get_search(
                'search',
                q=session['request']['query'],
                part=session['request']['part'],
                language=session['request']['language'],
                maxResults=session['request']['maxResults'],
                ranking=session['request']['ranking']
            )
            previous_token = search_results['nextPageToken']
            search_results_string = json.dumps(search_results, sort_keys = True, indent = 4, separators = (',', ': '))
            # session['counter'] += 1
            return render_template('results.html', search_results=search_results, string=search_results_string, counter=session['counter'], prev=previous_token)
        else:
            return render_template('search.html', message='api key not set')

    ## Go to next page
    elif request.method == 'GET' and request.args.get('nextPageToken'):
        session['counter'] += 1
        pageToken = request.args.get('nextPageToken')
        api = YouTube(api_key=session['api_key'])
        search_results = api.get_search(
            'search',
            q=session['request']['query'],
            part=session['request']['part'],
            language=session['request']['language'],
            maxResults=session['request']['maxResults'],
            ranking=session['request']['ranking'],
            pageToken=pageToken
        )
        search_results_string = json.dumps(search_results, sort_keys = True, indent = 2, separators = (',', ': '))
        return render_template('results.html', search_results=search_results, string=search_results_string, counter=session['counter'], prev=pageToken)
    ## Go to prev page
    # elif request.method == 'GET' and request.args.get('prevPageToken'):
    #     session['counter'] -= 1
    #     pageToken = request.args.get('prevPageToken')
    #     api = YouTube(api_key=session['api_key'])
    #     search_results = api.get_search(
    #         'search',
    #         q=session['request']['query'],
    #         part=session['request']['part'],
    #         language=session['request']['language'],
    #         maxResults=session['request']['maxResults'],
    #         ranking=session['request']['ranking'],
    #         pageToken=pageToken
    #     )
    #     search_results_string = json.dumps(search_results, sort_keys = True, indent = 2, separators = (',', ': '))
    #     return render_template('results.html', search_results=search_results, string=search_results_string, counter=session['counter'], prev=pageToken)
    return render_template('search.html')


@app.route('/process_results')
def process_results():
    ## prepare dir & files
    path_query = session['request']['query'] + '_' + session['request']['language'] + '_' + session['request']['ranking'] + '/'
    IO().create_dir(path_query)

    ## build request based on session
    session['counter'] = 0
    api = YouTube(api_key=session['api_key'])
    search_results = api.get_search(
        'search',
        q=session['request']['query'],
        part=session['request']['part'],
        language=session['request']['language'],
        maxResults=session['request']['maxResults'],
        ranking=session['request']['ranking']
    )
    ## save file
    name_file = str(session['counter']) + '.json'
    meta_inf = {
        'regionCode' : search_results['regionCode'],
        'pageInfo' : search_results['pageInfo'],
        'etag' : search_results['etag'],
        'kind' : search_results['kind']
    }
    meta_info_file = path_query + 'meta_info.txt'
    search_results_file = path_query + name_file
    IO().save_json(meta_info_file, meta_inf)
    IO().save_json(search_results_file, search_results['items'])

    ## mongo Insert
    ytb_db = mongo.db
    ## avoid duplicates
    # ytb_db.query.createIndex( { 'unique_id': 1 }, unique=True )
    ## insert query
    uid = uuid4()
    ytb_db.query.insert_one(
        {
        'unique_id': str(uid),
        'id': session['counter'],
        'query':session['request']['query'],
        'part' : session['request']['part'],
        'language' : session['request']['language'],
        'maxResults' : session['request']['maxResults'],
        'ranking' : session['request']['ranking'],
        }
    )
    ##insert videos
    for each in search_results['items']:
        each.update({'query_id' : str(uid)})
        ytb_db.videos.insert_one(
            each
        )
    ## Loop and save
    while 'nextPageToken' in search_results:
        session['counter'] += 1
        name_file = str(session['counter']) + '.json'
        search_results = api.get_search(
            'search',
            q=session['request']['query'],
            part=session['request']['part'],
            language=session['request']['language'],
            maxResults=session['request']['maxResults'],
            ranking=session['request']['ranking'],
            pageToken=search_results['nextPageToken']
        )
        if not search_results['items']:
            return render_template('download_process.html', message='ok it is done')
        ## save items
        search_results_file = path_query + name_file
        IO().save_json(search_results_file, search_results['items'])

        ## insert video-info
        for each in search_results['items']:
            each.update({'query_id' : str(uid)})
            ytb_db.videos.insert_one(each)

    return render_template('download_process.html', message='ok it is done')


@app.route('/aggregate_results', methods = ['POST', 'GET'])
def aggregate_results():
    if os.path.exists(data_dir):
        dir_list = os.listdir(data_dir)
        if request.method == 'POST':

            if request.form and request.form.get('del'):
                shutil.rmtree(data_dir + request.form.get('del'))
                dir_list = os.listdir(data_dir)
                return render_template('aggregate_results.html', dir_list=dir_list)

            if request.form and request.form.get('optionsRadios'):
                dir_to_check = request.form.get('optionsRadios')
                options_api = request.form.getlist('api_part')
                path_dir = data_dir + dir_to_check
                query_name = path_dir.replace('data/', '')
                part = ', '.join(request.form.getlist('part'))
                api_key = session['api_key']
                api = YouTube(api_key=api_key)

                ## Get list of video from list of vid (search)
                items = IO.list_file(path_dir)
                items_videoId = items['items_videoId']
                items_playlist = items['items_playlist']

                print(query_name)
                print('count of video :', len(items_videoId))
                print('count of playlist :', len(items_playlist))
                ############################
                if 'comments' in options_api:
                    path_comments = dir_to_check + '/comments/'
                    IO().create_dir(path_comments)
                    i = 0
                    ## prepare mongopy Cursor
                    ytb_db = mongo.db
                    ## for each video loop to comments
                    for id_video in items_videoId:
                        commentThreads_result = api.get_search(
                            'commentThreads',
                            videoId=id_video,
                            part='id, replies, snippet'
                        )
                        ## Check if error (eg unactivated comments)
                        if 'error' in commentThreads_result:
                            print(commentThreads_result['error']['errors'][0]['reason'])
                            continue
                        ## get OneByOne commentThreads & save json
                        for each in commentThreads_result['items']:
                            ## insert videos into mongoDB
                            if 'replies' in each:
                                each['snippet'].update({'replies' : each['replies']})
                            each['snippet'].update({'query_name' : query_name  })
                            ytb_db.comments.insert_one(
                                each['snippet']
                            )
                            ## save file
                            each_sanitized = json.loads(json_util.dumps(each['snippet']))
                            comments_file = path_comments + str(i) + '_commentThread.json'
                            IO().save_json(comments_file, each_sanitized)
                            i += 1
                        ## Loop and save
                        while 'nextPageToken' in commentThreads_result:
                            commentThreads_result = api.get_search(
                                'commentThreads',
                                videoId=id_video,
                                part='id, replies, snippet',
                                pageToken=commentThreads_result['nextPageToken']
                            )
                            ## Check if error (eg unactivated comments)
                            if 'error' in commentThreads_result:
                                print(commentThreads_result['error']['errors'][0]['reason'])
                                continue
                            for each in commentThreads_result['items']:
                                if 'replies' in each:
                                    each['snippet'].update({'replies' : each['replies']})
                                ytb_db.comments.insert_one(
                                    each['snippet']
                                )
                                ## save file
                                each_sanitized = json.loads(json_util.dumps(each['snippet']))
                                comments_file = path_comments + str(i) + '_commentThread.json'
                                IO().save_json(comments_file, each_sanitized)
                                i += 1
                        print(i)
                ############################
                if 'captions' in options_api:
                    path_captions = path_dir + '/captions/'
                    IO().create_dir(path_captions)
                    ## for each video loop to captions
                    for id_video in items_videoId:
                        captions_result = api.get_search(
                            'captions',
                            videoId=id_video,
                            part='id, snippet'
                        )
                        ## Check if error (eg unactivated captions)
                        if 'error' in captions_result:
                            print(captions_result['error']['errors'][0]['reason'])
                            continue
                        if not captions_result['items']:
                            print('empty captions')
                            continue
                        ## get different captions language
                        for key, val in captions_result.items():
                            if key == 'items': # if not captions_result['items'] and key == 'items':
                                for item in val:
                                    lang_caption = item['snippet']['language']
                                    caption_xml = 'https://www.youtube.com/api/timedtext?lang=' \
                                                 + lang_caption \
                                                 + '&v=' + id_video
                                    print(caption_xml)
                                    req_xml = requests.get(caption_xml)
                                    if req_xml.text:
                                        #saving cap
                                        name_file = id_video + '_' + lang_caption + '.xml'
                                        with open(path_captions + name_file, 'w') as f:
                                            f.write(req_xml.text)

                return render_template('download_process.html', message='ok it is done')

        return render_template('aggregate_results.html', dir_list=dir_list)

    return render_template('aggregate_results.html', message='hmmm it seems to have a bug on dir_path...')


@app.route('/config', methods = ['POST', 'GET'])
def config():
    if os.path.exists(data_dir):
        dir_list = os.listdir(data_dir)
        if request.method == 'POST':
            if request.form and request.form.get('del'):
                shutil.rmtree(data_dir + request.form.get('del'))
                dir_list = os.listdir(data_dir)

    if request.method == 'POST':
        print(request.form.get('api_key'))
        if request.form.get('api_key'):
            session['api_key'] = request.form.get('api_key')
    return render_template('config.html',  dir_list=dir_list)


@app.route('/reset', methods = ['POST'])
def reset():
    pp.pprint(session)
    if session['api_key']:
        session['api_key'] = None
    return render_template('config.html')


if __name__ == '__main__':
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    app.secret_key = os.urandom(24)
    app.run(debug=True)
    session['api_key'] = ''
