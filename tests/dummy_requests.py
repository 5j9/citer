#! /usr/bin/python
# -*- coding: utf-8 -*-

import requests
import re
from urllib.parse import urlparse
import os


class DummyRequests:
    
    """This class will be used to override the requests mudule in tests."""

    class Response:
        
        """Used for emulating requests response."""
        
        status_code = 200
    
    def get(self, url, *args, **kwargs):
        file = '/'.join(urlparse(url))
        file = re.sub('/+', '/', file)
        file = './offline_resources/' + file
        if file.endswith('/'):
            file = file[:-1]
        try:
            with open(file, 'rb') as f:
                content = f.read()
        except FileNotFoundError:
            path = '/'.join(file.split('/')[:-1]) + '/'
            os.makedirs(path, exist_ok=True)
            print('* Downloading ' + url)
            content = requests.get(url).content
            with open(file, 'wb') as f:
                f.write(content)
        self.Response.content = content
        return self.Response

    def head(self, url, *args, **kwargs):
        response_headers = {'content-type': 'text/html'}
        response_headers['content-length'] = str(len(self.get(url).content))
        self.Response.headers = response_headers
        return self.Response
