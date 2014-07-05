#!/data/project/yadkard/venv/bin/python3.2
# -*- coding: utf-8 -*-

import unittest
from pprint import pprint as p

import adinebook, googlebooks, noormags, noorlib
import doi, isbn

class AdinebookTest(unittest.TestCase):

    def test_ab1(self):
        """authors = 1, translators = 2, otheo = 1, isbn13"""
        i = 'http://www.adinebook.com/gp/product/9648165814/ref=sr_1_1000_42/905-6618179-9188955'
        o = adinebook.AdineBook(i)
        e = '* {{یادکرد کتاب|نام خانوادگی=لانسکی|نام=ویکی|ترجمه=فیروزه دالکی و مژگان امیرفروغی|دیگران= کی وایت (تصويرگر)|کتاب=101 راه برای اینکه پدر بهتری باشید|ناشر=پیک ادبیات|سال=1386|ماه=شهریور|شابک=978-964-8165-81-4|زبان=fa|تاریخ بازبینی='
        self.assertIn(e, o.cite)

    def test_ab2(self):
        """authors = 3, translators = 2, otheo = 0, isbn13"""
        i = 'http://www.adinebook.com/gp/product/9642823352/ref=sr_1_1000_41/905-6618179-9188955'
        o = adinebook.AdineBook(i)
        e = '* {{یادکرد کتاب|نام خانوادگی=کرسول|نام=جان|نام خانوادگی۲=کلارک|نام۲=ویکی پلانو|ترجمه=محسن نیازی و عباس زارعی|کتاب=روش های تحقیق تلفیقی|ناشر=علم و دانش|سال=1387|ماه=خرداد|شابک=978-964-2823-35-2|زبان=fa|تاریخ بازبینی='
        self.assertIn(e, o.cite)

    def test_ab3(self):
        """authors = 2, translators = 0, otheo = 4, isbn13"""
        i = 'http://www.adinebook.com/gp/product/6005883435'
        o = adinebook.AdineBook(i)
        e = '* {{یادکرد کتاب|نام خانوادگی=فخررحیمی|نام=علیرضا|نام خانوادگی۲=فخررحیمی|نام۲=الهام|دیگران= آرش نادرپور (مقدمه)،  امیر جابری (مقدمه)،  وحید شهبازیان (مقدمه) و  رضا مقدم (مقدمه)|کتاب=آموزش گام به گام پیکربندی مسیریابهای میکروتیک: آمادگی آزمون MTCNA|ناشر=نشرگستر|سال=1391|ماه=خرداد|شابک=978-600-5883-43-5|زبان=fa|تاریخ بازبینی='
        self.assertIn(e, o.cite)

    def test_ab4(self):
        """authors = 3, translators = 0, otheo = 0, isbn13"""
        i = 'http://www.adinebook.com/gp/product/9649563342/ref=ftr_1/905-6618179-9188955'
        o = adinebook.AdineBook(i)
        e = '* {{یادکرد کتاب|نام خانوادگی=کریمی|نام=نجمه|نام خانوادگی۲=یزدخواستی|نام۲=فروغ|نام خانوادگی۳=مختاری|نام۳=صفورا|کتاب=11 سپتامبر ... آرماگدون|ناشر=حدیث راه عشق|سال=1386|ماه=شهریور|شابک=978-964-95633-4-3|زبان=fa|تاریخ بازبینی='
        self.assertIn(e, o.cite)

    def test_ab5(self):
        """Year is interesting here."""
        i = 'http://www.adinebook.com/gp/product/9642656349/'
        o = adinebook.AdineBook(i)
        e = '* {{یادکرد کتاب|نام خانوادگی=نژاد|نام=یوسف علی یوسف|کتاب=فراهنجاری در مثنوی سرایی|ناشر=اردیبهشت|سال=1388|شابک=978-964-2656-34-9|زبان=fa|تاریخ بازبینی='
        self.assertIn(e, o.cite)

    def test_ab6(self):
        """Month and year detection."""
        i = 'http://www.adinebook.com/gp/product/9645300363/ref=pd_sim_b_title_4/905-6618179-9188955'
        o = adinebook.AdineBook(i)
        e = '* {{یادکرد کتاب|نام خانوادگی=مونس|نام=حسین|ترجمه=حمیدرضا شیخی|کتاب=تاریخ و تمدن مغرب|ناشر=سازمان مطالعه و تدوین کتب علوم انسانی دانشگاهها|سال=1392|ماه=شهریور|شابک=978-964-530-036-2|زبان=fa|تاریخ بازبینی='
        self.assertIn(e, o.cite)

    def test_ab7(self):
        """1 Editor."""
        i = 'http://www.adinebook.com/gp/product/9644593987/ref=pd_pos_b_title_4/905-6618179-9188955'
        o = adinebook.AdineBook(i)
        e = '* {{یادکرد کتاب|نام خانوادگی=دیماتیو|نام=ام.رابین|نام خانوادگی ویراستار=جباری|نام ویراستار=کریم|ترجمه=محمد کاویانی|دیگران= کیانوش هاشمیان (زيرنظر)|کتاب=روانشناسی سلامت به ضمیمه نگرشی بر منابع اسلامی|ناشر=سازمان مطالعه و تدوین کتب علوم انسانی دانشگاهها|سال=1389|ماه=دی|شابک=978-964-459-398-7|زبان=fa|تاریخ بازبینی='
        self.assertIn(e, o.cite)


