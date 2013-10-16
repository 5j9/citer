#! /usr/bin/env python
# -*- coding: utf-8 -*-

# These functions can be useful, but are not implemented yet

def fanum2en(string):
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
