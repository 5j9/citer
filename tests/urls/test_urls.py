# noinspection PyPackageRequirements
from unittest.mock import Mock, patch

from curl_cffi import CurlError
from pytest import mark

from lib.commons import dict_to_sfn_cit_ref
from lib.urls import (
    LANG_SEARCH,
    ContentTypeError,
    _analyze_home,
    url_to_dict,
)
from tests import FakeResponse


def urls_scr(*args):
    return dict_to_sfn_cit_ref(url_to_dict(*args))


def test_bostonglobe1():
    """boston.com, dateformat '%B %d, %Y'"""
    cit = urls_scr(
        'http://www.boston.com/cars/news-and-reviews/2014/06/28/hot-rod-stamps-google-road-prospectus/hylbVi9qonAwBIH10CwiDP/story.html',
        '%B %d, %Y',
    )[1]
    assert (
        '* {{cite web '
        '| last=Griffith '
        '| first=Bill '
        '| title=Hot Rod Stamps; Google on Road; A GM Prospectus '
        '| website=Boston.com '
        '| date=June 29, 2014 '
        '| url=https://www.boston.com/cars/news-and-reviews/2014/06/29/hot-rod-stamps-google-on-road-a-gm-prospectus '
        '| access-date'
    ) == cit[: cit.rfind('=')]


def test_bostonglobe2():
    """bostonglobe.com"""
    assert (
        '* {{cite web '
        '| last=Saltzman '
        '| first=Jonathan '
        '| last2=Farragher '
        '| first2=Thomas '
        '| title=Walsh meets with college leaders on off-campus housing '
        '| website=BostonGlobe.com '
        '| date=2014-06-03 '
        '| url=http://www.bostonglobe.com/metro/2014/06/03/walsh-meets-with-college-leaders-off-campus-housing/lsxtLSGJMD86Gbkjay3D6J/story.html '
        '| access-date='
    ) == urls_scr(
        'http://www.bostonglobe.com/metro/2014/06/03/walsh-meets-with-college-leaders-off-campus-housing/lsxtLSGJMD86Gbkjay3D6J/story.html'
    )[1][:-12]


def test_bostonglobe3():
    """bostonmagazine.com. Author tags return unrelated authors."""
    assert urls_scr(
        'http://www.bostonmagazine.com/news/blog/2013/08/21/'
        'juliette-kayyem-jumps-in-for-guv/'
    )[1][:-12] == (
        '* {{cite web '
        '| last=Bernstein '
        '| first=David S. '
        '| title=Juliette Kayyem Is Running for Governor of Massachusetts '
        '| website=Boston Magazine '
        '| date=2013-08-21 '
        '| url=http://www.bostonmagazine.com/news/blog/2013/08/21/'
        'juliette-kayyem-jumps-in-for-guv/ '
        '| access-date='
    )


def test_washingtonpost1():
    """`1 author, 2005, the pubdate is different from last edit date"""
    o = urls_scr(
        'http://www.washingtonpost.com/wp-dyn/content/article/2005/09/02/'
        'AR2005090200822.html'
    )
    assert '{{sfn | Sachs | 2005}}' in o[0]
    assert (
        '* {{cite web '
        '| last=Sachs '
        '| first=Andrea '
        '| title=March of the Migration '
        '| website=Washington Post '
        '| date=2005-09-04 '
        '| url=http://www.washingtonpost.com/wp-dyn/content/article/'
        '2005/09/02/AR2005090200822.html '
        '| access-date='
    ) == o[1][:-12]


def test_huffingtonpost1():
    """`1 author, 2013"""
    o = urls_scr(
        'http://www.huffingtonpost.ca/annelise-sorg/'
        'blackfish-killer-whale-seaworld_b_3686306.html'
    )
    assert '{{sfn | Sorg | 2013}}' == o[0]
    assert (
        '* {{cite web '
        '| last=Sorg '
        '| first=Annelise '
        '| title=When Killer Whales Kill: Why the movie'
        ' "Blackfish" Should Sink Captive Whale Programs '
        '| website=The Huffington Post '
        '| date=2013-08-01 '
        '| url=http://www.huffingtonpost.ca/annelise-sorg/'
        'blackfish-killer-whale-seaworld_b_3686306.html '
        '| access-date='
    ) == o[1][:-12]


def test_huffingtonpost2():
    """`class:author` returns wrong result. Disallow `\n` in fullnames."""
    i = (
        'http://www.huffingtonpost.com/jeremy-rifkin/'
        'obamas-climate-change-plan_b_5427656.html'
    )
    o = urls_scr(i)
    e2 = (
        '* {{cite web '
        '| last=Rifkin '
        '| first=Jeremy '
        "| title=Beyond Obama's Plan: "
        'A New Economic Vision for Addressing Climate Change '
        '| website=The Huffington Post '
        '| date=2014-06-02 '
        '| url=http://www.huffingtonpost.com/jeremy-rifkin/'
        'obamas-climate-change-plan_b_5427656.html '
        '| access-date='
    )
    assert '{{sfn | Rifkin | 2014}}' == o[0]
    assert e2 == o[1][:-12]


