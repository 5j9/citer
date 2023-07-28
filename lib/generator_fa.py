"""Codes required to create citation templates for wikifa."""
from collections import defaultdict
from logging import getLogger

from lib.generator_en import (
    DOI_URL_MATCH,
    FOUR_DIGIT_NUM,
    TYPE_TO_CITE,
    Date,
    fullname,
    hash_for_ref_name,
    sfn_cit_ref as en_citations,
)
from lib.language import TO_TWO_LETTER_CODE

CITE_TYPE_TO_PERSIAN = {
    'book': 'کتاب',
    'journal': 'ژورنال',
    'web': 'وب',
}.get

DIGITS_TO_FA = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')


def sfn_cit_ref(d: defaultdict) -> tuple:
    """Return sfn, citation, and ref."""
    if not (cite_type := TYPE_TO_CITE(d['cite_type'])):
        logger.warning('Unknown citation type: %s, d: %s', cite_type, d)
        cite_type = ''
    else:
        cite_type = CITE_TYPE_TO_PERSIAN(cite_type) or cite_type
    if cite_type in ('کتاب', 'ژورنال', 'وب'):
        cit = '* {{یادکرد ' + cite_type
    else:
        return en_citations(d)

    if authors := d['authors']:
        cit += names2para(authors, 'نام', 'نام خانوادگی', 'نویسنده')
        sfn = '<ref>{{پک'
        for first, last in authors[:4]:
            sfn += ' | ' + last
    else:
        sfn = '<ref>{{پک/بن'

    if editors := d['editors']:
        cit += names2para(
            editors, 'نام ویراستار', 'نام خانوادگی ویراستار', 'ویراستار'
        )

    if translators := d['translators']:
        cit += names1para(translators, 'ترجمه')

    if others := d['others']:
        cit += names1para(others, 'دیگران')

    date = d['date']
    if year := d['year']:
        sfn += ' | ' + year
    elif date is not None:
        if isinstance(date, str):
            year = FOUR_DIGIT_NUM(date)[0]
        else:
            year = date.strftime('%Y')
        sfn += f' | {year}'

    if cite_type == 'book':
        booktitle = d['booktitle'] or d['container-title']
    else:
        booktitle = None

    title = d['title']
    if booktitle:
        cit += ' | عنوان=' + booktitle
        if title:
            cit += ' | فصل=' + title
    elif title:
        cit += ' | عنوان=' + title
        sfn += ' | ک=' + d['title']

    if cite_type == 'ژورنال':
        journal = d['journal'] or d['container-title']
    else:
        journal = d['journal']

    if journal:
        cit += ' | ژورنال=' + journal
    else:
        website = d['website']
        if website:
            cit += ' | وبگاه=' + website

    if chapter := d['chapter']:
        cit += ' | فصل=' + chapter

    if publisher := (d['publisher'] or d['organization']):
        cit += ' | ناشر=' + publisher

    if address := (d['address'] or d['publisher-location']):
        cit += ' | مکان=' + address

    if edition := d['edition']:
        cit += ' | ویرایش=' + edition

    if series := d['series']:
        cit += ' | سری=' + series

    if volume := d['volume']:
        cit += ' | جلد=' + volume

    if issue := (d['issue'] or d['number']):
        cit += ' | شماره=' + issue

    if date is not None:
        if isinstance(date, str):
            cit += ' | تاریخ=' + date
        else:
            cit += ' | تاریخ=' + Date.isoformat(date)
    elif year:
        cit += ' | سال=' + year

    if isbn := d['isbn']:
        cit += ' | شابک=' + isbn

    if issn := d['issn']:
        cit += ' | issn=' + issn

    if pmid := d['pmid']:
        cit += ' | pmid=' + pmid

    if pmcid := d['pmcid']:
        cit += ' | pmc=' + pmcid

    if doi := d['doi']:
        cit += ' | doi=' + doi

    if oclc := d['oclc']:
        cit += ' | oclc=' + oclc

    if jstor := d['jstor']:
        cit += f' | jstor={jstor}'
        jstor_access = d['jstor-access']
        if jstor_access:
            cit += ' | jstor-access=free'

    pages = d['page']
    if cite_type == 'ژورنال':
        if pages:
            cit += ' | صفحه=' + pages

    if url := d['url']:
        # Don't add a DOI URL if we already have added a DOI.
        if not doi or not DOI_URL_MATCH(url):
            cit += ' | پیوند=' + url
        else:
            # To prevent addition of access date
            url = None

    if archive_url := d['archive-url']:
        cit += (
            f' | پیوند بایگانی={archive_url}'
            f' | تاریخ بایگانی={d["archive-date"].isoformat()}'
            f" | پیوند مرده={('آری' if d['url-status'] == 'yes' else 'نه')}"
        )

    if language := d['language']:
        language = TO_TWO_LETTER_CODE(language.lower(), language)
        if cite_type == 'وب':
            cit += f' | کد زبان={language}'
        else:
            cit += f' | زبان={language}'
        sfn += f' | زبان={language}'

    if pages:
        sfn += f' | ص={pages}'

    if url:
        cit += f' | تاریخ بازبینی={Date.today().isoformat()}'

    if not pages and cite_type != 'وب':
        sfn += ' | ص='

    cit += '}}'
    sfn += '}}\u200F</ref>'
    # Finally create the ref tag.
    ref = cit[2:]
    if pages and ' | صفحه=' not in ref:
        ref = f'{ref[:-2]} | صفحه={pages}}}}}'
    elif not url:
        ref = f'{ref[:-2]} | صفحه=}}}}'
    ref = f'<ref name="{hash_for_ref_name(d)}">{ref}\u200F</ref>'
    return sfn, cit, ref


def names2para(names, fn_parameter, ln_parameter, nofn_parameter=None):
    """Take list of names. Return the string to be appended to citation."""
    c = 0
    s = ''
    for first, last in names:
        c += 1
        if c == 1:
            if first or not nofn_parameter:
                s += (
                    f' | {ln_parameter}='
                    + last
                    + f' | {fn_parameter}='
                    + first
                )
            else:
                s += f' | {nofn_parameter}=' + fullname(first, last)
        else:
            if first or not nofn_parameter:
                s += (
                    f' | {ln_parameter}{str(c).translate(DIGITS_TO_FA)}'
                    f'={last} | {fn_parameter}{str(c).translate(DIGITS_TO_FA)}'
                    f'={first}'
                )
            else:
                s += (
                    f' | {nofn_parameter}{str(c).translate(DIGITS_TO_FA)}'
                    f'={fullname(first, last)}'
                )
    return s


def names1para(translators, para):
    """Take list of names. Return the string to be appended to citation."""
    s = f' | {para}='
    c = 0
    for first, last in translators:
        c += 1
        if c == 1:
            s += fullname(first, last)
        elif c == len(translators):
            s += f' و {fullname(first, last)}'
        else:
            s += f'، {fullname(first, last)}'
    return s


logger = getLogger(__name__)
