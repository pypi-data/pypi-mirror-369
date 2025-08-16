import sewerrat
import pytest


def test_list_fields(basic_config):
    url, mydir = basic_config

    tok = sewerrat.list_fields(url)
    assert len(tok) > 0

    filtered = sewerrat.list_fields(url, pattern="fir*")
    assert len(tok) > len(filtered)
    assert sorted(x["field"] for x in filtered) == [ "first" ]

    filtered = sewerrat.list_fields(url, count=True)
    assert [x["count"] for x in filtered] == [1] * len(filtered) 


def test_list_fields_truncation(basic_config, capfd):
    url, mydir = basic_config

    res = sewerrat.list_fields(url, number=0)
    out, err = capfd.readouterr()
    assert "truncated" in out
    assert len(res) == 0

    with pytest.warns(UserWarning, match="truncated"):
        res = sewerrat.list_fields(url, number=0, on_truncation="warning")
    assert len(res) == 0

    res = sewerrat.list_fields(url, number=0, on_truncation="none")
    assert len(res) == 0

    res = sewerrat.list_fields(url, number=float("inf"))
    assert len(res) > 0
