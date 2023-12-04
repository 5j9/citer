"""Functions for generating English Wikipedia citation templates."""
from datetime import date as Date
from functools import partial
from logging import getLogger
from random import choice, choices, seed
from string import ascii_lowercase, digits

from lib.commons import rc
from lib.language import TO_TWO_LETTER_CODE

# Includes ShortDOIs (See: http://shortdoi.org/) and
# https://www.crossref.org/display-guidelines/
DOI_URL_MATCH = rc(r'https?://(dx\.)?doi\.org/').match
DIGITS_TO_EN = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
FOUR_DIGIT_NUM = rc(r'\d\d\d\d').search

rm_ref_arg = partial(
    rc(r'( \| ref=({{.*?}}|harv))(?P<repl> \| |}})').sub, r'\g<repl>'
)

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
    # citoid
    'journalArticle': 'journal',
    # The same as INPROCEEDINGS, included for Scribe compatibility.
    'conference': 'conference',
    # An article in a conference proceedings.
    'inproceedings': 'conference',
    # A Master's thesis.
    # todo: convert to degree/type parameter
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
    'jrnl': 'journal',
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
    'thesis': 'thesis',
}.get

# According to https://en.wikipedia.org/wiki/Help:Footnotes,
# the characters '!$%&()*,-.:;<@[]^_`{|}~' are also supported. But they are
# hard to use.
ALPHA_NUM = digits + ascii_lowercase


def hash_for_ref_name(g: callable, number_of_digits=4):
    # A combination of possible `user_input`s is used as seed.
    seed(f'{g("url")}{g("doi")}{g("isbn")}{g("pmid")}{g("pmcid")}')
    return choice(
        ascii_lowercase
    ) + ''.join(  # it should contain at least one non-digit
        choices(digits, k=number_of_digits)
    )


