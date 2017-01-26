#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Discover all tests (except the ones inside test_fa.py) and run them."""


import unittest

import config


if __name__ == '__main__':
    config.lang = 'en'
    tests = unittest.defaultTestLoader.discover('.', '*_test.py')
    runner = unittest.runner.TextTestRunner()
    runner.run(tests)
