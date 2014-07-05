#!/data/project/yadkard/venv/bin/python3.2
# -*- coding: utf-8 -*-

"""Discover all tests and run them."""


import unittest


if __name__ == '__main__':
    tests = unittest.defaultTestLoader.discover('.', '*_test.py')
    runner = unittest.runner.TextTestRunner()
    runner.run(tests)