def test_dilytelegraph1():
    """`1 author, 2005"""
    i = (
        'http://www.telegraph.co.uk/news/health/3334755/'
        'We-could-see-the-whales-eyes-mouth...-'
        'the-barnacles-on-its-back.html'
    )
    o = urls_scr(i)
    e2 = (
        '* {{cite web '
        '| last=Fogle '
        '| first=Ben '
        "| title=We could see the whale's eyes, mouth... "
        'the barnacles on its back '
        '| website=Telegraph.co.uk '
        '| date=2005-12-22 '
        '| url=http://www.telegraph.co.uk/news/health/3334755/'
        'We-could-see-the-whales-eyes-mouth...-'
        'the-barnacles-on-its-back.html '
        '| access-date='
    )
    assert '{{sfn | Fogle | 2005}}' == o[0]
    assert e2 == o[1][:-12]


def test_dilytelegraph2():
    """1 author, 2003"""
    i = (
        'http://www.telegraph.co.uk/news/science/science-news/3313298/'
        'Marine-collapse-linked-to-whale-decline.html'
    )
    o = urls_scr(i)
    e2 = (
        '* {{cite web '
        '| last=Highfield '
        '| first=Roger '
        "| title=Marine 'collapse' linked to whale decline "
        '| website=Telegraph.co.uk '
        '| date=2003-09-29 '
        '| url=http://www.telegraph.co.uk/news/science/science-news/'
        '3313298/Marine-collapse-linked-to-whale-decline.html '
        '| access-date='
    )
    assert '{{sfn | Highfield | 2003}}' == o[0]
    assert e2 == o[1][:-12]


def test_dilytelegraph3():
    """1 author, 2011"""
    i = 'http://www.telegraph.co.uk/news/8323909/The-sperm-whale-works-in-extraordinary-ways.html'
    o = urls_scr(i)
    e2 = (
        '* {{cite web '
        '| last=Whitehead '
        '| first=Hal '
        '| title=The sperm whale works in extraordinary ways '
        '| website=Telegraph.co.uk '
        '| date=2011-02-15 '
        '| url=http://www.telegraph.co.uk/news/8323909/The-sperm-whale-works-in-extraordinary-ways.html '
        '| access-date='
    )
    assert '{{sfn | Whitehead | 2011}}' == o[0]
    assert e2 == o[1][:-12]


def test_dilymail1():
    """4 authors"""
    o = urls_scr(
        'http://www.dailymail.co.uk/news/article-2633025/'
        'London-cleric-convicted-NYC-terrorism-trial.html'
    )
    assert '{{sfn | Malm | Witheridge | Drury | Bates | 2014}}' == o[0]
    assert (
        '* {{cite web '
        '| last=Malm '
        '| first=Sara '
        '| last2=Witheridge '
        '| first2=Annette '
        '| last3=Drury '
        '| first3=Ian '
        '| last4=Bates '
        '| first4=Daniel '
        '| title=Abu Hamza found guilty in US court of helping'
        ' Al-Qaeda terrorists '
        '| website=Daily Mail Online '
        '| date=2014-05-19 '
        '| url=http://www.dailymail.co.uk/news/article-2633025/'
        'London-cleric-convicted-NYC-terrorism-trial.html '
        '| access-date='
    ) == o[1][:-12]


def test_dilymail2():
    """`for` in byline."""
    assert (
        '* {{cite web '
        '| last=Gower '
        '| first=Eleanor '
        "| title=Kim Kardashian's meltdown at nude magazine cover"
        ' three years before full frontal photoshoot '
        '| website=Daily Mail Online '
        '| date=2014-11-14 '
        '| url=http://www.dailymail.co.uk/tvshowbiz/article-2834145/'
        'I-m-never-taking-clothes-s-Vogue-Throwback-2011-video-shows-Kim-'
        'Kardashian-s-meltdown-nude-magazine-cover.html '
        '| access-date='
    ) == urls_scr(
        'http://www.dailymail.co.uk/tvshowbiz/article-2834145/'
        'I-m-never-taking-clothes-s-Vogue-Throwback-2011-video-'
        'shows-Kim-Kardashian-s-meltdown-nude-magazine-cover.html'
    )[1][:-12]


def test_bbc1():
    """no authors"""
    i = 'https://www.bbc.com/news/world-asia-27653361'
    o = urls_scr(i)
    ct = (
        '* {{cite web '
        "| title=US 'received Qatar assurances' on Afghan prisoner deal "
        '| website=BBC News '
        '| date=2014-06-01 '
        '| url=http://www.bbc.com/news/world-asia-27653361 '
        '| ref={{sfnref | BBC News | 2014}} '
        '| access-date='
    )
    assert ct == o[1][:-12]


def test_bbc2():
    """1 author"""
    assert (
        '* {{cite web '
        '| last=Gage '
        '| first=Suzi '
        '| title=Sea otter return boosts ailing seagrass in California '
        '| website=BBC News '
        '| date=2013-08-26 '
        '| url=http://www.bbc.com/news/science-environment-23814524 '
        '| access-date='
    ) == urls_scr('http://www.bbc.com/news/science-environment-23814524')[1][
        :-12
    ]


