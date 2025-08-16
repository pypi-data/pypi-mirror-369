import sewerrat
import os
import tempfile
import time
import pytest


def test_query_basic(basic_config):
    url, mydir = basic_config

    res = sewerrat.query(url, "aaron")
    assert len(res) == 1
    assert "metadata" in res[0]

    res = sewerrat.query(url, "lun*")
    assert len(res) == 2

    res = sewerrat.query(url, "lun* AND aaron")
    assert len(res) == 1

    res = sewerrat.query(url, "meal:lun*")
    assert len(res) == 1

    res = sewerrat.query(url, path="diet/") # has 'diet/' in the path
    assert len(res) == 1

    res = sewerrat.query(url, after=time.time() - 60) 
    assert len(res) == 2

    res = sewerrat.query(url, "lun*", number=float("inf"))
    assert len(res) == 2

    res = sewerrat.query(url, "aaron", metadata=False)
    assert len(res) == 1
    assert "metadata" not in res[0]


def test_query_truncation(basic_config, capfd):
    url, mydir = basic_config

    res = sewerrat.query(url, "lun", number=0)
    out, err = capfd.readouterr()
    assert "truncated" in out
    assert len(res) == 0

    with pytest.warns(UserWarning, match="truncated"):
        res = sewerrat.query(url, "lun", number=0, on_truncation="warning")
    assert len(res) == 0

    res = sewerrat.query(url, "lun", number=0, on_truncation="none")
    assert len(res) == 0

    res = sewerrat.query(url, "lun", number=float("inf"))
    assert len(res) > 0
