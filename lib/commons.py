#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Common variables, functions, and classes used in string conversions, etc."""

from calendar import month_abbr, month_name
from datetime import datetime
from datetime import date as datetime_date
from json import dumps as json_dumps

from isbnlib import mask as isbn_mask, NotValidISBNError
from jdatetime import date as jdate
from regex import compile as regex_compile, VERBOSE, IGNORECASE
from requests import Session

from config import LANG, SPOOFED_USER_AGENT, NCBI_TOOL, NCBI_EMAIL, USER_AGENT

if LANG == 'en':
    from lib.generator_en import sfn_cit_ref
else:
    from lib.generator_fa import sfn_cit_ref


b_TO_NUM = {name.lower(): num for num, name in enumerate(month_abbr) if num}
B_TO_NUM = {name.lower(): num for num, name in enumerate(month_name) if num}

# jB_TO_NUM contains entries for both ی and ي
jB_TO_NUM = {
    'فروردین': 1,
    'اردیبهشت': 2,
    'خرداد': 3,
    'تیر': 4,
    'مرداد': 5,
    'شهریور': 6,
    'مهر': 7,
    'آبان': 8,
    'آذر': 9,
    'دی': 10,
    'بهمن': 11,
    'اسفند': 12}

DOUBLE_DIGIT_SEARCH = regex_compile(r'\d\d').search

# Date patterns:

# January|February...
B = (
    r'''
    (?<B>(?:J(?:anuary|u(?:ne|ly))
    |
    February
    |
    Ma(?:rch|y)
    |
    A(?:pril|ugust)
    |
    (?:(?:(?:Sept|Nov|Dec)em)|Octo)ber))
    ''')
# فروردین|اردیبهشت|خرداد...
jB = (
    '(?>(?<jB>'
    + '|'.join([jm for jm in jB_TO_NUM]).replace('ی', '[یي]')
    + '))')
# Month abbreviations:
b = r'(?>(?<b>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)).?'
# Month numbers 0?1-12
m = r'(?<m>0?[1-9]|1[012])'
# Zero padded month numbers 01-12
zm = r'(?<m>0[1-9]|1[012])'
# Day (0?1-31)
d = r'(?<d>0?[1-9]|[12][0-9]|3[01])(?>st|nd|th)?'
# Zero-padded day (01-31)
zd = r'(?<d>0[1-9]|[12][0-9]|3[01])'
# Gregorian year pattern 1900-2099
Y = r'(?<Y>(?:19|20)\d\d)'
ANYDATE_PATTERN = (
    '(?:(?:' + B + '|' + b + r')\ ' + d + r',?\ ' + Y
    + '|' + d + r'\ (?:' + B + '|' + b + r')\ ' + Y
    + '|' + Y + '(?<sep>[-/])' + zm + '(?P=sep)' + zd
    + '|' + r'(?<d>\d\d?)\ ' + jB + r'\ (?<Y>\d\d\d\d)'
    + r'|\b' + Y + zm + zd
    + ')')
ANYDATE_SEARCH = regex_compile(ANYDATE_PATTERN, VERBOSE).search
DIGITS_FINDALL = regex_compile(r'\d').findall
MC_SUB = regex_compile(r'MC(\w)', IGNORECASE).sub


AGENT_HEADER = {
    'User-Agent': USER_AGENT,
    # Not required but recommended by
    # https://meta.wikimedia.org/wiki/User-Agent_policy
    'Api-User-Agent': NCBI_TOOL + '/' + NCBI_EMAIL}
SPOOFED_AGENT_HEADER = {'User-Agent': SPOOFED_USER_AGENT}


class InvalidNameError(ValueError):

    """Base class for RawName exceptions."""


class NumberInNameError(InvalidNameError):

    """Raise when a RawName() contains digits.."""


def fetch(url, spoof=False, **kwargs):
    with Session() as session:
        return session.request(
            method='get', url=url,
            headers=AGENT_HEADER if spoof else SPOOFED_AGENT_HEADER,
            timeout=10, **kwargs)


def dict_to_sfn_cit_ref(dictionary) -> tuple:
    """Return (sfn, cite, ref) strings.

    dictionary should be ready before calling this function.
    The dictionary will be cleaned up (empty values will be removed) and
    all values will be encoded using encode_for_template() function.
    ISBN (if exist) will be hyphenated.
    """
    value_encode(dictionary)
    isbn = dictionary['isbn']
    if isbn:
        try:
            dictionary['isbn'] = isbn_mask(isbn)
        except NotValidISBNError:
            # https://github.com/CrossRef/rest-api-doc/issues/214
            del dictionary['isbn']
    return sfn_cit_ref(dictionary)


