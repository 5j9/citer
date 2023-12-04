from datetime import date
from unittest.mock import patch

from lib.commons import find_any_date
from lib.generator_fa import sfn_cit_ref
from tests.doi_test import doi_scr
from tests.googlebooks_test import googlebooks_scr
from tests.isbn_oclc_test import isbn_scr
from tests.ketabir_test import ketabir_scr
from tests.noorlib_test import noorlib_scr
from tests.noormags_test import noormags_scr
from tests.pubmed_test import pmid_scr
from tests.urls_test import urls_scr

sfn_cit_ref_patcher = patch('lib.commons.sfn_cit_ref', sfn_cit_ref)
doi_patcher = patch('lib.doi.LANG', 'fa')
isbn_oclc_patcher = patch('lib.isbn_oclc.LANG', 'fa')


def setup_module():
    sfn_cit_ref_patcher.start()
    doi_patcher.start()
    isbn_oclc_patcher.start()


def test_ketabir1():
    """authors = 1, translators = 2, otheo = 1, isbn13"""
    assert (
        '* {{یادکرد کتاب | نام خانوادگی=لانسکی |'
        ' نام=ویکی | ترجمه=فیروزه دالکی و مژگان امیرفروغی |'
        ' دیگران=کی وایت (تصويرگر) |'
        ' عنوان=101 راه برای اینکه پدر بهتری باشید |'
        ' ناشر=پیک ادبیات | مکان=تهران - تهران |'
        ' سال=1386 | شابک=978-964-8165-81-4 | زبان=fa}}'
    ) == ketabir_scr(
        'https://ketab.ir/book/27b3444f-1175-4db0-8411-b1719a5d7ed1'
    )[1]


def test_ketabir2():
    """authors = 3, translators = 2, otheo = 0, isbn13"""
    assert (
        '* {{یادکرد کتاب | نام خانوادگی=کرسول | نام=جان | نام '
        'خانوادگی۲=پلانو\u200cکلارک | نام۲=ویکی | ترجمه=محسن نیازی و عباس زارعی | '
        'عنوان=روش\u200cهای تحقیق تلفیقی | ناشر=ثامن الحجج | مکان=تهران - تهران | '
        'جلد=1 | سال=1387 | شابک=978-964-2823-35-2 | زبان=fa}}'
    ) == ketabir_scr(
        'https://ketab.ir/book/667c900a-69bd-4a1a-a651-1870d2f63a68'
    )[1]


def test_ketabir3():
    """authors = 2, translators = 0, otheo = 4, isbn13"""
    assert (
        '* {{یادکرد کتاب | نام خانوادگی=فخررحیمی |'
        ' نام=علیرضا | نام خانوادگی۲=فخررحیمی |'
        ' نام۲=الهام | دیگران=آرش نادرپور'
        ' (مقدمه)، وحید شهبازیان (مقدمه)، رضا مقدم (مقدمه) '
        'و امیر جابری (مقدمه) | عنوان=آموزش گام'
        ' به گام پیکربندی مسیریابهای میکروتیک: آمادگی آزمون MTCNA '
        '| ناشر=نشرگستر | مکان=تهران - تهران |'
        ' سال=1391 | شابک=978-600-5883-43-5 | زبان=fa}}'
    ) == ketabir_scr(
        'https://ketab.ir/book/f37fad8e-8f0b-4cd9-8875-f5de0e0d86ef'
    )[1]


def test_ketabir4():
    """authors = 3, translators = 0, otheo = 0, isbn13"""
    assert (
        '* {{یادکرد کتاب | نام خانوادگی=کریمی |'
        ' نام=نجمه | نام خانوادگی۲=یزدخواستی |'
        ' نام۲=فروغ | نام خانوادگی۳=مختاری |'
        ' نام۳=صفورا | عنوان=11 سپتامبر ... آرماگدون |'
        ' ناشر=حدیث راه عشق | مکان=اصفهان - اصفهان |'
        ' سال=1386 | شابک=978-964-95633-4-3 | زبان=fa}}'
    ) == ketabir_scr(
        'https://ketab.ir/book/13a52229-5e3f-479e-8954-092b65e85923'
    )[1]


