#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Common variables, functions, and classes used in string conversions, etc."""

from datetime import datetime
import re
import json
import unicodedata

import langid
import isbnlib

import config
import jalali
if config.lang == 'en':
    import generator_en as generator
else:
    import generator_fa as generator


fa_months = (
    'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور', 'مهر',
    'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
)

# Date patterns:

# January|February...
B = r'(?:J(anuary|u(ne|ly))|February|Ma(rch|y)|' +\
    r'A(pril|ugust)|(((Sept|Nov|Dec)em)|Octo)ber)'
# فروردین|اردیبهشت|خرداد...
fa_B = '|'.join(fa_months).replace('ی', '[یي]')

# Month abbreviations:
b = r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)'
# Month numbers 0?1-12
m = r'(0?[1-9]|1[012])'
# Zero padded month numbers 01-12
zm = r'(0[1-9]|1[012])'
# Day (0?1-31)
d = r'(0?[1-9]|[12][0-9]|3[01])'
# Zero-padded day (01-31)
zd = r'(0[1-9]|[12][0-9]|3[01])'
# Gregorian year pattern 1900-2099
Y = r'(19|20)\d\d'


# July 3, 2001
BdY = re.compile(B + ' ' + d + ', ' + Y)
# Aug 22, 2001
bdY = re.compile(b + ' ' + d + ', ' + Y)
# 22 August 2001
dBY = re.compile(d + ' ' + B + ' ' + Y)
# ۲۷ مرداد ۱۳۹۳
fa_dBY = re.compile('(\d\d?)' + ' (' + fa_B + ') ' + '(\d\d\d\d)')

# 22 Aug 2001
dbY = re.compile(d + ' ' + b + ' ' + Y)

# 1900-01-01,2099-12-31
Ymd_dashed = re.compile(Y + '-' + zm + '-' + zd)
# 1900/01/01, 2099/12/31, 2099 12 31
Ymd_slashed = re.compile(Y + '/' + zm + '/' + zd)
#19000101, 20991231
Ymd = re.compile(Y + zm + zd)


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

    def __init__(self, fullname, seperator=None):
        """Create appropriate firstname, lastname and fullname properties."""
        self.firstname, self.lastname = firstname_lastname(fullname, seperator)
        if self.firstname:
            self.fullname = self.firstname + ' ' + self.lastname
        else:
            self.fullname = self.lastname

    def __repr__(self):
        return 'Name(' + self.fullname + ')'

    def nofirst_fulllast(self):
        '''Change firstname to an empty string and assign fullname to lastname.

        Use this method for corporate authors.
        '''
        self.lastname = self.fullname
        self.firstname = ''


class BaseResponse:

    """The base class for response objects."""

    # defaults
    error = 0
    reft = ''

    def detect_language(self, text, langset={}):
        """Detect language of text. Add the result to self.dictionary and error.

        'language' and 'error' keys will be added to dictionary.
        self.error property will be created.
        """
        lang, err = detect_language(text, langset)
        self.dictionary['language'] = lang
        self.dictionary['error'] = self.error = err

    def generate(self):
        """Generate self.sfnt, self.ctnt and self.reft.

        self.dictionary should be ready before calling this function.
        The dictionary will be cleaned up (empty values will be removed) and
        all values will be encoded using encode_for_template() function.
        ISBN (if exist) will be hyphenated.
        """
        self.dictionary = dict_cleanup(self.dictionary)
        self.dictionary = encode_for_template(self.dictionary)
        if 'isbn' in self.dictionary:
            masked = isbnlib.mask(self.dictionary['isbn'])
            if masked:
                self.dictionary['isbn'] = masked
        self.sfnt = generator.sfn_template(self.dictionary)
        self.ctnt = generator.citation_template(self.dictionary,
                                                self.date_format)
        self.reft = generator.reference_tag(self.dictionary,
                                            self.sfnt,
                                            self.ctnt)

    def api_json(self):
        """Generate api JSON response containing sfnt, ctnt and reft."""
        return json.dumps({'reference_tag': self.reft,
                           'citation_template': self.ctnt,
                           'shortened_footnote': self.sfnt})


def detect_language(text, langset={}):
    """Detect the language of the text. Return (lang, error).

    args:
    "langset" is the set of languages that the result should be limited to.

    return:
    "lang" will be a string containing an ISO 639-1 code.
    "error" will be an integer indicating a percentage. (Rounded to 2 digits)
    """
    if langset:
        langid.set_languages(langset)
    lang, confidence = langid.classify(text)
    error = round((1 - confidence) * 100, 2)
    return lang, error


