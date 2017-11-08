#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Test adinebook.py module."""


import unittest

from src import dummy_requests
from src import adinebook
from src.adinebook import adinehbook_sfn_cit_ref


class AdineBookTest(unittest.TestCase):

    def test_ab1(self):
        """authors = 1, translators = 2, otheo = 1, isbn13"""
        i = (
            'http://www.adinebook.com/gp/product/9648165814/'
            'ref=sr_1_1000_42/905-6618179-9188955'
        )
        o = adinehbook_sfn_cit_ref(i)
        e = (
            '* {{cite book '
            '| last=لانسکی '
            '| first=ویکی '
            '| others= کی وایت (تصويرگر), فیروزه دالکی (مترجم)'
            ', and مژگان امیرفروغی (مترجم) '
            '| title=101 راه برای اینکه پدر بهتری باشید '
            '| publisher=پیک ادبیات '
            '| year=1386 '
            '| isbn=978-964-8165-81-4 '
            '| language=fa '
            '| ref=harv'
        )
        self.assertIn(e, o[1])

    def test_ab2(self):
        """authors = 3, translators = 2, otheo = 0, isbn13"""
        i = (
            'http://www.adinebook.com/gp/product/9642823352/'
            'ref=sr_1_1000_41/905-6618179-9188955'
        )
        o = adinehbook_sfn_cit_ref(i)
        e = (
            '* {{cite book '
            '| last=کرسول '
            '| first=جان '
            '| last2=کلارک '
            '| first2=ویکی پلانو '
            '| others=محسن نیازی (مترجم), and عباس زارعی (مترجم) '
            '| title=روش های تحقیق تلفیقی '
            '| publisher=علم و دانش '
            '| year=1387 '
            '| isbn=978-964-2823-35-2 '
            '| language=fa '
            '| ref=harv'
        )
        self.assertIn(e, o[1])

    def test_ab3(self):
        """authors = 2, translators = 0, otheo = 4, isbn13"""
        i = 'http://www.adinebook.com/gp/product/6005883435'
        o = adinehbook_sfn_cit_ref(i)
        e = (
            '* {{cite book '
            '| last=فخررحیمی '
            '| first=علیرضا '
            '| last2=فخررحیمی '
            '| first2=الهام '
            '| others= آرش نادرپور (مقدمه),  امیر جابری (مقدمه)'
            ',  وحید شهبازیان (مقدمه), and  رضا مقدم (مقدمه) '
            '| title=آموزش گام به گام پیکربندی مسیریابهای میکروتیک'
            ': آمادگی آزمون MTCNA '
            '| publisher=نشرگستر '
            '| year=1391 '
            '| isbn=978-600-5883-43-5 '
            '| language=fa '
            '| ref=harv'
        )
        self.assertIn(e, o[1])

    def test_ab4(self):
        """authors = 3, translators = 0, otheo = 0, isbn13"""
        i = (
            'http://www.adinebook.com/gp/product/9649563342/'
            'ref=ftr_1/905-6618179-9188955'
        )
        o = adinehbook_sfn_cit_ref(i)
        e = (
            '* {{cite book '
            '| last=کریمی '
            '| first=نجمه '
            '| last2=یزدخواستی '
            '| first2=فروغ '
            '| last3=مختاری '
            '| first3=صفورا '
            '| title=11 سپتامبر ... آرماگدون '
            '| publisher=حدیث راه عشق '
            '| year=1386 '
            '| isbn=978-964-95633-4-3 '
            '| language=fa '
            '| ref=harv'
        )
        self.assertIn(e, o[1])

    def test_ab5(self):
        """Year is interesting here."""
        i = 'http://www.adinebook.com/gp/product/9642656349/'
        o = adinehbook_sfn_cit_ref(i)
        e = (
            '* {{cite book '
            '| last=نژاد '
            '| first=یوسف علی یوسف '
            '| title=فراهنجاری در مثنوی سرایی '
            '| publisher=اردیبهشت '
            '| year=1388 '
            '| isbn=978-964-2656-34-9 '
            '| language=fa '
            '| ref=harv'
        )
        self.assertIn(e, o[1])

    def test_ab6(self):
        """Month and year detection."""
        i = (
            'http://www.adinebook.com/gp/product/9645300363/'
            'ref=pd_sim_b_title_4/905-6618179-9188955'
        )
        o = adinehbook_sfn_cit_ref(i)
        e = (
            '* {{cite book '
            '| last=مونس '
            '| first=حسین '
            '| others=حمیدرضا شیخی (مترجم) '
            '| title=تاریخ و تمدن مغرب - جلد اول '
            '| publisher=سازمان مطالعه و تدوین کتب علوم انسانی دانشگاهها '
            '| year=1392 '
            '| isbn=978-964-530-036-2 '
            '| language=fa '
            '| ref=harv'
        )
        self.assertIn(e, o[1])

    def test_ab7(self):
        """1 Editor."""
        self.assertIn(
            '* {{cite book '
            '| last=دیماتیو '
            '| first=ام.رابین '
            '| editor-last=جباری '
            '| editor-first=کریم '
            '| others= کیانوش هاشمیان (زيرنظر), and محمد کاویانی (مترجم) '
            '| title=روانشناسی سلامت به ضمیمه نگرشی بر منابع اسلامی - جلد اول '
            '| publisher=سازمان مطالعه و تدوین کتب علوم انسانی دانشگاهها '
            '| year=1392 '
            '| isbn=978-964-459-398-7 '
            '| language=fa '
            '| ref=harv',
            adinehbook_sfn_cit_ref(
                'http://www.adinebook.com/gp/product/9644593987/'
                'ref=pd_pos_b_title_4/905-6618179-9188955'
            )[1],
        )


adinebook.requests_get = dummy_requests.DummyRequests().get
if __name__ == '__main__':
    unittest.main()
