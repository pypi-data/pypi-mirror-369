import re
from timedc import getTime

def test_getTime_basic():
    result = getTime("10m")
    assert result.startswith("<t:")
    assert result.endswith(">")

def test_getTime_with_format():
    result = getTime("2h", "R")
    assert re.match(r"<t:\d+:R>", result)

def test_invalid_duration():
    try:
        getTime("abc")
    except ValueError:
        assert True
    else:
        assert False

def test_invalid_format():
    try:
        getTime("10m", "X")
    except ValueError:
        assert True
    else:
        assert False
