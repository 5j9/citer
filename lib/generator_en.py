"""Codes required to create English Wikipedia citation templates."""


from datetime import date as Date
from functools import partial
from collections import defaultdict
from logging import getLogger

from regex import compile as regex_compile

from lib.language import TO_TWO_LETTER_CODE


# Includes ShortDOIs (See: http://shortdoi.org/) and
# https://www.crossref.org/display-guidelines/
DOI_URL_MATCH = regex_compile(r'https?://(dx\.)?doi\.org/').match
DIGITS_TO_EN = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
FOUR_DIGIT_NUM = regex_compile(r'\d\d\d\d').search

refless = partial(regex_compile(
    r'( \| ref=({{.*?}}|harv))(?P<repl> \| |}})'
).sub, r'\g<repl>')

TYPE_TO_CITE = {
    # BibTex types. Descriptions are from
    # http://ctan.um.ac.ir/biblio/bibtex/base/btxdoc.pdf
    # A part of a book, which may be a chapter (or section or whatever) and/or
    # a range of pages.
    'inbook': 'book',
    # A work that is printed and bound, but without a named publisher or
    # sponsoring institution.
    # Note: Yadkard does not currently support the `howpublished` option.
    'booklet': 'book',
    # A part of a book having its own title.
    'incollection': 'book',
    # Technical documentation.
    # Template:Cite manual is a redirect to Template:Cite_book on enwiki.
    'manual': 'book',
    # An article from a journal or magazine.
    'article': 'journal',
    'article-journal': 'journal',
    # The same as INPROCEEDINGS, included for Scribe compatibility.
    'conference': 'conference',
    # An article in a conference proceedings.
    'inproceedings': 'conference',
    # A Master's thesis.
    'mastersthesis': 'thesis',
    # A PhD thesis.
    'phdthesis': 'thesis',
    # A report published by a school or other institution, usually numbered
    # within a series.
    # Todo: Add support for Template:Cite techreport
    'techreport': 'techreport',
    # Use this type when nothing else fits.
    'misc': '',
    # Types used by Yadkard.
    'web': 'web',
    # crossref types (https://api.crossref.org/v1/types)
    'book-section': 'book',
    'monograph': 'book',
    'report': 'report',
    'book-track': 'book',
    'journal-article': 'journal',
    'book-part': 'book',
    'other': '',
    'book': 'book',
    'journal-volume': 'journal',
    'book-set': 'book',
    'reference-entry': '',
    'proceedings-article': 'conference',
    'journal': 'journal',
    'jour': 'journal',
    # https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=22368089&retmode=json&tool=my_tool&email=my_email@example.com
    'Journal Article': 'journal',
    'component': '',
    'book-chapter': 'book',
    'report-series': 'report',
    'proceedings': 'conference',
    'standard': '',
    'reference-book': 'book',
    'posted-content': '',
    'journal-issue': 'journal',
    'dissertation': 'thesis',
    'dataset': '',
    'book-series': 'book',
    'edited-book': 'book',
    'standard-series': '',
    'rprt': 'report',
}.get


