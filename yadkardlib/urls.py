#!/data/project/yadkard/venv/bin/python
# -*- coding: utf-8 -*-

"""Codes used for parsing contents of an arbitrary URL."""

import re
from urlparse import urlparse
import logging
import difflib

import requests
from bs4 import BeautifulSoup as BS


import conv
import config

if config.lang == 'en':
    import wikiref_en as wikiref
    import wikicite_en as wikicite
else:
    import wikiref_fa as wikiref
    import wikicite_fa  as wikicite


class Citation():

    """Create citation object."""

    def __init__(self, url, date_format='%Y-%m-%d'):
        self.url = url
        self.dictionary = url2dictionary(url)
        self.ref = wikiref.create(self.dictionary)
        self.cite = wikicite.create(self.dictionary, date_format)
        self.error = 0


class StatusCodeError(Exception):

    """Raise when requests.get.status_code != 200."""

    pass


def find_journal(bs):
    """Return journal title as a string."""
    try:
        #http://socialhistory.ihcs.ac.ir/article_319_84.html
        m = bs.find(attrs={'name': 'citation_journal_title'})
        return m['content'].strip()
    except Exception:
        pass


def find_url(bs, url):
    """Get a BeautifulSoup object it's url. Return og:url or url as a string."""
    try:
        #http://www.ft.com/cms/s/836f1b0e-f07c-11e3-b112-00144feabdc0,Authorised=false.html?_i_location=http%3A%2F%2Fwww.ft.com%2Fcms%2Fs%2F0%2F836f1b0e-f07c-11e3-b112-00144feabdc0.html%3Fsiteedition%3Duk&siteedition=uk&_i_referer=http%3A%2F%2Fwww.ft.com%2Fhome%2Fuk
        return bs.find(attrs={'property': 'og:url'})['content']
    except Exception:
        pass
    return url


def find_authors(bs):
    """Get a BeautifulSoup object. Return (Names, where)."""
    try:
        #http://socialhistory.ihcs.ac.ir/article_571_84.html
        #http://jn.physiology.org/content/81/1/319
        attrs = {'name': 'citation_author'}
        m = bs.find_all(attrs=attrs)
        authors = []
        for a in m:
            ss = a['content'].split(' and ')
            for s in ss:
                name = conv.Name(s)
                authors.append(name)
        if not authors:
            raise Exception('"authors" remained an empty list.')
        return authors, attrs
    except Exception:
        pass
    try:
        #http://www.telegraph.co.uk/science/8323909/The-sperm-whale-works-in-extraordinary-ways.html
        attrs={'name': 'DCSext.author'}
        m = bs.find(attrs=attrs)
        return byline_to_names(m['content']), attrs
    except Exception:
        pass
    try:
        #http://blogs.ft.com/energy-source/2009/03/04/the-source-platts-rocks-boat-300-crude-solar-shake-ups-hot-jobs/#axzz31G5iiTSq
        m = bs.find(class_='author_byline').text
        return byline_to_names(m), "class_='author_byline'"
    except Exception:
        pass
    try:
        #http://news.bbc.co.uk/2/hi/business/2570109.stm
        m = bs.find(class_='bylineAuthor').text
        return byline_to_names(m), "class_='bylineAuthor'"
    except Exception:
        pass
    try:
        #http://www.bbc.com/news/science-environment-26267918
        m = bs.find(class_='byline-name').text
        return byline_to_names(m), "class_='byline-name'"
    except Exception:
        pass
    try:
        m = bs.find(class_='story-byline').text
        return byline_to_names(m), "class_='story-byline'"
    except Exception:
        pass
    try:
        #http://www.dailymail.co.uk/news/article-2633025/
        #http://www.mirror.co.uk/news/uk-news/whale-doomed-to-die-557471
        #try before {'name':'author'}
        names = []
        for m in bs.find_all(class_='author'):
            names.extend(byline_to_names(m.text))
        if not names:
            raise Exception('"names" remained an empty list.')
        return names, "class_='author'"
    except Exception:
        pass
    try:
        #http://www.telegraph.co.uk/science/science-news/3313298/Marine-collapse-linked-to-whale-decline.html
        attrs = {'name': 'author'}
        m = bs.find(attrs=attrs)
        return byline_to_names(m['content']), attrs
    except Exception:
        pass
    try:
        #http://timesofindia.indiatimes.com/india/27-ft-whale-found-dead-on-Orissa-shore/articleshow/1339609.cms?referral=PM
        attrs = {'rel': 'author'}
        m = bs.find(attrs=attrs).text
        return byline_to_names(m), attrs
    except Exception:
        pass
    try:
        m = bs.find(class_='byline').text
        return byline_to_names(m), "class_='byline'"
    except Exception:
        pass
    try:
        #http://www.washingtonpost.com/wp-dyn/content/article/2006/12/20/AR2006122002165.html
        m = bs.find(id='byline').text
        return byline_to_names(m), "id='byline'"
    except Exception:
        pass
    try:
        #http://news.bbc.co.uk/2/hi/programmes/newsnight/5178122.stm
        m = bs.find(class_='byl').text
        return byline_to_names(m), "class_='byl'"
    except Exception:
        pass
    try:
        #http://www.nytimes.com/2003/10/09/us/adding-weight-to-suspicion-sonar-is-linked-to-whale-deaths.html
        attrs = {'name': 'byl'}
        m = bs.find(attrs=attrs)
        return byline_to_names(m['content']), attrs
    except Exception:
        pass
    try:
        #http://timesofindia.indiatimes.com/city/pune/UK-allows-working-visas-for-Indian-students/articleshow/1163528927.cms?
        m = bs.find(id='authortext').text
        return byline_to_names(m), "id='authortext'"
    except Exception:
        pass
    try:
        m = bs.find(class_='name').text
        return byline_to_names(m), "class_='name'"
    except Exception:
        pass
    try:
        #http://voices.washingtonpost.com/thefix/eye-on-2008/2008-whale-update.html
        m = re.search('[\n>"\']\s*By\s*(.*)[<\n"\']', bs.text, re.I).group(1)
        return byline_to_names(m), 'bs.text'
    except Exception:
        pass
    return None, None


