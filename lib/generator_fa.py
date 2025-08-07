"""Functions for generating citation templates for fa.wikipedia.org."""

from typing import Any

from lib import (
    doi_url_match,
    four_digit_num,
    fullname,
    logger,
    make_ref_name,
    open_access_url,
    type_to_cite,
)
from lib.generator_en import (
    Date,
    sfn_cit_ref as en_citations,
)
from lib.language import TO_TWO_LETTER_CODE

CITE_TYPE_TO_PERSIAN = {
    'book': 'کتاب',
    'journal': 'ژورنال',
    'web': 'وب',
}.get

DIGITS_TO_FA = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')


def sfn_cit_ref(
    d: dict[str, Any], _: str = '%Y-%m-%d', pipe: str = ' | ', /
) -> tuple:
    """Return sfn, citation, and ref."""
    g = d.get
    if not (cite_type := type_to_cite(g('cite_type', ''))):
        logger.warning('Unknown citation type: %s, d: %s', cite_type, d)
    else:
        cite_type = CITE_TYPE_TO_PERSIAN(cite_type) or cite_type
    if cite_type in ('کتاب', 'ژورنال', 'وب'):
        cit = '* {{یادکرد ' + cite_type
    else:
        return en_citations(d)

    if authors := g('authors'):
        cit += names2para(authors, 'نام', 'نام خانوادگی', 'نویسنده')
        sfn = '<ref>{{پک'
        for first, last in authors[:4]:
            sfn += ' | ' + last
    else:
        sfn = '<ref>{{پک/بن'

    if editors := g('editors'):
        cit += names2para(
            editors, 'نام ویراستار', 'نام خانوادگی ویراستار', 'ویراستار'
        )

    if translators := g('translators'):
        cit += names1para(translators, 'ترجمه')

    if others := g('others'):
        cit += names1para(others, 'دیگران')

    date = g('date')
    if year := g('year'):
        sfn += ' | ' + year
    elif date is not None:
        if isinstance(date, str):
            year = four_digit_num(date)
        else:
            year = date.strftime('%Y')
        sfn += f' | {year}'

    if cite_type == 'کتاب':
        booktitle = g('booktitle') or g('container-title')
    else:
        booktitle = None

    title = g('title')
    if booktitle:
        cit += ' | عنوان=' + booktitle
        if title:
            cit += ' | فصل=' + title
    elif title:
        cit += ' | عنوان=' + title
        sfn += ' | ک=' + g('title')
    else:
        cit += ' | عنوان='
        sfn += ' | ک='

    if cite_type == 'ژورنال':
        journal = g('journal') or g('container-title')
    else:
        journal = g('journal')

    if journal:
        cit += ' | ژورنال=' + journal
    else:
        website = g('website')
        if website:
            cit += ' | وبگاه=' + website

    if chapter := g('chapter'):
        cit += ' | فصل=' + chapter

    if publisher := (g('publisher') or g('organization')):
        cit += ' | ناشر=' + publisher

    if address := (g('address') or g('publisher-location')):
        cit += ' | مکان=' + address

    if edition := g('edition'):
        cit += ' | ویرایش=' + edition

    if series := g('series'):
        cit += ' | سری=' + series

    if volume := g('volume'):
        cit += ' | جلد=' + volume

    if issue := (g('issue') or g('number')):
        cit += ' | شماره=' + issue

    if date is not None:
        if isinstance(date, str):
            cit += ' | تاریخ=' + date
        else:
            cit += ' | تاریخ=' + Date.isoformat(date)
    elif year:
        cit += ' | سال=' + year

    if isbn := g('isbn'):
        cit += ' | شابک=' + isbn

    if issn := g('issn'):
        cit += ' | issn=' + issn

    if pmid := g('pmid'):
        cit += ' | pmid=' + pmid

    if pmcid := g('pmcid'):
        cit += ' | pmc=' + pmcid.lower().removeprefix('pmc')

    if doi := g('doi'):
        # invalid/temporary/test doi
        if not doi.startswith('10.5555'):
            cit += f' | doi={doi}'
            if (url := open_access_url(doi)) is not None:
                d['url'] = url
                cit += ' | doi-access=free'

    if oclc := g('oclc'):
        cit += ' | oclc=' + oclc

    if jstor := g('jstor'):
        cit += f' | jstor={jstor}'
        jstor_access = g('jstor-access')
        if jstor_access:
            cit += ' | jstor-access=free'

    pages = g('page')
    if cite_type == 'ژورنال':
        if pages:
            cit += ' | صفحه=' + pages

    if url := g('url'):
        # Don't add a DOI URL if we already have added a DOI.
        if not doi or not doi_url_match(url):
            cit += ' | پیوند=' + url
        else:
            # To prevent addition of access date
            url = None

    if archive_url := g('archive-url'):
        cit += (
            f' | پیوند بایگانی={archive_url}'
            f' | تاریخ بایگانی={g("archive-date").isoformat()}'
            f' | پیوند مرده={("آری" if g("url-status") == "yes" else "نه")}'
        )

    if language := g('language'):
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
    sfn += '}}\u200f</ref>'
    # Finally create the ref tag.
    ref = cit[2:]
    if pages and ' | صفحه=' not in ref:
        ref = f'{ref[:-2]} | صفحه={pages}}}}}'
    elif not url:
        ref = f'{ref[:-2]} | صفحه=}}}}'
    ref = f'<ref name="{make_ref_name(g)}">{ref}\u200f</ref>'
    return sfn, cit, ref


def names2para(names, fn_parameter, ln_parameter, nofn_parameter=None):
    """Take list of names. Return the string to be appended to citation."""
    if len(names) == 1:
        first, last = names[0]
        if first or not nofn_parameter:
            return f' | {ln_parameter}=' + last + f' | {fn_parameter}=' + first
        return f' | {nofn_parameter}=' + fullname(first, last)

    s = ''
    for c, (first, last) in enumerate(names, 1):
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
