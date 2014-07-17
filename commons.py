#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Common variables, functions, and classes used in string conversions, etc."""

from datetime import datetime
import re

import langid
import isbnlib

import config
if config.lang == 'en':
    import sfn_en as sfn
    import ctn_en as ctn
else:
    import sfn_fa as sfn
    import ctn_fa as ctn

# Date patterns:

# January|February...
B = r'(?:J(anuary|u(ne|ly))|February|Ma(rch|y)|' +\
    'A(pril|ugust)|(((Sept|Nov|Dec)em)|Octo)ber)'
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
    reftag = ''

    def detect_language(self, text, langset={}):
        """Detect language of text. Add the result to self.dictionary and error.

        'language' and 'error' keys will be added to dictionary.
        self.error property will be created.
        """
        lang, err = detect_language(text, langset)
        self.dictionary['language'] = lang
        self.dictionary['error'] = self.error = err

    def generate(self):
        """Generate self.sfnt, self.ctnt and self.reftag.

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
        self.sfnt = sfn.create(self.dictionary)
        self.ctnt = ctn.create(self.dictionary, self.date_format)
        self.create_reftag()

    def create_reftag(self):
        """Create a named reference tag using ctnt and sfnt properties."""
        name = self.sfnt[6:-2].replace('|', ' ')
        text = re.sub('(\|ref=({{.*?}}|harv))(?P<repl>\||}})',
                      '\g<repl>',
                      self.ctnt[2:])
        if name.endswith('p='):
            name = name.replace('p=', ' p. ')
            text = text[:-2] + '|page=}}'
        self.reftag = '<ref name="' + name + '">' + text + '</ref>'


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
        lastname = re.sub('MC(\w)',
                          lambda m: 'Mc' + m.group(1).upper(),
                          lastname,
                          flags=re.I)
    if suffix:
        firstname += suffix.title()
    return firstname, lastname


def fanum2en(string):
    """Convert Persian numerical string to equivalent English one."""
    string = string.replace('۰', '0')
    string = string.replace('۱', '1')
    string = string.replace('۲', '2')
    string = string.replace('۳', '3')
    string = string.replace('۴', '4')
    string = string.replace('۵', '5')
    string = string.replace('۶', '6')
    string = string.replace('۷', '7')
    string = string.replace('۸', '8')
    string = string.replace('۹', '9')
    return string


def ennum2fa(string_or_num):
    """Convert English numerical string to equivalent Persian one."""
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
    m = re.search(BdY, string)
    if m:
        return datetime.strptime(m.group(), '%B %d, %Y').date()
    m = re.search(bdY, string)
    if m:
        return datetime.strptime(m.group(), '%b %d, %Y').date()
    m = re.search(dBY, string)
    if m:
        return datetime.strptime(m.group(), '%d %B %Y').date()
    m = re.search(dbY, string)
    if m:
        return datetime.strptime(m.group(), '%d %b %Y').date()
    m = re.search(Ymd_dashed, string)
    if m:
        return datetime.strptime(m.group(), '%Y-%m-%d').date()
    m = re.search(Ymd_slashed, string)
    if m:
        return datetime.strptime(m.group(), '%Y/%m/%d').date()
    m = re.search(Ymd, string)
    if m:
        return datetime.strptime(m.group(), '%Y%m%d').date()


def dict_cleanup(dictionary):
    """Remove all empty values from the given dict. Return another dict."""
    d = {}
    for key in dictionary:
        if dictionary[key]:
            d[key] = dictionary[key]
    return d


def encode_for_template(dictionary):
    """Replace special characters with their respective HTML entities.

    Also .strip()s all values."""
    d = {}
    for k in dictionary:
        v = dictionary[k]
        if isinstance(v, str):
            v = dictionary[k].strip()
            v = v.replace('|', '&amp;#124;')
            v = v.replace('[', '&amp;#91;')
            v = v.replace(']', '&amp;#93;')
        d[k] = v
    return d
