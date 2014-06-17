#!/data/project/yadkard/venv/bin/python
# -*- coding: utf-8 -*-

import unittest
from pprint import pprint as p

import adinebook, googlebooks, noormags, noorlib, nyt, bbc, dailymail, mirror,\
       telegraph, huffingtonpost, washingtonpost, boston
import doi, isbn


class BostonTest(unittest.TestCase):

    def test_bg1(self):
        """boston.com"""
        i = 'http://www.boston.com/health/2014/06/02/companies-offer-health-plans-new-hampshire/GmmhqI6s4GmTlMWN3HBLnM/story.html'
        o = boston.Citation(i)
        e = u'* {{cite web|last=Ramer|first=Holly|title=5 companies to offer health plans in New Hampshire|website=The Boston Globe|date=2014-06-02|year=2014|url=http://www.boston.com/health/2014/06/02/companies-offer-health-plans-new-hampshire/GmmhqI6s4GmTlMWN3HBLnM/story.html|ref=harv|accessdate='
        self.assertIn(e, o.cite)

    def test_bg2(self):
        """bostonglobe.com"""
        i = 'http://www.bostonglobe.com/metro/2014/06/03/walsh-meets-with-college-leaders-off-campus-housing/lsxtLSGJMD86Gbkjay3D6J/story.html'
        o = boston.Citation(i)
        e = u'* {{cite web|last=Saltzman|first=Jonathan|last2=Farragher|first2=Thomas|title=Walsh meets with college leaders on off-campus housing|website=The Boston Globe|date=2014-06-03|year=2014|url=http://www.bostonglobe.com/metro/2014/06/03/walsh-meets-with-college-leaders-off-campus-housing/lsxtLSGJMD86Gbkjay3D6J/story.html|ref=harv|accessdate='
        self.assertIn(e, o.cite)
        

class WashingtonpostTest(unittest.TestCase):

    def test_wp1(self):
        """`1 author, 2005, the pubdate is different from last edit date"""
        i = 'http://www.washingtonpost.com/wp-dyn/content/article/2005/09/02/AR2005090200822.html'
        o = washingtonpost.Citation(i)
        e1 = u'{{sfn|Sachs|2005}}'
        e2 = u'* {{cite web|last=Sachs|first=Andrea|title=March of the Migration|website=The Washingtonpost Post|date=2005-09-04|year=2005|url=http://www.washingtonpost.com/wp-dyn/content/article/2005/09/02/AR2005090200822.html|ref=harv|accessdate='
        self.assertIn(e1, o.ref)
        self.assertIn(e2, o.cite)


class HuffingtonpostTest(unittest.TestCase):

    def test_hp1(self):
        """`1 author, 2013"""
        i = 'http://www.huffingtonpost.ca/annelise-sorg/blackfish-killer-whale-seaworld_b_3686306.html'
        o = huffingtonpost.Citation(i)
        e1 = u'{{sfn|Sorg|2013}}'
        e2 = u'* {{cite web|last=Sorg|first=Annelise|title=When Killer Whales Kill: Why the movie "Blackfish" Should Sink Captive Whale Programs|website=The Huffington Post|date=2013-08-01|year=2013|url=http://www.huffingtonpost.ca/annelise-sorg/blackfish-killer-whale-seaworld_b_3686306.html|ref=harv|accessdate='
        self.assertIn(e1, o.ref)
        self.assertIn(e2, o.cite)


class DilyTelegraphTest(unittest.TestCase):

    def test_dt1(self):
        """`1 author, 2005"""
        i = 'http://www.telegraph.co.uk/health/3334755/We-could-see-the-whales-eyes-mouth...-the-barnacles-on-its-back.html'
        o = telegraph.Citation(i)
        e1 = u'{{sfn|Fogle|2005}}'
        e2 = u"* {{cite web|last=Fogle|first=Ben|title=We could see the whale's eyes, mouth... the barnacles on its back|website=The Daily Telegraph|date=2005-12-22|year=2005|url=http://www.telegraph.co.uk/health/3334755/We-could-see-the-whales-eyes-mouth...-the-barnacles-on-its-back.html|ref=harv|accessdate="
        self.assertIn(e1, o.ref)
        self.assertIn(e2, o.cite)


