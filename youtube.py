import requests
import json
from bson import ObjectId
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
        url = self.api_base_url+endpoint
        # print(kwargs)
        try:
            req = requests.get(url, kwargs)
        except requests.exceptions.RequestException as e:
            print(e)
        return self.response(req)


    @staticmethod
    def response(response):
        return response.json()
