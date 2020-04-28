#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Test noormags.py module."""


from unittest import main, TestCase

from lib.noormags import noormags_sfn_cit_ref


class NoormagsTest(TestCase):

    def test_nm2(self):
        """The second author does not have a last name. (Bibtex file error)"""
        i = 'http://www.noormags.ir/view/fa/articlepage/105489/' \
            '%d8%aa%d8%ad%d9%84%db%8c%d9%84-%d9%85%d9%86%d8%a7%d9%81%d8%b9-' \
            '%d8%a8%d9%87%d8%b1%d9%87-%d9%88%d8%b1%db%8c-' \
            '%d9%86%d8%a7%d8%b4%db%8c-%d8%a7%d8%b2-' \
            '%d8%a7%d8%b5%d9%84%d8%a7%d8%ad%d8%a7%d8%aa-' \
            '%d8%b5%d9%86%d8%b9%d8%aa-%d8%a8%d8%b1%d9%82-' \
            '%d8%a7%d8%b3%d8%aa%d8%b1%d8%a7%d9%84%db%8c%d8%a7--' \
            '%da%86%d8%a7%d8%b1%da%86%d9%88%d8%a8-%d9%87%d8%a7%db%8c-' \
            '%d8%b1%d9%88%d8%b4-%d8%b4%d9%86%d8%a7%d8%ae%d8%aa%db%8c?q=' \
            '%D8%A8%D8%B1%D9%82&score=21.639421&rownumber=1'
        o = noormags_sfn_cit_ref(i)
        e = (
            '* {{cite journal '
            '| last=فتح\u200cالله\u200cزاده\u200cاقدم '
            '| first=\u200cرضا '
            '| title=تحلیل منافع بهره وری ناشی'
            ' از اصلاحات صنعت برق استرالیا: چارچوب های روش شناختی '
            '| journal=مطالعات اقتصاد انرژی '
            '| issue=3 '
            '| year=1383 '
            '| pages=55–55 '
            '| url=http://www.noormags.ir/view/fa/articlepage/105489 '
            '| language=fa '
            '| access-date='
        )
        self.assertIn(e, o[1])

    def test_nm3(self):
        """Reftag check."""
        o = noormags_sfn_cit_ref(
            'http://www.noormags.ir/view/fa/articlepage/'
            '692447?sta=%D8%AF%D8%B9%D8%A7%DB%8C%20%D8%A7%D8%A8%D9%88%D8%AD%'
            'D9%85%D8%B2%D9%87%20%D8%AB%D9%85%D8%A7%D9%84%DB%8C'
        )
        self.assertIn(
            '{{sfn | سلیمانی\u200cمیمند | 1389 | pp=103–124}}', o[0]
        )
        self.assertIn(
            '* {{cite journal '
            '| last=سلیمانی\u200cمیمند '
            '| first=\u200cمریم '
            '| title=بررسی فضایل قرآنی در دعای ابوحمزه ثمالی '
            '| journal=بینات (موسسه معارف اسلامی امام رضا علیه السلام) '
            '| issue=68 '
            '| year=1389 '
            '| pages=103–124 '
            '| url=http://www.noormags.ir/view/fa/articlepage/692447 '
            '| language=fa '
            '| access-date=', o[1])
        self.assertIn(
            '&lt;ref name="سلیمانی\u200cمیمند 1389 pp. 103–124"&gt;'
            '{{cite journal '
            '| last=سلیمانی\u200cمیمند '
            '| first=\u200cمریم '
            '| title=بررسی فضایل قرآنی در دعای ابوحمزه ثمالی '
            '| journal=بینات (موسسه معارف اسلامی امام رضا علیه السلام) '
            '| issue=68 '
            '| year=1389 '
            '| pages=103–124 '
            '| url=http://www.noormags.ir/view/fa/articlepage/692447 '
            '| language=fa '
            '| access-date=', o[2])


if __name__ == '__main__':
    main()