def test_bbc3():
    """https version of bbc2 (differs a lot!)"""
    i = 'https://www.bbc.com/news/science-environment-23814524'
    o = urls_scr(i)
    ct = (
        '* {{cite web '
        '| last=Gage '
        '| first=Suzi '
        '| title=Sea otter return boosts ailing seagrass in California '
        '| website=BBC News '
        '| date=2013-08-26 '
        '| url=http://www.bbc.com/news/science-environment-23814524 '
        '| access-date='
    )
    assert ct == o[1][:-12]


def test_bbc4():
    """news.bbc.co.uk, 1 author"""
    assert (
        '* {{cite web '
        '| last=Jones '
        '| first=Meirion '
        "| title=Malaria advice 'risks lives' "
        '| website=BBC NEWS '
        '| date=2006-07-13 '
        '| url='
        'http://news.bbc.co.uk/2/hi/programmes/newsnight/5178122.stm '
        '| access-date='
    ) == urls_scr(
        'http://news.bbc.co.uk/2/hi/programmes/newsnight/5178122.stm'
    )[1][:-12]


def test_bbc5():
    """news.bbc.co.uk, 1 author"""
    assert (
        '* {{cite web '
        '| last=Madslien '
        '| first=Jorn '
        '| title=Inside the Bentley factory '
        '| website=BBC NEWS '
        '| date=2002-12-24 '
        '| url=http://news.bbc.co.uk/2/hi/business/2570109.stm '
        '| access-date='
    ) == urls_scr('http://news.bbc.co.uk/2/hi/business/2570109.stm')[1][:-12]


def test_bbc6():
    """bbc.com, 1 author"""
    i = 'http://www.bbc.com/news/science-environment-26267918'
    o = urls_scr(i)
    ct = (
        '* {{cite web '
        '| last=Amos '
        '| first=Jonathan '
        '| title=European Space Agency picks Plato planet-hunting mission '
        '| website=BBC News '
        '| date=2014-02-20 '
        '| url=http://www.bbc.com/news/science-environment-26267918 '
        '| access-date='
    )
    assert ct == o[1][:-12]


def test_nyt1():
    """newstylct, 1 author"""
    i = 'http://www.nytimes.com/2014/05/30/business/international/on-the-internet-the-right-to-forget-vs-the-right-to-know.html?hp&_r=0'
    o = urls_scr(i)
    ct = (
        '* {{cite web '
        '| last=Hakim '
        '| first=Danny '
        '| title=Right to Be Forgotten? Not That Easy '
        '| website=The New York Times '
        '| date=2014-05-30 '
        '| url=https://www.nytimes.com/2014/05/30/business/international/on-the-internet-the-right-to-forget-vs-the-right-to-know.html?hp&_r=1 '
        '| access-date='
    )
    assert ct == o[1][:-12]


def test_nyt2():
    """newstylct, 2 authors"""
    ct = (
        '* {{cite web '
        '| last=Belson '
        '| first=Ken '
        '| last2=Sandomir '
        '| first2=Richard '
        '| title=$2 Billion for Clippers? In Time, '
        'It May Be a Steal for Steve Ballmer '
        '| website=The New York Times '
        '| date=2014-05-30 '
        '| url=https://www.nytimes.com/2014/05/31/sports/basketball/steven-a-ballmers-2-billion-play-for-clippers-is-a-big-bet-on-the-nba.html?hp&_r=0 '
        '| access-date='
    )
    assert (
        ct
        == urls_scr(
            'https://www.nytimes.com/2014/05/31/sports/basketball/steven-a-ballmers-2-billion-play-for-clippers-is-a-big-bet-on-the-nba.html?hp'
        )[1][:-12]
    )


def test_nyt3():
    """oldstylct, 1 author"""
    i = 'http://www.nytimes.com/2007/12/25/world/africa/25kenya.html'
    o = urls_scr(i)
    ct = (
        '* {{cite web '
        '| last=Gettleman '
        '| first=Jeffrey '
        '| title=Election Rules Complicate Kenya Race '
        '| website=The New York Times '
        '| date=2007-12-25 '
        '| url=http://www.nytimes.com/2007/12/25/world/africa/25kenya.html '
        '| access-date='
    )
    assert ct == o[1][:-12]


def test_nyt4():
    """newstylct, 2 authors, only byline"""
    i = 'http://dealbook.nytimes.com/2014/05/30/insider-trading-inquiry-includes-mickelson-and-icahn/'
    o = urls_scr(i)
    ct = (
        '* {{cite web '
        '| last=Goldstein '
        '| first=Matthew '
        '| last2=Protess '
        '| first2=Ben '
        '| title=Investor, Bettor, Golfer: '
        'Insider Trading Inquiry Includes Mickelson, Icahn and William T. '
        'Walters '
        '| website=DealBook '
        '| date=2014-06-12 '
        '| url=https://dealbook.nytimes.com/2014/05/30/insider-trading-inquiry-includes-mickelson-and-icahn/?_r=0 '
        '| access-date='
    )
    assert ct == o[1][:-12]


