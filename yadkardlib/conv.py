#!/data/project/yadkard/venv/bin/python
# -*- coding: utf-8 -*-

'''
Common variables, functions, and classes usually used in string conversions.
'''

from datetime import datetime
import re


#Date patterns:

#January|February...
B = r'(?:J(anuary|u(ne|ly))|February|Ma(rch|y)|' +\
    'A(pril|ugust)|(((Sept|Nov|Dec)em)|Octo)ber)'
#Month abbreviations:
b = r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)'

#July 3, 2001
BdY = B + ' \d\d?, \d\d\d\d'
#Aug 22, 2001
bdY = b + ' \d\d?, \d\d\d\d'

#22 August 2001
dBY = '\d\d? ' + B + ' \d\d\d\d'
#22 Aug 2001
dbY = '\d\d? ' + b + ' \d\d\d\d'

#1900-01-01,2099-12-31
Ymd_dashed = r'(19|20)\d\d-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])'
#1900/01/01, 2099/12/31
Ymd_slashed = r'(19|20)\d\d/(0[1-9]|1[012])/(0[1-9]|[12][0-9]|3[01])'
#19000101, 20991231
Ymd = r'(19|20)\d\d(0[1-9]|1[012])(0[1-9]|[12][0-9]|3[01])'


class LongNameError(Exception):
    
    """Raise when a Name() is too long to be a name."""

    pass


class NumberInNameError(Exception):
    
    """Raise when a Name() contains digits.."""

    pass


class Name():

    """Take a fullname and its' seperator; convert it to a Name object."""

    def __init__(self, fullname, seperator=None):
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

Example:

>>> firstname_lastname('JAMES C. MCKINLEY Jr.', None)
('James C. Jr.', 'McKinley')
'''
    fullname = fullname.strip()
    m = re.search(' (Jr\.|Sr\.)$', fullname, re.I)
    if m:
        suffix = m.group()
        fullname = fullname[:-4]
    else:
        suffix = None
    if seperator:
        if seperator in fullname:
            lastname, firstname = fullname.split(seperator)
        else:
            lastname, firstname = fullname, ''
    else:
        sname = fullname.split(seperator)
        lastname = sname.pop()
        firstname = ' '.join(sname)
    firstname = firstname.strip()
    if suffix:
        firstname += suffix
    if firstname:
        #if there is no firstname, it's probably an orgnization name
        #e.g. CBC, or AP. (no word-captalization should be done)
        firstname = firstname.title()
        lastname = lastname.title()
    lastname = re.sub('MC(\w)',
                      lambda m: 'Mc' + m.group(1).upper(),
                      lastname,
                      flags =re.I
                      )
    return firstname, lastname

  
def fanum2en(string):
    """Convert Persian numerical string to equivalent English one."""
    string = string.replace(u'۰', '0')
    string = string.replace(u'۱', '1')
    string = string.replace(u'۲', '2')
    string = string.replace(u'۳', '3')
    string = string.replace(u'۴', '4')
    string = string.replace(u'۵', '5')
    string = string.replace(u'۶', '6')
    string = string.replace(u'۷', '7')
    string = string.replace(u'۸', '8')
    string = string.replace(u'۹', '9')
    return string

def ennum2fa(string_or_num):
    """Convert English numerical string to equivalent Persian one."""
    string = str(string_or_num)
    string = string.replace('0', u'۰')
    string = string.replace('1', u'۱')
    string = string.replace('2', u'۲')
    string = string.replace('3', u'۳')
    string = string.replace('4', u'۴')
    string = string.replace('5', u'۵')
    string = string.replace('6', u'۶')
    string = string.replace('7', u'۷')
    string = string.replace('8', u'۸')
    string = string.replace('9', u'۹')
    return string

def famonth2num(string):
    """Convert English month number to Persian string."""
    string = string.replace(u'ژانویهٔ', '01')
    string = string.replace(u'فوریهٔ', '02')
    string = string.replace(u'مارس', '03')
    string = string.replace(u'آوریل', '04')
    string = string.replace(u'مهٔ', '05')
    string = string.replace(u'ژوئن', '06')
    string = string.replace(u'ژوئیهٔ', '07')
    string = string.replace(u'اوت', '08')
    string = string.replace(u'سپتامبر', '09')
    string = string.replace(u'اکتبر', '10')
    string = string.replace(u'نوامبر', '11')
    string = string.replace(u'دسامبر', '12')
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
