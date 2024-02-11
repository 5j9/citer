from json import JSONDecodeError, loads

from regex import ASCII, IGNORECASE, VERBOSE

from lib import four_digit_num
from lib.commons import (
    InvalidNameError,
    date_search,
    first_last,
    rc,
)

IV = IGNORECASE | VERBOSE
# Names in byline are required to be two or three parts
NAME_PATTERN = r'\w[\w.-]++\ \w[\w.-]++(?>\ \w[\w.-]+)?'

# BYLINE_PATTERN supports up to four names in a byline
# names may be separated with "and", a "comma" or "comma and"
BYLINE_PATTERN = rf"""
    \s*+By\s++{NAME_PATTERN}(
        ,\ {NAME_PATTERN}(
            ,\ {NAME_PATTERN}(
                ,\ {NAME_PATTERN}
                |
                ,?\ ++and\ {NAME_PATTERN}
            )?
            |
            ,?\ ++and\ {NAME_PATTERN}(
                ,\ {NAME_PATTERN}
                |
                ,?\ ++and\ {NAME_PATTERN}
            )?
        )?
        |
        ,?\ ++and\ {NAME_PATTERN}(
            ,\ {NAME_PATTERN}(
                ,\ {NAME_PATTERN}
                |
                ,?\ ++and\ {NAME_PATTERN}
            )?
            |
            ,?\ ++and\ {NAME_PATTERN}(
                ,\ {NAME_PATTERN}
                |
                ,?\ ++and\ {NAME_PATTERN}
            )?
        )?
    )?\s*
"""
BYLINE_PATTERN_SEARCH = rc(BYLINE_PATTERN, IV)

NORMALIZE_ANDS = rc(r'\s++and\s++', IGNORECASE).sub
NORMALIZE_COMMA_SPACES = rc(r'\s*+,\s++', IGNORECASE).sub
BY_PREFIX = rc(
    r"""
    ^(?:
        (?>
            [^b]++
            |
            (?<!\b)b
            |b(?!y)
        )*+
        \bby\s++
    )?
    ([^\r\n]++)
    [\s\S]*
    """,
    IV,
).sub
AND_OR_COMMA_SUFFIX = rc(r'(?> and|,)?\s*+$', IGNORECASE).sub
AND_OR_COMMA_SPLIT = rc(r', and | and |, |;', IGNORECASE).split
AND_SPLIT = rc(r', and | and |;', IGNORECASE).split

CONTENT_ATTR = r"""
    content=(?<q>["\'])
    (?<result>
        (?>
            [^'"]++
            |
            (?!(?P=q))['"]
        )++
    )(?P=q)
"""
AUTHOR_META_NAME_OR_PROP = r"""
    (?<id>(?:name|property)\s*+=\s*+(?<q>["\']?)
        (?>
            # http://socialhistory.ihcs.ac.ir/article_571_84.html
            # http://jn.physiology.org/content/81/1/319
            a(?>rticle:author|uthor)
            |citation_authors?
            |og:author
        )
    (?P=q))
"""
META_AUTHOR_FINDITER = rc(
    rf"""
    <meta\s[^>]*?(?:
        {AUTHOR_META_NAME_OR_PROP}\s[^c]*+[^>]*?{CONTENT_ATTR}
        |
        {CONTENT_ATTR}\s[^>]*?{AUTHOR_META_NAME_OR_PROP}
    )
    """,
    IV,
).finditer
# id=byline
# http://www.washingtonpost.com/wp-dyn/content/article/2006/12/20/AR2006122002165.html
# rel=author
# http://timesofindia.indiatimes.com/india/27-ft-whale-found-dead-on-Orissa-shore/articleshow/1339609.cms?referral=PM
BYLINE_TAG_FINDITER = rc(
    r"""
    (?>
        # author_byline example:
        # http://blogs.ft.com/energy-source/2009/03/04/the-source-platts-rocks-boat-300-crude-solar-shake-ups-hot-jobs/#axzz31G5iiTSq
        # try byline before class_='author'
        <(?<tag>[a-z]\w++)\s++[^>]*?
        (?<id>
            (?>class|id|rel)=
            (?<q>["\']?)
            (?>
                author[^'"\s>]*+
                |by(?>
                    line(?>Author|line-name)?
                    |_line(?:_date)?
                )
                |meta-author
                |story-byline
            )
        )
        \b(?P=q)[^>]*+>
        (?<result>[^<]*+[\s\S]*?)
        </(?P=tag)[^>]*+>
        |
        # http://www.dailymail.co.uk/news/article-2633025/London-cleric-convicted-NYC-terrorism-trial.html
        (?<id>authorName["\']?\s*+:\s*+["\'])(?<result>[^"\'>\n]++)["\']
        |
        # schema.org
        (?<q>["'])(?<id>author)(?P=q)\s*+:\s*+
        (?<result> \{ [^\}]* \} | \[ [^\]]* \] )
    )
    """,
    IV | ASCII,
).finditer


BYLINE_HTML_PATTERN = rc('>' + BYLINE_PATTERN + '<', IV).search
# [\n|]{BYLINE_PATTERN}\n
# http://voices.washingtonpost.com/thefix/eye-on-2008/2008-whale-update.html
BYLINE_TEXT_PATTERN = rc(r'[\n|]' + BYLINE_PATTERN + r'\n', IV).search

