from sample_pkg.core import add


def test_add_integers():
    assert add(2, 3) == 5


def test_add_strings():
    assert add("hello ", "world") == "hello world"