class GooglebookTest(unittest.TestCase):

    def test_gb1(self):
        i = 'http://books.google.com/books?id=pzmt3pcBuGYC&pg=PR11&lpg=PP1&dq=digital+library'
        o = googlebooks.GoogleBook(i)
        e = '* {{یادکرد کتاب|نام خانوادگی=Arms|نام=W.Y.|کتاب=Digital Libraries|ناشر=MIT Press|سری=Digital libraries and electronic publishing|سال=2001|شابک=9780262261340|پیوند=http://books.google.com/books?id=pzmt3pcBuGYC&pg=PR11|زبان=en|تاریخ بازبینی='
        self.assertIn(e, o.cite)

    def test_gb2(self):
        """a book with more than 4 authors (10 authors)"""
        i = 'http://books.google.com/books?id=U46IzqYLZvAC&pg=PT57#v=onepage&q&f=false'
        o = googlebooks.GoogleBook(i)
        e1 = '<ref>{{پک|Anderson|DeBolt|Featherstone|Gunther|2010|ک=InterACT with Web Standards: A holistic approach to web design|زبان=en|ص=57}}</ref>'
        e2 = '* {{یادکرد کتاب|نام خانوادگی=Anderson|نام=E.|نام خانوادگی۲=DeBolt|نام۲=V.|نام خانوادگی۳=Featherstone|نام۳=D.|نام خانوادگی۴=Gunther|نام۴=L.|نام خانوادگی۵=Jacobs|نام۵=D.R.|نام خانوادگی۶=Mills|نام۶=C.|نام خانوادگی۷=Schmitt|نام۷=C.|نام خانوادگی۸=Sims|نام۸=G.|نام خانوادگی۹=Walter|نام۹=A.|نام خانوادگی۱۰=Jensen-Inman|نام۱۰=L.|کتاب=InterACT with Web Standards: A holistic approach to web design|ناشر=Pearson Education|سال=2010|شابک=9780132704908|پیوند=http://books.google.com/books?id=U46IzqYLZvAC&pg=PT57|زبان=en|تاریخ بازبینی='
        self.assertIn(e1, o.ref)
        self.assertIn(e2, o.cite)

    def test_gb3(self):
        """Non-ascii characters in title"""
        i = 'http://books.google.com/books?id=icMEAAAAQBAJ&pg=PA588&dq=%22a+Delimiter+is%22&hl=en&sa=X&ei=oNKSUrKeDovItAbO_4CoBA&ved=0CC4Q6AEwAA#v=onepage&q=%22a%20Delimiter%20is%22&f=false'
        o = googlebooks.GoogleBook(i)
        e1 = '<ref>{{پک|Farrell|ک=Microsoft® Visual C# 2008 Comprehensive: An Introduction to Object-Oriented Programming|زبان=en|ص=588}}</ref>'
        e2 = '* {{یادکرد کتاب|نام خانوادگی=Farrell|نام=J.|کتاب=Microsoft® Visual C# 2008 Comprehensive: An Introduction to Object-Oriented Programming|ناشر=Cengage Learning|شابک=9781111786199|پیوند=http://books.google.com/books?id=icMEAAAAQBAJ&pg=PA588|زبان=en|تاریخ بازبینی='
        self.assertIn(e1, o.ref)
        self.assertIn(e2, o.cite)

    def test_gb4(self):
        """Non-ascii characters in author's name."""
        i = 'http://books.google.com/books?id=i8nZjjo_9ikC&pg=PA229&dq=%22legal+translation+is%22&hl=en&sa=X&ei=hEuYUr_mOsnKswb49oDQCA&ved=0CC4Q6AEwAA#v=onepage&q=%22legal%20translation%20is%22&f=false'
        o = googlebooks.GoogleBook(i)
        e1 = '<ref>{{پک|Šarčević|1997|ک=New Approach to Legal Translation|زبان=en|ص=229}}</ref>'
        e2 = '* {{یادکرد کتاب|نام خانوادگی=Šarčević|نام=S.|کتاب=New Approach to Legal Translation|ناشر=Kluwer Law International|سال=1997|شابک=9789041104014|پیوند=http://books.google.com/books?id=i8nZjjo_9ikC&pg=PA229|زبان=en|تاریخ بازبینی='
        self.assertIn(e1, o.ref)
        self.assertIn(e2, o.cite)

        
