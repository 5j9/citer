#! /usr/bin/python
# -*- coding: utf-8 -*-

import pickle

import requests


FORCE_CACHE_OVERWRITE = False  # Use for updating cache entries


class DummyRequests:

    """This class will be used to override the requests mudule in tests."""

    def get(self, url: str, headers=None, **kwargs):
        response = not FORCE_CACHE_OVERWRITE and CACHE.get(url)
        if not response:
            print('Downloading ' + url)
            response = requests.get(url, headers=headers)
            CACHE[url] = response
            save_cache(CACHE)
        return response

    def head(self, url: str, headers=None, **kwargs):
        return self.get(url, headers)


def save_cache(cache_dict):
    """Save cache as pickle."""
    print('saving new cache')
    with open(f'{__file__}/../.tests_cache', 'w+b') as f:
        pickle.dump(cache_dict, f)


def load_cache():
    """Return cache as a dict."""
    try:
        with open(f'{__file__}/../.tests_cache', 'r+b') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return {}


CACHE = load_cache()
print('len(CACHE) ==', len(CACHE))
