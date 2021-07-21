from lib.noorlib import noorlib_scr


def test_nl1():
    i = 'http://www.noorlib.ir/View/fa/Book/BookView/Image/6120'
    o = noorlib_scr(i)
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
    assert e in o[1]


def test_nl2():
    """The year parameter is not present."""
    i = 'http://www.noorlib.ir/View/fa/Book/BookView/Image/18454'
    o = noorlib_scr(i)
    assert '{{sfn | کورانی | p=}}' in o[0]
    assert (
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
        '| access-date='
    ) in o[1]
