from unittest import main, TestCase

from lib.jstor import jstor_scr


class JSTORTest(TestCase):

    def test_1(self):
        ae = self.assertEqual
        s, c, r = jstor_scr('https://www.jstor.org/stable/30078788')
        ae(s, '{{sfn | Lloyd | 1831 | pp=171–177}}')
        ae(c[:c.index('| access-date=')], (
            '* {{cite journal | last=Lloyd | first=Humphrey '
            '| title=On a New Case of Interference of the Rays of Light '
            '| publisher=Royal Irish Academy | volume=17 | year=1831 '
            '| pages=171–177 '
            '| url=http://www.jstor.org/stable/30078788 '))

    def test_2(self):
        s, c, r = jstor_scr('https://www.jstor.org/stable/resrep26363.7?Search=yes&resultItemClick=true&searchText=google&searchUri=%2Faction%2FdoBasicSearch%3FQuery%3Dgoogle%26acc%3Doff%26wc%3Don%26fc%3Doff%26group%3Dnone%26refreqid%3Dsearch%253A2e627536469ca8786b576957a9797d56&ab_segments=0%2Fbasic_search_gsv2%2Fcontrol&refreqid=fastly-default%3Af90c911269c590baf37330b9d16ae1cd&seq=1#metadata_info_tab_contents')
        self.assertEqual(c[:c.index('| access-date=')], (
            '* {{cite report | last=Singh | first=Spandana | last2=Blase '
            '| first2=Margerite | title=Google | publisher=New America '
            '| series=How Internet Platforms Are Addressing Election and Voter Suppression-Related Misinformation and Disinformation '
            '| year=2020 | url=http://www.jstor.org/stable/resrep26363.7 '))


if __name__ == '__main__':
    main()
