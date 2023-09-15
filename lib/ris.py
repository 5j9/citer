from regex import MULTILINE, VERBOSE

from lib.commons import ISBN_10OR13_SEARCH, InvalidNameError, first_last, rc
from lib.doi import DOI_SEARCH

RIS_FULLMATCH = rc(
    r'''
    (?: # this  group matches any line
        ^
        (?>
            A[U\d]\ {2}-\ (?<author>[^\r\n]++)
            |DA\ {2}-\ \d++/(?<month>\d++)[^\r\n]*+
            |EP\ {2}-\ (?<end_page>[^\r\n]++)
            |IS\ {2}-\ (?<issue>[^\r\n]++)
            |J[FA]\ {2}-\ (?<journal>[^\r\n]++)
            |LA\ {2}-\ (?<language>[^\r\n]++)
            |P(?>
                B\ {2}-\ (?<publisher>[^\r\n]++)
                |Y\ {2}-\ (?<year>\d++)[^\r\n]*+
            )
            |S(?>
                N\ {2}-\ (?<sn>\S*+)[^\r\n]*+
                |P\ {2}-\ (?<start_page>[^\r\n]++)
            )
            |T(?>
                [1I]\ {2}-\ (?<title>[^\r\n]++)
                |2\ {2}-\ (?<t2>[^\r\n]++)
                |3\ {2}-\ (?<series>[^\r\n]++)
                |Y\ {2}-\ (?<type>[^\r\n]++)
            )
            |UR\ {2}-\ (?<url>[^\r\n]++)
            |VL\ {2}-\ (?<volume>[^\r\n]++)
            |Y1\ {2}-\ (?<year>\d++)[^\r\n]*+
            # any other line
            |[^\r\n]*+
        )
        \r?\n
    )*
    ''',
    VERBOSE | MULTILINE,
).fullmatch


def ris_parse(ris_text):
    """Parse RIS_text data and return the result as a dictionary."""
    d = {}
    match = RIS_FULLMATCH(ris_text)
    d.update(match.groupdict())
    # cite_type: (book, journal, . . . )
    if (cite_type := d['type'].lower()) == 'jour':
        if (t2 := d['t2']) is not None:
            d['journal'] = t2
    url = d['url']
    if cite_type == 'elec' and url:
        d['cite_type'] = 'web'
    else:
        d['cite_type'] = cite_type

    if sn := d['sn']:
        # determine if it is ISBN or ISSN according to the cite_type
        if ISBN_10OR13_SEARCH(sn) is not None:
            d['isbn'] = sn
        else:
            d['issn'] = sn
    # author:
    # d['authors'] should not be created unless there are some authors
    if authors := match.captures('author'):
        # From RIS Format Specifications:
        # Each author must be on a separate line, preceded by this tag. Each
        # reference can contain unlimited author fields, and can contain up
        # to 255 characters for each field.
        # The author name must be in the following syntax:
        # Lastname,Firstname,Suffix
        # For Firstname, you can use full names, initials, or both.
        d['authors'] = []
        for author in authors:
            try:
                author = first_last(author, separator=',')
            except InvalidNameError:
                continue
            d['authors'].append(author)
    # DOIs may be in N1 (notes) tag, search for it in any tag
    if (m := DOI_SEARCH(ris_text)) is not None:
        d['doi'] = m[0]

    if start_page := d['start_page']:
        if end_page := d['end_page']:
            d['page'] = start_page + '–' + end_page
        else:
            d['page'] = start_page
    # in IRS, url can be separated using a ";"
    if url:
        d['url'] = url.partition(';')[0]
    return d
