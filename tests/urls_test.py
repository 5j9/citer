#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Test urls.py module."""


import unittest
import sys

import dummy_requests
sys.path.append('..')
import urls


class BostonTest(unittest.TestCase):

    def test_bg1(self):
        """boston.com, dateformat '%B %d, %Y'"""
        i = 'http://www.boston.com/cars/news-and-reviews/2014/06/28/hot-rod-stamps-google-road-prospectus/hylbVi9qonAwBIH10CwiDP/story.html'
        o = urls.Response(i, '%B %d, %Y')
        ct = '* {{cite web|last=Griffith|first=Bill|title=Hot Rod Stamps; Google on Road; A GM Prospectus|website=Boston.com|date=June 29, 2014|year=2014|url=http://www.boston.com/cars/news-and-reviews/2014/06/28/hot-rod-stamps-google-road-prospectus/hylbVi9qonAwBIH10CwiDP/story.html|ref=harv|accessdate='
        self.assertIn(ct, o.ctnt)

    def test_bg2(self):
        """bostonglobe.com"""
        i = 'http://www.bostonglobe.com/metro/2014/06/03/walsh-meets-with-college-leaders-off-campus-housing/lsxtLSGJMD86Gbkjay3D6J/story.html'
        o = urls.Response(i)
        ct = '* {{cite web|last=Saltzman|first=Jonathan|last2=Farragher|first2=Thomas|title=Walsh meets with college leaders on off-campus housing|website=BostonGlobe.com|date=2014-06-03|year=2014|url=https://www.bostonglobe.com/metro/2014/06/03/walsh-meets-with-college-leaders-off-campus-housing/lsxtLSGJMD86Gbkjay3D6J/story.html|ref=harv|accessdate='
        self.assertIn(ct, o.ctnt)

    def test_bg3(self):
        """bostonmagazine.com. Author tags return unrelated authors."""
        i = 'http://www.bostonmagazine.com/news/blog/2013/08/21/juliette-kayyem-jumps-in-for-guv/'
        o = urls.Response(i)
        ct = '* {{cite web|last=Bernstein|first=David S.|title=Juliette Kayyem Is Running for Governor of Massachusetts|website=Boston Magazine|date=2013-08-21|year=2013|url=http://www.bostonmagazine.com/news/blog/2013/08/21/juliette-kayyem-jumps-in-for-guv/|ref=harv|accessdate='
        self.assertIn(ct, o.ctnt)


class WashingtonpostTest(unittest.TestCase):

    def test_wp1(self):
        """`1 author, 2005, the pubdate is different from last edit date"""
        i = 'http://www.washingtonpost.com/wp-dyn/content/article/2005/09/02/AR2005090200822.html'
        o = urls.Response(i)
        e1 = '{{sfn|Sachs|2005}}'
        e2 = '* {{cite web|last=Sachs|first=Andrea|title=March of the Migration|website=Washington Post|date=2005-09-04|year=2005|url=http://www.washingtonpost.com/wp-dyn/content/article/2005/09/02/AR2005090200822.html|ref=harv|accessdate='
        self.assertIn(e1, o.sfnt)
        self.assertIn(e2, o.ctnt)


class HuffingtonpostTest(unittest.TestCase):

    def test_hp1(self):
        """`1 author, 2013"""
        i = 'http://www.huffingtonpost.ca/annelise-sorg/blackfish-killer-whale-seaworld_b_3686306.html'
        o = urls.Response(i)
        e1 = '{{sfn|Sorg|2013}}'
        e2 = '* {{cite web|last=Sorg|first=Annelise|title=When Killer Whales Kill: Why the movie "Blackfish" Should Sink Captive Whale Programs|website=The Huffington Post|date=2013-08-01|year=2013|url=http://www.huffingtonpost.ca/annelise-sorg/blackfish-killer-whale-seaworld_b_3686306.html|ref=harv|accessdate='
        self.assertIn(e1, o.sfnt)
        self.assertIn(e2, o.ctnt)

    def test_hp2(self):
        """`class:author` returns wrong result. Disallow `\n` in fullnames."""
        i = 'http://www.huffingtonpost.com/jeremy-rifkin/obamas-climate-change-plan_b_5427656.html'
        o = urls.Response(i)
        e1 = '{{sfn|Rifkin|2014}}'
        e2 = "* {{cite web|last=Rifkin|first=Jeremy|title=Beyond Obama's Plan: A New Economic Vision for Addressing Climate Change|website=The Huffington Post|date=2014-06-02|year=2014|url=http://www.huffingtonpost.com/jeremy-rifkin/obamas-climate-change-plan_b_5427656.html|ref=harv|accessdate="
        self.assertIn(e1, o.sfnt)
        self.assertIn(e2, o.ctnt)


