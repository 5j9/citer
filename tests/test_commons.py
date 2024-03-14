from lib.commons import date_search


def test_date_search_ignore_date_range():  # 54
    assert (
        date_search(
            '<small>Time frame: 1 November 2022 - 31 October 2023</small>'
        )
        is None
    )
