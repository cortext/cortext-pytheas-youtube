import requests
import json
import os

# freely inspirated from github.com/rhayun/python-youtube-api


class YouTube:
    api_key = None
    access_token = None
    api_base_url = 'https://www.googleapis.com/youtube/v3/'
    part = None

    def __init__(self, api_key, access_token=None, api_url=None):
        self.api_key = api_key
        self.access_token = access_token
        if api_url:
            self.api_url = api_url

    def get_search(self, endpoint, **kwargs):
        if self.access_token:
            kwargs['access_token'] = self.access_token
        else:
            kwargs['key'] = self.api_key
        if 'part' not in kwargs:
            kwargs['part'] = self.part
        kwargs = json.dumps(kwargs)
        kwargs = json.loads(kwargs)
        url = self.api_base_url + endpoint
        print(endpoint)
        print(kwargs)
        try:
            req = requests.get(url, kwargs)
        except requests.exceptions.RequestException as e:
            print(e)
        return self.response(req)

    def get_search_by_date(self, endpoint, **kwargs):
        return self.response(req)

    def get_comments(self, id_video):
        # Get list of video from list of vid (search)
        return

    def get_captions(self, endpoint, **kwargs):
        return

    @staticmethod
    def response(response):
        return response.json()

    #/* Alternative approach with new built in paginateResults function */
    #
    # // Same Params as before
    # params = {
    #     'q': 'Android',
    #     'type': 'video',
    #     'part': 'id, snippet',
    #     'maxResults': 50
    # }
    #
    # // an array to store page tokens so we can go back and forth
    # page_tokens = {}
    #
    # // make inital search
    # search = youtube.paginate_results(params, None)
    #
    # // store token
    # page_tokens.append(search['info']['nextPageToken'])
    #
    # // go to next page in result
    # search = youtube.paginate_results(params, page_tokens[0])
    #
    # // store token
    # pageTokens.append(search['info']['nextPageToken'])
    #
    # // go to next page in result
    # search = youtube.paginate_results(params, page_tokens[1])
    #
    # // store token
    # pageTokens.append(search['info']['nextPageToken'])
    #
    # // go back a page
    # search = youtube.paginate_results(params, page_tokens[0])
    #
    # // add results key with info parameter set
    # print search['results']

    language_code = [
        ('ab', 'Abkhazian'),
        ('aa', 'Afar'),
        ('af', 'Afrikaans'),
        ('ak', 'Akan'),
        ('sq', 'Albanian'),
        ('am', 'Amharic'),
        ('ar', 'Arabic'),
        ('an', 'Aragonese'),
        ('hy', 'Armenian'),
        ('as', 'Assamese'),
        ('av', 'Avaric'),
        ('ae', 'Avestan'),
        ('ay', 'Aymara'),
        ('az', 'Azerbaijani'),
        ('bm', 'Bambara'),
        ('ba', 'Bashkir'),
        ('eu', 'Basque'),
        ('be', 'Belarusian'),
        ('bn', 'Bengali'),
        ('bh', 'Bihari languages'),
        ('bi', 'Bislama'),
        ('nb', 'Bokmål, Norwegian; Norwegian Bokmål'),
        ('bs', 'Bosnian'),
        ('br', 'Breton'),
        ('bg', 'Bulgarian'),
        ('my', 'Burmese'),
        ('ca', 'Catalan; Valencian'),
        ('km', 'Central Khmer'),
        ('ch', 'Chamorro'),
        ('ce', 'Chechen'),
        ('zh', 'Chinese'),
        ('cu',
            'Church Slavic; Old Slavonic; Church Slavonic; Old Bulgarian; Old Church Slavonic'),
        ('cv', 'Chuvash'),
        ('kw', 'Cornish'),
        ('co', 'Corsican'),
        ('cr', 'Cree'),
        ('hr', 'Croatian'),
        ('cs', 'Czech'),
        ('da', 'Danish'),
        ('dv', 'Divehi; Dhivehi; Maldivian'),
        ('nl', 'Dutch; Flemish'),
        ('dz', 'Dzongkha'),
        ('en', 'English'),
        ('eo', 'Esperanto'),
        ('et', 'Estonian'),
        ('ee', 'Ewe'),
        ('fo', 'Faroese'),
        ('fj', 'Fijian'),
        ('fi', 'Finnish'),
        ('fr', 'French'),
        ('ff', 'Fulah'),
        ('gd', 'Gaelic; Scottish Gaelic'),
        ('gl', 'Galician'),
        ('lg', 'Ganda'),
        ('Ga', 'Georgian'),
        ('ka', 'Georgian'),
        ('de', 'German'),
        ('el', 'Greek, Modern (1453-)'),
        ('gn', 'Guarani'),
        ('gu', 'Gujarati'),
        ('ht', 'Haitian; Haitian Creole'),
        ('ha', 'Hausa'),
        ('he', 'Hebrew'),
        ('hz', 'Herero'),
        ('hi', 'Hindi'),
        ('ho', 'Hiri Motu'),
        ('hu', 'Hungarian'),
        ('is', 'Icelandic'),
        ('io', 'Ido'),
        ('ig', 'Igbo'),
        ('id', 'Indonesian'),
        ('ia', 'Interlingua (International Auxiliary Language Association)'),
        ('ie', 'Interlingue; Occidental'),
        ('iu', 'Inuktitut'),
        ('ik', 'Inupiaq'),
        ('ga', 'Irish'),
        ('it', 'Italian'),
        ('ja', 'Japanese'),
        ('jv', 'Javanese'),
        ('kl', 'Kalaallisut; Greenlandic'),
        ('kn', 'Kannada'),
        ('kr', 'Kanuri'),
        ('ks', 'Kashmiri'),
        ('kk', 'Kazakh'),
        ('ki', 'Kikuyu; Gikuyu'),
        ('rw', 'Kinyarwanda'),
        ('ky', 'Kirghiz; Kyrgyz'),
        ('kv', 'Komi'),
        ('kg', 'Kongo'),
        ('ko', 'Korean'),
        ('kj', 'Kuanyama; Kwanyama'),
        ('ku', 'Kurdish'),
        ('lo', 'Lao'),
        ('la', 'Latin'),
        ('lv', 'Latvian'),
        ('li', 'Limburgan; Limburger; Limburgish'),
        ('ln', 'Lingala'),
        ('lt', 'Lithuanian'),
        ('lu', 'Luba-Katanga'),
        ('lb', 'Luxembourgish; Letzeburgesch'),
        ('mk', 'Macedonian'),
        ('mg', 'Malagasy'),
        ('ms', 'Malay'),
        ('ml', 'Malayalam'),
        ('mt', 'Maltese'),
        ('gv', 'Manx'),
        ('mi', 'Maori'),
        ('mr', 'Marathi'),
        ('mh', 'Marshallese'),
        ('Mi', 'Micmac'),
        ('mn', 'Mongolian'),
        ('na', 'Nauru'),
        ('nv', 'Navajo; Navaho'),
        ('nd', 'Ndebele, North; North Ndebele'),
        ('nr', 'Ndebele, South; South Ndebele'),
        ('ng', 'Ndonga'),
        ('ne', 'Nepali'),
        ('se', 'Northern Sami'),
        ('no', 'Norwegian'),
        ('nn', 'Norwegian Nynorsk; Nynorsk, Norwegian'),
        ('oc', 'Occitan (post 1500)'),
        ('oj', 'Ojibwa'),
        ('or', 'Oriya'),
        ('om', 'Oromo'),
        ('os', 'Ossetian; Ossetic'),
        ('pi', 'Pali'),
        ('pa', 'Panjabi; Punjabi'),
        ('fa', 'Persian'),
        ('pl', 'Polish'),
        ('pt', 'Portuguese'),
        ('ps', 'Pushto; Pashto'),
        ('qu', 'Quechua'),
        ('ro', 'Romanian; Moldavian; Moldovan'),
        ('rm', 'Romansh'),
        ('rn', 'Rundi'),
        ('ru', 'Russian'),
        ('sm', 'Samoan'),
        ('sg', 'Sango'),
        ('sa', 'Sanskrit'),
        ('sc', 'Sardinian'),
        ('sr', 'Serbian'),
        ('sn', 'Shona'),
        ('ii', 'Sichuan Yi; Nuosu'),
        ('sd', 'Sindhi'),
        ('si', 'Sinhala; Sinhalese'),
        ('sk', 'Slovak'),
        ('sl', 'Slovenian'),
        ('so', 'Somali'),
        ('st', 'Sotho, Southern'),
        ('es', 'Spanish; Castilian'),
        ('su', 'Sundanese'),
        ('sw', 'Swahili'),
        ('ss', 'Swati'),
        ('sv', 'Swedish'),
        ('tl', 'Tagalog'),
        ('ty', 'Tahitian'),
        ('tg', 'Tajik'),
        ('ta', 'Tamil'),
        ('tt', 'Tatar'),
        ('te', 'Telugu'),
        ('th', 'Thai'),
        ('bo', 'Tibetan'),
        ('ti', 'Tigrinya'),
        ('to', 'Tonga (Tonga Islands)'),
        ('ts', 'Tsonga'),
        ('tn', 'Tswana'),
        ('tr', 'Turkish'),
        ('tk', 'Turkmen'),
        ('tw', 'Twi'),
        ('ug', 'Uighur; Uyghur'),
        ('uk', 'Ukrainian'),
        ('ur', 'Urdu'),
        ('uz', 'Uzbek'),
        ('ve', 'Venda'),
        ('vi', 'Vietnamese'),
        ('vo', 'Volapük'),
        ('wa', 'Walloon'),
        ('cy', 'Welsh'),
        ('fy', 'Western Frisian'),
        ('wo', 'Wolof'),
        ('xh', 'Xhosa'),
        ('yi', 'Yiddish'),
        ('yo', 'Yoruba'),
        ('za', 'Zhuang; Chuang'),
        ('zu', 'Zulu')
    ]