def byline_to_names(byline):
    '''Find authors in byline sting. Return name objects as a list.

The "By " prefix will be omitted.
Names will be seperated either with " and " or ", ".

stopwords = ('Reporter',
             'People',
             'Editor',
             'Correspondent',
             'Administrator',
             )

If any of the stopwords is found in a name. Then it will be omitted from the
result, unless it is the only name available.

Examples:

>>> byline_to_names('\n By Roger Highfield, Science Editor \n')
[Name(Roger Highfield)]

>>> byline_to_names(' By Erika Solomon in Beirut and Borzou Daragahi,\
 Middle East correspondent')
[Name(Erika Solomon), Name(Borzou Daragahi)]
'''
    if '|' in byline:
        raise Exception('Invalid character ("|") in byline.')
    if re.search('\d\d\d\d', byline):
        raise Exception('Found \d\d\d\d in byline. (byline needs to be pure)')
    byline = byline.strip()
    if re.match('by ', byline, re.I):
        byline = byline[3:]
    fullnames = re.split(', | and |;', byline, re.I)
    names = []
    stopwords = ('Reporter',
                 'People',
                 'Editor',
                 'Correspondent',
                 'Administrator',
                 )
    for fullname in fullnames:
        if ' in ' in fullname:
            fullname = fullname.split(' in ')[0]
        name = conv.Name(fullname)
        if re.search('|'.join(stopwords), name.lastname, re.I):
            name.nofirst_fulllast()
        names.append(name)
    if len(names) > 1:
        for name in names:
            if re.search('|'.join(stopwords), name.lastname, re.I):
                names.remove(name)
    return names


def find_issn(bs):
    """Return International Standard Serial Number as a string.

Normally ISSN should be in the  '\d{4}\-\d{3}[\dX]' format, but this function
does not check that.
"""
    try:
        #http://socialhistory.ihcs.ac.ir/article_319_84.html
        m = bs.find(attrs={'name': 'citation_issn'})
        return m['content'].strip()
    except Exception:
        pass


def find_pmid(bs):
    """Get the BS object of a page. Return pmid as a string."""
    try:
        #http://jn.physiology.org/content/81/1/319
        m = bs.find(attrs={'name': 'citation_pmid'})
        return m['content']
    except Exception:
        pass


def find_volume(bs):
    """Return citatoin volume number as a string."""
    try:
        #http://socialhistory.ihcs.ac.ir/article_319_84.html
        m = bs.find(attrs={'name': 'citation_volume'})
        return m['content'].strip()
    except Exception:
        pass


def find_issue(bs):
    """Return citatoin issue number as a string."""
    try:
        #http://socialhistory.ihcs.ac.ir/article_319_84.html
        m = bs.find(attrs={'name': 'citation_issue'})
        return m['content'].strip()
    except Exception:
        pass


