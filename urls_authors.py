#! /usr/bin/python
# -*- coding: utf-8 -*-

"""This module is used for finding the authors in a soup object.

It is in urls.py.
"""


import re

import commons


# Names in byline are required to be two or three parts
NAME_REGEX = r'[\w.-]+ [\w.-]+( [\w.-]+)?'

# This regex supports up to for names in a byline
# names may be seperated with "and", a "comma" or "comma and"

BYLINE_REGEX = (
    r"\s*By\s+(" + NAME_REGEX + r"(, " + NAME_REGEX + r"(, " + NAME_REGEX +
    r"(, " + NAME_REGEX + r"|,? +and " + NAME_REGEX + r")?|,? +and " +
    NAME_REGEX + r"(, " + NAME_REGEX + r"|,? +and " + NAME_REGEX +
    r")?)?|,? +and " + NAME_REGEX + r"(, " + NAME_REGEX + r"(, " +
    NAME_REGEX + r"|,? +and " + NAME_REGEX +
    r")?|,? +and " + NAME_REGEX + r"(, " + NAME_REGEX +
    r"|,? +and " + NAME_REGEX + r")?)?)?)\s*"
)

# FIND_PARAMETERS are used in find_authors(soup)
FIND_PARAMETERS = (
    # http://socialhistory.ihcs.ac.ir/article_571_84.html
    # http://jn.physiology.org/content/81/1/319
    (
        'soup',
        {'name': re.compile('citation_authors?')},
        'getitem',
        'content',
    ),
    (
        'soup',
        {'property': 'og:author'},
        'getitem',
        'content',
    ),
    (
        'soup',
        {'name': 'DCSext.author'},
        'getitem',
        'content',
    ),
    (
        'soup',
        {'class': "author-title"},
        'getattr',
        'text',
    ),
    # http://blogs.ft.com/energy-source/2009/03/04/the-source-platts-rocks-boat-300-crude-solar-shake-ups-hot-jobs/#axzz31G5iiTSq
    (
        'soup',
        {'class': 'author_byline'},
        'getattr',
        'text',
    ),
    (
        'soup',
        {'class': 'bylineAuthor'},
        'getattr',
        'text',
    ),
    (
        'soup',
        {'class': 'byline-name'},
        'getattr',
        'text',
    ),
    (
        'soup',
        {'class': 'story-byline'},
        'getattr',
        'text',
    ),
    (
        'soup',
        {'class': 'meta-author'},
        'getattr',
        'text',
    ),
    (
        'soup',
        {'class': 'authorInline'},
        'getattr',
        'text',
    ),
    # try before class_='author'
    (
        'soup',
        {'class': 'byline'},
        'getattr',
        'text',
    ),
    # disabled due to high error rate
    # try before {'name': 'author'}
    ##        (
    ##            'soup',
    ##            {'class': 'author'},
    ##            'getattr',
    ##            'text',
    ##        ),
    (
        'soup',
        {'name': 'author'},
        'getitem',
        'content',
    ),
    # http://www.washingtonpost.com/wp-dyn/content/article/2006/12/20/AR2006122002165.html
    (
        'soup',
        {'id': 'byline'},
        'getattr',
        'text',
    ),
    (
        'soup',
        {'class': 'byline'},
        'getattr',
        'text',
    ),
    (
        'soup',
        {'name': 'byl'},
        'getitem',
        'content',
    ),
    (
        'soup',
        {'id': 'authortext'},
        'getattr',
        'text',
    ),
    (
        'soup',
        {'class': "by_line_date"},
        'getattr',
        'text',
    ),
    (
        'soup',
        {'class': 'name'},
        'getattr',
        'text',
    ),
    # try before {'rel': 'author'}
    (
        'html',
        r'"author": "(.*?)"',
    ),
    # http://www.dailymail.co.uk/news/article-2633025/London-cleric-convicted-NYC-terrorism-trial.html
    (
        'html',
        r"authorName:\s*'(.*?)'",
    ),
    # http://timesofindia.indiatimes.com/india/27-ft-whale-found-dead-on-Orissa-shore/articleshow/1339609.cms?referral=PM
    (
        'soup',
        {'rel': 'author'},
        'getattr',
        'text',
    ),
    (
        'html',
        re.compile(
            r'>' + BYLINE_REGEX + r'<',
            re.IGNORECASE,
        ),
    ),
    # http://voices.washingtonpost.com/thefix/eye-on-2008/2008-whale-update.html
    (
        'text',
        re.compile(
            r'[\n\|]' + BYLINE_REGEX + r'\n',
            re.IGNORECASE,
        ),
    ),
)


