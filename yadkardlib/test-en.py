#! /usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from pprint import pprint as p

import adinebook, googlebooks, noormags, noorlib
import doi, isbn

class AdinebookTest(unittest.TestCase):

    def test_ab1(self):
        '''authors = 1, translators = 2, otheo = 1, isbn13'''
        i = 'http://www.adinebook.com/gp/product/9648165814/ref=sr_1_1000_42/905-6618179-9188955'
        o = adinebook.AdineBook(i)
        e = u'* {{cite book|last=لانسکی|first=ویکی|others= کی وایت (تصويرگر), فیروزه دالکی (مترجم), and مژگان امیرفروغی (مترجم)|title=101 راه برای اینکه پدر بهتری باشید|publisher=پیک ادبیات|year=1386|isbn=978-964-8165-81-4|language=fa|ref=harv|accessdate='
        self.assertIn(e, o.cite)

    def test_ab2(self):
        '''authors = 3, translators = 2, otheo = 0, isbn13'''
        i = 'http://www.adinebook.com/gp/product/9642823352/ref=sr_1_1000_41/905-6618179-9188955'
        o = adinebook.AdineBook(i)
        e = u'* {{cite book|last=کرسول|first=جان|last2=کلارک|first2=ویکی پلانو|others=محسن نیازی (مترجم), and عباس زارعی (مترجم)|title=روش های تحقیق تلفیقی|publisher=علم و دانش|year=1387|isbn=978-964-2823-35-2|language=fa|ref=harv|accessdate='
        self.assertIn(e, o.cite)

    def test_ab3(self):
        '''authors = 2, translators = 0, otheo = 4, isbn13'''
        i = 'http://www.adinebook.com/gp/product/6005883435'
        o = adinebook.AdineBook(i)
        e = u'* {{cite book|last=فخررحیمی|first=علیرضا|last2=فخررحیمی|first2=الهام|others= آرش نادرپور (مقدمه),  امیر جابری (مقدمه),  وحید شهبازیان (مقدمه), and  رضا مقدم (مقدمه)|title=آموزش گام به گام پیکربندی مسیریابهای میکروتیک: آمادگی آزمون MTCNA|publisher=نشرگستر|year=1391|isbn=978-600-5883-43-5|language=fa|ref=harv|accessdate='
        self.assertIn(e, o.cite)

    def test_ab4(self):
        '''authors = 3, translators = 0, otheo = 0, isbn13'''
        i = 'http://www.adinebook.com/gp/product/9649563342/ref=ftr_1/905-6618179-9188955'
        o = adinebook.AdineBook(i)
        e = u'* {{cite book|last=کریمی|first=نجمه|last2=یزدخواستی|first2=فروغ|last3=مختاری|first3=صفورا|title=11 سپتامبر ... آرماگدون|publisher=حدیث راه عشق|year=1386|isbn=978-964-95633-4-3|language=fa|ref=harv|accessdate='
        self.assertIn(e, o.cite)

    def test_ab5(self):
        '''Year is interesting here.'''
        i = 'http://www.adinebook.com/gp/product/9642656349/'
        o = adinebook.AdineBook(i)
        e = u'* {{cite book|last=نژاد|first=یوسف علی یوسف|title=فراهنجاری در مثنوی سرایی|publisher=اردیبهشت|year=1388|isbn=978-964-2656-34-9|language=fa|ref=harv|accessdate='
        self.assertIn(e, o.cite)

    def test_ab6(self):
        '''Month and year detection.'''
        i = 'http://www.adinebook.com/gp/product/9645300363/ref=pd_sim_b_title_4/905-6618179-9188955'
        o = adinebook.AdineBook(i)
        e = u'* {{cite book|last=مونس|first=حسین|others=حمیدرضا شیخی (مترجم)|title=تاریخ و تمدن مغرب|publisher=سازمان مطالعه و تدوین کتب علوم انسانی دانشگاهها|year=1392|isbn=978-964-530-036-2|language=fa|ref=harv|accessdate='
        self.assertIn(e, o.cite)

    def test_ab7(self):
        '''1 Editor.'''
        i = 'http://www.adinebook.com/gp/product/9644593987/ref=pd_pos_b_title_4/905-6618179-9188955'
        o = adinebook.AdineBook(i)
        e = u'* {{cite book|last=دیماتیو|first=ام.رابین|editor-last=جباری|editor-first=کریم|others= کیانوش هاشمیان (زيرنظر), and محمد کاویانی (مترجم)|title=روانشناسی سلامت به ضمیمه نگرشی بر منابع اسلامی|publisher=سازمان مطالعه و تدوین کتب علوم انسانی دانشگاهها|year=1389|isbn=978-964-459-398-7|language=fa|ref=harv|accessdate='
        self.assertIn(e, o.cite)