def firstname_lastname(fullname, seperator):
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
    m = re.search(' (Jr\.|Sr\.)$', fullname, re.I)
    if m:
        suffix = m.group()
        fullname = fullname[:-4]
    else:
        suffix = None
    if not seperator and ',' in fullname:
        seperator = ','
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
            lambda m: 'Mc' + m.group(1).upper(),
            lastname,
            flags=re.I
        )
    if suffix:
        firstname += suffix.title()
    return firstname, lastname


def uninum2en(string):
    """Convert non-ascii unicode digits to equivalent English one (0-9).

    Example:
    >>> uninum2en('٤۴৪౪')
    '4444'
    """
    digits = set(re.findall(r'\d', string))
    for d in digits:
        string = string.replace(d, str(unicodedata.digit(d)))
    return string


def ennum2fa(string_or_num):
    """Convert English numerical string to equivalent Persian one (‍۰-۹)."""
    string = str(string_or_num)
    string = string.replace('0', '۰')
    string = string.replace('1', '۱')
    string = string.replace('2', '۲')
    string = string.replace('3', '۳')
    string = string.replace('4', '۴')
    string = string.replace('5', '۵')
    string = string.replace('6', '۶')
    string = string.replace('7', '۷')
    string = string.replace('8', '۸')
    string = string.replace('9', '۹')
    return string


def finddate(string):
    """Try to find a date in input string and return it as a date object.

    If there is no matching date, return None.
    """
    try:
        return datetime.strptime(
            re.search(BdY, string).group(),
            '%B %d, %Y',
        ).date()
    except Exception:
        pass
    try:
        return datetime.strptime(
            re.search(bdY, string).group(),
            '%b %d, %Y',
        ).date()
    except Exception:
        pass
    try:
        return datetime.strptime(
            re.search(dBY, string).group(),
            '%d %B %Y',
        ).date()
    except Exception:
        pass
    try:
        return datetime.strptime(
            re.search(dbY, string).group(),
            '%d %b %Y',
        ).date()
    except Exception:
        pass
    try:
        return datetime.strptime(
            re.search(Ymd_dashed, string).group(),
            '%Y-%m-%d',
        ).date()
    except Exception:
        pass
    try:
        return datetime.strptime(
            re.search(Ymd_slashed, string).group(),
            '%Y/%m/%d',
        ).date()
    except Exception:
        pass
    try:
        return datetime.strptime(
            re.search(Ymd, string).group(),
            '%Y%m%d',
        ).date()
    except Exception:
        pass
    try:
        m = re.search(fa_dBY, string)
        return jalali.Persian(
            int(uninum2en(m.group(3))),
            fa_months.index(m.group(2).replace('ي', 'ی')) + 1,
            int(uninum2en(m.group(1))),
        ).gregorian_datetime()
    except Exception:
        pass


def dict_cleanup(dictionary):
    """Remove all empty values from the given dict. Return another dict."""
    d = {}
    for key in dictionary:
        if dictionary[key]:
            d[key] = dictionary[key]
    return d


def bidi_pop(string):
    """Makes sure all  LRE, RLE, LRO, or RLO chars are terminated with PDF."""
    isolates = [
        '\u2066', # LRI
        '\u2067', # RLI
        '\u2068', # FSI
    ]
    diff = sum(
        [string.count(c) for c in isolates]
    ) - string.count('\u2069') # PDI
    string = string + '\u2069' * diff
    embeddings_and_overrides = [
        '\u202A', # LRE
        '\u202B', # RLE
        '\u202D', # LRO
        '\u202E', # RLO
    ]
    diff = sum(
        [string.count(c) for c in embeddings_and_overrides]
    ) - string.count('\u202C') # PDF
    string = string + '\u202C' * diff
    return string


def encode_for_template(dictionary):
    """Replace special characters with their respective HTML entities.

    Also .strip()s all values."""
    d = {}
    for k in dictionary:
        v = dictionary[k]
        if isinstance(v, str):
            v = dictionary[k].strip()
            v = bidi_pop(v)
            v = v.replace('|', '&amp;#124;')
            v = v.replace('[', '&amp;#91;')
            v = v.replace(']', '&amp;#93;')
            v = v.replace('\r\n', ' ')
            v = v.replace('\n', ' ')
        d[k] = v
    return d
