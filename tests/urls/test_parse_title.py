from lib.urls import parse_title


def test_not_dash():
    # https://www.isu.org/inside-isu/rules-regulations/isu-statutes-constitution-regulations-technical
    assert parse_title(
        'Constitution & Regulations - International Skating Union',
        'isu.org',
        None,
        [None, 'Home - International Skating Union'],
        None,
    ) == (None, 'Constitution & Regulations', 'International Skating Union')


def test_when_analyze_home_fails():
    assert parse_title(
        'tp1 — tp2', 'www.un.org', None, [None, None], None
    ) == (None, 'tp1', None)


def test_all_parts_removed():
    # https://www.un.org/en/about-us/un-charter/full-text
    assert parse_title(
        'United Nations Charter (full text) | United Nations',
        'un.org',
        [('United', 'Nations')],
        [None, 'Welcome to the United Nations'],
        None,
    ) == (None, 'United Nations Charter (full text) ', 'United Nations')


def test_repeated_parts():
    # https://www.ilastik.org/
    assert parse_title(
        'ilastik - ilastik',
        'ilastik.org',
        [],
        [None, 'ilastik - ilastik'],
        None,
    ) == (None, 'ilastik', 'ilastik')