class DilyTelegraphTest(unittest.TestCase):

    def test_dt1(self):
        """`1 author, 2005"""
        i = 'http://www.telegraph.co.uk/health/3334755/We-could-see-the-whales-eyes-mouth...-the-barnacles-on-its-back.html'
        o = urls.Response(i)
        e1 = '{{sfn|Fogle|2005}}'
        e2 = "* {{cite web|last=Fogle|first=Ben|title=We could see the whale's eyes, mouth... the barnacles on its back|website=Telegraph.co.uk|date=2005-12-22|year=2005|url=http://www.telegraph.co.uk/health/3334755/We-could-see-the-whales-eyes-mouth...-the-barnacles-on-its-back.html|ref=harv|accessdate="
        self.assertIn(e1, o.sfnt)
        self.assertIn(e2, o.ctnt)

    def test_dt2(self):
        """1 author, 2003"""
        i = 'http://www.telegraph.co.uk/science/science-news/3313298/Marine-collapse-linked-to-whale-decline.html'
        o = urls.Response(i)
        e1 = '{{sfn|Highfield|2003}}'
        e2 = "* {{cite web|last=Highfield|first=Roger|title=Marine 'collapse' linked to whale decline|website=Telegraph.co.uk|date=2003-09-29|year=2003|url=http://www.telegraph.co.uk/science/science-news/3313298/Marine-collapse-linked-to-whale-decline.html|ref=harv|accessdate="
        self.assertIn(e1, o.sfnt)
        self.assertIn(e2, o.ctnt)

    def test_dt3(self):
        """1 author, 2011"""
        i = 'http://www.telegraph.co.uk/science/8323909/The-sperm-whale-works-in-extraordinary-ways.html'
        o = urls.Response(i)
        e1 = '{{sfn|Whitehead|2011}}'
        e2 = "* {{cite web|last=Whitehead|first=Hal|title=The sperm whale works in extraordinary ways|website=Telegraph.co.uk|date=2011-02-15|year=2011|url=http://www.telegraph.co.uk/science/8323909/The-sperm-whale-works-in-extraordinary-ways.html|ref=harv|accessdate="
        self.assertIn(e1, o.sfnt)
        self.assertIn(e2, o.ctnt)


class DilyMirrorTest(unittest.TestCase):

    def test_dmr1(self):
        """no authors"""
        i = 'http://www.mirror.co.uk/news/uk-news/whale-doomed-to-die-557471'
        o = urls.Response(i)
        e1 = '{{sfn|Mirror.co.uk|2005}}'
        e2 = '* {{cite web|author=Mirror.co.uk|title=WHALE DOOMED TO DIE|website=mirror|date=2005-09-15|year=2005|url=http://www.mirror.co.uk/news/uk-news/whale-doomed-to-die-557471|ref=harv|accessdate='
        self.assertIn(e1, o.sfnt)
        self.assertIn(e2, o.ctnt)


class DilyMailTest(unittest.TestCase):

    def test_dm1(self):
        """4 authors"""
        i = 'http://www.dailymail.co.uk/news/article-2633025/London-cleric-convicted-NYC-terrorism-trial.html'
        o = urls.Response(i)
        e1 = '{{sfn|Malm|Witheridge|Drury|Bates|2014}}'
        e2 = '* {{cite web|last=Malm|first=Sara|last2=Witheridge|first2=Annette|last3=Drury|first3=Ian|last4=Bates|first4=Daniel|title=Hate preacher Abu Hamza GUILTY of setting up US terror training camps|website=Mail Online|date=2014-05-19|year=2014|url=http://www.dailymail.co.uk/news/article-2633025/London-cleric-convicted-NYC-terrorism-trial.html|ref=harv|accessdate='
        self.assertIn(e1, o.sfnt)
        self.assertIn(e2, o.ctnt)