def test_ketabir5():
    """Year is interesting here."""
    assert (
        '* {{یادکرد کتاب | نام خانوادگی=یوسف\u200cنژاد | نام=یوسف\u200cعلی | '
        'عنوان=فراهنجاری در مثنوی\u200cسرایی: بررسی قالب غزل - مثنوی در ادب فارسی | '
        'ناشر=هنر رسانه اردیبهشت | مکان=تهران - تهران | سال=1388 | '
        'شابک=978-964-2656-34-9 | زبان=fa}}'
    ) == ketabir_scr(
        'https://ketab.ir/book/a5958832-5c43-460d-bf42-65acb6077e52'
    )[1]


def test_ketabir6():
    """Month and year detection."""
    assert (
        '* {{یادکرد کتاب | نام خانوادگی=مونس | نام=حسین | ترجمه=حمیدرضا شیخی | '
        'عنوان=تاریخ و تمدن مغرب | ناشر=سمت | مکان=مشهد - خراسان رضوی | جلد=1 | '
        'سال=1390 | شابک=978-964-530-036-2 | زبان=fa}}'
    ) == ketabir_scr(
        'https://ketab.ir/book/cb1989dc-ba09-4df6-aaee-fcdbd25ad322'
    )[1]


def test_ketabir7():
    """1 Editor."""
    assert (
        '* {{یادکرد کتاب | نام خانوادگی=دیماتیو | نام=ام.رابین | نام خانوادگی '
        'ویراستار=جباری | نام ویراستار=کریم | ترجمه=محمد کاویانی | دیگران=کیانوش '
        'هاشمیان (زيرنظر) | عنوان=روانشناسی سلامت به ضمیمه نگرشی بر منابع اسلامی | '
        'ناشر=سمت | مکان=تهران - تهران | جلد=1 | سال=1379 | شابک=978-964-459-398-7 | '
        'زبان=fa}}'
    ) == ketabir_scr(
        'https://ketab.ir/book/4cc231f9-35c2-4b60-a714-a0a11135e932'
    )[1]


def test_google_books_ending_page():
    r = googlebooks_scr(
        'https://www.google.com/books/edition/So_You_Want_to_Sing_World_Music/OlCwDwAAQBAJ?hl=en&gbpv=1&dq=Darya+Dadvar&pg=PA293&printsec=frontcover'
    )[2]
    assert r[-19:] == '| صفحه=293}}‏</ref>'


def test_google_books_1():
    assert (
        '* {{یادکرد کتاب | نام خانوادگی=Arms |'
        ' نام=W.Y. | عنوان=Digital Libraries | ناشر=MIT Press |'
        ' سری=Digital Libraries and Electronic Publishing |'
        ' سال=2001 | شابک=978-0-262-26134-0 |'
        ' پیوند=https://books.google.com/books?id=pzmt3pcBuGYC&pg=PR11 |'
        ' زبان=en | تاریخ بازبینی='
    ) in googlebooks_scr(
        'http://books.google.com/books?'
        'id=pzmt3pcBuGYC&pg=PR11&lpg=PP1&dq=digital+library'
    )[1]


