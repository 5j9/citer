# Yadkard

A citation generator tool for Wikipedia. Currently accessible on:
http://tools.wmflabs.org/yadkard/ (English version)

## Dependencies

Tested on Python 3.4.1

The following libraries are required:
* requests (2.3.0)
* beautifulsoup4 (4.3.2)
* langid (1.1.4dev)
They can be install using `pip install -r`.

* flup (1.0.3.dev-20140705)
By the default the setup won't install flup library and will use wsgiref.simple_server instead. This is what you want if you are running the script from your personal computer. But if you want to run the script on a server you will need to manually install flup using this command:
	```pip install git+https://github.com/a1tus/flup-py3.git```

## Usage

If running on local computer, the tool will be accessible from:
http://127.0.0.1:8051/

Specially useful for generating citation from Google Books URLs, DOI (Any Digital object Identifier) and ISBN (International Standard Book Number).
+ URL of many major news websites, including:
The New York Times, BBC, Daily Mail, Daily Mirror, The Daily Telegraph, The Huffington Post, The Washington Post, The Boston Globe, Bloomberg Businessweek, Financial Times, and The Times of India.

Some other tested and supported sites:
* http://www.noormags.com (نورمگز)
* http://www.noorlib.ir (کتابخانه دیجیتال نور)
* http://www.adinebook.com (آدینه‌بوک)
* http://socialhistory.ihcs.ac.ir/ (تحقیقات تاریخ اجتماعی)

## Language Setting
	The default language is English and currently this is the only supported language.
	In future versions you will be able to change language by changing the `lang = 'en'` line in config.py file. 