class GooglebookTest(unittest.TestCase):

    def test_gb1(self):
        i = 'http://books.google.com/books?id=pzmt3pcBuGYC&pg=PR11&lpg=PP1&dq=digital+library'
        o = googlebooks.GoogleBook(i)
        e = u'* {{cite book|last=Arms|first=W.Y.|title=Digital Libraries|publisher=MIT Press|series=Digital libraries and electronic publishing|year=2001|isbn=9780262261340|url=http://books.google.com/books?id=pzmt3pcBuGYC&pg=PR11|language=en|ref=harv|accessdate='
        self.assertIn(e, o.cite)

    def test_gb2(self):
        '''a book with more than 4 authors (10 authors)'''
        i = 'http://books.google.com/books?id=U46IzqYLZvAC&pg=PT57#v=onepage&q&f=false'
        o = googlebooks.GoogleBook(i)
        e1 = u'{{sfn|Anderson|DeBolt|Featherstone|Gunther|2010|p=57}}'
        e2 = u'* {{cite book|last=Anderson|first=E.|last2=DeBolt|first2=V.|last3=Featherstone|first3=D.|last4=Gunther|first4=L.|last5=Jacobs|first5=D.R.|last6=Mills|first6=C.|last7=Schmitt|first7=C.|last8=Sims|first8=G.|last9=Walter|first9=A.|last10=Jensen-Inman|first10=L.|title=InterACT with Web Standards: A holistic approach to web design|publisher=Pearson Education|year=2010|isbn=9780132704908|url=http://books.google.com/books?id=U46IzqYLZvAC&pg=PT57|language=en|ref=harv|accessdate='
        self.assertIn(e1, o.ref)
        self.assertIn(e2, o.cite)

    def test_gb3(self):
        '''Non-ascii characters in title'''
        i = 'http://books.google.com/books?id=icMEAAAAQBAJ&pg=PA588&dq=%22a+Delimiter+is%22&hl=en&sa=X&ei=oNKSUrKeDovItAbO_4CoBA&ved=0CC4Q6AEwAA#v=onepage&q=%22a%20Delimiter%20is%22&f=false'
        o = googlebooks.GoogleBook(i)
        e1 = u'{{sfn|Farrell|p=588}}'
        e2 = u'* {{cite book|last=Farrell|first=J.|title=Microsoft\xae Visual C# 2008 Comprehensive: An Introduction to Object-Oriented Programming|publisher=Cengage Learning|isbn=9781111786199|url=http://books.google.com/books?id=icMEAAAAQBAJ&pg=PA588|language=en|ref=harv|accessdate='
        self.assertIn(e1, o.ref)
        self.assertIn(e2, o.cite)

    def test_gb4(self):
        '''Non-ascii characters in author's name.'''
        i = 'http://books.google.com/books?id=i8nZjjo_9ikC&pg=PA229&dq=%22legal+translation+is%22&hl=en&sa=X&ei=hEuYUr_mOsnKswb49oDQCA&ved=0CC4Q6AEwAA#v=onepage&q=%22legal%20translation%20is%22&f=false'
        o = googlebooks.GoogleBook(i)
        e1 = u'{{sfn|Šarčević|1997|p=229}}'
        e2 = u'* {{cite book|last=Šarčević|first=S.|title=New Approach to Legal Translation|publisher=Kluwer Law International|year=1997|isbn=9789041104014|url=http://books.google.com/books?id=i8nZjjo_9ikC&pg=PA229|language=en|ref=harv|accessdate='
        self.assertIn(e1, o.ref)
        self.assertIn(e2, o.cite)

        
class NoormagsTest(unittest.TestCase):

    def test_nm1(self):
        i = 'http://www.noormags.com/view/fa/articlepage/5798/102/Text'
        o = noormags.NoorMag(i)
        e = u'* {{cite journal|last=موسوی|first=زهرا|title=مقرنس در معماری|journal=کتاب ماه هنر|issue=45|year=1381|pages=102–106|url=http://www.noormags.com/view/fa/articlepage/104040|language=fa|ref=harv|accessdate='
        self.assertIn(e, o.cite)

    def test_nm3(self):
        i = 'http://www.noormags.com/view/fa/articlepage/261461'
        o = noormags.NoorMag(i)
        e = u'* {{cite journal|last=ایرانی|first=هوشنگ|last2=آ. ولف|first2=|title=لوژیستیک|journal=دانش|issue=6|year=1328|pages=316–324|url=http://www.noormags.com/view/fa/articlepage/261461|language=fa|ref=harv|accessdate='
        self.assertIn(e, o.cite)


