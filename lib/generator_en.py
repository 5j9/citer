"""Functions for generating English Wikipedia citation templates."""

from datetime import date as Date
from functools import partial
from string import ascii_lowercase, digits

from lib import (
    doi_url_match,
    four_digit_num,
    fullname,
    logger,
    make_ref_name,
    open_access_url,
    rc,
    type_to_cite,
)
from lib.language import TO_TWO_LETTER_CODE

rm_ref_arg = partial(
    rc(r'(\s?\|\s?ref=({{.*?}}|harv))(?P<repl>\s?\|\s?|}})').sub, r'\g<repl>'
)
DIGITS_TO_EN = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')

# According to https://en.wikipedia.org/wiki/Help:Footnotes,
# the characters '!$%&()*,-.:;<@[]^_`{|}~' are also supported. But they are
# hard to use.
ALPHA_NUM = digits + ascii_lowercase


def sfn_cit_ref(
    d: dict, date_format: str = '%Y-%m-%d', pipe: str = ' | ', /
) -> tuple:
    """Return sfn, citation, and ref."""
    g = d.get
    if not (cite_type := type_to_cite(g('cite_type'))):
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
            cit += f'{pipe}degree={thesis_type}'

    if authors := g('authors'):
        cit += names2para(authors, pipe, 'first', 'last', 'author')
        # {{sfn}} only supports a maximum of four authors
        for first, last in authors[:4]:
            sfn += '|' + last
    else:
        # the same order should be used in citation_template:
        sfn += '|' + (
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
        cit += names2para(
            editors, pipe, 'editor-first', 'editor-last', 'editor'
        )
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
        cit += names1para(others, pipe, 'others')

    if cite_type == 'book':
        booktitle = g('booktitle') or g('container-title')
    else:
        booktitle = None

    if booktitle:
        cit += f'{pipe}title={booktitle}'
        if title:
            cit += f'{pipe}chapter={title}'
    elif title:
        cit += f'{pipe}title={title}'
    else:
        cit += f'{pipe}title='

    if journal:
        cit += f'{pipe}journal={journal}'
    elif website:
        cit += f'{pipe}website={website}'

    if chapter := g('chapter'):
        cit += f'{pipe}chapter={chapter}'

    if publisher := (g('publisher') or g('organization')):
        cit += f'{pipe}publisher={publisher}'

    if address := (g('address') or g('publisher-location')):
        cit += f'{pipe}publication-place={address}'

    if edition := g('edition'):
        cit += f'{pipe}edition={edition}'

    if series := g('series'):
        cit += f'{pipe}series={series}'

    if volume := g('volume'):
        cit += f'{pipe}volume={volume.translate(DIGITS_TO_EN)}'

    if issue := (g('issue') or g('number')):
        cit += f'{pipe}issue={issue}'

    if date := g('date'):
        if not isinstance(date, str):
            date = date.strftime(date_format)
        cit += f'{pipe}date={date}'

    if year := g('year'):
        year = str(int(year))  # convert any non-Latin digits to English ones
        if not date or year not in date:
            cit += f'{pipe}year={year}'
        sfn += f'|{year}'
    elif date is not None:
        if isinstance(date, str):
            year = four_digit_num(date)[0]
        else:
            year = date.strftime('%Y')
        sfn += f'|{year}'

    if isbn := g('isbn'):
        cit += f'{pipe}isbn={isbn}'

    if issn := g('issn'):
        cit += f'{pipe}issn={issn}'

    if pmid := g('pmid'):
        cit += f'{pipe}pmid={pmid}'

    pmcid: str | None
    if (pmcid := g('pmcid')) is not None:
        cit += f'{pipe}pmc=' + pmcid.lower().removeprefix('pmc')

    if doi := g('doi'):
        # To avoid Check |doi= value error
        # invalid/temporary/test doi[1]
        # https://en.wikipedia.org/wiki/Help:CS1_errors#bad_doi
        if not doi.startswith('10.5555'):
            cit += f'{pipe}doi={doi}'
            if (url := open_access_url(doi)) is not None:
                d['url'] = url
                cit += f'{pipe}doi-access=free'

    if oclc := g('oclc'):
        cit += f'{pipe}oclc={oclc}'

    if jstor := g('jstor'):
        cit += f'{pipe}jstor={jstor}'
        jstor_access = g('jstor-access')
        if jstor_access:
            cit += f'{pipe}jstor-access=free'

    pages_in_cit = pages_in_sfn = False
    if pages := g('page'):
        if '–' in pages:
            sfn += f'|pp={pages}'
            pages_in_sfn = 2
            if cite_type == 'journal':
                cit += f'{pipe}pages={pages}'
                pages_in_cit = 2
        else:
            sfn += f'|p={pages}'
            pages_in_sfn = 1
            if cite_type == 'journal':
                cit += f'{pipe}page={pages}'
                pages_in_cit = 1

    if url := g('url'):
        # Don't add a DOI URL if we already have added a DOI.
        if not doi or not doi_url_match(url):
            cit += f'{pipe}url={url}'
        else:
            # To prevent addition of access date
            url = None

    if not pages and cite_type != 'web':
        pages_in_sfn = 1
        sfn += '|p='

    if archive_url := g('archive-url'):
        cit += (
            f'{pipe}archive-url={archive_url}'
            f'{pipe}archive-date={g("archive-date").strftime(date_format)}'
            f'{pipe}url-status={g("url-status")}'
        )

    if language := g('language'):
        language = TO_TWO_LETTER_CODE(language.lower(), language)
        if language.lower() != 'en':
            cit += f'{pipe}language=' + language

    if not authors:
        # order should match sfn_template
        cit += (
            f'{pipe}'
            'ref={{sfnref|'
            f'{publisher or journal or website or title or "Anon."}'
        )
        if year:
            cit += f'|{year}'
        cit += '}}'

    if url:
        cit += f'{pipe}access-date={Date.today().strftime(date_format)}'

    cit += '}}'
    sfn += '}}'
    # Finally create the ref tag.
    ref_name = make_ref_name(g)

    ref_content = rm_ref_arg(cit[2:])
    if pages_in_sfn and not pages_in_cit:
        ref_content = (
            f'{ref_content[:-2]}{pipe}page={pages if pages else ""}}}}}'
        )

    ref = f'<ref name="{ref_name}">{ref_content}</ref>'
    return sfn, cit, ref


def names2para(names, pipe, fn_parameter, ln_parameter, nofn_parameter=None):
    """Take list of names. Return the string to be appended to citation."""
    c = 0
    s = ''
    for first, last in names:
        c += 1
        if len(names) == 1:
            if first or not nofn_parameter:
                s += f'{pipe}{ln_parameter}={last}{pipe}{fn_parameter}={first}'
            else:
                s += f'{pipe}{nofn_parameter}={fullname(first, last)}'
        else:
            if first or not nofn_parameter:
                s += f'{pipe}{ln_parameter}{c}={last}{pipe}{fn_parameter}{c}={first}'
            else:
                s += f'{pipe}{nofn_parameter}{c}={fullname(first, last)}'
    return s


def names1para(translators, pipe, para):
    """Take list of names. Return the string to be appended to citation."""
    s = f'{pipe}{para}='
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
