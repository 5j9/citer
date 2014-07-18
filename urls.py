#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Codes used for parsing contents of an arbitrary URL."""


import re
from urllib.parse import urlparse
import logging
import difflib
from threading import Thread

import requests
import bs4

import commons


class Response(commons.BaseResponse):

    """Create URL's response object."""

    def __init__(self, url, date_format='%Y-%m-%d'):
        """Make the dictionary and run self.generate()."""
        self.date_format = date_format
        try:
            self.url = url
            self.dictionary = url2dictionary(url)
            self.generate()
        except (ContentTypeError, ContentLengthError) as e:
            self.sfnt = 'Could not process the request.'
            self.ctnt = e.message
            self.error = 100
            logger.exception(url)


class ContentTypeError(Exception):

    """Raise when content-type header does not start with 'text/'."""

    pass


class ContentLengthError(Exception):

    """Raise when content-length header indicates a very long content."""

    pass


class StatusCodeError(Exception):

    """Raise when requests.get.status_code != 200."""

    pass


class InvalidByLineError(Exception):

    """Raise in for errors in byline_to_names()."""

    pass


def find_journal(soup):
    """Return journal title as a string."""
    try:
        # http://socialhistory.ihcs.ac.ir/article_319_84.html
        m = soup.find(attrs={'name': 'citation_journal_title'})
        return m['content'].strip()
    except Exception:
        pass


def find_url(soup, url):
    """Get a BeautifulSoup object it's url. Return og:url or url as a string."""
    try:
        # http://www.ft.com/cms/s/836f1b0e-f07c-11e3-b112-00144feabdc0,Authorised=false.html?_i_location=http%3A%2F%2Fwww.ft.com%2Fcms%2Fs%2F0%2F836f1b0e-f07c-11e3-b112-00144feabdc0.html%3Fsiteedition%3Duk&siteedition=uk&_i_referer=http%3A%2F%2Fwww.ft.com%2Fhome%2Fuk
        ogurl = soup.find(attrs={'property': 'og:url'})['content']
        if urlparse(ogurl).path:
            return ogurl
    except Exception:
        pass
    return url