class NoorlibTest(unittest.TestCase):

    def test_nl1(self):
        i = 'http://www.noorlib.ir/View/fa/Book/BookView/Image/18879'
        o = noorlib.NoorLib(i)
        e = u'* {{cite book|last=مرتضی زبیدی|first=محمد بن محمد|last2=شیری|first2=علی|title=تاج العروس من جواهر القاموس|publisher=دار الفکر|series=تاج العروس من جواهر القاموس|volume=10|year=|url=http://www.noorlib.ir/View/fa/Book/BookView/Image/18879|language=عربی|ref=harv|accessdate='
        self.assertIn(e, o.cite)


class DoiTest(unittest.TestCase):

    def test_di1(self):
        i = 'http://dx.doi.org/10.1038/nrd842'
        o = doi.Doi(i)
        e = u'* {{cite journal|last=Atkins|first=Joshua H.|last2=Gershell|first2=Leland J.|title=From the analysts couch: Selective anticancer drugs|journal=Nature Reviews Drug Discovery|publisher=Nature Publishing Group|volume=1|issue=7|year=2002|pages=491–492|url=http://dx.doi.org/10.1038/nrd842|doi=10.1038/nrd842|language=en|ref=harv|accessdate='
        self.assertIn(e, o.cite)

    def test_di2(self):
        '''DOI with unsafe characters (<>) Warning: this test fials a lot due
to "HTTPError: HTTP Error 500: Internal Server Error".
Also be aware that there was an &amp; entity which was manually substitute in
expected output'''

        i = '10.1002/(SICI)1097-0010(199604)70:4<422::AID-JSFA514>3.0.CO;2-5'
        o = doi.Doi(i, pure = True)
        e = u'* {{cite journal|last=Dian|first=Noor Lida Habi Mat|last2=Sudin|first2=Nor’aini|last3=Yusoff|first3=Mohd Suria Affandi|title=Characteristics of Microencapsulated Palm-Based Oil as Affected by Type of Wall Material|journal=Journal of the Science of Food and Agriculture|publisher=Wiley Blackwell (John Wiley &amp; Sons)|volume=70|issue=4|year=1996|pages=422–426|url=http://dx.doi.org/10.1002/(SICI)1097-0010(199604)70:4<422::AID-JSFA514>3.0.CO;2-5|doi=10.1002/(SICI)1097-0010(199604)70:4<422::AID-JSFA514>3.0.CO;2-5|language=en|ref=harv|accessdate='
        self.assertIn(e, o.cite)


class IsbnTest(unittest.TestCase):

    def test_is1(self):
        '''not found in adinebook'''
        i = '9780349119168'
        o = isbn.Isbn(i, pure = True)
        e = u'* {{cite book|last=Adkins|first=Roy|title=The war for all the oceans : from Nelson at the Nile to Napoleon at Waterloo|publisher=Abacus|year=2007|isbn=9780349119168|language=en|ref=harv|accessdate='
        self.assertIn(e, o.cite)

    def test_is2(self):
        '''not found in ottobib'''
        i = '978-964-6736-71-9'
        o = isbn.Isbn(i, pure = True)
        e = u'* {{cite book|others=بدیل بن علی خاقانی (شاعر),  جهانگیر منصور (به اهتمام), and  بدیع الزمان فروزانفر (مقدمه)|title=دیوان خاقانی شروانی|publisher=نگاه|year=1389|isbn=978-964-6736-71-9|language=fa|ref={{sfnref|دیوان خاقانی شروانی|1389}}|accessdate='
        self.assertIn(e, o.cite)

    def test_is3(self):
        '''exists in both'''
        i = '964-6736-34-3 '
        o = isbn.Isbn(i)
        e = u'* {{cite book|others=سحر معصومی (به اهتمام)|title=راز گل سرخ: نقد و گزیده شعرهای سهراب سپهری|publisher=نگاه|year=1386|isbn=964-6736-34-3|language=fa|ref={{sfnref|راز گل سرخ: نقد و گزیده شعرهای سهراب سپهری|1386}}|accessdate='
        self.assertIn(e, o.cite)
        
    def test_is4(self):
        '''unpure isbn10 not found in ottobib'''
        i = 'choghondar 964-92962-6-3 شلغم'
        o = isbn.Isbn(i)
        e = u'* {{cite book|last=حافظ|first=شمس الدین محمد|others= رضا نظرزاده (به اهتمام)|title=دیوان کامل حافظ همراه با فالنامه|publisher=دیوان|year=1385|isbn=964-92962-6-3|language=fa|ref=harv|accessdate='
        self.assertIn(e, o.cite)

if __name__ == '__main__':
    unittest.main()
