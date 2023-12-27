from pytest import mark

from lib.urls_authors import (
    BYLINE_PATTERN,
    IV,
    byline_to_names,
    find_authors,
    json_ld_authors,
    rc,
)
from tests.urls_test import urls_scr

BYLINE_PATTERN_REGEX = rc(rf'^{BYLINE_PATTERN}$', IV)


def test_byline_pattern_one_author():
    """http://www.defense.gov/News/NewsArticle.aspx?ID=18509"""
    assert BYLINE_PATTERN_REGEX.search('By Jim Garamone')


def test_byline_pattern_cap_names_joined_by_and():
    """Test two authors with and.

    Example:
    https://www.eff.org/deeplinks/2014/06/
    sudan-tech-sanctions-harm-innovation-development-us-government-and-
    corporations-must-act

    Note the two consecutive spaces.

    """
    assert BYLINE_PATTERN_REGEX.search('By Kimberly Carlson  and Jillian York')


def test_byline_pattern_four_authors():
    """Test four authors, last one with and.

    http://arstechnica.com/science/2007/09/
    the-pseudoscience-behind-homeopathy/

    """
    assert BYLINE_PATTERN_REGEX.search(
        'by John Timmer, Matt Ford, Chris Lee, and Jonathan Gitlin Sept'
    )


@mark.xfail
def test_byline_pattern_four_authors_with_for():
    """Test four authors, having a "for" at the end.

    http://arstechnica.com/science/2007/09/
    the-pseudoscience-behind-homeopathy/

    """
    assert BYLINE_PATTERN_REGEX.search(
        'By Sara Malm and Annette Witheridge and '
        'Ian Drury for the Daily Mail and Daniel Bates'
    )


def test_byline_to_names_two_author_seperated_by_comma():
    names = byline_to_names('\n By Roger Highfield, Science Editor \n')
    assert len(names) == 1
    assert names[0][0] == 'Roger'


def test_byline_to_names_in_in_byline():
    byline = (
        ' By Erika Solomon in Beirut and Borzou Daragahi,'
        ' Middle East correspondent'
    )
    names = byline_to_names(byline)
    assert len(names) == 2
    assert names[0][0] == 'Erika'
    assert names[1][0] == 'Borzou'


def test_byline_to_names_byline_ends_with_comma():
    names = byline_to_names('by \n Tony Smith, \n')
    assert len(names) == 1
    assert names[0][0] == 'Tony'


def test_byline_to_names_semicolon_seperated_names_and_for():
    names = byline_to_names(
        'Sara Malm;Annette Witheridge;Ian Drury for the Daily Mail;'
        'Daniel Bates'
    )
    assert len(names) == 4
    assert names[2][0] == 'Ian'
    assert names[2][1] == 'Drury'


def test_byline_to_names_newline_after_and():
    names = byline_to_names('\nIan Sample and \nStuart Clark in Darmstadt')
    assert len(names) == 2
    assert names[1][1] == 'Clark'


def test_byline_to_names_schema_author():
    # https://www.abc.net.au/news/2020-09-06/glow-worms-in-wollemi-national-park-survived-summer-bushfire/12634762
    assert find_authors(
        '<script data-react-helmet="true" type="application/ld+json">'
        '{"@context":"http://schema.org","@type":"NewsArticle","author":'
        '[{"@type":"Person","name":"Kathleen Ferguson"}],'
    ) == [('Kathleen', 'Ferguson')]


def test_authors_meta_tag_with_no_quote():  # 28
    # <meta property=article:author content="Brian Truitt"/>
    assert (
        '{{cite web | last=Truitt | first=Brian '
        "| title='Star Wars': Disney+ switches up controversial "
        'Han Solo/Greedo scene | website=USA TODAY | date=2019-11-12 '
        '| url=https://www.usatoday.com/story/entertainment/movies/2019/11/12/star-wars-disney-plus-changes-controversial-han-solo-greedo-scene/2576097001/ '
        '| access-date='
    ) == urls_scr(
        'https://www.usatoday.com/story/entertainment/movies/2019/11/12/star-wars-disney-plus-changes-controversial-han-solo-greedo-scene/2576097001/'
    )[1][2:-12]


def test_uppercase_sitename_in_authors():  # 28
    # note: must use the specific testdata stored at
    # https://gist.github.com/5j9/ec831edb740363191e21c4f500cb9a09#file-usatoday_toolforge-html-L86
    assert (
        '{{cite web | last=Truitt | first=Brian '
        "| title=The infamous 'Han shot first' scene in 'Star Wars' has changed yet again on Disney+ "
        '| website=USA TODAY | date=2019-11-12 '
        '| url=https://www.usatoday.com/story/entertainment/movies/2019/11/12/star-wars-disney-plus-changes-controversial-han-solo-greedo-scene/2576097001/ '
        '| access-date='
    ) == urls_scr(
        'https://www.usatoday.com/story/entertainment/movies/2019/11/12/2576097001/'
    )[1][2:-12]


def test_byline_ending_with_semicolon():
    # https://pubmed.ncbi.nlm.nih.gov/32687126/
    # <meta name="citation_authors" content="Ojewola RW;Tijani KH;Fatuga AL;Onyeze CI;Okeke CJ;">
    assert byline_to_names(
        'Ojewola RW;Tijani KH;Fatuga AL;Onyeze CI;Okeke CJ;'
    ) == [  # it used to raise error however first are last are still swapped
        ('Ojewola', 'RW'),
        ('Tijani', 'KH'),
        ('Fatuga', 'AL'),
        ('Onyeze', 'CI'),
        ('Okeke', 'CJ'),
    ]


def test_find_authors_json_ld_url_between_type_and_name():
    # https://www.nytimes.com/1997/09/30/nyregion/worker-dies-as-scaffold-collapses-in-repair-job.html
    assert find_authors(
        '"author":[{"@context":"http://schema.org","@type":"Person","url":"https://www.nytimes.com/by/michael-cooper","name":"Michael Cooper"}],'
    ) == [('Michael', 'Cooper')]


def test_json_ld_author_name_is_list():
    # https://www.npr.org/2012/05/31/153720369/requiem-for-a-cabaret-the-oak-room-closes
    assert find_authors(
        ',"author":{"@type":"Person","name":["Jeff Lunden"]},'
    ) == [('Jeff', 'Lunden')]


def test_json_ld_first_name_only():
    # https://www.reuters.com/world/europe/russia-says-ukrainian-forces-have-crossed-river-dnipro-face-hell-fire-death-2023-11-15/
    # used to raise TypeError
    assert not json_ld_authors(
        '[{"@type":"Person","name":"Reuters","sameAs":"https://www.reuters.comundefined"}]'
    )


def test_json_ld_name_not_a_list():
    # https://www.fr.de/frankfurt/magische-maschinen-im-frankfurter-liebieghaus-92326311.html
    # used to raise TypeError
    assert find_authors('"author":["Andreas Hartmann"]') == [
        ('["Andreas', 'Hartmann"]')
    ]
