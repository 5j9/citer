#! /usr/bin/python
# -*- coding: utf-8 -*-


from setuptools import setup, find_packages 
from os import path

# Get the long description from the relevant file
here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='Yadkard',
    # Versions should comply with PEP440. For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # http://packaging.python.org/en/latest/tutorial.html#version
    version='1.2.0',
    description='An application used to generate Wikipedia citation templats.',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/irdb/yadkard/',

    # Author details
    author='Dalba',
    author_email='dalba.wiki@gmail.com',

    # Choose your license
    license='GPLv3+',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        # 3 - Alpha
        # 4 - Beta
        # 5 - Production/Stable
        'Development Status :: 4 - Beta',

        'Environment :: Web Environment',
        
        # Indicate who your project is intended for
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Other Audience',

        'Topic :: Text Processing',
        'Topic :: Utilities',

        'Natural Language :: English',
        'Natural Language :: Persian',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',

        #Operating system
        'Operating System :: Microsoft',
        'Operating System :: POSIX',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.4',
    ],

    # What does your project relate to?
    keywords='Wikipedia citation text processing generator',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(),

    # List run-time dependencies here. These will be installed by pip when your
    # project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/technical.html#install-requires-vs-requirements-files
    install_requires=['requests>=2.3.0',
                      'beautifulsoup4>=4.3.2',
                      'langid>=1.1.4dev',
                      #'flup>=1.0.3.dev-20140705'
                      ],

    # If there are data files included in your packages that need to be
    # installed, specify them here. If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    ##package_data={
    ##    'sample': ['package_data.dat'],
    ##},

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages.
    # see http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    ##data_files=[('my_data', ['data/data_file'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'yadkard=yadkard:main',
        ],
    },
)