class NoormagsTest(unittest.TestCase):

    def test_nm1(self):
        i = 'http://www.noormags.com/view/fa/articlepage/5798/102/Text'
        o = noormags.NoorMag(i)
        e = '* {{یادکرد ژورنال|نام خانوادگی=موسوی|نام=زهرا|عنوان=مقرنس در معماری|ژورنال=کتاب ماه هنر|شماره=45|سال=1381|صفحه=102–106|پیوند=http://www.noormags.com/view/fa/articlepage/104040|زبان=fa|تاریخ بازبینی='
        self.assertIn(e, o.cite)

    def test_nm2(self):
        i = 'http://www.noormags.com/view/fa/ArticlePage/454096'
        o = noormags.NoorMag(i)
        e = '* {{یادکرد ژورنال|عنوان=زندگی نامه علمی دکتر کاووس حسن لی|ژورنال=شعر|شماره=62|سال=1387|صفحه=17–19|پیوند=http://www.noormags.com/view/fa/articlepage/454096|زبان=fa|تاریخ بازبینی='
        self.assertIn(e, o.cite)

    def test_nm3(self):
        i = 'http://www.noormags.com/view/fa/articlepage/261461'
        o = noormags.NoorMag(i)
        e = '* {{یادکرد ژورنال|نام خانوادگی=ایرانی|نام=هوشنگ|نام خانوادگی۲=آ. ولف|نام۲=|عنوان=لوژیستیک|ژورنال=دانش|شماره=6|سال=1328|صفحه=316–324|پیوند=http://www.noormags.com/view/fa/articlepage/261461|زبان=fa|تاریخ بازبینی='
        self.assertIn(e, o.cite)


class NoorlibTest(unittest.TestCase):

    def test_nl1(self):
        i = 'http://www.noorlib.ir/View/fa/Book/BookView/Image/18879'
        o = noorlib.NoorLib(i)
        e = '* {{یادکرد کتاب|نام خانوادگی=مرتضی زبیدی|نام=محمد بن محمد|نام خانوادگی۲=شیری|نام۲=علی|کتاب=تاج العروس من جواهر القاموس|ناشر=دار الفکر|سری=تاج العروس من جواهر القاموس|جلد=10|سال=|پیوند=http://www.noorlib.ir/View/fa/Book/BookView/Image/18879|زبان=عربی|تاریخ بازبینی='
        self.assertIn(e, o.cite)