def test_nyt5():
    """special case for date format (not in usual meta tags)"""
    i = (
        'https://www.nytimes.com/2007/06/13/world/americas/'
        '13iht-whale.1.6123654.html'
    )
    o = urls_scr(i)
    ct = (
        '* {{cite web '
        '| title=19th-century harpoon gives clue on whales '
        '| website=The New York Times '
        '| date=2007-06-13 '
        '| url=http://www.nytimes.com/2007/06/13/world/americas/'
        '13iht-whale.1.6123654.html '
        '| ref={{sfnref | The New York Times | 2007}} '
        '| access-date='
    )
    assert ct == o[1][:-12]


def test_nyt6():
    """lastname=O'Connor"""
    i = 'http://www.nytimes.com/2003/10/09/us/adding-weight-to-suspicion-sonar-is-linked-to-whale-deaths.html'
    o = urls_scr(i)
    ct = (
        '* {{cite web '
        "| last=O'Connor "
        '| first=Anahad '
        '| title=Adding Weight to Suspicion, '
        'Sonar Is Linked to Whale Deaths '
        '| website=The New York Times '
        '| date=2003-10-09 '
        '| url=http://www.nytimes.com/2003/10/09/us/adding-weight-to-suspicion-sonar-is-linked-to-whale-deaths.html '
        '| access-date='
    )
    assert ct == o[1][:-12]


def test_tgdaily1():
    # Hard to find author and date.
    assert urls_scr(
        'http://www.tgdaily.com/web/100381-apple-might-buy-beats-for-32-billion'
    )[1][:-12] == (
        '* {{cite web '
        '| title=Apple might buy Beats for $3.2 billion '
        '| website=TG Daily '
        '| date=2014-05-09 '
        '| url=http://www.tgdaily.com/web/'
        '100381-apple-might-buy-beats-for-32-billion '
        '| ref={{sfnref | TG Daily | 2014}} '
        '| access-date='
    )


def test_tgdaily2():
    """ "Staff" in author name."""
    i = (
        'http://www.tgdaily.com/space-features/'
        '82906-sma-reveals-giant-star-cluster-in-the-making'
    )
    o = urls_scr(i)
    ct = (
        '* {{cite web '
        '| title=SMA reveals giant star cluster in the making '
        '| website=TG Daily '
        '| date=2013-12-17 '
        '| url=http://www.tgdaily.com/space-features/'
        '82906-sma-reveals-giant-star-cluster-in-the-making '
        '| ref={{sfnref | TG Daily | 2013}} '
        '| access-date='
    )
    assert ct == o[1][:-12]


@mark.skip
def test_tgdaily3():
    """ABCNews. Wrong author:  | last=News | first=ABC."""
    i = 'http://abcnews.go.com/blogs/headlines/2006/12/saddam_executed/'
    o = urls_scr(i)
    ct = (
        '* {{cite web '
        '| last=Ross '
        '| first=Brian '
        '| title=Saddam Executed; An Era Comes to an End '
        '| website=ABC News Blogs '
        '| date=2006-12-30 '
        '| url=http://abcnews.go.com/blogs/headlines/2006/12/'
        'saddam_executed/ '
        '| access-date='
    )
    assert ct == o[1][:-12]


def test_oth2():
    """Times of India, author could not be detected."""
    i = (
        'http://timesofindia.indiatimes.com/city/pune/'
        'UK-allows-working-visas-for-Indian-students/'
        'articleshow/1163528927.cms?'
    )
    o = urls_scr(i)
    sfn = '{{sfn | Kashyap | 2001}}'
    assert sfn in o[0]


def test_text_search():
    """Match byline on soup.text."""
    assert (
        '* {{cite web '
        '| last=Carlson '
        '| first=Kimberly '
        '| last2=York '
        '| first2=Jillian C. '
        '| title=Sudan Tech Sanctions Harm Innovation and Development: '
        'US Government and Corporations Must Act '
        '| website=Electronic Frontier Foundation '
        '| date=2014-06-26 '
        '| url=https://www.eff.org/deeplinks/2014/06/'
        'sudan-tech-sanctions-harm-innovation-development-us-'
        'government-and-corporations-must-act '
        '| access-date='
    ) == urls_scr(
        'https://www.eff.org/deeplinks/2014/06/'
        'sudan-tech-sanctions-harm-innovation-development-us-'
        'government-and-corporations-must-act'
    )[1][:-12]


# Disable because relies on class="author" which has been disabled due
# to hight error rate.
@mark.skip
def test_oth3():
    """4 authors."""
    i = (
        'https://arstechnica.com/science/2007/09/'
        'the-pseudoscience-behind-homeopathy/'
    )
    o = urls_scr(i)
    ct = (
        '* {{cite web '
        '| last=Timmer '
        '| first=John '
        '| last2=Ford '
        '| first2=Matt '
        '| last3=Lee '
        '| first3=Chris '
        '| last4=Gitlin '
        '| first4=Jonathan '
        '| title=Diluting the scientific method:  Ars looks at homeopathy '
        '| website=Ars Technica '
        '| date=2007-09-12 '
        '| url=https://arstechnica.com/science/2007/09/'
        'the-pseudoscience-behind-homeopathy/ '
        '| access-date='
    )
    assert ct == o[1][:-12]


