from tests.helpers import pp


def test_Contains():
    t0 = pp("'foobar'.replace('o', '0')")
    t1 = pp("print('foobar'.replace('o', '0'))")
    assert t0 in t1
    assert t1 not in t0