def sfn_cit_ref_to_json(response) -> str:
    """Generate api JSON response containing sfn, cite and ref."""
    return json_dumps({
        'reference_tag': response.ref,
        'citation_template': response.cite,
        'shortened_footnote': response.sfn,
    })


def first_last(fullname, separator=None) -> tuple:
    """Return firstname and lastname as a tuple.

    (Jr.|Sr.) suffixes will be considered as part of the firstname.
    Usually called from RawName() class and not used directly.

    Examples:

    >>> first_last('JAMES C. MCKINLEY Jr.', None)
    ('James C. Jr.', 'McKinley')

    >>> first_last('DeBolt, V.', ',')
    ('V.', 'DeBolt')

    >>> first_last('BBC', None)
    ('', 'BBC')
    """
    fullname = fullname.strip()
    if (
        '\n' in fullname
        or len(fullname) > 40
        # "Jennifer 8. Lee"
        or DOUBLE_DIGIT_SEARCH(fullname)
    ):
        raise InvalidNameError
    if fullname[-4:] in (' Sr.', ' Jr.'):
        suffix = fullname[-4:]
        fullname = fullname[:-4]
    else:
        suffix = None
    if not separator:
        if ',' in fullname:
            separator = ','
        elif '،' in fullname:
            separator = '،'
    if separator:
        if separator in fullname:
            lastname, _, firstname = fullname.partition(separator)
        else:
            lastname, firstname = fullname, ''
    else:
        sname = fullname.split()
        lastname = sname.pop()
        firstname = ' '.join(sname)
    firstname = firstname.strip()
    if (firstname.isupper() and lastname.isupper()) or \
       (firstname.islower() and lastname.islower()):
        firstname = firstname.title()
        lastname = lastname.title()
        lastname = MC_SUB(
            lambda mtch: 'Mc' + mtch.group(1).upper(),
            lastname,
        )
    if suffix:
        firstname += suffix.title()
    return firstname, lastname


def uninum2en(string) -> str:
    """Convert non-ascii unicode digits to equivalent English ones (0-9).

    Example:
    >>> uninum2en('٤۴৪౪')
    '4444'
    """
    if not string:
        raise ValueError
    digits = set(DIGITS_FINDALL(string))
    for digit in digits:
        string = string.replace(digit, str(int(digit)))
    return string


def find_any_date(str_or_match) -> datetime.date or None:
    """Try to find a date in input string and return it as a date object.

    If there is no matching date, return None.
    The returned date can't be from the future.
    """
    if isinstance(str_or_match, str):
        match = ANYDATE_SEARCH(str_or_match)
    else:
        match = str_or_match
    if not match:
        return None
    groupdict = match.groupdict()
    day = int(groupdict['d'])
    year = int(groupdict['Y'])
    month = groupdict.get('jB')
    today = datetime.today().date()
    if month:
        date = jdate(year, jB_TO_NUM[month], day).togregorian()
        if date <= today:
            return date
        return
    month = groupdict.get('B')
    if month:
        date = datetime_date(year, B_TO_NUM[month.lower()], day)
        if date <= today:
            return date
        return
    month = groupdict.get('b')
    if month:
        date = datetime_date(year, b_TO_NUM[month.lower()], day)
        if date <= today:
            return date
        return
    month = groupdict.get('m')
    if month:
        date = datetime_date(year, int(month), day)
        if date <= today:
            return date
        return


def bidi_pop(string) -> str:
    """Makes sure all  LRE, RLE, LRO, or RLO chars are terminated with PDF."""
    # Pop isolations
    isolates = [
        '\u2066',  # LRI
        '\u2067',  # RLI
        '\u2068',  # FSI
    ]
    diff = sum(string.count(c) for c in isolates) - \
        string.count('\u2069')  # PDI
    string += '\u2069' * diff
    # Pop embeddings and overrides
    diff = sum(
        string.count(c) for c in (
            '\u202A',  # LRE
            '\u202B',  # RLE
            '\u202D',  # LRO
            '\u202E',  # RLO
        )
    ) - string.count('\u202C')  # PDF
    return string + '\u202C' * diff


def value_encode(dictionary) -> None:
    """Cleanup dictionary values.

    * Remove any key with False bool value.
    * Replace special characters in dictionary values with their respective
        HTML entities.
    * Strip all values.
    """
    for k, v in dictionary.items():
        if isinstance(v, str):
            v = (
                bidi_pop(v.strip())
                .replace('|', '&amp;#124;')
                .replace('[', '&amp;#91;')
                .replace(']', '&amp;#93;')
                .replace('\r\n', ' ')
                .replace('\n', ' ')
            )
            dictionary[k] = v