def test_oth4():
    """rel="author" tag contains invalid information."""
    assert (
        '* {{cite web '
        '| last=Ghose '
        '| first=Tia '
        "| title='Revolutionary' Physics:"
        ' Do Sterile Neutrinos Lurk in the Universe? '
        '| website=Live Science '
        '| date=2014-07-01 '
        '| url=http://www.livescience.com/46619-sterile-neutrino-experiment-beginning.html?cmpid=514645_20140702_27078936 '
        '| access-date='
    ) == urls_scr(
        'http://www.livescience.com/46619-sterile-neutrino-experiment-beginning.html?cmpid=514645_20140702_27078936'
    )[1][:-12]


def test_oth5():
    """Getting the date is tricky here."""
    o = urls_scr('http://www.magiran.com/npview.asp?ID=1410487')
    assert "{{sfn | ''Magiran'' | 2007}}" in o[0]
    assert (
        '* {{cite web '
        # todo: could this be fixed for the new format of magiran?
        # '| last=نوري '
        # '| first=آزاده شهمير '
        '| title=روزنامه سرمایه (1386/03/01): دکتر طاهر صباحی، محقق و '
        'مجموعه دار فرش: بازار جهانی با تولید فرش هنری نصیب ایران می شود '
        '| website=Magiran '
        '| date=2007-05-22 '
        '| url=https://www.magiran.com/article/1410487 '
        '| language=fa '
        '| ref={{sfnref | Magiran | 2007}} '
        '| access-date='
    ) == o[1][:-12]


def test_oth6():
    """Detection of website name."""
    o = urls_scr('http://www.farsnews.com/newstext.php?nn=13930418000036')
    assert (
        '* {{cite web | title=آیت\u200cالله محمدی گیلانی دارفانی را وداع گفت | publisher=Fars News Agency | date=2014-07-09 | url=http://www.farsnews.com/newstext.php?nn=13930418000036 | language=fa | ref={{sfnref | Fars News Agency | 2014}} | access-date='
    ) == o[1][:-12]
    assert '{{sfn | Fars News Agency | 2014}}' in o[0]
    # Fars news is using 'خبرگزاری فارس' as og:author which is wrong
    # and thats why its name is not italicized in sfn.


def test_oth7():
    """Contains a By Topic line and also the byline contains ' | '."""
    assert (
        '* {{cite web '
        '| last=Chandler '
        '| first=David L. '
        '| title=Traffic lights: There’s a better way '
        '| website=MIT News '
        '| date=2014-07-07 '
        '| url=http://news.mit.edu/2014/'
        'traffic-lights-theres-a-better-way-0707 '
        '| access-date='
    ) == urls_scr(
        'http://news.mit.edu/2014/' 'traffic-lights-theres-a-better-way-0707'
    )[1][:-12]


def test_oth8():
    """Two authors from guardian that are mentions in other tags, too."""
    i = (
        'http://www.theguardian.com/world/2014/jul/14/'
        'israel-drone-launched-gaza-ashdod'
    )
    o = urls_scr(i)
    ct = (
        '* {{cite web '
        '| last=Beaumont '
        '| first=Peter '
        '| last2=Crowcroft '
        '| first2=Orlando '
        '| title=Israel says it has shot down drone launched from Gaza '
        '| website=the Guardian '
        '| date=2014-07-14 '
        '| url=https://www.theguardian.com/world/2014/jul/14/'
        'israel-drone-launched-gaza-ashdod '
        '| access-date='
    )
    assert ct == o[1][:-12]


def test_oth10():
    """The Times. (Authors found by "byline" css selector)"""
    assert (
        '* {{cite web '
        '| last=Lagan '
        '| first=Bernard '
        '| last2=Charter '
        '| first2=David '
        '| title='
        'Woman who lost brother on MH370 mourns relatives on board MH17 '
        '| website=The Times & The Sunday Times '
        '| date=2014-07-18 '
        '| url=https://www.thetimes.co.uk/article/woman-who-lost-brother-on-mh370-mourns-relatives-on-board-mh17-r07q5rwppl0 '
        '| access-date='
    ) == urls_scr(
        'https://www.thetimes.co.uk/article/woman-who-lost-brother-on-mh370-mourns-relatives-on-board-mh17-r07q5rwppl0'
    )[1][:-12]


def test_oth11():
    """Business News Daily."""
    i = 'http://www.businessnewsdaily.com/6762-male-female-entrepreneurs.html?cmpid=514642_20140715_27858876'
    o = urls_scr(i)
    ct = (
        '* {{cite web '
        '| last=Helmrich '
        '| first=Brittney '
        '| title=Male vs. Female Entrepreneurs: How Are They Different? '
        '| website=Business News Daily '
        '| date=2014-07-10 '
        '| url=http://www.businessnewsdaily.com/6762-male-female-entrepreneurs.html?cmpid=514642_20140715_27858876 '
        '| access-date='
    )
    assert ct == o[1][:-12]


