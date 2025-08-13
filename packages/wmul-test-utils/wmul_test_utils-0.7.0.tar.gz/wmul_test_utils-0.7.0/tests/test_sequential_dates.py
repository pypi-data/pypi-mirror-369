from datetime import datetime
from wmul_test_utils import sequential_dates


def test_first_10_dates():
    previous_date = datetime(year=1999, month=12, day=31, hour=23, minute=59, second=59)

    seq_gen = sequential_dates()

    for _ in range(10):
        this_date = next(seq_gen)
        assert this_date.year == 2000
        assert previous_date < this_date
        previous_date = this_date


def test_first_30_dates():
    previous_date = datetime(year=1999, month=12, day=31, hour=23, minute=59, second=59)

    seq_gen = sequential_dates()

    for _ in range(10):
        this_date = next(seq_gen)
        assert this_date.year == 2000
        assert previous_date < this_date
        previous_date = this_date
    
    for _ in range(10):
        this_date = next(seq_gen)
        assert this_date.year == 2001
        assert previous_date < this_date
        previous_date = this_date

    for _ in range(10):
        this_date = next(seq_gen)
        assert this_date.year == 2002
        assert previous_date < this_date
        previous_date = this_date


def test_1000_dates():
    previous_date = datetime(year=1999, month=12, day=31, hour=23, minute=59, second=59)

    seq_gen = sequential_dates()

    for _ in range(1000):
        this_date = next(seq_gen)
        assert previous_date < this_date
        previous_date = this_date

    assert this_date.year == 2100
