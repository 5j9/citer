from unittest import TestCase, main

from lib.isbn_oclc import isbn_scr, oclc_scr
from lib.commons import ISBN_10OR13_SEARCH


class IsbnTest(TestCase):

    def test_is1(self):
        """not found in ketabir"""
        self.assertIn((
            '* {{cite book '
            '| last=Adkins '
            '| first=Roy '
            '| title=The war for all the oceans : '
            'from Nelson at the Nile to Napoleon at Waterloo '
            '| publisher=Abacus '
            '| publication-place=London '
            '| year=2007 '
            '| isbn=978-0-349-11916-8 '
            '| oclc=137313052}}'
        ), isbn_scr('9780349119168', pure=True)[1])

    def test_is2(self):
        """not found in ottobib"""
        self.assertEqual(
            '* {{cite book | others=بدیل‌بن‌علی خاقانی (شاعر)'
            ', جهانگیر منصور (به‌اهتمام), and محمدحسن فروزانفر (مقدمه) '
            '| title=دیوان خاقانی شروانی | publisher=موسسه انتشارات نگاه '
            '| publication-place=تهران - تهران | year=1396 '
            '| isbn=978-964-6736-71-9 | language=fa | ref={{sfnref '
            '| موسسه انتشارات نگاه |'
            ' 1396}}}}',
            isbn_scr('978-964-6736-71-9', pure=True)[1]
        )

    def test_is3(self):
        """exists in both"""
        self.assertEqual((
            '* {{cite book | last=Sipihrī | first=Suhrāb '
            '| title=Rāz-i gul-i surkh '
            '| publisher=Muʼassasah-ʼi Intishārāt-i Nigāh '
            '| publication-place=Tihrān | year=1379 | isbn=964-6736-34-3 '
            '| oclc=53446327}}'
        ), isbn_scr('964-6736-34-3 ')[1])

    def test_is4(self):
        """unpure isbn10 not found in ottobib"""
        self.assertEqual((
            '* {{cite book | last=حافظ | first=شمس‌الدین‌محمد '
            '| others=رضا نظرزاده (به‌اهتمام) '
            '| title=دیوان کامل حافظ همراه با فالنامه | publisher=دیوان '
            '| publication-place=قم - قم | year=1385 | isbn=964-92962-6-3 '
            '| language=fa}}'
        ), isbn_scr('choghondar 964-92962-6-3 شلغم')[1])


class OCLCTest(TestCase):

    def test_oclc1(self):
        self.maxDiff = None
        self.assertEqual((
            '* {{cite book '
            '| last=Lewis '
            '| first=James Bryant '
            '| last2=Sesay '
            '| first2=Amadu '
            '| title=Korea and globalization :'
            ' politics, economics and culture '
            '| publisher=RoutledgeCurzon '
            '| year=2002 '
            '| isbn=0-7007-1512-6 '
            '| oclc=875039842}}'
        ), oclc_scr('875039842')[1])

    def test_elec_type_with_url(self):
        self.assertIn((
            "* {{cite web "
            "| last=Rahman "
            "| first=Mizanur "
            "| title=MediaWiki Administrators' Tutorial Guide "
            "| publisher=Packt Pub. "
            "| year=2007 "
            "| isbn=978-1-84719-045-1 "
            "| oclc=809771201 "
            "| url=http://public.eblib.com/choice/publicfullrecord.aspx?p="
            "995605 "
            "| access-date="
        ), oclc_scr('809771201')[1])

    def test_fullname_in_ris(self):
        self.assertEqual((
            '* {{cite book '
            '| author=Universidade Federal do Rio de Janeiro '
            '| title=Universidade do Brasil, 1948-1966 '
            '| year=1966 '
            '| oclc=24680975 '
            '| language=pt}}'
        ), oclc_scr('24680975')[1])

    def test_hyphened_isbn_match(self):  # 30
        self.assertTrue(ISBN_10OR13_SEARCH('2-253-00422-7'))


if __name__ == '__main__':
    main()
