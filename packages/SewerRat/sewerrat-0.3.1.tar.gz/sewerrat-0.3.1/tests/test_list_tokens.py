import sewerrat
import pytest


def test_list_tokens(basic_config):
    url, mydir = basic_config

    tok = sewerrat.list_tokens(url)
    assert len(tok) > 0

    filtered = sewerrat.list_tokens(url, pattern="lun*")
    assert len(tok) > len(filtered)
    assert sorted(x["token"] for x in filtered) == [ "lun", "lunch" ]

    filtered = sewerrat.list_tokens(url, field="first")
    assert len(tok) > len(filtered)
    assert [x["token"] for x in filtered] == [ "aaron" ]

    filtered = sewerrat.list_tokens(url, count=True)
    assert [x["count"] for x in filtered] == [1] * len(filtered) 


def test_list_tokens_truncation(basic_config, capfd):
    url, mydir = basic_config

    res = sewerrat.list_tokens(url, number=0)
    out, err = capfd.readouterr()
    assert "truncated" in out
    assert len(res) == 0

    with pytest.warns(UserWarning, match="truncated"):
        res = sewerrat.list_tokens(url, number=0, on_truncation="warning")
    assert len(res) == 0

    res = sewerrat.list_tokens(url, number=0, on_truncation="none")
    assert len(res) == 0

    res = sewerrat.list_tokens(url, number=float("inf"))
    assert len(res) > 0
