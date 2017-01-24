#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Common variables, functions, and classes used in string conversions, etc."""

from datetime import datetime
import re
import json

import langid
from isbnlib import mask as isbn_mask
from jdatetime import date as jdate

from config import lang


FA_MONTHS = (
    'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور', 'مهر',
    'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
)

# Date patterns:

# January|February...
B = (
    r'(?:J(?:anuary|u(?:ne|ly))|February|Ma(?:rch|y)|'
    r'A(?:pril|ugust)|(?:(?:(?:Sept|Nov|Dec)em)|Octo)ber)'
)
# فروردین|اردیبهشت|خرداد...
fa_B = '|'.join(FA_MONTHS).replace('ی', '[یي]')

# Month abbreviations:
b = r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).?'
# Month numbers 0?1-12
m = r'(?:0?[1-9]|1[012])'
# Zero padded month numbers 01-12
zm = r'(?:0[1-9]|1[012])'
# Day (0?1-31)
d = r'(?:0?[1-9]|[12][0-9]|3[01])'
# Zero-padded day (01-31)
zd = r'(?:0[1-9]|[12][0-9]|3[01])'
# Gregorian year pattern 1900-2099
Y = r'(?:19|20)\d\d'


# July 3, 2001
BdY = re.compile(B + ' ' + d + ', ' + Y)
# Aug 22, 2001
bdY = re.compile(b + ' ' + d + ', ' + Y)
# 22 August 2001
dBY = re.compile(d + ' ' + B + ' ' + Y)
# ۲۷ مرداد ۱۳۹۳
fa_dBY = re.compile('(?:\d\d?) (' + fa_B + ') (?:\d\d\d\d)')

# 22 Aug 2001
dbY = re.compile(d + ' ' + b + ' ' + Y)

# 1900-01-01,2099-12-31
Ymd_dashed = re.compile(Y + '-' + zm + '-' + zd)
# 1900/01/01, 2099/12/31, 2099 12 31
Ymd_slashed = re.compile(Y + '/' + zm + '/' + zd)
# 19000101, 20991231
Ymd = re.compile(Y + zm + zd)

ANYDATE_SEARCH = re.compile(
    '(?:' + B + ' ' + d + ', ' + Y + '|' +
    b + ' ' + d + ', ' + Y + '|' +
    d + ' ' + B + ' ' + Y + '|' +
    d + ' ' + b + ' ' + Y + '|' +
    Y + '-' + zm + '-' + zd + '|' +
    Y + '/' + zm + '/' + zd + '|' +
    '(?P<jd>\d\d?) (?P<jB>' + fa_B + ') (?P<jY>\d\d\d\d)|' +
    Y + zm + zd + ')'
).search

USER_AGENT_HEADER = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:30.0)'
        ' Gecko/20100101 Firefox/30.0'
}


class InvalidNameError(Exception):

    """Base class for Name exceptions."""

    pass


class LongNameError(InvalidNameError):

    """Raise when a Name() is too long to be a name."""

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


class BaseResponse:

    """The base class for response objects."""

    # defaults
    error = 0
    ref = cite = sfn = ''


def dictionary_to_citations(dictionary) -> tuple:
    """Return (sfn, cite, ref) strings..

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
    return citations(dictionary) # cite, sfn, ref


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
    if '\n' in fullname:
        raise InvalidNameError('There was a newline in fullname.')
    if len(fullname) > 40:
        raise LongNameError('Lastname was longer than 40 chars.')
    if re.search('\d\d', fullname, re.U):
        # Remember "Jennifer 8. Lee"
        raise NumberInNameError('The name contains a two-digit number.')
    match = re.search(' (Jr\.|Sr\.)$', fullname, re.I)
    if match:
        suffix = match.group()
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
        lastname = re.sub(
            'MC(\w)',
            lambda mtch: 'Mc' + mtch.group(1).upper(),
            lastname,
            flags=re.I
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
    digits = set(re.findall(r'\d', string))
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


def jalali_string_to_date(match) -> jdate:
    """Return the date object for given Jalali string."""
    return jdate(
        int(uninum2en(match.group('jY'))),
        FA_MONTHS.index(match.group('jB').replace('ي', 'ی')) + 1,
        int(uninum2en(match.group('jd'))),
    ).togregorian()


def finddate(string) -> datetime.date:
    """Try to find a date in input string and return it as a date object.

    If there is no matching date, return None.
    The returned date can't be from the future.

    """
    match = ANYDATE_SEARCH(string)
    today = datetime.today().date()
    while match:
        date_string = match.group(0)
        try:
            date = datetime.strptime(date_string, '%B %d, %Y').date()
            if date <= today:
                return date
        except ValueError:
            pass
        try:
            date = datetime.strptime(
                date_string.replace('.', ''),
                '%b %d, %Y'
            ).date()
            if date <= today:
                return date
        except ValueError:
            pass
        try:
            date = datetime.strptime(date_string, '%d %B %Y').date()
            if date <= today:
                return date
        except ValueError:
            pass
        try:
            date = datetime.strptime(
                date_string.replace('.', ''),
                '%d %b %Y'
            ).date()
            if date <= today:
                return date
        except ValueError:
            pass
        try:
            date = datetime.strptime(date_string, '%Y-%m-%d').date()
            if date <= today:
                return date
        except ValueError:
            pass
        try:
            date = datetime.strptime(date_string, '%Y/%m/%d').date()
            if date <= today:
                return date
        except ValueError:
            pass
        try:
            date = jalali_string_to_date(match)
            if date <= today:
                return date
        except ValueError:
            pass
        try:
            date = datetime.strptime(date_string, '%Y%m%d').date()
            if date <= today:
                return date
        except ValueError:
            pass
        pos = match.end()
        match = ANYDATE_SEARCH(string, pos)


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
    * Replace special characters in dictionay values with their respective
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