def find_authors(soup):
    """Get a BeautifulSoup object. Return (Names, where)."""
    try:
        # http://socialhistory.ihcs.ac.ir/article_571_84.html
        # http://jn.physiology.org/content/81/1/319
        attrs = {'name': re.compile('citation_authors?')}
        m = soup.find_all(attrs=attrs)
        authors = []
        for a in m:
            ss = a['content'].split(' and ')
            for s in ss:
                try:
                    name = commons.Name(s)
                    authors.append(name)
                except commons.InvalidNameError:
                    continue
        if not authors:
            raise Exception('"authors" remained an empty list.')
        return authors, attrs
    except Exception:
        pass
    try:
        attrs = {'property': 'og:author'}
        m = soup.find(attrs=attrs)
        return byline_to_names(m['content']), attrs
    except Exception:
        pass
    try:
        # http://www.telegraph.co.uk/science/8323909/The-sperm-whale-works-in-extraordinary-ways.html
        attrs = {'name': 'DCSext.author'}
        m = soup.find(attrs=attrs)
        return byline_to_names(m['content']), attrs
    except Exception:
        pass
    try:
        # http://blogs.ft.com/energy-source/2009/03/04/the-source-platts-rocks-boat-300-crude-solar-shake-ups-hot-jobs/#axzz31G5iiTSq
        m = soup.find(class_='author_byline').text
        return byline_to_names(m), "class_='author_byline'"
    except Exception:
        pass
    try:
        # http://news.bbc.co.uk/2/hi/business/2570109.stm
        m = soup.find(class_='bylineAuthor').text
        return byline_to_names(m), "class_='bylineAuthor'"
    except Exception:
        pass
    try:
        # http://www.bbc.com/news/science-environment-26267918
        m = soup.find(class_='byline-name').text
        return byline_to_names(m), "class_='byline-name'"
    except Exception:
        pass
    try:
        m = soup.find(class_='story-byline').text
        return byline_to_names(m), "class_='story-byline'"
    except Exception:
        pass
    try:
        m = soup.find(class_='meta-author').text
        return byline_to_names(m), 'class="meta-author"'
    except Exception:
        pass
    try:
        names = []
        for m in soup.find_all(class_='authorInline'):
            try:
                names.extend(byline_to_names(m.text))
            except InvalidByLineError:
                continue
        if not names:
            raise Exception('`names` remained an empty list.')
        return names, "class_='authorInline's"
    except Exception:
        pass
    try:
        # try before class_='byline'
        names = []
        for m in soup.find_all(class_='byline-author'):
            try:
                names.extend(byline_to_names(m.text))
            except InvalidByLineError:
                continue
        if not names:
            raise Exception('`names` remained an empty list.')
        return names, "class_='byline-author's"
    except Exception:
        pass
    try:
        # try before class_='author'
        m = soup.find(class_='byline').text
        return byline_to_names(m), "class_='byline'"
    except Exception:
        pass
    try:
        # try before {'name': 'author'}
        names = []
        for m in soup.find_all(class_='author'):
            try:
                names.extend(byline_to_names(m.text))
            except InvalidByLineError:
                continue
        if not names:
            raise Exception('`names` remained an empty list.')
        return names, "class_='author's"
    except Exception:
        pass
    try:
        names = []
        for m in soup.find_all(attrs={'name': 'author'}):
            names.extend(byline_to_names(m['content']))
        if not names:
            raise Exception('"names" remained an empty list.')
        return names, "{'name': 'author'}s"
    except Exception:
        pass
    try:
        # http://www.washingtonpost.com/wp-dyn/content/article/2006/12/20/AR2006122002165.html
        m = soup.find(id='byline').text
        return byline_to_names(m), "id='byline'"
    except Exception:
        pass
    try:
        m = soup.find(class_='byl').text
        return byline_to_names(m), "class_='byl'"
    except Exception:
        pass
    try:
        # http://www.nytimes.com/2003/10/09/us/adding-weight-to-suspicion-sonar-is-linked-to-whale-deaths.html
        attrs = {'name': 'byl'}
        m = soup.find(attrs=attrs)
        return byline_to_names(m['content']), attrs
    except Exception:
        pass
    try:
        # http://timesofindia.indiatimes.com/city/pune/UK-allows-working-visas-for-Indian-students/articleshow/1163528927.cms?
        m = soup.find(id='authortext').text
        return byline_to_names(m), "id='authortext'"
    except Exception:
        pass
    try:
        m = soup.find(class_='name').text
        return byline_to_names(m), "class_='name'"
    except Exception:
        pass
    try:
        # try before {'rel': 'author'}
        m = re.search('"author": "(.*?)"', str(soup)).group(1)
        return byline_to_names(m), '"author": "(.*?)"'
    except Exception:
        pass
    try:
        # http://timesofindia.indiatimes.com/india/27-ft-whale-found-dead-on-Orissa-shore/articleshow/1339609.cms?referral=PM
        attrs = {'rel': 'author'}
        m = soup.find(attrs=attrs).text
        return byline_to_names(m), attrs
    except Exception:
        pass
    try:
        m = re.search('>[Bb]y\s+(.*?)<', str(soup)).group(1)
        return byline_to_names(m), 'str(soup)'
    except Exception:
        pass
    try:
        # http://voices.washingtonpost.com/thefix/eye-on-2008/2008-whale-update.html
        m = re.search('[\n\|]\s*[Bb]y\s+(.*?)[\n]', soup.text).group(1)
        return byline_to_names(m), 'soup.text'
    except Exception:
        pass
    return None, None


