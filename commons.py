#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Common variables, functions, and classes used in string conversions, etc."""

import regex
import json
import calendar
from datetime import datetime
from collections import namedtuple

import langid
from isbnlib import mask as isbn_mask
from jdatetime import date as jdate
from datetime import date as gdate

from config import lang


b_TO_NUM = {name: num for num, name in enumerate(calendar.month_abbr) if num}
B_TO_NUM = {name: num for num, name in enumerate(calendar.month_name) if num}

# jB_TO_NUM contains entries for both ی and ي
jB_TO_NUM = {
    'فروردین': 1,
    'فروردين': 1,
    'اردیبهشت': 2,
    'ارديبهشت': 2,
    'خرداد': 3,
    'تیر': 4,
    'تير': 4,
    'مرداد': 5,
    'شهریور': 6,
    'شهريور': 6,
    'مهر': 7,
    'آبان': 8,
    'آذر': 9,
    'دی': 10,
    'دي': 10,
    'بهمن': 11,
    'اسفند': 12,
}

DOUBLE_DIGIT_SEARCH = regex.compile(r'\d\d').search

# Date patterns:

# January|February...
B = (
    r'(?<B>'
    r'(?:J(?:anuary|u(?:ne|ly))|February|Ma(?:rch|y)|'
    r'A(?:pril|ugust)|(?:(?:(?:Sept|Nov|Dec)em)|Octo)ber)'
    r')'
)
# فروردین|اردیبهشت|خرداد...
jB = '(?<jB>{})'.format(
    '|'.join([jm for jm in jB_TO_NUM]).replace('ی', '[یي]')
)

# Month abbreviations:
b = r'(?<b>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).?'
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

# Todo: Migrate to 3.6 and use f-string
ANYDATE_SEARCH = regex.compile(
    r'(?:'
    r'(?:{B}|{b}) {d}, {Y}'
    r'|{d} (?:{B}|{b}) {Y}'
    r'|{Y}(?<sep>[-/]){zm}\g<sep>{zd}'
    r'|(?<d>\d\d?) {jB} (?<Y>\d\d\d\d)'
    r'|{Y}{zm}{zd}'
    r')'.format(**locals())
).search

USER_AGENT_HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:50.0) '
    'Gecko/20100101 Firefox/50.0'
}

Response = namedtuple('Response', 'cite sfn ref error')


class InvalidNameError(Exception):

    """Base class for Name exceptions."""

    pass


class NumberInNameError(InvalidNameError):

    """Raise when a Name() contains digits.."""

    pass


class Name:

    """Take a fullname and its' seperator. Convert it to a Name object.

    If no seperator is provided, ',' or ' ' will be used.
    """

    def __init__(self, fullname: str, seperator: str=None) -> None:
        """Create appropriate firstname, lastname and fullname properties."""
        self.firstname, self.lastname = firstname_lastname(fullname, seperator)
        if self.firstname:
            self.fullname = self.firstname + ' ' + self.lastname
        else:
            self.fullname = self.lastname

    def __repr__(self) -> str:
        return 'Name("' + self.fullname + '")'

    def nofirst_fulllast(self) -> None:
        """Change firstname to an empty string and assign fullname to lastname.

        Use this method for corporate authors.

        """
        self.lastname = self.fullname
        self.firstname = ''


def dictionary_to_response(dictionary) -> Response:
    """Return (sfn, cite, ref, error) strings..

    dictionary should be ready before calling this function.
    The dictionary will be cleaned up (empty values will be removed) and
    all values will be encoded using encode_for_template() function.
    ISBN (if exist) will be hyphenated.

    """
    value_encode(dictionary)
    isbn = dictionary.get('isbn')
    if isbn:
        dictionary['isbn'] = isbn_mask(isbn) or isbn
    if lang == 'en':
        from generator_en import citations
    else:
        from generator_fa import citations
    cite, sfn, ref = citations(dictionary)
    return Response(cite, sfn, ref, dictionary.get('error'))


def response_to_json(response) -> str:
    """Generate api JSON response containing sfn, cite and ref."""
    return json.dumps({
        'reference_tag': response.ref,
        'citation_template': response.cite,
        'shortened_footnote': response.sfn,
    })


def detect_language(text, langset=None) -> tuple:
    """Detect the language of the text. Return (lang, error).

    args:
    "langset" is the set of languages that the result should be limited to.

    return:
    "lang" will be a string containing an ISO 639-1 code.
    "error" will be an integer indicating a percentage. (Rounded to 2 digits)
    """
    if langset:
        langid.set_languages(langset)
    language, confidence = langid.classify(text)
    error = round((1 - confidence) * 100, 2)
    return language, error


def firstname_lastname(fullname, seperator) -> tuple:
    """Return firstname and lastname as a tuple.

    Add Jr.|Sr. suffix to first name.
    Usually not used directly, called from Name() class.

    Examples:

    >>> firstname_lastname('JAMES C. MCKINLEY Jr.', None)
    ('James C. Jr.', 'McKinley')

    >>> firstname_lastname('DeBolt, V.', ',')
    ('V.', 'DeBolt')

    >>> firstname_lastname('BBC', None)
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
    if fullname.endswith(' Jr.') or fullname.endswith(' Sr.'):
        suffix = fullname[-4:]
        fullname = fullname[:-4]
    else:
        suffix = None
    if not seperator:
        if ',' in fullname:
            seperator = ','
        elif '،' in fullname:
            seperator = '،'
    if seperator:
        if seperator in fullname:
            lastname, firstname = fullname.split(seperator)
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
        lastname = regex.sub(
            'MC(\w)',
            lambda mtch: 'Mc' + mtch.group(1).upper(),
            lastname,
            flags=regex.I
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
    digits = set(regex.findall(r'\d', string))
    for digit in digits:
        string = string.replace(digit, str(int(digit)))
    return string


def ennum2fa(string_or_num) -> str:
    """Convert English numerical string to equivalent Persian one (‍۰-۹)."""
    return (
        str(string_or_num)
        .replace('0', '۰')
        .replace('1', '۱')
        .replace('2', '۲')
        .replace('3', '۳')
        .replace('4', '۴')
        .replace('5', '۵')
        .replace('6', '۶')
        .replace('7', '۷')
        .replace('8', '۸')
        .replace('9', '۹')
    )


def finddate(string) -> datetime.date or None:
    """Try to find a date in input string and return it as a date object.

    If there is no matching date, return None.
    The returned date can't be from the future.

    """
    match = ANYDATE_SEARCH(string)
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
        date = gdate(year, B_TO_NUM[month], day)
        if date <= today:
            return date
        return
    month = groupdict.get('b')
    if month:
        date = gdate(year, b_TO_NUM[month], day)
        if date <= today:
            return date
        return
    month = groupdict.get('m')
    if month:
        date = gdate(year, int(month), day)
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
