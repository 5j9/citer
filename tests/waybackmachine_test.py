from lib.commons import dict_to_sfn_cit_ref
from lib.waybackmachine import url_to_dict


def waybackmachine_scr(*args):
    return dict_to_sfn_cit_ref(url_to_dict(*args))


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
    assert (
        '* {{cite web '
        '| title=London Development Centre: Support, time, recovery (STR) '
        'workers '
        '| website=londondevelopmentcentre.org '
        '| date=2007-02-12 '
        '| url=http://www.londondevelopmentcentre.org/page.php?s=1&p=2462 '
        '| archive-url=https://web.archive.org/web/20070429193849id_/'
        'http://www.londondevelopmentcentre.org/page.php?s=1&p=2462 '
        '| archive-date=2007-04-29 '
        '| url-status=dead '
        '| ref={{sfnref | londondevelopmentcentre.org | 2007}} '
        '| access-date='
    ) == waybackmachine_scr(
        'https://web.archive.org/web/20070429193849id_/http://www.londondevelopmentcentre.org/page.php?s=1&p=2462'
    )[1][:-12]


def test_webless_url():
    """The 'web/ component of the url can be omitted sometimes."""
    o = waybackmachine_scr(
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
    )
    ct = (
        '* {{cite web '
        '| title=روانچی: در ارتباط با مواضع نامناسب '
        'اخیر مقامات انگلیسی در مورد ایران گفت‌وگو خواهیم کرد |'
        ' website=ایسنا |'
        ' date=2017-01-18 '
        '| url=http://www.isna.ir/news/95102918901/'
        '%D8%B1%D9%88%D8%A7%D9%86%DA%86%DB%8C-%D8%AF%D8%B1-'
        '%D8%A7%D8%B1%D8%AA%D8%A8%D8%A7%D8%B7-%D8%A8%D8%A7-'
        '%D9%85%D9%88%D8%A7%D8%B6%D8%B9-'
        '%D9%86%D8%A7%D9%85%D9%86%D8%A7%D8%B3%D8%A8-'
        '%D8%A7%D8%AE%DB%8C%D8%B1-%D9%85%D9%82%D8%A7%D9%85%D8%A7%D8%AA-'
        '%D8%A7%D9%86%DA%AF%D9%84%DB%8C%D8%B3%DB%8C-%D8%AF%D8%B1-'
        '%D9%85%D9%88%D8%B1%D8%AF '
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
        '| ref={{sfnref | ایسنا | 2017}} '
        '| access-date='
    )
    assert ct in o[1]