def find_pages(bs):
    """Return citatoin pages as a string."""
    try:
        #http://socialhistory.ihcs.ac.ir/article_319_84.html
        fp = bs.find(attrs={'name': 'citation_firstpage'})['content'].strip()
        lp = bs.find(attrs={'name': 'citation_lastpage'})['content'].strip()
        return fp + u'–' + lp
    except Exception:
        pass


def find_sitename(bs, url, authors):
    '''Return (site's name as a string, where).

Get page's bs object, it's title, and authors. Return site's name as a string.
'''
    try:
        attrs = {'name': 'og:site_name'}
        return bs.find(attrs=attrs)['content'].strip(), attrs
    except Exception:
        pass
    try:
        #https://www.bbc.com/news/science-environment-26878529
        attrs={'property': 'og:site_name'}
        return bs.find(attrs=attrs)['content'].strip(), attrs
    except Exception:
        pass
    try:
        #http://www.nytimes.com/2007/06/13/world/americas/13iht-whale.1.6123654.html?_r=0
        attrs={'name': 'PublisherName'}
        return bs.find(attrs=attrs)['value'].strip(), attrs
    except Exception:
        pass
    try:
        #http://www.bbc.com/news/science-environment-26878529 (Optional)
        attrs={'name': 'CPS_SITE_NAME'}
        return bs.find(attrs=attrs)['content'].strip(), attrs
    except Exception:
        pass
    try:
        #http://www.nytimes.com/2013/10/01/science/a-wealth-of-data-in-whale-breath.html
        attrs={'name': 'cre'}
        return bs.find(attrs=attrs)['content'].strip(), attrs
    except Exception:
        pass
    try:
        logger.info('Searching for site_name through bs.title.\r\n' + url)
        return parse_title(bs.title.text, url, authors)[2], 'bs.title.text'
    except Exception:
        pass


def find_title(bs):
    """Get a BeautifulSoup object. Return (title_string, where)."""
    try:
        #http://socialhistory.ihcs.ac.ir/article_319_84.html
        attrs = {'name': 'citation_title'}
        return bs.find(attrs=attrs)['content'].strip(), attrs
    except Exception:
        pass
    try:
        #http://www.telegraph.co.uk/earth/earthnews/6190335/Whale-found-dead-in-Thames.html
        #Should be tried before og:title
        attrs = {'name': 'title'}
        return bs.find(attrs=attrs)['content'].strip(), attrs
    except Exception:
        pass
    try:
        #http://www.bostonglobe.com/ideas/2014/04/28/new-study-reveals-how-honky-tonk-hits-respond-changing-american-fortunes/9ep0iPknDBl9EFFaoXfbmL/comments.html
        #Should be tried before og:title
        attrs = {'class': 'main-hed'}
        return bs.find(attrs=attrs).text.strip(), attrs
    except Exception:
        pass
    try:
        #http://timesofindia.indiatimes.com/city/thiruvananthapuram/Whale-shark-dies-in-aquarium/articleshow/32607977.cms
        #Should be tried before og:title
        attrs = {'class': 'arttle'}
        return bs.find(attrs=attrs).text.strip(), attrs
    except Exception:
        pass
    try:
        #http://www.bbc.com/news/science-environment-26878529
        attrs = {'property': 'og:title'}
        return bs.find(attrs=attrs)['content'].strip(), attrs
    except Exception:
        pass
    try:
        #http://www.bbc.com/news/science-environment-26267918
        attrs = {'name': 'Headline'}
        return bs.find(attrs=attrs)['content'].strip(), attrs
    except Exception:
        pass
    try:
        #http://www.nytimes.com/2007/06/13/world/americas/13iht-whale.1.6123654.html?_r=0
        attrs = {'class': 'articleHeadline'}
        return bs.find(attrs=attrs).text.strip(), attrs
    except Exception:
        pass
    try:
        #http://www.nytimes.com/2007/09/11/us/11whale.html
        attrs = {'name': 'hdl'}
        return bs.find(attrs=attrs)['content'].strip(), attrs
    except Exception:
        pass
    try:
        #ftalphaville.ft.com/2012/05/16/1002861/recap-and-tranche-primer/?Authorised=false
        attrs = {'class': 'entry-title'}
        return bs.find(attrs=attrs).text.strip(), attrs
    except Exception:
        pass
    try:
        #http://voices.washingtonpost.com/thefix/eye-on-2008/2008-whale-update.html
        attrs = {'id': 'entryhead'}
        return bs.find(attrs=attrs).text.strip(), attrs
    except Exception:
        pass
    try:
        return bs.title.text.strip(), 'bs.title.text.strip()'
    except Exception:
        pass