def byline_to_names(byline):
    """Find authors in byline sting. Return name objects as a list.

    The "By " prefix will be omitted.
    Names will be seperated either with " and " or ", ".

    specialwords = ('Reporter',
                    'People',
                    'Editor',
                    'Correspondent',
                    'Administrator',
                    'Staff',
                    'Writer',
                    'Office',
                    'News',
                    )

    If any of the specialwords is found in a name. Then it will be omitted from
    the result, unless it is the only name available.

    Examples:

    >>> byline_to_names('\n By Roger Highfield, Science Editor \n')
    [Name(Roger Highfield)]

    >>> byline_to_names(' By Erika Solomon in Beirut and Borzou Daragahi,\
     Middle East correspondent')
    [Name(Erika Solomon), Name(Borzou Daragahi)]
    """
    specialwords = ('Reporter',
                    'People',
                    'Editor',
                    'Correspondent',
                    'Administrator',
                    'Staff',
                    'Writer',
                    'Office',
                    'News',
                    )

    def isspecial(string):
        """Return True if the string contains one of the special words."""
        for sp in specialwords:
            if sp.lower() in string.lower():
                return True
        return False
    for c in ':+':
        if c in byline:
            raise InvalidByLineError('Invalid character ("%s") in byline.' % c)
    if re.search('\d\d\d\d', byline):
        raise InvalidByLineError('Found \d\d\d\d in byline. ' +
                                 '(byline needs to be pure)')
    byline = byline.strip()
    if byline.lower().startswith('by '):
        byline = byline[3:]
    byline = byline.partition('|')[0]
    fullnames = re.split(', and | and |, |;', byline, flags=re.I)
    names = []
    for fullname in fullnames:
        fullname = fullname.partition(' in ')[0]
        name = commons.Name(fullname)
        if isspecial(name.lastname):
            name.nofirst_fulllast()
        names.append(name)
    # Remove names containing special words or not having firstname (orgs)
    name0 = names[0]  # In case nothing remains of names
    names = [n for n in names if n.firstname and not isspecial(n.lastname)]
    if not names:
        names.append(name0)
    return names


def find_issn(soup):
    """Return International Standard Serial Number as a string.

    Normally ISSN should be in the  '\d{4}\-\d{3}[\dX]' format, but this function
    does not check that.
    """
    try:
        # http://socialhistory.ihcs.ac.ir/article_319_84.html
        # http://psycnet.apa.org/journals/edu/30/9/641/
        m = soup.find(attrs={'name': 'citation_issn'})
        return m['content'].strip()
    except Exception:
        pass


def find_pmid(soup):
    """Get the BS object of a page. Return pmid as a string."""
    try:
        # http://jn.physiology.org/content/81/1/319
        m = soup.find(attrs={'name': 'citation_pmid'})
        return m['content']
    except Exception:
        pass


def find_volume(soup):
    """Return citatoin volume number as a string."""
    try:
        # http://socialhistory.ihcs.ac.ir/article_319_84.html
        m = soup.find(attrs={'name': 'citation_volume'})
        return m['content'].strip()
    except Exception:
        pass


def find_issue(soup):
    """Return citatoin issue number as a string."""
    try:
        # http://socialhistory.ihcs.ac.ir/article_319_84.html
        m = soup.find(attrs={'name': 'citation_issue'})
        return m['content'].strip()
    except Exception:
        pass


def find_pages(soup):
    """Return citatoin pages as a string."""
    try:
        # http://socialhistory.ihcs.ac.ir/article_319_84.html
        fp = soup.find(attrs={'name': 'citation_firstpage'})['content'].strip()
        lp = soup.find(attrs={'name': 'citation_lastpage'})['content'].strip()
        return fp + '–' + lp
    except Exception:
        pass


