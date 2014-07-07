#!/data/project/yadkard/venv/bin/python
# -*- coding: utf-8 -*-

"""Common variables, functions, and classes used in string conversions, etc."""

from datetime import datetime
import re


#Date patterns:

#January|February...
B = r'(?:J(anuary|u(ne|ly))|February|Ma(rch|y)|' +\
    'A(pril|ugust)|(((Sept|Nov|Dec)em)|Octo)ber)'
#Month abbreviations:
b = r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)'
#Month numbers 0?1-12
m = r'(0?[1-9]|1[012])'
#Zero padded month numbers 01-12
zm = r'(0?[1-9]|1[012])'
#Day (0?1-31)
d = r'(0?[1-9]|[12][0-9]|3[01])'
#Zero-padded day (01-31)
zd = r'(0?[1-9]|[12][0-9]|3[01])'
#Gregorian year pattern 1900-2099
Y = r'(19|20)\d\d'

#common date seperators
sep = '[ -/]'

#July 3, 2001
BdY = re.compile(B + ' ' + d + ', ' + Y)
#Aug 22, 2001
bdY = re.compile(b + ' ' + d + ', ' + Y)

#22 August 2001
dBY = re.compile(d + sep + B + sep + Y)
#22 Aug 2001
dbY = re.compile(d + sep + b + sep + Y)

#1900-01-01,2099-12-31
Ymd_dashed = re.compile(Y + '-'  + zm + '-' + zd)
#1900/01/01, 2099/12/31, 2099 12 31
Ymd_slashed = re.compile(Y + sep + zm + sep + zd)
#19000101, 20991231
Ymd = re.compile(Y + m + d)


class InvalidNameError(Exception):
    
    """Base class for Name exceptions."""

    pass

class LongNameError(InvalidNameError):

    """Raise when a Name() is too long to be a name."""

    pass


class NumberInNameError(InvalidNameError):

    """Raise when a Name() contains digits.."""

    pass


class Name():

    """Take a fullname and its' seperator. Convert it to a Name object.

If no seperator is provided, ',' or ' ' will be used."""

    def __init__(self, fullname, seperator=None):
        """Create appropriate firstname, lastname and fullname properties."""
        if len(fullname)>40:
            raise LongNameError('Lastname was longer than 40 chars.')
        if re.search('\d\d', fullname, re.U):
            #Remember "Jennifer 8. Lee"
            raise NumberInNameError('The name contains a two-digit number.')
        self.firstname, self.lastname = firstname_lastname(fullname, seperator)
        self.fullname = self.firstname + ' ' + self.lastname

    def __repr__(self):
        return 'Name(' + self.fullname + ')'

    def nofirst_fulllast(self):
        '''Change firstname to an empty string and assign fullname to lastname.

Use this method for corporate authors.
'''
        self.lastname = self.fullname
        self.firstname = ''


def firstname_lastname(fullname, seperator):
    '''Return firstname and lastname as a tuple.

Add Jr.|Sr. suffix to first name.
Usually not used directly, called from Name() class.

Examples:

>>> firstname_lastname('JAMES C. MCKINLEY Jr.', None)
('James C. Jr.', 'McKinley')

>>> firstname_lastname('DeBolt, V.', ',')
('V.', 'DeBolt')

>>> firstname_lastname('BBC', None)
('', 'BBC')
'''
    fullname = fullname.strip()
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
              flags =re.I)
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

def famonth2num(string):
    """Convert English month number to Persian string."""
    string = string.replace('ژانویهٔ', '01')
    string = string.replace('فوریهٔ', '02')
    string = string.replace('مارس', '03')
    string = string.replace('آوریل', '04')
    string = string.replace('مهٔ', '05')
    string = string.replace('ژوئن', '06')
    string = string.replace('ژوئیهٔ', '07')
    string = string.replace('اوت', '08')
    string = string.replace('سپتامبر', '09')
    string = string.replace('اکتبر', '10')
    string = string.replace('نوامبر', '11')
    string = string.replace('دسامبر', '12')
    return string

def finddate(string):
    '''Try to find a date in input string and return it as a datetime object.

If there is no matching date, return None.
'''
    m = re.search(BdY, string)
    if m:
        return datetime.strptime(m.group(), '%B %d, %Y')
    m = re.search(bdY, string)
    if m:
        return datetime.strptime(m.group(), '%b %d, %Y')
    m = re.search(dBY, string)
    if m:
        return datetime.strptime(m.group(), '%d %B %Y')
    m = re.search(dbY, string)
    if m:
        return datetime.strptime(m.group(), '%d %b %Y')
    m = re.search(Ymd_dashed, string)
    if m:
        return datetime.strptime(m.group(), '%Y-%m-%d')
    m = re.search(Ymd_slashed, string)
    if m:
        return datetime.strptime(m.group(), '%Y/%m/%d')
    m = re.search(Ymd, string)
    if m:
        return datetime.strptime(m.group(), '%Y%m%d')


def chdateformat(string, format_):
    """Find a date in string and return it in specified format_.

The date in string can be in any format defined in finddate().
Format_ should be a string containing standard formatting directives.
Return the original string if unsuccessful.

Examples:

>>> chdateformat('date: 2014-06-21 time:02:09', '%B %d, %Y')
'June 21, 2014'

>>> chdateformat('date: 2914-06-21 time:02:09', '%B %d, %Y')
'date: 2914-06-21 time:02:09'
"""
    date = finddate(string)
    if date:
        return date.strftime(format_)
    return string


def dict_cleanup(dictionary):
    """Remove all empty values from the given dict. Return another dict."""
    d = {}
    for key in dictionary:
        if dictionary[key]:
            d[key] = dictionary[key]
    return d