def test_google_books2():
    """a book with more than 4 authors (10 authors)"""
    o = googlebooks_scr(
        'http://books.google.com/books?id='
        'U46IzqYLZvAC&pg=PT57#v=onepage&q&f=false'
    )
    assert (
        '<ref>'
        '{{پک | Anderson | DeBolt | Featherstone | Gunther | 2010'
        ' | ک=InterACT with Web Standards: A'
        ' holistic approach to web design | زبان=en | ص=57}}'
        '\u200f</ref>'
    ) in o[0]
    assert (
        '* {{یادکرد کتاب |'
        ' نام خانوادگی=Anderson |'
        ' نام=E. |'
        ' نام خانوادگی۲=DeBolt | نام۲=V. |'
        ' نام خانوادگی۳=Featherstone |'
        ' نام۳=D. | نام خانوادگی۴=Gunther |'
        ' نام۴=L. |'
        ' نام خانوادگی۵=Jacobs | نام۵=D.R. | نام خانوادگی۶=Mills |'
        ' نام۶=C. |'
        ' نام خانوادگی۷=Schmitt | نام۷=C. | نام خانوادگی۸=Sims |'
        ' نام۸=G. |'
        ' نام خانوادگی۹=Walter | نام۹=A. |'
        ' نام خانوادگی۱۰=Jensen-Inman |'
        ' نام۱۰=L. |'
        ' عنوان=InterACT with Web Standards:'
        ' A holistic approach to web design |'
        ' ناشر=Pearson Education |'
        ' سری=Voices That Matter | سال=2010 |'
        ' شابک=978-0-13-270490-8 |'
        ' پیوند=https://books.google.com/books?id=U46IzqYLZvAC&pg=PT57 |'
        ' زبان=en |'
        ' تاریخ بازبینی='
    ) in o[1]


def test_google_books3():
    """Non-ascii characters in title"""
    o = googlebooks_scr(
        'http://books.google.com/books?'
        'id=icMEAAAAQBAJ&pg=PA588&dq=%22a+Delimiter+is%22&hl='
        'en&sa=X&ei=oNKSUrKeDovItAbO_4CoBA&ved=0CC4Q6AEwAA#v='
        'onepage&q=%22a%20Delimiter%20is%22&f=false'
    )
    assert (
        '<ref>'
        '{{پک | Farrell | 2009 '
        '| ک=Microsoft Visual C# 2008 Comprehensive: '
        'An Introduction to Object-Oriented Programming |'
        ' زبان=en | ص=588}}'
        '\u200f</ref>'
    ) in o[0]
    assert (
        '* {{یادکرد کتاب | نام خانوادگی=Farrell |'
        ' نام=J. | عنوان=Microsoft Visual C# 2008 Comprehensive: '
        'An Introduction to Object-Oriented Programming |'
        ' ناشر=Cengage Learning | سال=2009 | شابک=978-1-111-78619-9 |'
        ' پیوند=https://books.google.com/books?id=icMEAAAAQBAJ&pg=PA588 |'
        ' زبان=en | تاریخ بازبینی='
    ) in o[1]


def test_google_books4():
    """Non-ascii characters in author's name."""
    o = googlebooks_scr(
        'http://books.google.com/books?id=i8nZjjo_9ikC&pg=PA229&dq=%22legal+translation+is%22&hl=en&sa=X&ei=hEuYUr_mOsnKswb49oDQCA&ved=0CC4Q6AEwAA#v=onepage&q=%22legal%20translation%20is%22&f=false'
    )
    assert (
        '<ref>{{پک | Sarcevic | \x8aar?evi? | 1997 | ک=New Approach to Legal Translation | زبان=en | ص=229}}\u200f</ref>'
    ) == o[0]
    assert (
        '* {{یادکرد کتاب | نام خانوادگی=Sarcevic | نام=S. | نام خانوادگی۲=\x8aar?evi? | نام۲=S. | عنوان=New Approach to Legal Translation | ناشر=Springer Netherlands | سال=1997 | شابک=978-90-411-0401-4 | پیوند=https://books.google.com/books?id=i8nZjjo_9ikC&pg=PA229 | زبان=en | تاریخ بازبینی='
    ) in o[1]