def find_sitename(soup, url, authors, hometitle_list, thread):
    """Return (site's name as a string, where).

    Parameters:
        soup: BS object of the page being processed.
        url: URL of the page.
        authors: Authors list returned from find_authors function.
        hometitle_list: A list containing hometitle string.
        thread: The thread that should be joined before using hometitle_list.
    Returns site's name as a string.
    """
    try:
        attrs = {'name': 'og:site_name'}
        return soup.find(attrs=attrs)['content'].strip(), attrs
    except Exception:
        pass
    try:
        # https://www.bbc.com/news/science-environment-26878529
        attrs = {'property': 'og:site_name'}
        return soup.find(attrs=attrs)['content'].strip(), attrs
    except Exception:
        pass
    try:
        # http://www.nytimes.com/2007/06/13/world/americas/13iht-whale.1.6123654.html?_r=0
        attrs = {'name': 'PublisherName'}
        return soup.find(attrs=attrs)['value'].strip(), attrs
    except Exception:
        pass
    try:
        # http://www.bbc.com/news/science-environment-26878529 (Optional)
        attrs = {'name': 'CPS_SITE_NAME'}
        return soup.find(attrs=attrs)['content'].strip(), attrs
    except Exception:
        pass
    try:
        # http://www.nytimes.com/2013/10/01/science/a-wealth-of-data-in-whale-breath.html
        attrs = {'name': 'cre'}
        return soup.find(attrs=attrs)['content'].strip(), attrs
    except Exception:
        pass
    try:
        # search the title
        sitename = parse_title(soup.title.text, url, authors, hometitle_list,
                               thread)[2]
        if sitename:
            return sitename, 'parse_title'
    except Exception:
        pass
    try:
        # using hometitle
        thread.join()
        if ':' in hometitle_list[0]:
            # http://www.washingtonpost.com/wp-dyn/content/article/2005/09/02/AR2005090200822.html
            sitename = hometitle_list[0].split(':')[0].strip()
            if sitename:
                return sitename, 'hometitle.split(":")[0]'
        sitename = parse_title(hometitle_list[0], url, None)[2]
        if sitename:
            return sitename, 'parsed hometitle'
        return hometitle_list[0], 'hometitle_list[0]'
    except Exception:
        pass
    # return hostname
    if urlparse(url).hostname.startswith('www.'):
        return urlparse(url).hostname[4:], 'hostname'
    else:
        return urlparse(url).hostname, 'hostname'


def try_find(soup, find_parameters):
    """Return the first matching item in find_paras as (string, used_attrs).

    args:
        soup: The beautiful soup object.
        find_parameters: List of parameters to try on soup in the following
            format:
                ({atrr_name, value}, 'getitem|getattr', 'content|text|...')
                where {atrrn, value} will be used in
                bs.find(attrs={atrrn, value}).
    Return (None, None) if none of the parameters match bs.
    """
    for fp in find_parameters:
        try:
            attrs = fp[0]
            m = soup.find(attrs=attrs)
            if fp[1] == 'getitem':
                string = m[fp[2]].strip()
                return string, attrs
            elif fp[1] == 'getattr':
                string = getattr(m, fp[2]).strip()
                return string, attrs
        except Exception:
            pass
    return None, None


def find_title(soup, url, authors, hometitle_list, thread):
    """Return (title_string, where_info)."""
    find_parameters = (
        # http://socialhistory.ihcs.ac.ir/article_319_84.html
        ({'name': 'citation_title'}, 'getitem', 'content'),
        # http://www.telegraph.co.uk/earth/earthnews/6190335/Whale-found-dead-in-Thames.html
        # Should be tried before og:title
        ({'name': 'title'}, 'getitem', 'content'),
        # http://www.bostonglobe.com/ideas/2014/04/28/new-study-reveals-how-honky-tonk-hits-respond-changing-american-fortunes/9ep0iPknDBl9EFFaoXfbmL/comments.html
        # Should be tried before og:title
        ({'class': 'main-hed'}, 'getattr', 'text'),
        # http://timesofindia.indiatimes.com/city/thiruvananthapuram/Whale-shark-dies-in-aquarium/articleshow/32607977.cms
        # Should be tried before og:title
        ({'class': 'arttle'}, 'getattr', 'text'),
        # http://www.bbc.com/news/science-environment-26878529
        ({'property': 'og:title'}, 'getitem', 'content'),
        # http://www.bbc.com/news/science-environment-26267918
        ({'name': 'Headline'}, 'getitem', 'content'),
        # http://www.nytimes.com/2007/06/13/world/americas/13iht-whale.1.6123654.html?_r=0
        ({'class': 'articleHeadline'}, 'getattr', 'text'),
        # http://www.nytimes.com/2007/09/11/us/11whale.html
        ({'name': 'hdl'}, 'getitem', 'content'),
        # http://ftalphaville.ft.com/2012/05/16/1002861/recap-and-tranche-primer/?Authorised=false
        ({'class': 'entry-title'}, 'getattr', 'text'),
        # http://www.ensani.ir/fa/content/326173/default.aspx
        ({'class': 'title'}, 'getattr', 'text'),
        # http://voices.washingtonpost.com/thefix/eye-on-2008/2008-whale-update.html
        ({'id': 'entryhead'}, 'getattr', 'text'),
    )
    raw_title, tag = try_find(soup, find_parameters)
    if not raw_title:
        try:
            raw_title, tag = soup.title.text.strip(), 'soup.title.text'
        except Exception:
            pass
    if raw_title:
        logger.debug('Unparsed title tag: ' + str(tag))
        parsed_title = parse_title(raw_title, url, authors, hometitle_list,
                                   thread)
        logger.debug('Parsed title: ' + str(parsed_title))
        return parsed_title[1], tag
    else:
        return None, None