class IO:
    data_dir = "data/"

    def __init__(self):
        data_dir = self.data_dir

    def create_dir(self, path_query):
        data_dir = self.data_dir
        complete_path = data_dir + path_query
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            if not os.path.exists(complete_path):
                os.makedirs(complete_path)
        else:
            if not os.path.exists(complete_path):
                os.makedirs(complete_path)
        return

    def save_json(self, path_file, data):
        data_dir = self.data_dir
        with open(data_dir + path_file, 'w') as outfile:
            json.dump(data, outfile)
        return

    def list_file(path):
        items_videoId = []
        items_playlist = []
        for json_file in os.listdir(path):
            if any(word in json_file for word in ['comments', 'captions', 'meta_info.txt']):
                continue
            path_file = path + '/' + json_file
        items_videoId = []
        with open(path_file, 'r') as json_data:
            search_data = json.load(json_data)
            for item in search_data:
                if not 'video_result' in search_data:
                    if 'videoId' in item['id']:
                        id_video = item['id']['videoId']
                        items_videoId.append(id_video)
                    elif 'playlistId'in item['id']:
                        id_playlist = item['id']['playlistId']
                        items_playlist.append(id_playlist)

        return {'items_videoId': items_videoId,
                'items_playlist': items_playlist}

    def process(path):
        return


class Mongo:
    data_db = "youtube"

    def __init__(self):
        data_db = self.data_db

    def insert_mongo():
        # insert video-info
        for each in search_results['items']:
            each.update({'query_id': str(uid)})
            ytb_db.videos.insert_one(each)
        return

    def update_mongo():
        # update video-info
        for each in search_results['items']:
            each.update({'query_id': str(uid)})
            ytb_db.videos.insert_one(each)
        return


# class JSONEncoder(json.JSONEncoder):
#     def default(self, o):
#         if isinstance(o, ObjectId):
#             return str(o)
#         return json.JSONEncoder.default(self, o)
# JSONEncoder().encode(analytics)