class DilyMirrorTest(unittest.TestCase):

    def test_dm1(self):
        """no authors"""
        i = 'http://www.mirror.co.uk/news/uk-news/whale-doomed-to-die-557471'
        o = mirror.Citation(i)
        e1 = u'{{sfn|Daily Mirror|2005}}'
        e2 = u'* {{cite web|title=WHALE DOOMED TO DIE|website=Daily Mirror|date=2005-09-15|year=2005|url=http://www.mirror.co.uk/news/uk-news/whale-doomed-to-die-557471|ref={{sfnref|Daily Mirror|2005}}|accessdate='
        self.assertIn(e1, o.ref)
        self.assertIn(e2, o.cite)


class DilyMailTest(unittest.TestCase):

    def test_dm1(self):
        """4 authors"""
        i = 'http://www.dailymail.co.uk/news/article-2633025/London-cleric-convicted-NYC-terrorism-trial.html'
        o = dailymail.Citation(i)
        e1 = u'{{sfn|Malm|Witheridge|Drury|Bates|2014}}'
        e2 = u'* {{cite web|last=Malm|first=Sara|last2=Witheridge|first2=Annette|last3=Drury|first3=Ian|last4=Bates|first4=Daniel|title=Hate preacher Abu Hamza GUILTY of setting up US terror training camps|website=Daily Mail|date=2014-05-20|year=2014|url=http://www.dailymail.co.uk/news/article-2633025/London-cleric-convicted-NYC-terrorism-trial.html|ref=harv|accessdate='
        self.assertIn(e1, o.ref)
        self.assertIn(e2, o.cite)
        

class BbcTest(unittest.TestCase):

    def test_bbc1(self):
        """no authors"""
        i = 'https://www.bbc.com/news/world-asia-27653361'
        o = bbc.Citation(i)
        e = u"* {{cite web|title=US 'received Qatar assurances' on Afghan prisoner deal|website=BBC|date=2014-06-01|year=2014|url=https://www.bbc.com/news/world-asia-27653361|ref={{sfnref|BBC|2014}}|accessdate="
        self.assertIn(e, o.cite)

    def test_bbc2(self):
        """1 author"""
        i = 'https://www.bbc.com/news/science-environment-23814524'
        o = bbc.Citation(i)
        e = u'* {{cite web|last=Gage|first=Suzi|title=Sea otter return boosts ailing seagrass in California|website=BBC|date=2013-08-26|year=2013|url=https://www.bbc.com/news/science-environment-23814524|ref=harv|accessdate='
        self.assertIn(e, o.cite)

    def test_bbc3(self):
        """1 author"""
        i = 'https://www.bbc.com/news/science-environment-23814524'
        o = bbc.Citation(i)
        e = u'* {{cite web|last=Gage|first=Suzi|title=Sea otter return boosts ailing seagrass in California|website=BBC|date=2013-08-26|year=2013|url=https://www.bbc.com/news/science-environment-23814524|ref=harv|accessdate='
        self.assertIn(e, o.cite)
        
    def test_bbc4(self):
        """news.bbc.co.uk, 1 author"""
        i = 'http://news.bbc.co.uk/2/hi/programmes/newsnight/5178122.stm'
        o = bbc.Citation(i)
        e = u"* {{cite web|last=Jones|first=Meirion|title=Malaria advice 'risks lives'|website=BBC|date=2006-07-13|year=2006|url=http://news.bbc.co.uk/2/hi/programmes/newsnight/5178122.stm|ref=harv|accessdate="
        self.assertIn(e, o.cite)
        
