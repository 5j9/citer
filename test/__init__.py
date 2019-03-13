#! /usr/bin/python
# -*- coding: utf-8 -*-
from atexit import register as atexit_register
from pickle import dump, load
from os.path import abspath

from requests import Session

# Do not import library parts here. commons.py should not be loaded
# until LANG is set by test_fa and test_en.


FORCE_CACHE_OVERWRITE = False  # Use for updating cache entries
NEW_DOWNLOAD = False
CACHE_PATH = abspath(__file__ + '/../.tests_cache')


def fake_request(method, url, **kwargs):
    assert method == 'get'
    response = cache.get(url)
    if FORCE_CACHE_OVERWRITE or response is None:
        print('Downloading ' + url)
        response = Session().request(method, url, **kwargs)
        cache[url] = response
        global NEW_DOWNLOAD
        NEW_DOWNLOAD = True
    return response


def save_cache(cache_dict):
    """Save cache as pickle."""
    if not NEW_DOWNLOAD:
        return
    print('saving new cache')
    with open(CACHE_PATH, 'wb') as f:
        dump(cache_dict, f)


def load_cache():
    """Return cache as a dict."""
    try:
        with open(CACHE_PATH, 'rb') as f:
            return load(f)
    except FileNotFoundError:
        return {}


Session.request = staticmethod(fake_request)

cache = load_cache()
print('len(cache) ==', len(cache))
atexit_register(save_cache, cache)
