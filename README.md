# Yadkard

A citation generator tool for Wikipedia. Currently accessible from:
http://tools.wmflabs.org/yadkard/ (English version)

## Dependencies

Tested on Python 3.4.1

The following libraries are required:
* beautifulsoup4
* numpy
* requests
* isbnlib
* flup6
* langid
* lxml
* jdatetime
* regex

These can be install using `pip install -r requirements.txt`.

If flup is not found, wsgiref.simple_server will be used instead. Usually this is what you want if you are running the script on your personal computer.

## Usage

If running on local computer, the main page will be accessible from:
http://127.0.0.1:5000/

Yadkard is specially useful for generating citations from Google Books URLs, DOIs (Any Digital object Identifiers) and ISBNs (International Standard Book Numbers).
Additionally URL of many major news websites are supported, including:
The New York Times, BBC, Daily Mail, Daily Mirror, The Daily Telegraph, The Huffington Post, The Washington Post, The Boston Globe, Bloomberg Businessweek, Financial Times, and The Times of India. Sepecial support for the URLs of the [Wayback Machine](https://en.wikipedia.org/wiki/Wayback_Machine) is also implemented.

Some other tested and supported Persian web-sites:
* http://www.noormags.com (نورمگز)
* http://www.noorlib.ir (کتابخانه دیجیتال نور)
* http://www.adinebook.com (آدینه‌بوک)
* http://socialhistory.ihcs.ac.ir/ (تحقیقات تاریخ اجتماعی)

## Language Setting
The default language is English and can be change to Persian using the setting in config.py file.