def parse_title(title, url, authors, hometitle_list=None, thread=None):
    """Return (intitle_author, pure_title, intitle_sitename).

    Examples:

    >>> parse_title("Rockhopper raises Falklands oil estimate - FT.com",
            "http://www.ft.com/cms/s/ea29ffb6-c759-11e0-9cac-00144feabdc0",
            None)
    (None, 'Rockhopper raises Falklands oil estimate', 'FT.com')

    >>> parse_title('some title - FT.com - something unknown',
            "http://www.ft.com/cms/s/ea29ffb6-c759-11e0-9cac-00144feabdc0",
            None)
    (None, 'some title - something unknown', 'FT.com')

    >>> parse_title("Alpha decay - Wikipedia, the free encyclopedia",
            "https://en.wikipedia.org/wiki/Alpha_decay",
            None)
    (None, 'Alpha decay', 'Wikipedia, the free encyclopedia')

    >>> parse_title("	BBC NEWS | Health | New teeth 'could soon be grown'",
            'http://news.bbc.co.uk/2/hi/health/3679313.stm',
            None)
    (None, "Health - New teeth 'could soon be grown'", 'BBC NEWS')
    """
    intitle_author = intitle_sitename = None
    sep_regex = ' - | — |\|'
    title_parts = re.split(sep_regex, title.strip())
    if len(title_parts) == 1:
        return (None, title, None)
    hostname = urlparse(url).hostname.replace('www.', '')
    # Searching for intitle_sitename
    # 1. In hostname
    hnset = set(hostname.split('.'))
    for part in title_parts:
        if (part in hostname) or not set(part.lower().split()) - hnset:
            intitle_sitename = part
            break
    if not intitle_sitename:
        # 2. Using difflib on hostname
        # Cutoff = 0.3: 'BBC - Homepage' will match u'‭BBC ‮فارسی‬'
        close_matches = difflib.get_close_matches(hostname, title_parts, n=1,
                                                  cutoff=.3)
        if close_matches:
            intitle_sitename = close_matches[0]
    if not intitle_sitename:
        if thread:
            thread.join()
        if hometitle_list:
            hometitle = hometitle_list[0]
        # 3. In homepage title
        for part in title_parts:
            if (part in hometitle):
                intitle_sitename = part
                break
    if not intitle_sitename:
        # 4. Using difflib on hometitle
        close_matches = difflib.get_close_matches(hometitle, title_parts, n=1,
                                                  cutoff=.3)
        if close_matches:
            intitle_sitename = close_matches[0]
    # Searching for intitle_author
    if authors:
        for author in authors:
            for part in title_parts:
                if author.lastname.lower() in part.lower():
                    intitle_author = part
    # Title purification
    if intitle_sitename:
        title_parts.remove(intitle_sitename)
        intitle_sitename = intitle_sitename.strip()
    if intitle_author:
        title_parts.remove(intitle_author)
        intitle_author = intitle_author.strip()
    pure_title = ' - '.join(title_parts)
    return intitle_author, pure_title, intitle_sitename


def try_find_date(soup, find_parameters):
    """Similar to try_find(), but for finding dates.

    Return a string in '%Y-%m-%d' format.
    """
    for fp in find_parameters:
        try:
            attrs = fp[0]
            m = soup.find(attrs=attrs)
            if fp[1] == 'getitem':
                string = m[fp[2]]
                date = commons.finddate(string)
                if date:
                    return date, attrs
            elif fp[1] == 'getattr':
                string = getattr(m, fp[2])
                date = commons.finddate(string)
                if date:
                    return date, attrs
        except Exception:
            pass
    return None, None


