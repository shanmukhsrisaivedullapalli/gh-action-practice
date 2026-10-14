from app import add, is_healthy

def test_add():
    assert add(2, 3) == 5

def test_add():
    assert add(3, 3) == 6

def test_is_healthy():
    assert is_healthy() is True