def parse_title(title_string, url, authors):
    '''Return (intitle_author, pure_title, intitle_sitename).

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
'''
    intitle_author = intitle_sitename = None
    sep_regex = u'( - | — | \| )'
    title_parts = re.split(sep_regex, title_string.strip())
    if len(title_parts) == 1:
        return (None, title_string, None)
    netloc = urlparse(url)[1].lower().replace('www.', '')
    #detecting intitle_sitename
    netlocset = set(netloc.split('.'))
    for p in title_parts:
        if (p in netloc) or not set(p.lower().split()) - netlocset:
            intitle_sitename = p
            break
    if not intitle_sitename:
        #using difflib
        close_matches = difflib.get_close_matches(netloc, title_parts, n=2,
                                                  cutoff=.35)
        if close_matches:
            intitle_sitename = close_matches[0]
    #detecting intitle_author
    if authors:
        for author in authors:
            for part in title_parts:
                if author.lastname.lower() in part.lower():
                    intitle_author = part
    if intitle_sitename:
        title_parts.remove(intitle_sitename)
        intitle_sitename = intitle_sitename.strip()
    if intitle_author:
        title_parts.remove(intitle_author)
        intitle_author = intitle_author.strip()
    if re.match(sep_regex, title_parts[0]):
        title_parts.pop(0)
    if re.match(sep_regex, title_parts[-1]):
        title_parts.pop()
    pure_title = ''.join(title_parts)
    pure_title = re.sub(sep_regex + sep_regex, r'\1', pure_title)
    # Replacing special characters with their respective HTML entities
    pure_title = pure_title.replace('|', '&#124;').strip()
    pure_title = pure_title.replace('[', '&#91;').strip()
    pure_title = pure_title.replace(']', '&#93;').strip()
    return intitle_author, pure_title, intitle_sitename