def test_noormags1():
    assert (
        '* {{یادکرد ژورنال |'
        ' عنوان=زندگی نامه علمی دکتر کاووس حسن لی |'
        ' ژورنال=شعر | شماره=62 | سال=1387 | صفحه=17–19 |'
        ' پیوند=https://www.noormags.ir/view/fa/articlepage/454096 |'
        ' زبان=fa | تاریخ بازبینی='
    ) in noormags_scr('http://www.noormags.com/view/fa/ArticlePage/454096')[1]


def test_noorlib1():
    i = 'http://www.noorlib.ir/View/fa/Book/BookView/Image/3232'
    o = noorlib_scr(i)
    e = (
        '* {{یادکرد کتاب '
        '| نام خانوادگی=ابن اثیر '
        '| نام=علی بن محمد '
        '| عنوان=الكامل في التاريخ '
        '| ناشر=دار صادر '
        '| مکان=بیروت - لبنان '
        '| سری=الكامل في التاريخ '
        '| جلد=13 '
        '| پیوند=https://www.noorlib.ir/View/fa/Book/BookView/Image/3232 '
        '| زبان=عربی '
        '| تاریخ بازبینی='
    )
    assert e in o[1]


def test_doi1():
    # Note: Language detection is wrong, it should be en
    assert (
        '* {{یادکرد ژورنال | نام خانوادگی=Atkins |'
        ' نام=Joshua H. | نام خانوادگی۲=Gershell | نام۲=Leland J. |'
        ' عنوان=Selective anticancer drugs |'
        ' ژورنال=Nature Reviews Drug Discovery |'
        ' ناشر=Springer Science and Business Media LLC '
        '| جلد=1 | شماره=7 |'
        ' سال=2002 | issn=1474-1776 | doi=10.1038/nrd842 |'
        ' صفحه=491–492 |'
        ' زبان=da}}'
    ) in doi_scr('http://dx.doi.org/10.1038/nrd842')[1]


def test_isbn_exists_on_ottobib_not_ketabir():
    assert (
        '* {{یادکرد کتاب | نام خانوادگی=Adkins | نام=Roy A. | نام خانوادگی۲=Adkins | نام۲=Lesley | عنوان=The War for All the Oceans | ناشر=Abacus (UK) | مکان=London | تاریخ=2007 | شابک=978-0-349-11916-8 | oclc=137313052 | زبان=en}}'
    ) in isbn_scr('9780349119168', True)[1]


def test_isbn_exists_on_ketabir_not_ottobib():
    assert (
        '* {{یادکرد کتاب | دیگران=بدیل\u200cبن\u200cعلی خاقانی (شاعر)، جهانگیر منصور '
        '(به\u200cاهتمام) و محمدحسن فروزانفر (مقدمه) | عنوان=دیوان خاقانی شروانی | '
        'ناشر=نگاه | مکان=تهران - تهران | سال=1396 | شابک=978-964-6736-71-9 | '
        'oclc=1176150182 | زبان=fa}}'
    ) == isbn_scr('978-964-6736-71-9', True)[1]


def test_isbn_exists_on_ketabir_and_ottobib():
    assert (
        '* {{یادکرد کتاب | دیگران=سحر معصومی (به\u200cاهتمام) | عنوان=راز گل سرخ: نقد '
        'و گزیده شعرهای سهراب سپهری | ناشر=نگاه | مکان=تهران - تهران | سال=1386 | '
        'شابک=964-6736-34-3 | oclc=53446327 | زبان=fa}}'
    ) == isbn_scr('964-6736-34-3 ')[1]


def test_isbn_unpure_input():
    assert (
        '* {{یادکرد کتاب | نام خانوادگی=حافظ | نام=شمس\u200cالدین\u200cمحمد | '
        'دیگران=رضا نظرزاده (به\u200cاهتمام) | عنوان=دیوان کامل حافظ همراه با فالنامه '
        '| ناشر=دیوان | مکان=قم - قم | سال=1385 | شابک=964-92962-6-3 | زبان=fa}}'
    ) == isbn_scr('choghondar 964-92962-6-3 شلغم')[1]


