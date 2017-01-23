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

    def get(self, url, headers=None, *args, **kwargs):
        pu = urlparse(url)
        file = './offline_resources/' +\
               re.sub('/+', '/', '/'.join(pu)).rstrip('/') + '.html'
        try:
            with open(file, 'rb') as f:
                content = f.read()
            try:
                text = content.decode('utf-8')
            except UnicodeDecodeError:
                text = None
        except FileNotFoundError:
            path = '/'.join(file.split('/')[:-1]) + '/'
            os.makedirs(path, exist_ok=True)
            print('* Downloading ' + url)
            r = requests.get(url, headers=headers)
            content = r.content
            text = r.text
            with open(file, 'wb') as f:
                f.write(content)
        self.Response.content = content
        self.Response.text = text
        return self.Response

    def head(self, url, headers=None, *args, **kwargs):
        rheaders = {
            'content-type': 'text/html',
            'content-length': str(len(self.get(url, headers=headers).content))
        }
        self.Response.headers = rheaders
        return self.Response
