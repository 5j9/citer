from lib.ketabir import ketabir_scr


def test_ab1():
    """authors = 1, translators = 2, otheo = 1, isbn13"""
    assert (
        '* {{cite book | last=لانسکی | first=ویکی '
        '| others=کی وایت (تصويرگر), فیروزه دالکی (مترجم), '
        'and مژگان امیرفروغی (مترجم) '
        '| title=101 راه برای اینکه پدر بهتری باشید '
        '| publisher=پیک ادبیات | publication-place=تهران - تهران '
        '| year=1386 | isbn=978-964-8165-81-4 | language=fa}}'
    ) == ketabir_scr('http://www.ketab.ir/bookview.aspx?bookid=1323394')[1]


def test_ab2():
    """authors = 3, translators = 2, otheo = 0, isbn13"""
    assert (
        '* {{cite book | last=کرسول | first=جان | last2=پلانو‌کلارک '
        '| first2=ویکی | others=عباس زارعی (مترجم), '
        'and محسن نیازی (مترجم) | title=روش‌های تحقیق تلفیقی '
        '| publisher=ثامن‌ الحجج‌(ع) | publication-place=تهران - تهران '
        '| volume=1 | year=1387 | isbn=978-964-2823-35-2 | language=fa}}'
    ) == ketabir_scr('http://www.ketab.ir/bookview.aspx?bookid=1369975')[1]


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
    ) == ketabir_scr('http://www.ketab.ir/bookview.aspx?bookid=1676357')[1]


def test_ab4():
    """authors = 3, translators = 0, otheo = 0, isbn13"""
    assert (
        '* {{cite book | last=کریمی | first=نجمه | last2=یزدخواستی '
        '| first2=فروغ | last3=مختاری | first3=صفورا '
        '| title=11 سپتامبر ... آرماگدون | publisher=حدیث راه عشق '
        '| publication-place=اصفهان - اصفهان | year=1386 '
        '| isbn=978-964-95633-4-3 | language=fa}}'
    ) == ketabir_scr('http://www.ketab.ir/bookview.aspx?bookid=1324978')[1]


def test_ab5():
    """Year is interesting here."""
    assert (
        '* {{cite book | last=یوسف‌نژاد | first=یوسف‌علی '
        '| title=فراهنجاری '
        'در مثنوی‌سرایی: بررسی قالب غزل - مثنوی در ادب فارسی '
        '| publisher=هنر رسانه اردی‌بهشت '
        '| publication-place=تهران - تهران | year=1388 '
        '| isbn=978-964-2656-34-9 | language=fa}}'
    ) == ketabir_scr('http://www.ketab.ir/bookview.aspx?bookid=1430801')[1]


def test_ab6():
    """Month and year detection."""
    assert (
        '* {{cite book | last=مونس | first=حسین '
        '| others=حمیدرضا شیخی (مترجم) | title=تاریخ و تمدن مغرب '
        '| publisher=سازمان‌ مطالعه ‌و تدوین‌ کتب‌ علوم'
        ' ‌انسانی ‌دانشگاهها (سمت) '
        '| publication-place=خراسان رضوی - مشهد | volume=1 '
        '| year=1390 | isbn=978-964-530-036-2 | language=fa}}'
    ) == ketabir_scr('http://www.ketab.ir/bookview.aspx?bookid=1643445')[1]


def test_ab7():
    """1 Editor."""
    assert (
        '* {{cite book | last=دیماتیو | first=ام.رابین '
        '| editor-last=جباری | editor-first=کریم '
        '| others=کیانوش هاشمیان (زيرنظر), and محمد کاویانی (مترجم) '
        '| title=روانشناسی سلامت به ضمیمه نگرشی بر منابع اسلامی '
        '| publisher=سازمان‌ مطالعه'
        ' ‌و تدوین‌ کتب‌ علوم ‌انسانی ‌دانشگاهها (سمت) '
        '| publication-place=تهران - تهران | volume=1 | year=1379 '
        '| isbn=964-459-398-7 | language=fa}}'
    ) == ketabir_scr('http://www.ketab.ir/bookview.aspx?bookid=227129')[1]
