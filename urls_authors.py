#! /usr/bin/python
# -*- coding: utf-8 -*-

"""This module is used for finding the authors in a soup object.

It is in urls.py.
"""


import re

from commons import ANYDATE_SEARCH, Name


# Names in byline are required to be two or three parts
NAME_PATTERN = r'[\w.-]+ [\w.-]+( [\w.-]+)?'

# This regex supports up to four names in a byline
# names may be seperated with "and", a "comma" or "comma and"

BYLINE_PATTERN = (
    r'\s*By\s+({NAME_PATTERN}(, {NAME_PATTERN}(, {NAME_PATTERN}(, '
    r'{NAME_PATTERN}|,? +and {NAME_PATTERN})?|,? +and {NAME_PATTERN}'
    r'(, {NAME_PATTERN}|,? +and {NAME_PATTERN})?)?|,? +and {NAME_PATTERN}'
    r'(, {NAME_PATTERN}(, {NAME_PATTERN}|,? +and {NAME_PATTERN})?|,? +and '
    r'{NAME_PATTERN}(, {NAME_PATTERN}|,? +and {NAME_PATTERN})?)?)?)\s*'
).format(NAME_PATTERN=NAME_PATTERN)

# FIND_AUTHOR_PARAMETERS are used in find_authors(soup)
FIND_AUTHOR_PARAMETERS = (
    # http://socialhistory.ihcs.ac.ir/article_571_84.html
    # http://jn.physiology.org/content/81/1/319
    (
        'soup',
        {'name': re.compile(r'^citation_authors?')},
        'getitem',
        'content',
    ),
    (
        'soup',
        {'property': re.compile(r'^(og:|article).*?author')},
        'getitem',
        'content',
    ),
    (
        'soup',
        {'name': 'DCSext.author'},
        'getitem',
        'content',
    ),
    # author_byline example:
    # http://blogs.ft.com/energy-source/2009/03/04/the-source-platts-rocks-boat-300-crude-solar-shake-ups-hot-jobs/#axzz31G5iiTSq
    # try byline before class_='author'
    # {'class': 'author'} disabled due to high error rate
    (
        'soup',
        {
            'class': re.compile(
                r'^(author-title|author_byline|bylineAuthor|byline-name'
                r'|story-byline|meta-author|authorInline|byline)'
            )
        },
        'getattr',
        'text',
    ),
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
        {'class': re.compile('^(?:by_line_date|name)')},
        'getattr',
        'text',
    ),
    (
        'select',
        '.byline > .author',
        'getattr',
        'text',
    ),
    # http://www.dailymail.co.uk/news/article-2633025/London-cleric-convicted-NYC-terrorism-trial.html
    (
        'html',
        re.compile(
            r'authorName:\s*["\']([^"\']+)["\']|"author": ["\']([^"\']+)["\']'
        ).search,
    ),
    # http://timesofindia.indiatimes.com/india/27-ft-whale-found-dead-on-Orissa-shore/articleshow/1339609.cms?referral=PM
    (
        'soup',
        {'rel': 'author'},
        'getattr',
        'text',
    ),
    # Example for [\n|]{BYLINE_PATTERN}\n
    # http://voices.washingtonpost.com/thefix/eye-on-2008/2008-whale-update.html
    (
        'html',
        re.compile(
            r'>{BYLINE_PATTERN}<|[\n|]{BYLINE_PATTERN}\n'.format(
                BYLINE_PATTERN=BYLINE_PATTERN
            ),
            re.IGNORECASE,
        ).search,
    ),
)

STOPWORDS_SEARCH = re.compile(r'|'.join((
    r'\bReporter\b',
    r'\bPeople\b',
    r'\bEditors?\b',
    r'\bCorrespondent\b',
    r'\bAdministrator\b',
    r'\bStaff\b',
    r'\bWriter\b',
    r'\bOffice\b',
    r'\bNews\b',
    r'\.com\b',
    r'\.ir\b',
    r'www\.',
)), re.IGNORECASE).search


def find_authors_loop(soup) -> list or None:
    """Try to find authors in soup using the FIND_AUTHOR_PARAMETERS."""
    html = str(soup)
    text = soup.text
    for fparams in FIND_AUTHOR_PARAMETERS:
        fparam0 = fparams[0]
        if fparam0 == 'soup':
            # try:  # Todo: can this try be removed safely?
            attrs = fparams[1]
            finding = soup.find(attrs=attrs)
            if not finding:
                continue
            next_siblings = finding.find_next_siblings(attrs=attrs)
            next_siblings.insert(0, finding)
            names = []

            if fparams[2] == 'getitem':
                for finding in next_siblings:
                    string = finding[fparams[3]]
                    name = byline_to_names(string)
                    if not name:
                        continue
                    names.extend(name)
            else:
                # fp[2] == 'getattr':
                for finding in next_siblings:
                    name = byline_to_names(getattr(finding, fparams[3]))
                    if not name:
                        continue
                    names.extend(name)
            if names:
                return names
            # except AttributeError:
            #     pass
        elif fparam0 == 'html':
            m = fparams[1](html)
            if not m:
                continue
            name = byline_to_names(m.group(1))
            if name:
                return name
        elif fparam0 == 'text':
            m = fparams[1](text)
            if not m:
                continue
            name = byline_to_names(m.group(1))
            if name:
                return name
        else:
            # fp[2] == 'select':
            selection = soup.select(fparams[1])
            if len(selection) == 1:
                name = byline_to_names(selection[0].string)
                if name:
                    return name
    return None
    

def find_authors(soup) -> list or None:
    """Get a BeautifulSoup object. Return (Names, where_found_string)."""
    return find_authors_loop(soup)


def byline_to_names(byline) -> list or None:
    r"""Find authors in byline sting. Return name objects as a list.

    The "By " prefix will be omitted.
    Names will be seperated either with " and " or ", ".
    
    If any of the STOPWORDS is found in a name then it will be omitted from
    the result.

    Examples:

    >>> byline_to_names('\n By Roger Highfield, Science Editor \n')
    [Name("Roger Highfield")]

    >>> byline_to_names(
    ...    ' By Erika Solomon in Beirut and Borzou Daragahi, '
    ...    'Middle East correspondent'
    ... )
    [Name("Erika Solomon"), Name("Borzou Daragahi")]
    """
    if not byline:
        return None
    byline = byline.partition('|')[0]
    if ':' in byline or ':' in byline:
        return None
    m = ANYDATE_SEARCH(byline)
    if m:
        # Removing the date part
        byline = byline[:m.start()]
    if re.search('\d\d\d\d', byline):
        return None
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
        name = Name(fullname)
        fn_startswith = name.firstname.startswith
        if fn_startswith('The ') or fn_startswith('خبرگزار'):
            name.nofirst_fulllast()
        if STOPWORDS_SEARCH(name.lastname):
            continue
        names.append(name)
    if not names:
        return None
    # Remove names not having firstname (orgs)
    name0 = names[0]  # In case no name remains at the end
    names = [n for n in names if n.firstname]
    if not names:
        names.append(name0)
    return names
