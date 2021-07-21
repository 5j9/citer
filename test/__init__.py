from atexit import register as atexit_register
from contextlib import contextmanager
from pickle import dump, load
from os.path import abspath

from requests import Session

# Do not import library parts here. commons.py should not be loaded
# until LANG is set by test_fa and test_en.


FORCE_CACHE_OVERWRITE = False  # Use for updating cache entries
CACHE_CHANGE = False
CACHE_PATH = abspath(__file__ + '/../.tests_cache')


# noinspection PyDecorator
@staticmethod
def fake_request(self, url, data=None, stream=False, **kwargs):
    global CACHE_CHANGE
    if data:
        cache_key = url + repr(sorted(data))
    else:
        cache_key = url
    response = cache.get(cache_key)
    if FORCE_CACHE_OVERWRITE or response is None:
        print('Downloading ' + url)
        with real_request():
            response = Session().request(
                self, url, data=data, **kwargs)
        cache[cache_key] = response
        CACHE_CHANGE = True
    if stream is True:
        def iter_content(*_):
            # this closure over response will simulate a bound method
            return iter((response.content,))
        response.iter_content = iter_content
    return response


def save_cache(cache_dict):
    """Save cache as pickle."""
    if not CACHE_CHANGE:
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


def invalidate_cache(in_url):
    global CACHE_CHANGE
    lower_url = in_url.lower()
    for k in cache.copy():
        if lower_url in k:
            del cache[k]
            CACHE_CHANGE = True


@contextmanager
def real_request():
    Session.request = original_request
    yield
    Session.request = fake_request


original_request = Session.request
Session.request = fake_request


cache = load_cache()
# invalidate_cache('shora')
print('len(cache) ==', len(cache))
atexit_register(save_cache, cache)
