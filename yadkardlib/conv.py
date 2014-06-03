#! /usr/bin/env python
# -*- coding: utf-8 -*-

# These functions can be useful, but are not implemented yet

'''common functions and classes'''

class Name():
    '''Takes a fullname and its' seperator; converts it to a Name object.'''
    def __init__(self, fullname, seperator=None):
        self.firstname, self.lastname = firstname_lastname(fullname, seperator)
        self.fullname = self.firstname + ' ' + self.lastname

        
def firstname_lastname(fullname, seperator):
    '''Returns firstname and lastname as a tuple.
Usually this function is not used directly. It's called from class Name()'''
    fullname = fullname.strip()
    if seperator:
        if seperator in fullname:
            lastname, firstname = fullname.split(seperator)
        else:
            lastname, firstname = fullname, ''
    else:
        sname = fullname.split(seperator)
        lastname = sname.pop().strip()
        firstname = ' '.join(sname).strip()
    if firstname:
        #if there is no firstname, it's probably name of an orgnization
        #e.g. CBC, or AP. (no captalization is needed)
        return camelize(firstname), camelize(lastname)
    else:
        return firstname, lastname

def camelize(string):
    '''Returnes CamelCased string only if it's completely uppercase/lowercase.
First letter and letters after space or dot will be capitalized.'''
    if string != string.upper() and string != string.lower():
        return string
    else:
        string = ' '.join([t.capitalize() for t in string.split()])
        string = '.'.join([t.capitalize() for t in string.split('.')])
        return string
  
def fanum2en(string):
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