def sfn_cit_ref(d: dict) -> tuple:
    """Return sfn, citation, and ref."""
    g = d.get
    date_format = g('date_format')
    if not (cite_type := TYPE_TO_CITE(g('cite_type'))):
        logger.warning('Unknown citation type: %s, d: %s', cite_type, d)
        cite_type = ''
        cit = '* {{cite'
    else:
        cit = '* {{cite ' + cite_type
    sfn = '{{sfn'

    publisher = g('publisher')
    website = g('website')
    title = g('title')

    if cite_type == 'journal':
        journal = g('journal') or g('container-title')
    else:
        journal = g('journal')

    if cite_type == 'thesis':
        if (thesis_type := g('thesisType')) is not None:
            cit += f' | degree={thesis_type}'

    if authors := g('authors'):
        cit += names2para(authors, 'first', 'last', 'author')
        # {{sfn}} only supports a maximum of four authors
        for first, last in authors[:4]:
            sfn += ' | ' + last
    else:
        # the same order should be used in citation_template:
        sfn += ' | ' + (
            publisher
            or (
                f"''{journal}''"
                if journal
                else f"''{website}''"
                if website
                else title or 'Anon.'
            )
        )

    if editors := g('editors'):
        cit += names2para(editors, 'editor-first', 'editor-last', 'editor')
    if translators := g('translators'):
        for i, (first, last) in enumerate(translators):
            translators[i] = first, f'{last} (مترجم)'
        # Todo: add a 'Translated by ' before name of translators?
        others = g('others')
        if others:
            others.extend(g('translators'))
        else:
            d['others'] = g('translators')
    if others := g('others'):
        cit += names1para(others, 'others')

    if cite_type == 'book':
        booktitle = g('booktitle') or g('container-title')
    else:
        booktitle = None

    if booktitle:
        cit += f' | title={booktitle}'
        if title:
            cit += f' | chapter={title}'
    elif title:
        cit += f' | title={title}'
    else:
        cit += ' | title='

    if journal:
        cit += f' | journal={journal}'
    elif website:
        cit += f' | website={website}'

    if chapter := g('chapter'):
        cit += f' | chapter={chapter}'

    if publisher := (g('publisher') or g('organization')):
        cit += f' | publisher={publisher}'

    if address := (g('address') or g('publisher-location')):
        cit += f' | publication-place={address}'

    if edition := g('edition'):
        cit += f' | edition={edition}'

    if series := g('series'):
        cit += f' | series={series}'

    if volume := g('volume'):
        cit += f' | volume={volume.translate(DIGITS_TO_EN)}'

    if issue := (g('issue') or g('number')):
        cit += f' | issue={issue}'

    if date := g('date'):
        if not isinstance(date, str):
            date = date.strftime(date_format)
        cit += f' | date={date}'

    if year := g('year'):
        year = str(int(year))  # convert any non-Latin digits to English ones
        if not date or year not in date:
            cit += f' | year={year}'
        sfn += f' | {year}'
    elif date is not None:
        if isinstance(date, str):
            year = FOUR_DIGIT_NUM(date)[0]
        else:
            year = date.strftime('%Y')
        sfn += f' | {year}'

    if isbn := g('isbn'):
        cit += f' | isbn={isbn}'

    if issn := g('issn'):
        cit += f' | issn={issn}'

    if pmid := g('pmid'):
        cit += f' | pmid={pmid}'

    if pmcid := g('pmcid'):
        cit += f' | pmc={pmcid}'

    if doi := g('doi'):
        # To avoid Check |doi= value error
        # invalid/temporary/test doi[1]
        # https://en.wikipedia.org/wiki/Help:CS1_errors#bad_doi
        if not doi.startswith('10.5555'):
            cit += f' | doi={doi}'

    if oclc := g('oclc'):
        cit += f' | oclc={oclc}'

    if jstor := g('jstor'):
        cit += f' | jstor={jstor}'
        jstor_access = g('jstor-access')
        if jstor_access:
            cit += ' | jstor-access=free'

    pages_in_cit = pages_in_sfn = False
    if pages := g('page'):
        if '–' in pages:
            sfn += f' | pp={pages}'
            pages_in_sfn = 2
            if cite_type == 'journal':
                cit += f' | pages={pages}'
                pages_in_cit = 2
        else:
            sfn += f' | p={pages}'
            pages_in_sfn = 1
            if cite_type == 'journal':
                cit += f' | page={pages}'
                pages_in_cit = 1

    if url := g('url'):
        # Don't add a DOI URL if we already have added a DOI.
        if not doi or not DOI_URL_MATCH(url):
            cit += f' | url={url}'
        else:
            # To prevent addition of access date
            url = None

    if not pages and cite_type != 'web':
        pages_in_sfn = 1
        sfn += ' | p='

    if archive_url := g('archive-url'):
        cit += (
            f' | archive-url={archive_url}'
            f' | archive-date={g("archive-date").strftime(date_format)}'
            f' | url-status={g("url-status")}'
        )

    if language := g('language'):
        language = TO_TWO_LETTER_CODE(language.lower(), language)
        if language.lower() != 'en':
            cit += ' | language=' + language

    if not authors:
        # order should match sfn_template
        cit += (
            ' | ref={{sfnref | '
            f'{publisher or journal or website or title or "Anon."}'
        )
        if year:
            cit += f' | {year}'
        cit += '}}'

    if url:
        cit += f' | access-date={Date.today().strftime(date_format)}'

    cit += '}}'
    sfn += '}}'
    # Finally create the ref tag.
    ref_name = sfn[8:-2].replace(' | ', ' ').replace("'", '')
    if pages_in_sfn == 1:
        ref_name = ref_name.replace(' p=', ' p. ')
    elif pages_in_sfn == 2:
        ref_name = ref_name.replace(' pp=', ' pp. ')
    else:
        ref_name += ' ' + hash_for_ref_name(g, 3)

    ref_content = rm_ref_arg(cit[2:])
    if pages_in_sfn and not pages_in_cit:
        ref_content = f'{ref_content[:-2]} | page={pages if pages else ""}}}}}'

    ref = f'<ref name="{ref_name}">{ref_content}</ref>'
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
