# Citer

A citation generator tool for Wikipedia. Currently accessible from:\
[https://citer.toolforge.org/](https://citer.toolforge.org/) (the English version)\
[https://yadfa.toolforge.org/](https://yadfa.toolforge.org/) (the Persian version)

## What does it do?

Citer is especially useful for generating citations from Google Books URLs, DOIs (Any Digital object Identifiers) and ISBNs (International Standard Book Numbers).
Additionally, any URL, including the URL of many major news websites can be processed to generate a citation.

URLs of [Wayback Machine](https://en.wikipedia.org/wiki/Wayback_Machine) and [archive.today](https://archive.ph/) are also supported and generate a citation template with archive parameters filled.

## Installation

To run Citer on your local computer:

1. Install Python 3.11+
2. Clone the project
3. Install the dependencies using `pip install --user -r requirements.txt`
4. Copy `config.py.example` to `config.py` (You might want to get an NCBI API key and add it to the config file if you're going to use its services)
5. Run `python3 app.py`

If everything goes fine, the main page will be accessible from:\
    [http://localhost:5000/](http://localhost:5000/)

If you experience any problems or have questions, please open an issue on this repo.

## Language Setting
The default language is English and can be changed to Persian using the setting in the config.py file.


## Known issues
* The bookmarklet does not work on archive.org (issue #26) or any other website that does not allow opening external links. One needs to use Citer directly in such cases.
