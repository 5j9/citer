from unittest.mock import patch

from lib.archives import archive_org_data, archive_today_data
from lib.commons import data_to_sfn_cit_ref


def waybackmachine_scr(url):
    return data_to_sfn_cit_ref(archive_org_data(url))


def today_scr(url):
    return data_to_sfn_cit_ref(archive_today_data(url))


def test_live_og_link():
    """dead-link=no"""
    assert (
        '* {{cite web '
        '| last=Stuart '
        '| first=Hunter '
        '| title=LOOK: Bieber Fan Had $100K Worth Of Plastic Surgery To '
        'Look Like His Idol '
        '| website=The Huffington Post '
        '| date=2013-10-19 '
        '| url=http://www.huffingtonpost.com/2013/10/19/'
        'plastic-surgery-justin-bieber-100k_n_4128563.html?'
        'utm_hp_ref=mostpopular '
        '| archive-url=http://web.archive.org/web/20131021230444/http://www.huffingtonpost.com/2013/10/19/plastic-surgery-justin-bieber-100k_n_4128563.html?utm_hp_ref=mostpopular '
        '| archive-date=2013-10-21 '
        '| url-status=live '
        '| access-date='
    ) == waybackmachine_scr(
        'http://web.archive.org/web/20131021230444/'
        'http://www.huffingtonpost.com/2013/10/19/'
        'plastic-surgery-justin-bieber-100k_n_4128563.html?'
        'utm_hp_ref=mostpopular'
    )[1][:-12]


def test_dead_url():
    """url-status=dead"""
    assert waybackmachine_scr(
        'https://web.archive.org/web/20070429193849id_/http://www.londondevelopmentcentre.org/page.php?s=1&p=2462'
    )[1][:-12] == (
        '* {{cite web '
        '| title=London Development Centre: Support, time, recovery (STR) '
        'workers '
        '| website=londondevelopmentcentre.org '
        '| date=2007-02-12 '
        '| url=http://www.londondevelopmentcentre.org/page.php?s=1&p=2462 '
        '| archive-url=https://web.archive.org/web/20070429193849id_/http://www.londondevelopmentcentre.org/page.php?s=1&p=2462 '
        '| archive-date=2007-04-29 '
        '| url-status=dead '
        '| ref={{sfnref|londondevelopmentcentre.org|2007}} '
        '| access-date='
    )


def test_webless_url():
    """The 'web/ component of the url can be omitted sometimes."""
    assert waybackmachine_scr(
        'https://web.archive.org/web/20170119050001/'
        'http://www.isna.ir/news/95102918901/'
        '%D8%B1%D9%88%D8%A7%D9%86%DA%86%DB%8C-%D8%AF%D8%B1-'
        '%D8%A7%D8%B1%D8%AA%D8%A8%D8%A7%D8%B7-%D8%A8%D8%A7-'
        '%D9%85%D9%88%D8%A7%D8%B6%D8%B9-'
        '%D9%86%D8%A7%D9%85%D9%86%D8%A7%D8%B3%D8%A8-'
        '%D8%A7%D8%AE%DB%8C%D8%B1-'
        '%D9%85%D9%82%D8%A7%D9%85%D8%A7%D8%AA-'
        '%D8%A7%D9%86%DA%AF%D9%84%DB%8C%D8%B3%DB%8C-'
        '%D8%AF%D8%B1-%D9%85%D9%88%D8%B1%D8%AF'
    )[1][:-12] == (
        '* {{cite web '
        '| title=روانچی: در ارتباط با مواضع نامناسب '
        'اخیر مقامات انگلیسی در مورد ایران گفت‌وگو خواهیم کرد |'
        ' website=ایسنا |'
        ' date=2017-01-18 '
        '| url=http://www.isna.ir/news/95102918901/روانچی-در-ارتباط-با-مواضع-نامناسب-اخیر-مقامات-انگلیسی-در-مورد '
        '| archive-url=https://web.archive.org/web/20170119050001/'
        'http://www.isna.ir/news/95102918901/'
        '%D8%B1%D9%88%D8%A7%D9%86%DA%86%DB%8C-%D8%AF%D8%B1-'
        '%D8%A7%D8%B1%D8%AA%D8%A8%D8%A7%D8%B7-%D8%A8%D8%A7-'
        '%D9%85%D9%88%D8%A7%D8%B6%D8%B9-'
        '%D9%86%D8%A7%D9%85%D9%86%D8%A7%D8%B3%D8%A8-'
        '%D8%A7%D8%AE%DB%8C%D8%B1-'
        '%D9%85%D9%82%D8%A7%D9%85%D8%A7%D8%AA-'
        '%D8%A7%D9%86%DA%AF%D9%84%DB%8C%D8%B3%DB%8C-%D8%AF%D8%B1-'
        '%D9%85%D9%88%D8%B1%D8%AF '
        '| archive-date=2017-01-19 '
        '| url-status=live '
        '| language=fa '
        '| ref={{sfnref|ایسنا|2017}} '
        '| access-date='
    )


def test_dead_redirect():
    """original urls that redirect to a generic or homepage url instead of throwing 404 should still be considered dead"""
    assert waybackmachine_scr(
        'https://web.archive.org/web/20220113020216/www.lib.city.minato.tokyo.jp/yukari/e/man-detail.cgi?id=79'
    )[1][:-12] == (
        '* {{cite web '
        '| title=Prominent People of Minato City (Henricus Conradus Joannes Heusken) '
        '| website=lib.city.minato.tokyo.jp '
        '| date=2021-12-04 '
        '| url=http://www.lib.city.minato.tokyo.jp/yukari/e/man-detail.cgi?id=79 '
        '| archive-url=https://web.archive.org/web/20220113020216/www.lib.city.minato.tokyo.jp/yukari/e/man-detail.cgi?id=79 '
        '| archive-date=2022-01-13 '
        '| url-status=dead '
        '| language=ja '
        '| ref={{sfnref|lib.city.minato.tokyo.jp|2021}} '
        '| access-date='
    )


def test_archive_today_data():
    assert today_scr('https://archive.ph/N3fQ')[1][:-12] == (
        "* {{cite web | title=Brendan Fraser's Looney Adventure | website=cbsnews.com "
        '| date=2012-12-11 | '
        'url=http://www.cbsnews.com/stories/2003/11/12/earlyshow/leisure/celebspot/main583274.shtml '
        '| archive-url=https://archive.ph/N3fQ | archive-date=2012-12-11 | '
        'url-status=dead | ref={{sfnref|cbsnews.com|2012}} | access-date='
    )


@patch('lib.archives.url_text')
@patch('lib.urls.request')
def test_target_url_is_unquoted(request_mock, url_text_mock):
    # request_mock.side_effect = NotImplementedError
    url_text_mock.return_value = '', ''

    # Define the URLs
    input_url = (
        'https://web.archive.org/web/20240722174924/'
        'https%3A%2F%2Fwww.hindustantimes.com%2Fcities%2Fothers%2F'
        'gauhati-hc-issues-summons-to-bjp-mp-from-assam-over-alleged-poll-irregularities-'
        '101721657172227-amp.html'
    )
    expected_url = (
        'https://www.hindustantimes.com/cities/others/'
        'gauhati-hc-issues-summons-to-bjp-mp-from-assam-over-alleged-poll-irregularities-'
        '101721657172227-amp.html'
    )
    # Suppress the NotImplementedError during the test
    # with raises(NotImplementedError):
    archive_org_data(input_url)

    calls = request_mock.call_args_list
    assert len(calls) == 1
    assert calls[0].args[0] == expected_url