class BbcTest(unittest.TestCase):

    def test_bbc1(self):
        """no authors"""
        i = 'https://www.bbc.com/news/world-asia-27653361'
        o = urls.Response(i)
        ct = "* {{cite web|title=US 'received Qatar assurances' on Afghan prisoner deal|website=BBC News|date=2014-06-01|year=2014|url=http://www.bbc.com/news/world-asia-27653361|ref={{sfnref|BBC News|2014}}|accessdate="
        self.assertIn(ct, o.ctnt)

    def test_bbc2(self):
        """1 author"""
        i = 'http://www.bbc.com/news/science-environment-23814524'
        o = urls.Response(i)
        ct = '* {{cite web|last=Gage|first=Suzi|title=Sea otter return boosts seagrass|website=BBC News|date=2013-08-26|year=2013|url=http://www.bbc.co.uk/news/science-environment-23814524|ref=harv|accessdate='
        self.assertIn(ct, o.ctnt)

    def test_bbc2(self):
        """https version of bbc2 (differs a lot!)"""
        i = 'https://www.bbc.com/news/science-environment-23814524'
        o = urls.Response(i)
        ct = '* {{cite web|last=Gage|first=Suzi|title=Sea otter return boosts ailing seagrass in California|website=BBC News|date=2013-08-26|year=2013|url=http://www.bbc.com/news/science-environment-23814524|ref=harv|accessdate='
        self.assertIn(ct, o.ctnt)

    def test_bbc4(self):
        """news.bbc.co.uk, 1 author"""
        i = 'http://news.bbc.co.uk/2/hi/programmes/newsnight/5178122.stm'
        o = urls.Response(i)
        ct = "* {{cite web|last=Jones|first=Meirion|title=Malaria advice 'risks lives'|website=BBC NEWS|date=2006-07-13|year=2006|url=http://news.bbc.co.uk/2/hi/programmes/newsnight/5178122.stm|ref=harv|accessdate="
        self.assertIn(ct, o.ctnt)

    def test_bbc5(self):
        """news.bbc.co.uk, 1 author"""
        i = 'http://news.bbc.co.uk/2/hi/business/2570109.stm'
        o = urls.Response(i)
        ct = "* {{cite web|last=Madslien|first=Jorn|title=Inside the Bentley factory|website=BBC NEWS|date=2002-12-24|year=2002|url=http://news.bbc.co.uk/2/hi/business/2570109.stm|ref=harv|accessdate="
        self.assertIn(ct, o.ctnt)

    def test_bbc6(self):
        """bbc.com, 1 author"""
        i = 'http://www.bbc.com/news/science-environment-26267918'
        o = urls.Response(i)
        ct = "* {{cite web|last=Amos|first=Jonathan|title=Europe picks Plato planet-hunter|website=BBC News|date=2014-02-20|year=2014|url=http://www.bbc.com/news/science-environment-26267918|ref=harv|accessdate="
        self.assertIn(ct, o.ctnt)

        