def find_date(soup, url):
    """Get the BS object and url of a page. Return (date_obj, where)."""
    find_parameters = (
        # http://socialhistory.ihcs.ac.ir/article_319_84.html
        ({'name': 'citation_date'}, 'getitem', 'content'),
        # http://jn.physiology.org/content/81/1/319
        ({'name': 'citation_publication_date'}, 'getitem', 'content'),
        # http://www.telegraph.co.uk/news/worldnews/northamerica/usa/9872625/Kasatka-the-killer-whale-gives-birth-in-pool-at-Sea-World-in-San-Diego.html
        ({'name': 'last-modified'}, 'getitem', 'content'),
        # http://www.mirror.co.uk/news/weird-news/amazing-rescue-drowning-diver-saved-409479
        # should be placed before article:modified_time
        ({'itemprop': 'datePublished'}, 'getitem', 'datetime'),
        # http://www.mirror.co.uk/news/uk-news/how-reid-will-get-it-all-off-pat--535323
        # should be placed before article:modified_time
        ({'data-type': 'pub-date'}, 'getattr', 'text'),
        # http://dealbook.nytimes.com/2014/05/30/insider-trading-inquiry-includes-mickelson-and-icahn/
        # place before {'property': 'article:modified_time'}
        ({'property': 'article:published_time'}, 'getitem', 'content'),
        # http://www.dailymail.co.uk/news/article-2384832/Great-White-sharks-hunt-seals-South-Africa.html
        ({'property': 'article:modified_time'}, 'getitem', 'content'),
        # http://www.tgdaily.com/web/100381-apple-might-buy-beats-for-32-billion
        ({'property': 'dc:date dc:created'}, 'getitem', 'content'),
        # http://www.bbc.co.uk/news/science-environment-20890389
        ({'name': 'OriginalPublicationDate'}, 'getitem', 'content'),
        ({'name': 'publish-date'}, 'getitem', 'content'),
        # http://www.washingtonpost.com/wp-srv/style/movies/reviews/godsandmonsterskempley.htm
        ({'name': 'pub_date'}, 'getitem', 'content'),
        # http://www.economist.com/node/1271090?zid=313&ah=fe2aac0b11adef572d67aed9273b6e55
        ({'name': 'pubdate'}, 'getitem', 'content'),
        # http://www.ft.com/cms/s/ea29ffb6-c759-11e0-9cac-00144feabdc0,Authorised=false.html?_i_location=http%3A%2F%2Fwww.ft.com%2Fcms%2Fs%2F0%2Fea29ffb6-c759-11e0-9cac-00144feabdc0.html%3Fsiteedition%3Duk&siteedition=uk&_i_referer=#axzz31G5ZgwCH
        ({'id': 'publicationDate'}, 'getattr', 'text'),
        # http://www.nytimes.com/2007/06/13/world/americas/13iht-whale.1.6123654.html?_r=0
        ({'class': 'dateline'}, 'getattr', 'text'),
        # http://www.nytimes.com/2003/12/14/us/willy-whale-dies-in-norway.html
        ({'name': 'DISPLAYDATE'}, 'getitem', 'content'),
        # http://www.washingtonpost.com/wp-dyn/content/article/2006/01/19/AR2006011902990.html
        ({'name': 'DC.date.issued'}, 'getitem', 'content'),
        # http://www.farsnews.com/newstext.php?nn=13930418000036
        ({'name': 'dc.Date'}, 'getitem', 'content'),
        # http://www.huffingtonpost.ca/arti-patel/nina-davuluri_b_3936174.html
        ({'name': 'sailthru.date'}, 'getitem', 'content'),
        # http://ftalphaville.ft.com/2012/05/16/1002861/recap-and-tranche-primer/?Authorised=false
        ({'class': 'entry-date'}, 'getattr', 'text'),
        # http://www.huffingtonpost.com/huff-wires/20121203/us-sci-nasa-voyager/
        ({'class': 'updated'}, 'getattr', 'text'),
        # http://timesofindia.indiatimes.com/city/thiruvananthapuram/Whale-shark-dies-in-aquarium/articleshow/32607977.cms
        ({'class': 'byline'}, 'getattr', 'text'),
        # wikipedia
        ({'id': 'footer-info-lastmod'}, 'getattr', 'text'),
    )
    date, tag = try_find_date(soup, find_parameters)
    if date:
        return date, tag
    else:
        # http://ftalphaville.ft.com/2012/05/16/1002861/recap-and-tranche-primer/?Authorised=false
        date = commons.finddate(url)
    if date:
        return date, 'url'
    else:
        # https://www.bbc.com/news/uk-england-25462900
        date = commons.finddate(soup.text)
    if date:
        return date, 'soup.text'
    else:
        logger.info('Searching for date in page content.\n' + url)
        return commons.finddate(str(soup)), 'str(soup)'
    return None, None