def test_oth12():
    # thebulletin.org
    assert urls_scr(
        'http://thebulletin.org/evidence-shows-iron-dome-not-working7318'
    )[1][:-12] == (
        '* {{cite web '
        '| last=Postol '
        '| first=Theodore A. '
        '| title=The evidence that shows Iron Dome is not working '
        '| website=Bulletin of the Atomic Scientists '
        '| date=2014-07-19 '
        '| url=http://thebulletin.org/'
        'evidence-shows-iron-dome-not-working7318 '
        '| access-date='
    )


def test_reverse_name():
    """Author is `Martin, Tracy`. Tracy should be the first name."""
    assert (
        '* {{cite web '
        '| last=Martin '
        '| first=Tracy '
        '| title=Dynamometers Explained '
        '| publisher=Dealernews '
        '| date=2014-07-01 '
        '| url=https://www.highbeam.com/doc/1P3-3372742961.html '
        '| access-date='
    ) == urls_scr('http://www.highbeam.com/doc/1P3-3372742961.html')[1][:-12]


def test_oth14():
    """thebulletin.org"""
    i = (
        'http://www.independent.co.uk/news/business/'
        'the-investment-column-tt-group-1103208.html'
    )
    o = urls_scr(i)
    ct = (
        '* {{cite web '
        '| title=The Investment column: TT Group '
        '| website=The Independent '
        '| date=1999-06-29 '
        '| url=http://www.independent.co.uk/news/business/'
        'the-investment-column-tt-group-1103208.html '
        '| ref={{sfnref | The Independent | 1999}} '
        '| access-date='
    )
    assert ct == o[1][:-12]


def test_oth15():
    """Contains <link property="og:site_name" href="ایسنا" />"""
    assert (
        '* {{cite web '
        '| title=برجام شرایط بین‌المللی ایران را کاملا متحول کرد '
        '| website=ایسنا '
        '| date=2017-01-25 '
        '| url=http://www.isna.ir/news/95110603890/%D8%A8%D8%B1%D8%AC%D8%A7%D9%85-%D8%B4%D8%B1%D8%A7%DB%8C%D8%B7-%D8%A8%DB%8C%D9%86-%D8%A7%D9%84%D9%85%D9%84%D9%84%DB%8C-%D8%A7%DB%8C%D8%B1%D8%A7%D9%86-%D8%B1%D8%A7-%DA%A9%D8%A7%D9%85%D9%84%D8%A7-%D9%85%D8%AA%D8%AD%D9%88%D9%84-%DA%A9%D8%B1%D8%AF '
        '| language=fa '
        '| ref={{sfnref | ایسنا | 2017}} '
        '| access-date='
    ) == urls_scr(
        'http://www.isna.ir/news/95110603890/%D8%A8%D8%B1%D8%AC%D8%A7%D9%85-%D8%B4%D8%B1%D8%A7%DB%8C%D8%B7-%D8%A8%DB%8C%D9%86-%D8%A7%D9%84%D9%85%D9%84%D9%84%DB%8C-%D8%A7%DB%8C%D8%B1%D8%A7%D9%86-%D8%B1%D8%A7-%DA%A9%D8%A7%D9%85%D9%84%D8%A7-%D9%85%D8%AA%D8%AD%D9%88%D9%84-%DA%A9%D8%B1%D8%AF'
    )[1][:-12]


def test_invalid_name():
    """Test that URL does not fail with InvalidNameError."""
    url = 'http://www.irinn.ir/fa/news/499654/%D8%A7%D9%86%D8%AA%D8%AE%D8%A7%D8%A8%D8%A7%D8%AA-96-%D8%A8%D9%87-%D8%B1%D9%88%D8%A7%DB%8C%D8%AA-%D8%A2%D9%85%D8%A7%D8%B1'
    assert (
        '* {{cite web | title=انتخابات 96 به روایت آمار | publisher=پایگاه اطلاع رسانی شبکه خبر صدا و سیمای جمهوری اسلامی ایران | date=2017-05-24 | url=http://www.irinn.ir/fa/news/499654/%D8%A7%D9%86%D8%AA%D8%AE%D8%A7%D8%A8%D8%A7%D8%AA-96-%D8%A8%D9%87-%D8%B1%D9%88%D8%A7%DB%8C%D8%AA-%D8%A2%D9%85%D8%A7%D8%B1 | language=fa | ref={{sfnref | پایگاه اطلاع رسانی شبکه خبر صدا و سیمای جمهوری اسلامی ایران | 2017}} | access-date='
    ) == urls_scr(url)[1][:-12]


def test_pages_from_html_meta():
    """Test extracting pages from html meta tags."""
    assert urls_scr('http://socialhistory.ihcs.ac.ir/article_319_84.html')[1][
        :-12
    ] == (
        '* {{cite journal '
        '| last=جلیلیان '
        '| first=شهرام '
        '| title=نهاد دایگانی در دورۀ ساسانیان '
        '| journal=تحقیقات تاریخ اجتماعی '
        '| volume=2 '
        '| issue=1 '
        '| date=2012-09-17 '
        '| issn=2383-0484 '
        '| pages=53–74 '
        '| url=http://socialhistory.ihcs.ac.ir/article_319_84.html '
        '| language=fa '
        '| access-date='
    )