class NytTest(unittest.TestCase):

    def test_nyt1(self):
        """newstyle, 1 author"""
        i = 'http://www.nytimes.com/2014/05/30/business/international/on-the-internet-the-right-to-forget-vs-the-right-to-know.html?hp&_r=0'
        o = nyt.Citation(i)
        e = u'* {{cite web|last=Hakim|first=Danny|title=Right to Be Forgotten? Not That Easy|website=The New York Times|date=2014-05-29|year=2014|url=http://www.nytimes.com/2014/05/30/business/international/on-the-internet-the-right-to-forget-vs-the-right-to-know.html?hp&_r=0|ref=harv|accessdate='
        self.assertIn(e, o.cite)

    def test_nyt2(self):
        """newstyle, 2 authors"""
        i = 'http://www.nytimes.com/2014/05/31/sports/basketball/steven-a-ballmers-2-billion-play-for-clippers-is-a-big-bet-on-the-nba.html?hp'
        o = nyt.Citation(i)
        e = u'* {{cite web|last=Belson|first=Ken|last2=Sandomir|first2=Richard|title=$2 Billion for Clippers? In Time, It May Be a Steal for Steve Ballmer|website=The New York Times|date=2014-05-30|year=2014|url=http://www.nytimes.com/2014/05/31/sports/basketball/steven-a-ballmers-2-billion-play-for-clippers-is-a-big-bet-on-the-nba.html?hp|ref=harv|accessdate='
        self.assertIn(e, o.cite)

    def test_nyt3(self):
        """oldstyle, 1 author"""
        i = 'http://www.nytimes.com/2007/12/25/world/africa/25kenya.html'
        o = nyt.Citation(i)
        e = u'* {{cite web|last=Gettleman|first=Jeffrey|title=Election Rules Complicate Kenya Race|website=The New York Times|date=2007-12-25|year=2007|url=http://www.nytimes.com/2007/12/25/world/africa/25kenya.html|ref=harv|accessdate='
        self.assertIn(e, o.cite)

    def test_nyt4(self):
        """newstyle, 2 authors, only byline"""
        i = 'http://dealbook.nytimes.com/2014/05/30/insider-trading-inquiry-includes-mickelson-and-icahn/'
        o = nyt.Citation(i)
        e = u'* {{cite web|last=Goldstein|first=Matthew|last2=Protess|first2=Ben|website=The New York Times|date=2014-05-30|year=2014|url=http://dealbook.nytimes.com/2014/05/30/insider-trading-inquiry-includes-mickelson-and-icahn/|ref=harv|accessdate='
        self.assertIn(e, o.cite)

    def test_nyt5(self):
        """special case for date format (not in usual meta tags)"""
        i = 'http://www.nytimes.com/2007/06/13/world/americas/13iht-whale.1.6123654.html'
        o = nyt.Citation(i)
        e = u'* {{cite web|website=The New York Times|date=2007-06-13|year=2007|url=http://www.nytimes.com/2007/06/13/world/americas/13iht-whale.1.6123654.html|ref={{sfnref|The New York Times|2007}}|accessdate='
        self.assertIn(e, o.cite)
        