def get_hometitle(url, headers, hometitle_list):
    """Get homepage of the url and return it's title.

    hometitle_list will be used to return the thread result.
    This function is invoked through a thread.
    """
    homeurl = '://'.join(urlparse(url)[:2])
    try:
        requests_visa(homeurl, headers)
        content = requests.get(homeurl, headers=headers, timeout=15).content
        strainer = bs4.SoupStrainer('title')
        soup = bs4.BeautifulSoup(content, parse_only=strainer)
        hometitle_list.append(soup.title.text.strip())
    except Exception:
        pass


def requests_visa(url, request_headers=None):
    """Check content-type and content-length of the response.

    Return True if content-type is text/* and content-length is less than 1MB.
    Also return True if no information is available. Else return False.
    """
    response_headers = requests.head(url, headers=request_headers).headers
    if 'content-length' in response_headers:
        megabytes = int(response_headers['content-length']) / 1000000.
        if megabytes > 1:
            raise ContentLengthError('Content-length was too long. (' +
                                     format(megabytes, '.2f') +
                                     ' MB)')
    if 'content-type' in response_headers:
        if response_headers['content-type'].startswith('text/'):
            return True
        else:
            raise ContentTypeError(
                'Invalid content-type: ' +
                response_headers['content-type'] +
                ' (URL-content is supposed to be text/html)')
    return True


def url2dictionary(url):
    """Get url and return the result as a dictionary."""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:30.0)' +
               ' Gecko/20100101 Firefox/30.0'}

    # Creating a thread to fetch homepage title in background
    hometitle_list = []  # A mutable variable used to get the thread result
    thread = Thread(target=get_hometitle, args=(url, headers, hometitle_list))
    thread.start()

    requests_visa(url, headers)
    r = requests.get(url, headers=headers, timeout=15)
    if r.status_code != 200:
        raise StatusCodeError(r.status_code)
    soup = bs4.BeautifulSoup(r.content)
    d = {}
    d['url'] = find_url(soup, url)
    authors, tag = find_authors(soup)
    if authors:
        logger.debug('Authors tag: ' + str(tag))
        d['authors'] = authors
    d['issn'] = find_issn(soup)
    d['pmid'] = find_pmid(soup)
    d['volume'] = find_volume(soup)
    d['issue'] = find_issue(soup)
    d['pages'] = find_pages(soup)
    d['journal'] = find_journal(soup)
    if d['journal']:
        d['type'] = 'jour'
    else:
        d['type'] = 'web'
        d['website'], tag = find_sitename(soup, url, authors, hometitle_list,
                                          thread)
        logger.debug('Website tag: ' + str(tag))
    d['title'], tag = find_title(soup, url, authors, hometitle_list, thread)
    date, tag = find_date(soup, url)
    if date:
        logger.debug('Date tag: ' + str(tag))
        d['date'] = date
        d['year'] = str(date.year)
    d['language'], d['error'] = commons.detect_language(soup.text)
    return d


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("langid").setLevel(logging.WARNING)
    logger = logging.getLogger()
else:
    logger = logging.getLogger(__name__)
