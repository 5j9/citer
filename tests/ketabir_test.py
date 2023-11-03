from lib.commons import dict_to_sfn_cit_ref
from lib.ketabir import isbn_to_url, url_to_dict

ketabir_scr = lambda *args: dict_to_sfn_cit_ref(url_to_dict(*args))


def test_ab1():
    """authors = 1, translators = 2, otheo = 1, isbn13"""
    assert (
        '* {{cite book | last=لانسکی | first=ویکی '
        '| others=کی وایت (تصويرگر), فیروزه دالکی (مترجم), '
        'and مژگان امیرفروغی (مترجم) '
        '| title=101 راه برای اینکه پدر بهتری باشید '
        '| publisher=پیک ادبیات | publication-place=تهران - تهران '
        '| year=1386 | isbn=978-964-8165-81-4 | language=fa}}'
    ) == ketabir_scr(
        'https://ketab.ir/book/27b3444f-1175-4db0-8411-b1719a5d7ed1'
    )[1]


def test_ab2():
    """authors = 3, translators = 2, otheo = 0, isbn13"""
    assert (
        '* {{cite book | last=کرسول | first=جان | last2=پلانو‌کلارک '
        '| first2=ویکی '
        '| others=محسن نیازی (مترجم), and عباس زارعی (مترجم) '
        '| title=روش\u200cهای تحقیق تلفیقی '
        '| publisher=ثامن الحجج | publication-place=تهران - تهران '
        '| volume=1 | year=1387 | isbn=978-964-2823-35-2 | language=fa}}'
    ) == ketabir_scr(
        'https://ketab.ir/book/667c900a-69bd-4a1a-a651-1870d2f63a68'
    )[1]


def test_ab3():
    """authors = 2, translators = 0, otheo = 4, isbn13"""
    assert (
        '* {{cite book | last=فخررحیمی | first=علیرضا | last2=فخررحیمی '
        '| first2=الهام '
        '| others=آرش نادرپور '
        '(مقدمه), وحید شهبازیان (مقدمه), رضا مقدم (مقدمه), and'
        ' امیر جابری (مقدمه) '
        '| title=آموزش گام به گام پیکربندی مسیریابهای میکروتیک:'
        ' آمادگی آزمون MTCNA | publisher=نشرگستر '
        '| publication-place=تهران - تهران | year=1391 '
        '| isbn=978-600-5883-43-5 | language=fa}}'
    ) == ketabir_scr(
        'https://ketab.ir/book/f37fad8e-8f0b-4cd9-8875-f5de0e0d86ef'
    )[1]


def test_ab4():
    """authors = 3, translators = 0, otheo = 0, isbn13"""
    assert (
        '* {{cite book | last=کریمی | first=نجمه | last2=یزدخواستی '
        '| first2=فروغ | last3=مختاری | first3=صفورا '
        '| title=11 سپتامبر ... آرماگدون | publisher=حدیث راه عشق '
        '| publication-place=اصفهان - اصفهان | year=1386 '
        '| isbn=978-964-95633-4-3 | language=fa}}'
    ) == ketabir_scr(
        'https://ketab.ir/book/13a52229-5e3f-479e-8954-092b65e85923'
    )[1]


def test_ab5():
    """Year is interesting here."""
    assert (
        '* {{cite book | last=یوسف‌نژاد | first=یوسف‌علی '
        '| title=فراهنجاری '
        'در مثنوی‌سرایی: بررسی قالب غزل - مثنوی در ادب فارسی '
        '| publisher=هنر رسانه اردیبهشت '
        '| publication-place=تهران - تهران | year=1388 '
        '| isbn=978-964-2656-34-9 | language=fa}}'
    ) == ketabir_scr(
        'https://ketab.ir/book/a5958832-5c43-460d-bf42-65acb6077e52'
    )[1]


def test_ab6():
    """Month and year detection."""
    assert ketabir_scr(
        'https://ketab.ir/book/cb1989dc-ba09-4df6-aaee-fcdbd25ad322'
    )[1] == (
        '* {{cite book | last=مونس | first=حسین | others=حمیدرضا شیخی (مترجم) | '
        'title=تاریخ و تمدن مغرب | publisher=سمت | publication-place=مشهد - خراسان '
        'رضوی | volume=1 | year=1390 | isbn=978-964-530-036-2 | language=fa}}'
    )


def test_ab7():
    """1 Editor."""
    assert (
        '* {{cite book | last=دیماتیو | first=ام.رابین | editor-last=جباری | '
        'editor-first=کریم | others=کیانوش هاشمیان (زيرنظر), and محمد کاویانی (مترجم) '
        '| title=روانشناسی سلامت به ضمیمه نگرشی بر منابع اسلامی | publisher=سمت | '
        'publication-place=تهران - تهران | volume=1 | year=1379 | '
        'isbn=978-964-459-398-7 | language=fa}}'
    ) == ketabir_scr(
        'https://ketab.ir/book/4cc231f9-35c2-4b60-a714-a0a11135e932'
    )[1]


def test_isbn2url():
    assert (
        isbn_to_url('978-964-459-398-7')
        == 'https://ketab.ir/book/4cc231f9-35c2-4b60-a714-a0a11135e932'
    )
