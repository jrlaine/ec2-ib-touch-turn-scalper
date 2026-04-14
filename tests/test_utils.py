from trading_bot.utils import fib_level


def test_fib_level():
    assert fib_level(100.0, 90.0, 0.382) == 100.0 - (100.0 - 90.0) * 0.382