class NytTest(unittest.TestCase):

    def test_nyt1(self):
        """newstylct, 1 author"""
        i = 'http://www.nytimes.com/2014/05/30/business/international/on-the-internet-the-right-to-forget-vs-the-right-to-know.html?hp&_r=0'
        o = urls.Response(i)
        ct = '* {{cite web|last=Hakim|first=Danny|title=Right to Be Forgotten? Not That Easy|website=The New York Times|date=2014-05-29|year=2014|url=http://www.nytimes.com/2014/05/30/business/international/on-the-internet-the-right-to-forget-vs-the-right-to-know.html|ref=harv|accessdate='
        self.assertIn(ct, o.ctnt)

    def test_nyt2(self):
        """newstylct, 2 authors"""
        i = 'http://www.nytimes.com/2014/05/31/sports/basketball/steven-a-ballmers-2-billion-play-for-clippers-is-a-big-bet-on-the-nba.html?hp'
        o = urls.Response(i)
        ct = '* {{cite web|last=Belson|first=Ken|last2=Sandomir|first2=Richard|title=$2 Billion for Clippers? In Time, It May Be a Steal for Steve Ballmer|website=The New York Times|date=2014-05-30|year=2014|url=http://www.nytimes.com/2014/05/31/sports/basketball/steven-a-ballmers-2-billion-play-for-clippers-is-a-big-bet-on-the-nba.html|ref=harv|accessdate='
        self.assertIn(ct, o.ctnt)

    def test_nyt3(self):
        """oldstylct, 1 author"""
        i = 'http://www.nytimes.com/2007/12/25/world/africa/25kenya.html'
        o = urls.Response(i)
        ct = '* {{cite web|last=Gettleman|first=Jeffrey|title=Election Rules Complicate Kenya Race|website=The New York Times|date=2007-12-25|year=2007|url=http://www.nytimes.com/2007/12/25/world/africa/25kenya.html|ref=harv|accessdate='
        self.assertIn(ct, o.ctnt)

    def test_nyt4(self):
        """newstylct, 2 authors, only byline"""
        i = 'http://dealbook.nytimes.com/2014/05/30/insider-trading-inquiry-includes-mickelson-and-icahn/'
        o = urls.Response(i)
        ct = '* {{cite web|last=Goldstein|first=Matthew|last2=Protess|first2=Ben|title=Investor, Bettor, Golfer: Insider Trading Inquiry Includes Mickelson, Icahn and William T. Walters|website=DealBook|date=2014-05-30|year=2014|url=http://dealbook.nytimes.com/2014/05/30/insider-trading-inquiry-includes-mickelson-and-icahn/|ref=harv|accessdate='
        self.assertIn(ct, o.ctnt)

    def test_nyt5(self):
        """special case for date format (not in usual meta tags)"""
        i = 'http://www.nytimes.com/2007/06/13/world/americas/13iht-whale.1.6123654.html'
        o = urls.Response(i)
        ct = '* {{cite web|title=19th-century harpoon gives clue on whales|website=The New York Times|date=2007-06-13|year=2007|url=http://www.nytimes.com/2007/06/13/world/americas/13iht-whale.1.6123654.html|ref={{sfnref|The New York Times|2007}}|accessdate='
        self.assertIn(ct, o.ctnt)

    def test_nyt5(self):
        """lastname=O'Connor"""
        i = 'http://www.nytimes.com/2003/10/09/us/adding-weight-to-suspicion-sonar-is-linked-to-whale-deaths.html'
        o = urls.Response(i)
        ct = "* {{cite web|last=O'Connor|first=Anahad|title=Adding Weight to Suspicion, Sonar Is Linked to Whale Deaths|website=The New York Times|date=2003-10-09|year=2003|url=http://www.nytimes.com/2003/10/09/us/adding-weight-to-suspicion-sonar-is-linked-to-whale-deaths.html|ref=harv|accessdate="
        self.assertIn(ct, o.ctnt)
        

class TGDaily(unittest.TestCase):

    def test_tgd1(self):
        """Apparently two authors, but only one of them is valid."""
        i = 'http://www.tgdaily.com/sustainability-features/79712-are-more-wind-turbines-the-answer'
        o = urls.Response(i)
        ct = '* {{cite web|last=Danko|first=Pete|title=Are more wind turbines the answer?|website=TG Daily|date=2013-09-16|year=2013|url=http://www.tgdaily.com/sustainability-features/79712-are-more-wind-turbines-the-answer|ref=harv|accessdate='
        self.assertIn(ct, o.ctnt)

    def test_tgd2(self):
        """Hard to find author and date."""
        i = 'http://www.tgdaily.com/web/100381-apple-might-buy-beats-for-32-billion'
        o = urls.Response(i)
        ct = '* {{cite web|last=Wright|first=Guy|title=Apple might buy Beats for $3.2 billion|website=TG Daily|date=2014-05-09|year=2014|url=http://www.tgdaily.com/web/100381-apple-might-buy-beats-for-32-billion|ref=harv|accessdate='
        self.assertIn(ct, o.ctnt)

    def test_tgd3(self):
        """"Staff" in author name."""
        i = 'http://www.tgdaily.com/space-features/82906-sma-reveals-giant-star-cluster-in-the-making'
        o = urls.Response(i)
        ct = '* {{cite web|title=SMA reveals giant star cluster in the making|website=TG Daily|date=2013-12-17|year=2013|url=http://www.tgdaily.com/space-features/82906-sma-reveals-giant-star-cluster-in-the-making|ref={{sfnref|TG Daily|2013}}|accessdate='
        self.assertIn(ct, o.ctnt)


