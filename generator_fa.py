#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Codes required to create citation templates for wikifa."""


from datetime import date

from commons import ennum2fa
from string import digits, ascii_lowercase
from random import seed as randseed, choice as randchoice


# According to https://en.wikipedia.org/wiki/Help:Footnotes,
# the characters '!$%&()*,-.:;<@[]^_`{|}~' are also supported. But they are
# hard to use.
lower_alpha_digits = digits + ascii_lowercase


def citations(d) -> tuple:
    """Create citation templates using the given dictionary."""
    type_ = d.get('type')
    if type_ in ('book', 'incollection'):
        cite = '* {{یادکرد کتاب'
    elif type_ in ('article', 'jour'):
        cite = '* {{یادکرد ژورنال'
    elif type_ == 'web':
        cite = '* {{یادکرد وب'
    else:
        raise KeyError(type_ + " is not a valid value for d['type']")

    authors = d.get('authors')
    if authors:
        cite += names2para(authors, 'نام', 'نام خانوادگی', 'نویسنده')
        sfn = '&lt;ref&gt;{{پک'
        for author in authors[:4]:
            sfn += ' | ' + author.lastname
    else:
        sfn = '&lt;ref&gt;{{پک/بن'
    editors = d.get('editors')
    if editors:
        cite += names2para(
            editors, 'نام ویراستار', 'نام خانوادگی ویراستار', 'ویراستار'
        )
    translators = d.get('translators')
    if translators:
        cite += names1para(translators, 'ترجمه')
    others = d.get('others')
    if others:
        cite += names1para(others, 'دیگران')
    year = d.get('year')
    if year:
        sfn += ' | ' + year
    booktitle = d.get('booktitle')
    title = d.get('title')
    if booktitle:
        cite += ' | عنوان=' + booktitle
        if title:
            cite += ' | فصل=' + title
    elif title:
        cite += ' | عنوان=' + title
        sfn += ' | ک=' + d['title']
    journal = d.get('journal')
    if journal:
        cite += ' | ژورنال=' + journal
    else:
        website = d.get('website')
        if website:
            cite += ' | وب‌گاه=' + website
    publisher = d.get('publisher')
    if publisher:
        cite += ' | ناشر=' + publisher
    address = d.get('address')
    if address:
        cite += ' | مکان=' + address
    series = d.get('series')
    if series:
        cite += ' | سری=' + series
    volume = d.get('volume')
    if volume:
        cite += ' | جلد=' + volume
    issue = d.get('issue')
    if issue:
        cite += ' | شماره=' + issue
    ddate = d.get('date')
    if ddate:
        if isinstance(ddate, str):
            cite += ' | تاریخ=' + ddate
        else:
            cite += ' | تاریخ=' + date.isoformat(ddate)
    if year:
        cite += ' | سال=' + year
    month = d.get('month')
    if month:
        cite += ' | ماه=' + month
    isbn = d.get('isbn')
    if isbn:
        cite += ' | شابک=' + isbn
    issn = d.get('issn')
    if issn:
        cite += ' | issn=' + issn
    pmid = d.get('pmid')
    if pmid:
        cite += ' | pmid=' + pmid
    pages = d.get('pages')
    if type_ in ('article', 'jour'):
        if pages:
            cite += ' | صفحه=' + pages
    url = d.get('url')
    if url:
        cite += ' | پیوند=' + url
    archive_url = d.get('archive-url')
    if archive_url:
        cite += (
            ' | پیوند بایگانی=' + archive_url +
            ' | تاریخ بایگانی=' + d['archive-date'].isoformat() +
            ' | پیوند مرده=' + ('آری' if d['dead-url'] == 'yes' else 'نه')
        )
    doi = d.get('doi')
    if doi:
        cite += ' | doi=' + doi
    language = d.get('language')
    if language:
        if type_ == 'web':
            cite += ' | کد زبان=' + language
        else:
            cite += ' | زبان=' + language
        sfn += ' | زبان=' + language
    if pages:
        sfn += ' | ص=' + pages
    # Seed the random generator before adding today's date.
    randseed(cite)
    ref_name = (
        randchoice(ascii_lowercase)  # it should contain at least one non-digit
        + ''.join(randchoice(lower_alpha_digits) for _ in range(4))
    )
    if url:
        cite += ' | تاریخ بازبینی=' + date.today().isoformat()
    else:
        sfn += ' | ص='
    cite += '}}'
    sfn += '}}\u200F&lt;/ref&gt;'
    # Finally create the ref tag.
    ref = cite[2:]
    if pages and ' | صفحه=' not in ref:
        ref = ref[:-2] + ' | صفحه=' + pages + '}}'
    elif not url:
        ref = ref[:-2] + ' | صفحه=}}'
    ref = '&lt;ref name="' + ref_name + '"&gt;' + ref + '\u200F&lt;/ref&gt;'
    return cite, sfn, ref


def names2para(names, fn_parameter, ln_parameter, nofn_parameter=None):
    """Take list of names. Return the string to be appended to citation."""
    c = 0
    s = ''
    for name in names:
        c += 1
        if c == 1:
            if name.firstname or not nofn_parameter:
                s += ' | ' + ln_parameter + '=' + name.lastname
                s += ' | ' + fn_parameter + '=' + name.firstname
            else:
                s += ' | ' + nofn_parameter + '=' + name.fullname
        else:
            if name.firstname or not nofn_parameter:
                s += ' | ' + ln_parameter + ennum2fa(c) + '=' + name.lastname
                s += ' | ' + fn_parameter + ennum2fa(c) + '=' + name.firstname
            else:
                s += ' | ' + nofn_parameter + ennum2fa(c) + '=' + name.fullname
    return s


def names1para(translators, para):
    """Take list of names. Return the string to be appended to citation."""
    s = ' | ' + para + '='
    c = 0
    for name in translators:
        c += 1
        if c == 1:
            s += name.fullname
        elif c == len(translators):
            s += ' و ' + name.fullname
        else:
            s += '، ' + name.fullname
    return s
