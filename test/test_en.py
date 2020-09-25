"""Discover all tests (except the ones inside test_fa.py) and run them."""


from unittest import defaultTestLoader
from unittest.runner import TextTestRunner

import config


if __name__ == '__main__':
    config.LANG = 'en'
    tests = defaultTestLoader.discover('.', '*_test.py')
    runner = TextTestRunner()
    runner.run(tests)