class DoiTest(unittest.TestCase):

    def test_di1(self):
        i = 'http://dx.doi.org/10.1038/nrd842'
        o = doi.Doi(i)
        e = '* {{یادکرد ژورنال|نام خانوادگی=Atkins|نام=Joshua H.|نام خانوادگی۲=Gershell|نام۲=Leland J.|عنوان=From the analysts couch: Selective anticancer drugs|ژورنال=Nature Reviews Drug Discovery|ناشر=Nature Publishing Group|جلد=1|شماره=7|سال=2002|ماه=Jul|صفحه=491–492|پیوند=http://dx.doi.org/10.1038/nrd842|doi=10.1038/nrd842|زبان=en|تاریخ بازبینی='
        self.assertIn(e, o.cite)

    def test_di2(self):
        '''DOI with unsafe characters (<>) Warning: this test fials a lot due
to "HTTPError: HTTP Error 500: Internal Server Error".
Also be aware that there was an &amp; entity which was manually substitute in
expected output'''

        i = '10.1002/(SICI)1097-0010(199604)70:4<422::AID-JSFA514>3.0.CO;2-5'
        o = doi.Doi(i, pure = True)
        e = '* {{یادکرد ژورنال|نام خانوادگی=Dian|نام=Noor Lida Habi Mat|نام خانوادگی۲=Sudin|نام۲=Nor’aini|نام خانوادگی۳=Yusoff|نام۳=Mohd Suria Affandi|عنوان=Characteristics of Microencapsulated Palm-Based Oil as Affected by Type of Wall Material|ژورنال=Journal of the Science of Food and Agriculture|ناشر=Wiley Blackwell (John Wiley &amp; Sons)|جلد=70|شماره=4|سال=1996|ماه=Apr|صفحه=422–426|پیوند=http://dx.doi.org/10.1002/(SICI)1097-0010(199604)70:4<422::AID-JSFA514>3.0.CO;2-5|doi=10.1002/(SICI)1097-0010(199604)70:4<422::AID-JSFA514>3.0.CO;2-5|زبان=en|تاریخ بازبینی='
        self.assertIn(e, o.cite)


class IsbnTest(unittest.TestCase):

    def test_is1(self):
        """not found in adinebook"""
        i = '9780349119168'
        o = isbn.Isbn(i, pure = True)
        e = '* {{یادکرد کتاب|نام خانوادگی=Adkins|نام=Roy|کتاب=The war for all the oceans : from Nelson at the Nile to Napoleon at Waterloo|ناشر=Abacus|سال=2007|شابک=9780349119168|زبان=en|تاریخ بازبینی='
        self.assertIn(e, o.cite)

    def test_is2(self):
        """not found in ottobib"""
        i = '978-964-6736-71-9'
        o = isbn.Isbn(i, pure = True)
        e = '* {{یادکرد کتاب|دیگران=بدیل بن علی خاقانی (شاعر)،  جهانگیر منصور (به اهتمام) و  بدیع الزمان فروزانفر (مقدمه)|کتاب=دیوان خاقانی شروانی|ناشر=نگاه|سال=1389|ماه=مرداد|شابک=978-964-6736-71-9|زبان=fa|تاریخ بازبینی='
        self.assertIn(e, o.cite)

    def test_is3(self):
        """exists in both"""
        i = '964-6736-34-3 '
        o = isbn.Isbn(i)
        e = '* {{یادکرد کتاب|دیگران=سحر معصومی (به اهتمام)|کتاب=راز گل سرخ: نقد و گزیده شعرهای سهراب سپهری|ناشر=نگاه|سال=1386|ماه=بهمن|شابک=964-6736-34-3|زبان=fa|تاریخ بازبینی='
        self.assertIn(e, o.cite) 

    def test_is4(self):
        """unpure isbn10"""
        i = 'choghondar 964-92962-6-3 شلغم'
        o = isbn.Isbn(i)
        e = '* {{یادکرد کتاب|نام خانوادگی=حافظ|نام=شمس الدین محمد|دیگران= رضا نظرزاده (به اهتمام)|کتاب=دیوان کامل حافظ همراه با فالنامه|ناشر=دیوان|سال=1385|ماه=آذر|شابک=964-92962-6-3|زبان=fa|تاریخ بازبینی='
        self.assertIn(e, o.cite)

if __name__ == '__main__':
    unittest.main()