def test_2letter_langcode():
    """Test that 3letter language code is converted to a 2-letter one."""
    # Todo: The fawiki template mixes Persian and Chinese characters...
    assert pmid_scr('11938998')[1] == (
        '* {{یادکرد ژورنال | نام خانوادگی=Huang | نام=Y. | نام خانوادگی۲=Lu | نام۲=J. '
        '| نام خانوادگی۳=Shen | نام۳=Y. | نام خانوادگی۴=Lu | نام۴=J. | عنوان=[The '
        'protective effects of total flavonoids from Lycium Barbarum L. on lipid '
        'peroxidation of liver mitochondria and red blood cell in rats] | ژورنال=Wei '
        'Sheng Yan Jiu = Journal of Hygiene Research | جلد=28 | شماره=2 | '
        'تاریخ=1999-03-30 | issn=1000-8020 | pmid=11938998 | صفحه=115–116}}'
    )


def test_either_year_or_date():
    assert (
        urls_scr(
            'https://www.shora-gc.ir/fa/news/1815/%D8%A7%D8%B5%D9%84-%D9%87%D9%81%D8%AA%D8%A7%D8%AF-%D9%88-%D8%B3%D9%88%D9%85'
        )[1][:-12]
        == '* {{یادکرد وب | عنوان=اصل هفتاد و سوم | ناشر=پایگاه اطلاع رسانی شورای نگهبان - shora-gc.ir | تاریخ=2020-06-07 | پیوند=https://www.shora-gc.ir/fa/news/1815/%D8%A7%D8%B5%D9%84-%D9%87%D9%81%D8%AA%D8%A7%D8%AF-%D9%88-%D8%B3%D9%88%D9%85 | کد زبان=fa | تاریخ بازبینی='
    )


def test_arabic_ya():
    assert find_any_date(
        'تاریخ انتشار : جمعه ۳ ارديبهشت ۱۳۸۹ ساعت ۱۶:۴۸'
    ) == date(2010, 4, 23)


def test_sfn_extract_year_from_date():
    s, c, r = doi_scr('10.1073/pnas.2015159118')
    assert (
        s
        == '<ref>{{پک | Almeida | Viala | Nachtigall | Broe | 2021 | ک=Tracking the recruitment and evolution of snake toxins using the evolutionary context provided by the <i>Bothrops jararaca</i> genome | زبان=en | ص=}}\u200f</ref>'
    )
    assert (
        c
        == '* {{یادکرد ژورنال | نام خانوادگی=Almeida | نام=Diego Dantas | نام خانوادگی۲=Viala | نام۲=Vincent Louis | نام خانوادگی۳=Nachtigall | نام۳=Pedro Gabriel | نام خانوادگی۴=Broe | نام۴=Michael | نام خانوادگی۵=Gibbs | نام۵=H. Lisle | نام خانوادگی۶=Serrano | نام۶=Solange Maria de Toledo | نام خانوادگی۷=Moura-da-Silva | نام۷=Ana Maria | نام خانوادگی۸=Ho | نام۸=Paulo Lee | نام خانوادگی۹=Nishiyama-Jr | نام۹=Milton Yutaka | نام خانوادگی۱۰=Junqueira-de-Azevedo | نام۱۰=Inácio L. M. | عنوان=Tracking the recruitment and evolution of snake toxins using the evolutionary context provided by the <i>Bothrops jararaca</i> genome | ژورنال=Proceedings of the National Academy of Sciences | ناشر=Proceedings of the National Academy of Sciences | جلد=118 | شماره=20 | تاریخ=2021-05-10 | issn=0027-8424 | doi=10.1073/pnas.2015159118 | زبان=en}}'
    )


def teardown_module():
    sfn_cit_ref_patcher.stop()
    doi_patcher.stop()
    isbn_oclc_patcher.stop()