STOPWORDS = '|'.join(
    (
        r'\bReporter\b',
        r'\bPeople\b',
        r'\bEditor\b',
        r'\bCorrespondent\b',
        r'\bAdministrator\b',
        r'\bStaff\b',
        r'\bWriter\b',
        r'\bOffice\b',
        r'\bNews\b',
        r'\.com\b',
        r'\.ir\b',
        r'www\.',
    )
)


class InvalidByLineError(Exception):

    """Raise in for errors in byline_to_names()."""

    pass


def try_find_authors(soup):
    """Try to find authors in soup using the provided parameters."""
    html = str(soup)
    text = soup.text
    for fp in FIND_PARAMETERS:
        if fp[0] == 'soup':
            try: #can this try be removed safely?
                attrs = fp[1]
                f = soup.find(attrs=attrs)
                fs = f.find_next_siblings(attrs=attrs)
                fs.insert(0, f)
                names = []
                
                if fp[2] == 'getitem':
                    for f in fs:
                        try:
                            string = f[fp[3]]
                            name = byline_to_names(string)
                            names.extend(name)
                        except Exception:
                            pass
                else:
                    # fp[2] == 'getattr':
                    for f in fs:
                        try:
                            string = getattr(f, fp[3])
                            name = byline_to_names(string)
                            names.extend(name)
                        except Exception:
                            pass
         
                if names:
                    return names, attrs
            except Exception:
                pass
        elif fp[0] == 'html':
            try:
                m = re.search(fp[1], html).group(1)
                return byline_to_names(m), fp[1]
            except Exception:
                pass
        else:
            # fp[0] == 'text'
            try:
                m = re.search(fp[1], text).group(1)
                return byline_to_names(m), fp[1]
            except Exception:
                pass
    return None, None
    

def find_authors(soup):
    """Get a BeautifulSoup object. Return (Names, where_found_string)."""
    names, where = try_find_authors(soup)
    if names:
        return names, where
    return None, None


def isstopword(string):
        """Return True if the string contains one of the STOPWORDS."""
        if re.search(STOPWORDS, string, re.IGNORECASE):
            return True
        return False


def byline_to_names(byline):
    """Find authors in byline sting. Return name objects as a list.

    The "By " prefix will be omitted.
    Names will be seperated either with " and " or ", ".
    
    If any of the STOPWORDS is found in a name then it will be omitted from
    the result.

    Examples:

    >>> byline_to_names('\n By Roger Highfield, Science Editor \n')
    [Name(Roger Highfield)]

    >>> byline_to_names(' By Erika Solomon in Beirut and Borzou Daragahi,\
     Middle East correspondent')
    [Name(Erika Solomon), Name(Borzou Daragahi)]
    """

    byline = byline.partition('|')[0]
    for c in ':+':
        if c in byline:
            raise InvalidByLineError(
                'Invalid character ("%s") in byline.' % c
            )
    m = re.search(commons.ANYDATE_REGEX, byline)
    if m:
        # Removing the date part
        byline = byline[:m.start()]
    if re.search('\d\d\d\d', byline):
        raise InvalidByLineError(
            'Found \d\d\d\d in byline. (byline needs to be pure)'
        )
    # Replace 'and\n' (and similar expressions) with 'and '
    # This should be done before cutting the byline at the first newline
    byline = re.sub(r'\s+and\s+', ' and ', byline, 1, re.IGNORECASE)
    byline = re.sub(r'\s*,\s+', ', ', byline, 1, re.IGNORECASE)
    # Remove starting "by", cut at the first newline and lstrip
    byline = re.search(r'^\s*(by\s+)?(.*)', byline, re.IGNORECASE).group(2)
    # Removing ending " and" or ',' and rstrip
    byline = re.sub(r'( and|,)?\s*$', '', byline, 1, re.IGNORECASE)
    if ' and ' in byline.lower() or ' ' in byline.replace(', ', ''):
        fullnames = re.split(', and | and |, |;', byline, flags=re.I)
    else:
        fullnames = re.split(', and | and |;', byline, flags=re.I)
    names = []
    for fullname in fullnames:
        fullname = fullname.partition(' in ')[0]
        fullname = fullname.partition(' for ')[0]
        name = commons.Name(fullname)
        if isstopword(name.lastname):
            continue
        names.append(name)
    if not names:
        raise InvalidByLineError(
            'No valid name remained after parsing byline.'
        )
    # Remove names not having firstname (orgs)
    name0 = names[0]  # In case no name remains at the end
    names = [n for n in names if n.firstname]
    if not names:
        names.append(name0)
    return names