TAGS_SUB = rc(r'</?[a-z][^>]*+>', IGNORECASE).sub

# http://www.businessnewsdaily.com/6762-male-female-entrepreneurs.html?cmpid=514642_20140715_27858876
#  .byline > .author
BYLINE_AUTHOR = rc(
    r'<[a-z]++[^c]*+[^>]*?class=(?<q>["\']?)author\b(?P=q)'
    r'[^>]*+>(?<result>[^<>]++)',
    IGNORECASE | ASCII,
).finditer

STOPWORDS_SEARCH = rc(
    r"""
    \b(?>
        Administrator
        |By
        |Correspondent
        |Editors?
        |News
        |Office
        |People
        |Reporter
        |Staff
        |Team
        |Writer
        |سایت # tabnak.ir
    )\b
    |\.(?>com|ir)\b
    |www\.
    """,
    IV,
).search


def json_ld_authors(s: str) -> list[tuple[str, str]] | None:
    try:
        j = loads(s)
    except JSONDecodeError:
        return
    try:
        if type(j) is list:  # noqa: E721
            ns = []
            for d in j:
                if d['@type'] == 'Person':
                    ns += byline_to_names(d['name'])
            return ns

        # assert type(j) is dict
        if j['@type'] == 'Person':
            if type(j['name']) is str:  # noqa: E721
                return byline_to_names(j['name'])
            # assert type(j['name']) is list
            ns = []
            for n in j['name']:
                ns += byline_to_names(n)
            return ns
    except (KeyError, TypeError):
        return


def find_authors(html) -> list[tuple[str, str]]:
    """Return authors names found in html."""
    names = []
    for match in META_AUTHOR_FINDITER(html):
        if match_names := byline_to_names(match['result']):
            names += match_names
    if names:
        # meta authors may contain duplicate names.
        # Only return unique authors, preserving the order.
        return [*dict.fromkeys(names)]
    match_id = None
    results = set()
    for match in BYLINE_TAG_FINDITER(html):
        # Only match authors using the same search criteria.
        if match_id is not None and match_id != match['id']:
            break
        result = match['result']
        if result in results:
            break  # avoid duplicate results
        results.add(result)
        if match['tag']:
            if ns := byline_to_names(TAGS_SUB('', result)):
                match_id = match['id']
                names += ns
                continue
            for m in BYLINE_AUTHOR(result):
                names += byline_to_names(m['result'])
            if names:
                return names
        else:  # not containing tags
            if match['id'] == 'author':
                if ns := json_ld_authors(match['result']):
                    return ns
            if ns := byline_to_names(result):
                match_id = match['id']
                names += ns
    if names:
        return names
    if (match := BYLINE_TEXT_PATTERN(TAGS_SUB('', html))) is not None:
        return byline_to_names(match[0])
    return names


def byline_to_names(byline) -> list[tuple[str, str]]:
    r"""Find authors in byline sting. Return name objects as a list.

    The "By " prefix will be omitted.
    Names will be seperated either with " and " or ", ".

    If any of the STOPWORDS is found in a name then it will be omitted from
    the result.

    Examples:

    >>> byline_to_names('\n By Roger Highfield, Science Editor \n')
    [RawName("Roger Highfield")]

    >>> byline_to_names(
    ...    ' By Erika Solomon in Beirut and Borzou Daragahi, '
    ...    'Middle East correspondent'
    ... )
    [RawName("Erika Solomon"), RawName("Borzou Daragahi")]
    """
    byline = byline.partition('|')[0].strip(' ;\t\n')
    if ':' in byline:
        return []
    if (m := date_search(byline)) is not None:
        # Removing the date part
        byline = byline[: m.start()]
    if not byline:
        return []
    if four_digit_num(byline) is not None:
        return []
    # Normalize 'and\n' (and the similar) to standard 'and '
    # This should be done before cutting the byline at the first newline
    byline = NORMALIZE_ANDS(' and ', byline)
    byline = NORMALIZE_COMMA_SPACES(', ', byline)
    # Remove starting "by", cut at the first newline and lstrip
    byline = BY_PREFIX(r'\1', byline)
    # Removing ending " and" or ',' and rstrip
    byline = AND_OR_COMMA_SUFFIX('', byline)
    if ' and ' in byline.lower() or ' ' in byline.partition(', ')[0]:
        fullnames = AND_OR_COMMA_SPLIT(byline)
    else:
        # Comma may be the separator of first name and last name.
        fullnames = AND_SPLIT(byline)
    names = []
    for i, fullname in enumerate(fullnames):
        fullname = fullname.partition(' in ')[0].partition(' for ')[0]
        if STOPWORDS_SEARCH(fullname) or (i and fullname.isupper()):
            break
        try:
            first, last = first_last(fullname)
        except InvalidNameError:
            continue
        if first.startswith(('The ', 'خبرگزار')) or last.islower():
            first, last = '', f'{first} {last}'
        names.append((first, last))
    if not names:
        return names
    # Remove names not having first name (orgs)
    name0 = names[0]  # In case no name remains at the end
    names = [(fn, ln) for fn, ln in names if fn]
    if not names:
        names.append(name0)
    return names
