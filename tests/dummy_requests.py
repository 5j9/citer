#! /usr/bin/python
# -*- coding: utf-8 -*-

import requests
import re
from urllib.parse import urlparse
import os


class DummyRequests:

    """This class will be used to override the requests mudule in tests."""

    class Response:

        """Use for emulating requests response."""

        status_code = 200

    def get(self, url, *args, **kwargs):
        pu = urlparse(url)
        file = './offline_resources/' +\
               re.sub('/+', '/', '/'.join(pu)).rstrip('/') + '.html'
        try:
            with open(file, 'rb') as f:
                content = f.read()
        except (FileNotFoundError):
            path = '/'.join(file.split('/')[:-1]) + '/'
            os.makedirs(path, exist_ok=True)
            print('* Downloading ' + url)
            content = requests.get(url).content
            with open(file, 'wb') as f:
                f.write(content)
        self.Response.content = content
        return self.Response

    def head(self, url, *args, **kwargs):
        headers = {'content-type': 'text/html'}
        headers['content-length'] = str(len(self.get(url).content))
        self.Response.headers = headers
        return self.Response
