# Yadkard

A citation generator tool for Wikipedia. Currently accessible from:
http://tools.wmflabs.org/yadkard/ (the English version)
http://tools.wmflabs.org/yadfa/ (the Persian version)

## What does it do?

Yadkard is specially useful for generating citations from Google Books URLs, DOIs (Any Digital object Identifiers) and ISBNs (International Standard Book Numbers).
Additionally URL of many major news websites are supported, including:
The New York Times, BBC, Daily Mail, Daily Mirror, The Daily Telegraph, The Huffington Post, The Washington Post, The Boston Globe, Bloomberg Businessweek, Financial Times, and The Times of India. Sepecial support for the URLs of the [Wayback Machine](https://en.wikipedia.org/wiki/Wayback_Machine) is also implemented.

Some other tested and supported Persian web-sites:
* http://www.noormags.com (نورمگز)
* http://www.noorlib.ir (کتابخانه دیجیتال نور)
* http://www.adinebook.com (آدینه‌بوک)
* http://socialhistory.ihcs.ac.ir/ (تحقیقات تاریخ اجتماعی)


## Installation

To run Yadkard on your local computer:

1. Install Python 3.6+.
2. Clone the project.
3. Install the dependencies using `pip install -r requirements.txt`.
3. Make sure that `flup` is __not__ installed in your environment.
4. Run Yadkard by calling `main.py`.

If everything goes fine, the main page will be accessible from:
    http://127.0.0.1:5000/


## Language Setting
The default language is English and can be change to Persian using the setting in config.py file.
