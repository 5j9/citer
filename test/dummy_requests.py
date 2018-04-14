#! /usr/bin/python
# -*- coding: utf-8 -*-

from atexit import register as atexit_register
from pickle import dump, load

import requests


FORCE_CACHE_OVERWRITE = False  # Use for updating cache entries
NEW_DOWNLOAD = False


class DummyRequests:

    """This class will be used to override the requests mudule in tests."""

    @staticmethod
    def get(url: str, headers=None, **kwargs):
        response = cache.get(url)
        if FORCE_CACHE_OVERWRITE or response is None:
            print('Downloading ' + url)
            response = requests.get(url, headers=headers)
            cache[url] = response
            global NEW_DOWNLOAD
            NEW_DOWNLOAD = True
        return response

    def head(self, url: str, headers=None, **kwargs):
        return self.get(url, headers)


def save_cache(cache_dict):
    """Save cache as pickle."""
    if not NEW_DOWNLOAD:
        return
    print('saving new cache')
    with open(f'{__file__}/../.tests_cache', 'w+b') as f:
        dump(cache_dict, f)


def load_cache():
    """Return cache as a dict."""
    try:
        with open(f'{__file__}/../.tests_cache', 'r+b') as f:
            return load(f)
    except FileNotFoundError:
        return {}


cache = load_cache()
print('len(cache) ==', len(cache))
atexit_register(save_cache, cache)