def find_date(bs, url):
    """Get the BS object and url of a page. Return (date_obj, where)."""
    try:
        #http://socialhistory.ihcs.ac.ir/article_319_84.html
        attrs = {'name': 'citation_date'}
        m = bs.find(attrs=attrs)
        return conv.finddate(m['content']).strftime('%Y-%m-%d'), attrs
    except Exception:
        pass
    try:
        #http://jn.physiology.org/content/81/1/319
        attrs = {'name': 'citation_publication_date'}
        m = bs.find(attrs=attrs)
        return conv.finddate(m['content']).strftime('%Y-%m-%d'), attrs
    except Exception:
        pass
    try:
        #http://www.telegraph.co.uk/news/worldnews/northamerica/usa/9872625/Kasatka-the-killer-whale-gives-birth-in-pool-at-Sea-World-in-San-Diego.html
        attrs = {'name': 'last-modified'}
        m = bs.find(attrs=attrs)
        return conv.finddate(m['content']).strftime('%Y-%m-%d'), attrs
    except Exception:
        pass
    try:
        #http://www.mirror.co.uk/news/weird-news/amazing-rescue-drowning-diver-saved-409479
        #should be placed before article:modified_time
        attrs = {'itemprop': 'datePublished'}
        m = bs.find(attrs=attrs)
        return conv.finddate(m['datetime']).strftime('%Y-%m-%d'), attrs
    except Exception:
        pass
    try:
        #http://www.mirror.co.uk/news/uk-news/how-reid-will-get-it-all-off-pat--535323
        #should be placed before article:modified_time
        attrs = {'data-type': 'pub-date'}
        m = bs.find(attrs=attrs)
        return conv.finddate(m.text).strftime('%Y-%m-%d'), attrs
    except Exception:
        pass
    try:
        attrs = {'property': 'article:modified_time'}
        m = bs.find(attrs=attrs)
        return conv.finddate(m['content']).strftime('%Y-%m-%d'), attrs
    except Exception:
        pass
    try:
        attrs = {'property': 'article:published_time'}
        m = bs.find(attrs=attrs)
        return conv.finddate(m['content']).strftime('%Y-%m-%d'), attrs
    except Exception:
        pass
    try:
        attrs = {'name': 'OriginalPublicationDate'}
        m = bs.find(attrs=attrs)
        return conv.finddate(m['content']).strftime('%Y-%m-%d'), attrs
    except Exception:
        pass
    try:
        attrs = {'name': 'publish-date'}
        m = bs.find(attrs=attrs)
        return conv.finddate(m['content']).strftime('%Y-%m-%d'), attrs
    except Exception:
        pass
    try:
        attrs = {'name': 'pub_date'}
        m = bs.find(attrs=attrs)
        return conv.finddate(m['content']).strftime('%Y-%m-%d'), attrs
    except Exception:
        pass
    try:
        #http://www.ft.com/cms/s/ea29ffb6-c759-11e0-9cac-00144feabdc0,Authorised=false.html?_i_location=http%3A%2F%2Fwww.ft.com%2Fcms%2Fs%2F0%2Fea29ffb6-c759-11e0-9cac-00144feabdc0.html%3Fsiteedition%3Duk&siteedition=uk&_i_referer=#axzz31G5ZgwCH
        attrs = {'id': 'publicationDate'}
        m = bs.find(attrs=attrs)
        return conv.finddate(m.text).strftime('%Y-%m-%d'), attrs
    except Exception:
        pass
    try:
        #http://www.nytimes.com/2007/06/13/world/americas/13iht-whale.1.6123654.html?_r=0
        attrs = {'class': 'dateline'}
        m = bs.find(attrs=attrs).text
        return conv.finddate(m).strftime('%Y-%m-%d'), attrs
    except Exception:
        pass
    try:
        #http://www.nytimes.com/2003/12/14/us/willy-whale-dies-in-norway.html
        attrs = {'name': 'DISPLAYDATE'}
        m = bs.find(attrs=attrs)
        return conv.finddate(m['content']).strftime('%Y-%m-%d'), attrs
    except Exception:
        pass
    try:
        #http://www.washingtonpost.com/wp-dyn/content/article/2006/01/19/AR2006011902990.html
        attrs = {'name': 'DC.date.issued'}
        m = bs.find(attrs=attrs)
        return conv.finddate(m['content']).strftime('%Y-%m-%d'), attrs
    except Exception:
        pass
    try:
        #http://www.huffingtonpost.ca/arti-patel/nina-davuluri_b_3936174.html
        attrs = {'name': 'sailthru.date'}
        m = bs.find(attrs=attrs)
        return conv.finddate(m['content']).strftime('%Y-%m-%d'), attrs
    except Exception:
        pass
    try:
        #http://ftalphaville.ft.com/2012/05/16/1002861/recap-and-tranche-primer/?Authorised=false
        attrs = {'class': 'entry-date'}
        m = bs.find(attrs=attrs).text
        return conv.finddate(m).strftime('%Y-%m-%d'), attrs
    except Exception:
        pass
    try:
        attrs = {'class': 'updated'}
        m = unicode(bs.find(attrs=attrs))
        return conv.finddate(m).strftime('%Y-%m-%d'), attrs
    except Exception:
        pass
    try:
        #http://timesofindia.indiatimes.com/city/thiruvananthapuram/Whale-shark-dies-in-aquarium/articleshow/32607977.cms
        attrs = {'class': 'byline'}
        m = bs.find(attrs=attrs).text
        return conv.finddate(m).strftime('%Y-%m-%d'), attrs
    except Exception:
        pass
    try:
        #http://ftalphaville.ft.com/2012/05/16/1002861/recap-and-tranche-primer/?Authorised=false
        return conv.finddate(url).strftime('%Y-%m-%d'), 'url'
    except Exception:
        pass
    try:
        #https://www.bbc.com/news/uk-england-25462900
        logger.info(u'Searching for date in bs.text.\r\n' + url)
        return conv.finddate(bs.text).strftime('%Y-%m-%d'), 'bs.text'
    except Exception:
        pass


def url2dictionary(url):
    """Get url and return the result as a dictionary."""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:29.0)' +
               ' Gecko/20100101 Firefox/29.0'}
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        raise StatusCodeError(r.status_code)
    bs = BS(r.content)
    d = {}
    d['journal'] = find_journal(bs)
    if d['journal']:
        d['type'] = 'jour'
    else:
        d['type'] = 'web'
    d['url'] = find_url(bs, url)
    authors = find_authors(bs)[0]
    if authors:
        d['authors'] = authors
    d['issn'] = find_issn(bs)
    d['pmid'] = find_pmid(bs)
    d['volume'] = find_volume(bs)
    d['issue'] = find_issue(bs)
    d['pages'] = find_pages(bs)
    d['website'] = find_sitename(bs, url, authors)[0]
    if d['type'] == 'web' and not d['website']:
        if urlparse(url)[1].startswith('www.'):
            d['website'] = urlparse(url)[1][4:]
        else:
            d['website'] = urlparse(url)[1]
    title = find_title(bs)[0]
    d['title'] = parse_title(title, url, authors)[1]
    m = find_date(bs, url)[0]
    if m:
        d['date'] = m
        d['year'] = d['date'][:4]
    #Remove all empty keys
    dictionary = {}
    for key in d:
        if d[key]:
            dictionary[key] = d[key]
    return dictionary

logger = logging.getLogger(__name__)