@unittest.skip
class NotWorking(unittest.TestCase):
    def test_tgd1(self):
        """ABCNews. Wrong author: |last=News|first=ABC."""
        i = 'http://abcnews.go.com/blogs/headlines/2006/12/saddam_executed/'
        o = urls.Response(i)
        ct = '* {{cite web|last=Ross|first=Brian|title=Saddam Executed; An Era Comes to an End|website=ABC News Blogs|date=2006-12-30|year=2006|url=http://abcnews.go.com/blogs/headlines/2006/12/saddam_executed/|ref=harv|accessdate='
        self.assertIn(ct, o.ctnt)

    def test_oth12(self):
        """Times of India, author could not be detected."""
        i = 'http://timesofindia.indiatimes.com/city/pune/UK-allows-working-visas-for-Indian-students/articleshow/1163528927.cms?'
        o = urls.Response(i)
        sfnt = "{{sfn|Kashyap|2001}}"
        self.assertIn(sfnt, o.sfnt)


class Others(unittest.TestCase):

    def test_oth1(self):
        """Get title by hometitle comparison."""
        i = 'http://www.ensani.ir/fa/content/326173/default.aspx'
        o = urls.Response(i)
        ct = '* {{cite web|last=جلیلیان|first=شهرام|last2=نیا|first2=امیر علی|title=ورود کاسی ها به میان رودان و پیامدهای آن|website=پرتال جامع علوم انسانی|date=2014-05-20|year=2014|url=http://www.ensani.ir/fa/content/326173/default.aspx|language=fa|ref=harv|accessdate='
        self.assertIn(ct, o.ctnt)

    def test_oth2(self):
        """Byline through body search."""
        i = 'https://www.eff.org/deeplinks/2014/06/sudan-tech-sanctions-harm-innovation-development-us-government-and-corporations-must-act'
        o = urls.Response(i)
        ct = '* {{cite web|last=Carlson|first=Kimberly|last2=York|first2=Jillian|title=Sudan Tech Sanctions Harm Innovation and Development: US Government and Corporations Must Act|website=Electronic Frontier Foundation|date=2014-06-26|year=2014|url=https://www.eff.org/deeplinks/2014/06/sudan-tech-sanctions-harm-innovation-development-us-government-and-corporations-must-act|ref=harv|accessdate='
        self.assertIn(ct, o.ctnt)

    def test_oth3(self):
        """3 authors."""
        i = 'http://arstechnica.com/science/2007/09/the-pseudoscience-behind-homeopathy/'
        o = urls.Response(i)
        ct = '* {{cite web|last=Timmer|first=John|last2=Ford|first2=Matt|last3=Lee|first3=Chris|last4=Gitlin|first4=Jonathan|title=Diluting the scientific method:  Ars looks at homeopathy|website=Ars Technica|date=2007-09-12|year=2007|url=http://arstechnica.com/science/2007/09/the-pseudoscience-behind-homeopathy/|ref=harv|accessdate='
        self.assertIn(ct, o.ctnt)

    def test_oth4(self):
        """rel="author" tag contains invalid information."""
        i = 'http://www.livescience.com/46619-sterile-neutrino-experiment-beginning.html?cmpid=514645_20140702_27078936'
        o = urls.Response(i)
        ct = "* {{cite web|last=Ghose|first=Tia|title='Revolutionary' Physics: Do Sterile Neutrinos Lurk in the Universe?|website=LiveScience.com|date=2014-07-02|year=2014|url=http://www.livescience.com/46619-sterile-neutrino-experiment-beginning.html|ref=harv|accessdate="
        self.assertIn(ct, o.ctnt)

    def test_oth5(self):
        """Getting the date is tricky here."""
        i = 'http://www.magiran.com/npview.asp?ID=1410487'
        o = urls.Response(i)
        sf = "{{sfn|نوري|2007}}"
        ct = "* {{cite web|last=نوري|first=آزاده شهمير|title=روزنامه سرمايه86/3/1: دكتر طاهر صباحي، محقق و مجموعه دار فرش: بازار جهاني با توليد فرش هنري نصيب ايران مي شود|website=magiran.com|date=2007-05-22|year=2007|url=http://www.magiran.com/npview.asp?ID=1410487|language=fa|ref=harv|accessdate="
        self.assertIn(sf, o.sfnt)
        self.assertIn(ct, o.ctnt)

    def test_oth6(self):
        """Detection of website name."""
        i = 'http://www.farsnews.com/newstext.php?nn=13930418000036'
        o = urls.Response(i)
        sf = "{{sfn|''Fars News Agency''|2014}}"
        ct = "* {{cite web|title=آیت‌الله محمدی گیلانی دارفانی را وداع گفت|website=Fars News Agency|date=2014-07-09|year=2014|url=http://www.farsnews.com/newstext.php?nn=13930418000036|language=fa|ref={{sfnref|Fars News Agency|2014}}|accessdate="
        self.assertIn(sf, o.sfnt)
        self.assertIn(ct, o.ctnt)

    def test_oth7(self):
        """Contains a By Topic line and also the byline contains '|'."""
        i = 'http://newsoffice.mit.edu/2014/traffic-lights-theres-a-better-way-0707'
        o = urls.Response(i)
        ct = "* {{cite web|last=Chandler|first=David L.|title=Traffic lights: There’s a better way|website=MIT News Office|date=2014-07-07|year=2014|url=http://newsoffice.mit.edu/2014/traffic-lights-theres-a-better-way-0707|ref=harv|accessdate="
        self.assertIn(ct, o.ctnt)

    def test_oth8(self):
        """Two authors from guardian that are mentions in other tags, too."""
        i = 'http://www.theguardian.com/world/2014/jul/14/israel-drone-launched-gaza-ashdod'
        o = urls.Response(i)
        ct = '* {{cite web|last=Beaumont|first=Peter|last2=Crowcroft|first2=Orlando|title=Israel says it has shot down drone launched from Gaza|website=the Guardian|date=2014-07-14|year=2014|url=http://www.theguardian.com/world/2014/jul/14/israel-drone-launched-gaza-ashdod|ref=harv|accessdate='
        self.assertIn(ct, o.ctnt)

    def test_oth9(self):
        """Author in str(soup)."""
        i = 'http://www.defense.gov/News/NewsArticle.aspx?ID=18509'
        o = urls.Response(i)
        ct = "* {{cite web|last=Garamone|first=Jim|title=Defense.gov News Article: Prison Stands as Testament to Saddam's Evil|website=United States Department of Defense (defense.gov)|date=2005-12-17|year=2005|url=http://www.defense.gov/News/NewsArticle.aspx?ID=18509|ref=harv|accessdate="
        self.assertIn(ct, o.ctnt)

    def test_oth10(self):
        """The Times. (Authors found by "byline" css selector)"""
        i = 'http://www.thetimes.co.uk/tto/news/world/australia-newzealand/article4151214.ece'
        o = urls.Response(i)
        ct = "* {{cite web|last=Lagan|first=Bernard|last2=Charter|first2=David|title=Woman who lost brother on MH370 mourns relatives on board MH17|website=The Times|date=2014-07-17|year=2014|url=http://www.thetimes.co.uk/tto/news/world/australia-newzealand/article4151214.ece|ref=harv|accessdate="
        self.assertIn(ct, o.ctnt)

    def test_oth11(self):
        """businessnewsdaily."""
        i = 'http://www.businessnewsdaily.com/6762-male-female-entrepreneurs.html?cmpid=514642_20140715_27858876'
        o = urls.Response(i)
        ct = "* {{cite web|last=Helmrich|first=Brittney|title=Male vs. Female Entrepreneurs: How Are They Different?|website=BusinessNewsDaily.com|date=2014-07-15|year=2014|url=http://www.businessnewsdaily.com/6762-male-female-entrepreneurs.html|ref=harv|accessdate="
        self.assertIn(ct, o.ctnt)

    def test_oth12(self):
        """thebulletin.org"""
        i = 'http://thebulletin.org/evidence-shows-iron-dome-not-working7318'
        o = urls.Response(i)
        ct = "* {{cite web|last=Postol|first=Theodore A.|title=The evidence that shows Iron Dome is not working|website=Bulletin of the Atomic Scientists|date=2014-01-14|year=2014|url=http://thebulletin.org/evidence-shows-iron-dome-not-working7318|ref=harv|accessdate="
        self.assertIn(ct, o.ctnt)

    def test_oth13(self):
        """thebulletin.org"""
        i = 'http://www.highbeam.com/doc/1P3-3372742961.html'
        o = urls.Response(i)
        ct = "* {{cite web|last=Martin|first=Tracy|title=Dynamometers Explained|website=HighBeam Research|date=10 Nov 2014|year=2014|url=http://www.highbeam.com/doc/1P3-3372742961.html|ref=harv|accessdate="
        self.assertIn(ct, o.ctnt)

        
urls.requests = dummy_requests.DummyRequests()
if __name__ == '__main__':
    unittest.main()