def sfn_cit_ref(d: defaultdict) -> tuple:
    """Return sfn, citation, and ref."""
    date_format = d['date_format']
    if not (cite_type := TYPE_TO_CITE(d['cite_type'])):
        logger.warning('Unknown citation type: %s, d: %s', cite_type, d)
        cite_type = ''
        cit = '* {{cite'
    else:
        cit = '* {{cite ' + cite_type
    sfn = '{{sfn'

    publisher = d['publisher']
    website = d['website']
    title = d['title']

    if cite_type == 'journal':
        journal = d['journal'] or d['container-title']
    else:
        journal = d['journal']

    if authors := d['authors']:
        cit += names2para(authors, 'first', 'last', 'author')
        # {{sfn}} only supports a maximum of four authors
        for first, last in authors[:4]:
            sfn += ' | ' + last
    else:
        # the same order should be used in citation_template:
        sfn += ' | ' + (
            publisher or
            f"''{journal}''" if journal else
            f"''{website}''" if website else
            title or 'Anon.'
        )

    if editors := d['editors']:
        cit += names2para(editors, 'editor-first', 'editor-last', 'editor')
    if translators := d['translators']:
        for i, (first, last) in enumerate(translators):
            translators[i] = first, f'{last} (مترجم)'
        # Todo: add a 'Translated by ' before name of translators?
        others = d['others']
        if others:
            others.extend(d['translators'])
        else:
            d['others'] = d['translators']
    if others := d['others']:
        cit += names1para(others, 'others')

    if cite_type == 'book':
        booktitle = d['booktitle'] or d['container-title']
    else:
        booktitle = None

    if booktitle:
        cit += f' | title={booktitle}'
        if title:
            cit += f' | chapter={title}'
    elif title:
        cit += f' | title={title}'

    if journal:
        cit += f' | journal={journal}'
    elif website:
        cit += f' | website={website}'

    if chapter := d['chapter']:
        cit += f' | chapter={chapter}'

    if publisher := (d['publisher'] or d['organization']):
        cit += f' | publisher={publisher}'

    if address := (d['address'] or d['publisher-location']):
        cit += f' | publication-place={address}'

    if edition := d['edition']:
        cit += f' | edition={edition}'

    if series := d['series']:
        cit += f' | series={series}'

    if volume := d['volume']:
        cit += f' | volume={volume.translate(DIGITS_TO_EN)}'

    if issue := (d['issue'] or d['number']):
        cit += f' | issue={issue}'

    if date := d['date']:
        if not isinstance(date, str):
            date = date.strftime(date_format)
        cit += f' | date={date}'

    if year := d['year']:
        year = str(int(year))  # convert any non-Latin digits to English ones
        if not date or year not in date:
            cit += f' | year={year}'
        sfn += f' | {year}'
    elif date is not None:
        if not isinstance(date, str):
            y = date.strftime('%Y')
        else:
            y = FOUR_DIGIT_NUM(date)[0]
        sfn += f' | {y}'

    if isbn := d['isbn']:
        cit += f' | isbn={isbn}'

    if issn := d['issn']:
        cit += f' | issn={issn}'

    if pmid := d['pmid']:
        cit += f' | pmid={pmid}'

    if pmcid := d['pmcid']:
        cit += f' | pmc={pmcid}'

    if doi := d['doi']:
        cit += f' | doi={doi}'

    if oclc := d['oclc']:
        cit += f' | oclc={oclc}'

    if jstor := d['jstor']:
        cit += f' | jstor={jstor}'
        jstor_access = d['jstor-access']
        if jstor_access:
            cit += f' | jstor-access=free'

    if pages := d['page']:
        if '–' in pages:
            sfn += f' | pp={pages}'
        else:
            sfn += f' | p={pages}'
    if cite_type == 'journal':
        if pages:
            if '–' in pages:
                cit += f' | pages={pages}'
            else:
                cit += f' | page={pages}'

    if url := d['url']:
        # Don't add a DOI URL if we already have added a DOI.
        if not doi or not DOI_URL_MATCH(url):
            cit += f' | url={url}'
        else:
            # To prevent addition of access date
            url = None

    if not pages and cite_type != 'web':
        sfn += ' | p='

    if archive_url := d['archive-url']:
        cit += (
            f' | archive-url={archive_url}'
            f' | archive-date={d["archive-date"].strftime(date_format)}'
            f' | url-status={d["url-status"]}')

    if language := d['language']:
        language = TO_TWO_LETTER_CODE(language.lower(), language)
        if language.lower() != 'en':
            cit += ' | language=' + language

    if not authors:
        # order should match sfn_template
        cit += ' | ref={{sfnref | ' \
            f'{publisher or journal or website or title or "Anon."}'
        if year:
            cit += f' | {year}'
        cit += '}}'

    if url:
        cit += f' | access-date={Date.today().strftime(date_format)}'

    cit += '}}'
    sfn += '}}'
    # Finally create the ref tag.
    name = sfn[8:-2].replace(' | ', ' ').replace("'", '')
    text = refless(cit[2:])
    if ' p=' in name and ' | page=' not in text:
        name = name.replace(' p=', ' p. ')
        if pages:
            text = f'{text[:-2]} | page={pages}}}}}'
        else:
            text = f'{text[:-2]} | page=}}}}'
    elif ' pp=' in name:
        name = name.replace(' pp=', ' pp. ')
        if pages and ' | pages=' not in text:
            text = f'{text[:-2]} | pages={pages}}}}}'
    ref = f'&lt;ref name="{name}"&gt;{text}&lt;/ref&gt;'
    return sfn, cit, ref


def names2para(names, fn_parameter, ln_parameter, nofn_parameter=None):
    """Take list of names. Return the string to be appended to citation."""
    c = 0
    s = ''
    for first, last in names:
        c += 1
        if c == 1:
            if first or not nofn_parameter:
                s += f' | {ln_parameter}={last} | {fn_parameter}={first}'
            else:
                s += f' | {nofn_parameter}={fullname(first, last)}'
        else:
            if first or not nofn_parameter:
                s += f' | {ln_parameter}{c}={last} | {fn_parameter}{c}={first}'
            else:
                s += f' | {nofn_parameter}{c}={fullname(first, last)}'
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
            s += f', and {fullname(first, last)}'
        else:
            s += f', {fullname(first, last)}'
    return s


def fullname(first: str, last: str) -> str:
    if first:
        return f'{first} {last}'
    return last


logger = getLogger(__name__)