class AdinebookTest(unittest.TestCase):

    def test_ab1(self):
        """authors = 1, translators = 2, otheo = 1, isbn13"""
        i = 'http://www.adinebook.com/gp/product/9648165814/ref=sr_1_1000_42/905-6618179-9188955'
        o = adinebook.Citation(i)
        e = u'* {{cite book|last=لانسکی|first=ویکی|others= کی وایت (تصويرگر), فیروزه دالکی (مترجم), and مژگان امیرفروغی (مترجم)|title=101 راه برای اینکه پدر بهتری باشید|publisher=پیک ادبیات|year=1386|isbn=978-964-8165-81-4|language=fa|ref=harv'
        self.assertIn(e, o.cite)

    def test_ab2(self):
        """authors = 3, translators = 2, otheo = 0, isbn13"""
        i = 'http://www.adinebook.com/gp/product/9642823352/ref=sr_1_1000_41/905-6618179-9188955'
        o = adinebook.Citation(i)
        e = u'* {{cite book|last=کرسول|first=جان|last2=کلارک|first2=ویکی پلانو|others=محسن نیازی (مترجم), and عباس زارعی (مترجم)|title=روش های تحقیق تلفیقی|publisher=علم و دانش|year=1387|isbn=978-964-2823-35-2|language=fa|ref=harv'
        self.assertIn(e, o.cite)

    def test_ab3(self):
        """authors = 2, translators = 0, otheo = 4, isbn13"""
        i = 'http://www.adinebook.com/gp/product/6005883435'
        o = adinebook.Citation(i)
        e = u'* {{cite book|last=فخررحیمی|first=علیرضا|last2=فخررحیمی|first2=الهام|others= آرش نادرپور (مقدمه),  امیر جابری (مقدمه),  وحید شهبازیان (مقدمه), and  رضا مقدم (مقدمه)|title=آموزش گام به گام پیکربندی مسیریابهای میکروتیک: آمادگی آزمون MTCNA|publisher=نشرگستر|year=1391|isbn=978-600-5883-43-5|language=fa|ref=harv'
        self.assertIn(e, o.cite)

    def test_ab4(self):
        """authors = 3, translators = 0, otheo = 0, isbn13"""
        i = 'http://www.adinebook.com/gp/product/9649563342/ref=ftr_1/905-6618179-9188955'
        o = adinebook.Citation(i)
        e = u'* {{cite book|last=کریمی|first=نجمه|last2=یزدخواستی|first2=فروغ|last3=مختاری|first3=صفورا|title=11 سپتامبر ... آرماگدون|publisher=حدیث راه عشق|year=1386|isbn=978-964-95633-4-3|language=fa|ref=harv'
        self.assertIn(e, o.cite)

    def test_ab5(self):
        """Year is interesting here."""
        i = 'http://www.adinebook.com/gp/product/9642656349/'
        o = adinebook.Citation(i)
        e = u'* {{cite book|last=نژاد|first=یوسف علی یوسف|title=فراهنجاری در مثنوی سرایی|publisher=اردیبهشت|year=1388|isbn=978-964-2656-34-9|language=fa|ref=harv'
        self.assertIn(e, o.cite)

    def test_ab6(self):
        """Month and year detection."""
        i = 'http://www.adinebook.com/gp/product/9645300363/ref=pd_sim_b_title_4/905-6618179-9188955'
        o = adinebook.Citation(i)
        e = u'* {{cite book|last=مونس|first=حسین|others=حمیدرضا شیخی (مترجم)|title=تاریخ و تمدن مغرب|publisher=سازمان مطالعه و تدوین کتب علوم انسانی دانشگاهها|year=1392|isbn=978-964-530-036-2|language=fa|ref=harv'
        self.assertIn(e, o.cite)

    def test_ab7(self):
        """1 Editor."""
        i = 'http://www.adinebook.com/gp/product/9644593987/ref=pd_pos_b_title_4/905-6618179-9188955'
        o = adinebook.Citation(i)
        e = u'* {{cite book|last=دیماتیو|first=ام.رابین|editor-last=جباری|editor-first=کریم|others= کیانوش هاشمیان (زيرنظر), and محمد کاویانی (مترجم)|title=روانشناسی سلامت به ضمیمه نگرشی بر منابع اسلامی|publisher=سازمان مطالعه و تدوین کتب علوم انسانی دانشگاهها|year=1389|isbn=978-964-459-398-7|language=fa|ref=harv'
        self.assertIn(e, o.cite)


