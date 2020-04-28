#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Test noorlib.py module."""


from unittest import main, TestCase

from lib.noorlib import noorlib_sfn_cit_ref


class NoorlibTest(TestCase):

    def test_nl1(self):
        i = 'http://www.noorlib.ir/View/fa/Book/BookView/Image/6120'
        o = noorlib_sfn_cit_ref(i)
        e = (
            '* {{cite book '
            '| last=رشید یاسمی '
            '| first=غلامرضا '
            '| last2=کریستن سن '
            '| first2=آرتور امانویل '
            '| title=ایران در زمان ساسانیان: تاریخ ایران ساسانی تا'
            ' حمله عرب و وضع دولت و ملت در زمان ساسانیان '
            '| publisher=دنیای کتاب '
            '| publication-place=تهران - ایران '
            '| series=ایران در زمان ساسانیان: تاریخ ایران ساسانی تا'
            ' حمله عرب و وضع دولت و ملت در زمان ساسانیان '
            '| volume=1 '
            '| year=1368 '
            '| url=http://www.noorlib.ir/View/fa/Book/BookView/Image/6120 '
            '| language=فارسی '
            '| access-date='
        )
        self.assertIn(e, o[1])

    def test_nl2(self):
        """The year parameter is not present."""
        i = 'http://www.noorlib.ir/View/fa/Book/BookView/Image/18454'
        o = noorlib_sfn_cit_ref(i)
        self.assertIn('{{sfn | کورانی | p=}}', o[0])
        self.assertIn(
            '* {{cite book '
            '| last=کورانی '
            '| first=علی '
            '| title=المعجم الموضوعی لاحادیث '
            'الامام المهدی عجل الله تعالی فرجه الشریف '
            '| publisher=دار المرتضی '
            '| publication-place=بيروت '
            '| series=المعجم الموضوعي لإحادیث'
            ' الإمام المهدي (عجل الله فرجه الشریف) '
            '| volume=1 '
            '| url=http://www.noorlib.ir/View/fa/Book/BookView/Image/18454 '
            '| language=عربی '
            '| access-date=',
            o[1],
        )


if __name__ == '__main__':
    main()