def test_empty_meta_author_content():
    """Test that the output will not be malformed because empty meta."""
    assert (
        '* {{cite web '
        "| title=UAE's Enoc pays Iran $4 billion in oil dues "
        '| website=Al Jazeera '
        '| date=2017-05-29 '
        '| url=http://www.aljazeera.com/news/2017/05/uae-enoc-pays-iran-4-billion-oil-dues-170529171315570.html '
        '| ref={{sfnref | Al Jazeera | 2017}} '
        '| access-date='
    ) == urls_scr(
        'http://www.aljazeera.com/news/2017/05/'
        'uae-enoc-pays-iran-4-billion-oil-dues-170529171315570.html'
    )[1][:-12]


def test_citation_author_reverse_order():
    """Test correct detection of citation_author.

    first name and last name are in reverse order.

    """
    assert (
        '* {{cite web '
        '| last=Hartman '
        '| first=JudithAnn R. '
        '| last2=Nelson '
        '| first2=Eric A. '
        '| title=Automaticity in Computation and Student Success in '
        'Introductory Physical Science Courses '
        '| website=arXiv.org e-Print archive '
        '| date=2016-08-17 '
        '| url=https://arxiv.org/abs/1608.05006?utm_medium=email&utm_source=other&utm_campaign=opencourse.GdeNrll1EeSROyIACtiVvg.announcements%257Eopencourse.GdeNrll1EeSROyIACtiVvg.4xDVKzx5EeeJjRJrkGD1dA '
        '| access-date='
    ) == urls_scr(
        'https://arxiv.org/abs/1608.05006?utm_medium=email&utm_source='
        'other&utm_campaign=opencourse.GdeNrll1EeSROyIACtiVvg.'
        'announcements%257Eopencourse.GdeNrll1EeSROyIACtiVvg.'
        '4xDVKzx5EeeJjRJrkGD1dA'
    )[1][:-12]


def test_single_line_meta_tags():
    """Issue #9."""
    assert (
        "* {{cite web | last=Shoichet | first=Catherine E. | title=Spill spews tons of coal ash into North Carolina's Dan River | website=CNN | date=2014-02-09 | url=https://edition.cnn.com/2014/02/09/us/north-carolina-coal-ash-spill/ | access-date="
    ) == urls_scr(
        'https://edition.cnn.com/2014/02/09/us/north-carolina-coal-ash-spill/'
    )[1][:-12]


def test_abc_author():
    assert (
        '* {{cite web | last=Ferguson | first=Kathleen '
        '| title=Glow worms in Wollemi National Park survived Gospers Mountain bushfire '
        '| website=ABC News '
        '| date=2020-09-06 | url=https://www.abc.net.au/news/2020-09-06/'
        'glow-worms-in-wollemi-national-park-survived-summer-bushfire/'
        '12634762 | access-date='
    ) == urls_scr(
        'https://www.abc.net.au/news/2020-09-06/'
        'glow-worms-in-wollemi-national-park-survived-summer-bushfire/'
        '12634762'
    )[1][:-12]


def test_indaily():
    assert urls_scr(
        'https://indaily.com.au/news/2020/03/19/epidemics-expert-contradicts-marshalls-schools-advice/'
    )[1][:-12] == (
        '* {{cite web | last=Siebert | first=Bension '
        "| title=Epidemics expert questions Marshall's schools advice "
        '| website=InDaily | date=2020-03-19 '
        '| url=https://indaily.com.au/news/2020/03/19/epidemics-expert-contradicts-marshalls-schools-advice/ '
        '| access-date='
    )


def test_language_not_de_csbc():
    assert (
        '{{cite web '
        '| last=Martin '
        '| first=Emmie '
        '| title=In San Francisco, households earning $117,000 qualify as ‘low income’ '
        '| website=CNBC '
        '| date=2018-06-28 '
        '| url=https://www.cnbc.com/2018/06/28/families-earning-117000-qualify-as-low-income-in-san-francisco.html '
        '| access-date='
    ) == urls_scr(
        'https://www.cnbc.com/2018/06/28/families-earning-117000-qualify-as-low-income-in-san-francisco.html'
    )[1][2:-12]


def test_language_not_zh():
    assert (
        '{{cite web '
        '| last=Jonscher '
        '| first=Samantha '
        "| title=Malcolm Abbott's domestic violence past shows 'urgent action' required to support First Nations "
        '| website=ABC News '
        '| date=2022-05-14 '
        '| url=https://www.abc.net.au/news/2022-05-15/malcolm-abbott-domestic-violence-prevention-fails/101059440 '
        '| access-date='
    ) == urls_scr(
        'https://www.abc.net.au/news/2022-05-15/malcolm-abbott-domestic-violence-prevention-fails/101059440'
    )[1][2:-12]


def test_home_site_name():
    # this url does contain site name, but its homepage does
    assert (
        '* {{cite web | title=Black Convicts | website=University of Tasmania '
        '| url=https://www.utas.edu.au/library/companion_to_tasmanian_history/B/Black%20Convicts.htm '
        '| ref={{sfnref | University of Tasmania}} | access-date='
    ) == urls_scr(
        'https://www.utas.edu.au/library/companion_to_tasmanian_history/B/Black%20Convicts.htm'
    )[1][:-12]