class GooglebooksTest(unittest.TestCase):

    def test_gb1(self):
        i = 'http://books.google.com/books?id=pzmt3pcBuGYC&pg=PR11&lpg=PP1&dq=digital+library'
        o = googlebooks.Citation(i)
        e = u'* {{cite book|last=Arms|first=W.Y.|title=Digital Libraries|publisher=MIT Press|series=Digital libraries and electronic publishing|year=2000|isbn=9780262261340|url=http://books.google.com/books?id=pzmt3pcBuGYC&pg=PR11|ref=harv|accessdate='
        self.assertIn(e, o.cite)

    def test_gb2(self):
        """a book with more than 4 authors (10 authors)"""
        i = 'http://books.google.com/books?id=U46IzqYLZvAC&pg=PT57#v=onepage&q&f=false'
        o = googlebooks.Citation(i)
        e1 = u'{{sfn|Anderson|DeBolt|Featherstone|Gunther|2010|p=57}}'
        e2 = u'* {{cite book|last=Anderson|first=E.|last2=DeBolt|first2=V.|last3=Featherstone|first3=D.|last4=Gunther|first4=L.|last5=Jacobs|first5=D.R.|last6=Mills|first6=C.|last7=Schmitt|first7=C.|last8=Sims|first8=G.|last9=Walter|first9=A.|last10=Jensen-Inman|first10=L.|title=InterACT with Web Standards: A holistic approach to web design|publisher=Pearson Education|year=2010|isbn=9780132704908|url=http://books.google.com/books?id=U46IzqYLZvAC&pg=PT57|ref=harv|accessdate='
        self.assertIn(e1, o.ref)
        self.assertIn(e2, o.cite)

    def test_gb3(self):
        """Non-ascii characters in title (Some of them where removed later)"""
        i = 'http://books.google.com/books?id=icMEAAAAQBAJ&pg=PA588&dq=%22a+Delimiter+is%22&hl=en&sa=X&ei=oNKSUrKeDovItAbO_4CoBA&ved=0CC4Q6AEwAA#v=onepage&q=%22a%20Delimiter%20is%22&f=false'
        o = googlebooks.Citation(i)
        e1 = u'{{sfn|Farrell|2009|p=588}}'
        e2 = u'* {{cite book|last=Farrell|first=J.|title=Microsoft Visual C# 2008 Comprehensive: An Introduction to Object-Oriented Programming|publisher=Cengage Learning|year=2009|isbn=9781111786199|url=http://books.google.com/books?id=icMEAAAAQBAJ&pg=PA588|ref=harv|accessdate='
        self.assertIn(e1, o.ref)
        self.assertIn(e2, o.cite)

    def test_gb4(self):
        """Non-ascii characters in author's name."""
        i = 'http://books.google.com/books?id=i8nZjjo_9ikC&pg=PA229&dq=%22legal+translation+is%22&hl=en&sa=X&ei=hEuYUr_mOsnKswb49oDQCA&ved=0CC4Q6AEwAA#v=onepage&q=%22legal%20translation%20is%22&f=false'
        o = googlebooks.Citation(i)
        e1 = u'{{sfn|Šarčević|1997|p=229}}'
        e2 = u'* {{cite book|last=Šarčević|first=S.|title=New Approach to Legal Translation|publisher=Kluwer Law International|year=1997|isbn=9789041104014|url=http://books.google.com/books?id=i8nZjjo_9ikC&pg=PA229|ref=harv|accessdate='
        self.assertIn(e1, o.ref)
        self.assertIn(e2, o.cite)

        
class NoormagsTest(unittest.TestCase):

    def test_nm1(self):
        i = 'http://www.noormags.com/view/fa/articlepage/5798/102/Text'
        o = noormags.Citation(i)
        e = u'* {{cite journal|last=موسوی|first=زهرا|title=مقرنس در معماری|journal=کتاب ماه هنر|issue=45|year=1381|pages=102–106|url=http://www.noormags.com/view/fa/articlepage/104040|language=fa|ref=harv|accessdate='
        self.assertIn(e, o.cite)

    def test_nm3(self):
        i = 'http://www.noormags.com/view/fa/articlepage/261461'
        o = noormags.Citation(i)
        e = u'* {{cite journal|last=ایرانی|first=هوشنگ|last2=آ. ولف|first2=|title=لوژیستیک|journal=دانش|issue=6|year=1328|pages=316–324|url=http://www.noormags.com/view/fa/articlepage/261461|language=fa|ref=harv|accessdate='
        self.assertIn(e, o.cite)


class NoorlibTest(unittest.TestCase):

    def test_nl1(self):
        i = 'http://www.noorlib.ir/View/fa/Book/BookView/Image/18879'
        o = noorlib.Citation(i)
        e = u'* {{cite book|last=مرتضی زبیدی|first=محمد بن محمد|last2=شیری|first2=علی|title=تاج العروس من جواهر القاموس|publisher=دار الفکر|series=تاج العروس من جواهر القاموس|volume=10|year=|url=http://www.noorlib.ir/View/fa/Book/BookView/Image/18879|language=عربی|ref=harv|accessdate='
        self.assertIn(e, o.cite)


class DoiTest(unittest.TestCase):

    def test_di1(self):
        i = 'http://dx.doi.org/10.1038/nrd842'
        o = doi.Citation(i)
        e = u'* {{cite journal|last=Atkins|first=Joshua H.|last2=Gershell|first2=Leland J.|title=From the analyst’s couch: Selective anticancer drugs|journal=Nat. Rev. Drug Disc.|publisher=Nature Publishing Group|volume=1|issue=7|year=2002|pages=491–492|url=http://dx.doi.org/10.1038/nrd842|doi=10.1038/nrd842|ref=harv|accessdate='
        self.assertIn(e, o.cite)

    def test_di2(self):
        '''DOI with unsafe characters (<>)

Warning: this test fials a lot due to "HTTPError: HTTP Error 500: Internal
Server Error". Also be aware that there was an &amp; entity which was manually substitute in
expected output
'''
        i = '10.1002/(SICI)1097-0010(199604)70:4<422::AID-JSFA514>3.0.CO;2-5'
        o = doi.Citation(i, pure = True)
        e = u'* {{cite journal|last=Dian|first=Noor Lida Habi Mat|last2=Sudin|first2=Nor\u2019aini|last3=Yusoff|first3=Mohd Suria Affandi|title=Characteristics of Microencapsulated Palm-Based Oil as Affected by Type of Wall Material|journal=J. Sci. Food Agric.|publisher=Wiley-Blackwell|volume=70|issue=4|year=1996|pages=422\u2013426|url=http://dx.doi.org/10.1002/(SICI)1097-0010(199604)70:4<422::AID-JSFA514>3.0.CO;2-5|doi=10.1002/(sici)1097-0010(199604)70:4<422::aid-jsfa514>3.0.co;2-5|ref=harv|accessdate='
        self.assertIn(e, o.cite)


class IsbnTest(unittest.TestCase):

    def test_is1(self):
        """not found in adinebook"""
        i = '9780349119168'
        o = isbn.Citation(i, pure = True)
        e = u'* {{cite book|last=Adkins|first=Roy|title=The war for all the oceans : from Nelson at the Nile to Napoleon at Waterloo|publisher=Abacus|year=2007|isbn=9780349119168|ref=harv'
        self.assertIn(e, o.cite)

    def test_is2(self):
        """not found in ottobib"""
        i = '978-964-6736-71-9'
        o = isbn.Citation(i, pure = True)
        e = u'* {{cite book|others=بدیل بن علی خاقانی (شاعر),  جهانگیر منصور (به اهتمام), and  بدیع الزمان فروزانفر (مقدمه)|title=دیوان خاقانی شروانی|publisher=نگاه|year=1389|isbn=978-964-6736-71-9|language=fa|ref={{sfnref|نگاه|1389}}'
        self.assertIn(e, o.cite)

    def test_is3(self):
        """exists in both"""
        i = '964-6736-34-3 '
        o = isbn.Citation(i)
        e = u'* {{cite book|others=سحر معصومی (به اهتمام)|title=راز گل سرخ: نقد و گزیده شعرهای سهراب سپهری|publisher=نگاه|year=1386|isbn=964-6736-34-3|language=fa|ref={{sfnref|نگاه|1386}}'
        self.assertIn(e, o.cite)
        
    def test_is4(self):
        """unpure isbn10 not found in ottobib"""
        i = 'choghondar 964-92962-6-3 شلغم'
        o = isbn.Citation(i)
        e = u'* {{cite book|last=حافظ|first=شمس الدین محمد|others= رضا نظرزاده (به اهتمام)|title=دیوان کامل حافظ همراه با فالنامه|publisher=دیوان|year=1385|isbn=964-92962-6-3|language=fa|ref=harv'
        self.assertIn(e, o.cite)

if __name__ == '__main__':
    unittest.main()