def test_use_doi_if_available():
    assert urls_scr('https://pubmed.ncbi.nlm.nih.gov/32687126/')[1] == (
        '* {{cite journal | last=Ojewola | first=RufusWale | last2=Tijani | '
        'first2=KehindeHabeeb | last3=Fatuga | first3=AdedejiLukman | '
        'last4=Onyeze | first4=ChigozieInnocent | last5=Okeke | '
        'first5=ChikeJohn | title=Management of a giant prostatic '
        'enlargement: Case report and review of the literature | '
        'journal=Nigerian Postgraduate Medical Journal | publisher=Medknow | '
        'volume=27 | issue=3 | year=2020 | issn=1117-1936 | '
        'doi=10.4103/npmj.npmj_69_20 | doi-access=free | page=242}}'
    )


def test_dspace_publisher():  # 27
    assert urls_scr('https://repositorio.unesp.br/handle/11449/86528')[1][
        :-12
    ] == (
        '* {{cite web | last=J&uacute | first=Carvalho | title=A neve em Palmas/PR: '
        'da reconstituição histórica à abordagem dinâmica | publisher=Universidade '
        'Estadual Paulista (Unesp) | date=2004 | '
        'url=https://repositorio.unesp.br/handle/11449/86528 | language=pt | '
        'access-date='
    )


def test_find_website_meta_pipe():
    # https://meta.wikimedia.org/w/index.php?diff=prev&oldid=25155870
    scr = urls_scr(
        'https://zn.ua/ukr/war/ochilnik-khersonskoji-ova-serednij-riven-pidtoplennja-na-ranok-5-6-metra-evakujovano-majzhe-2-tisjachi-ljudej-.html'
    )
    assert scr[1][:-12] == (
        '* {{cite web | last=Хмілевська | first=Вікторія | title=Очільник Херсонської ОВА: Середній рівень підтоплення на ранок | website=Зеркало недели | date=2023-06-08 | url=https://zn.ua/ukr/war/ochilnik-khersonskoji-ova-serednij-riven-pidtoplennja-na-ranok-5-6-metra-evakujovano-majzhe-2-tisjachi-ljudej-.html | language=uk | access-date='
    )


def test_pipe_in_home_title_as_website():
    # https://meta.wikimedia.org/w/index.php?diff=next&oldid=25196965
    scr = urls_scr(
        'https://babel.ua/en/news/94854-russia-submitted-a-statement-against-ukraine-to-the-international-criminal-court-kyiv-is-accused-of-destroying-the-kakhovka-hpp'
    )
    assert scr[1][:-12] == (
        '* {{cite web | last=Telishevska | first=Sofiia | title=Russia submitted a statement against Ukraine to the International Criminal Court. Kyiv is accused of destroying the Kakhovka HPP | website=Бабель  | date=2023-06-08 | url=https://babel.ua/en/news/94854-russia-submitted-a-statement-against-ukraine-to-the-international-criminal-court-kyiv-is-accused-of-destroying-the-kakhovka-hpp | access-date='
    )


def test_lang_search():
    assert LANG_SEARCH('<html lang=en>')[1] == 'en'


@patch(
    'lib.urls.request', return_value=FakeResponse('', b'', 200, {}, 'utf-8')
)
@patch('lib.urls.check_response', side_effect=ContentTypeError)
def test_non_text_content(_0, _1):
    scr = urls_scr('https://example.com/')
    assert scr[1][:-12] == (
        '* {{cite web | title= | url=https://example.com/ | ref={{sfnref | Anon.}} | access-date='
    )


def test_find_title_meta_pipe():
    # https://meta.wikimedia.org/w/index.php?diff=prev&oldid=25155870
    scr = urls_scr(
        'https://www.wsj.com/articles/the-dangerous-denial-of-sex-11581638089'
    )
    assert scr[1][:-12] == (
        '* {{cite web | last=Wright | first=Colin M. | last2=Hilton | first2=Emma N. | title=The Dangerous Denial of Sex | website=WSJ | date=2020-02-13 | url=https://www.wsj.com/articles/the-dangerous-denial-of-sex-11581638089 | access-date='
    )


@patch('lib.urls.get_html', side_effect=CurlError('test'))
def test_citoid_thesis_invalid_doi(get_html: Mock):
    assert urls_scr('https://dl.acm.org/doi/10.5555/1123678')[1][:-12] == (
        '* {{cite thesis | degree=phd | last=Madden | first=Samuel Ross | title=The '
        'design and evaluation of a query processing architecture for sensor networks '
        '| publisher=University of California at Berkeley | publication-place=USA | '
        'date=2003 | url=https://dl.acm.org/doi/10.5555/1123678 '
        '| access-date='
    )
    get_html.assert_called_once()


@patch('lib.urls.request', side_effect=CurlError('<test>'))
def test__analyze_home_stream_request_raises_connect_error(_request_mock):
    assert _analyze_home(('https', 'example.com'), []) is None
