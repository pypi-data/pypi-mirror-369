import sewerrat
import os
import tempfile
import pytest


def test_list_registered_directories(basic_config):
    url, mydir = basic_config

    regged = sewerrat.list_registered_directories(url)
    assert len(regged) > 0

    found = False
    for x in regged:
        if x["path"] == mydir:
            found = True
            assert x["names"] == [ "metadata.json" ]
    assert found

    # Filter by user.
    filtered = sewerrat.list_registered_directories(url, user=True)
    assert regged == filtered

    filtered = sewerrat.list_registered_directories(url, user=regged[0]["user"] + "_asdasdasd")
    assert len(filtered) == 0

    # Filter by contains.
    filtered = sewerrat.list_registered_directories(url, contains=os.path.join(mydir, "metadata.json"))
    assert regged == filtered

    filtered = sewerrat.list_registered_directories(url, contains=os.path.join(mydir + "-asdasd"))
    assert len(filtered) == 0

    # Filter by prefix.
    filtered = sewerrat.list_registered_directories(url, within=os.path.dirname(mydir))
    assert regged == filtered

    filtered  = sewerrat.list_registered_directories(url, within=os.path.dirname(mydir) + "-asdasdad")
    assert len(filtered) == 0

    # Multiple filters work.
    filtered  = sewerrat.list_registered_directories(url, within=os.path.dirname(mydir), user=True, contains=os.path.join(mydir, "metadata.json"))
    assert regged == filtered

    # Existence filter works.
    tmp = str(tempfile.mkdtemp())
    sewerrat.register(tmp, names="metadata.json", url=url)
    try:
        filtered = sewerrat.list_registered_directories(url, prefix=tmp, exists=True)
        assert filtered[0]["path"] == tmp

        os.rmdir(tmp)
        filtered2 = sewerrat.list_registered_directories(url, prefix=tmp, exists=False)
        assert filtered == filtered2

        filtered = sewerrat.list_registered_directories(url, prefix=tmp, exists=True)
        assert len(filtered) == 0
    finally:
        sewerrat.deregister(tmp, url=url)


def test_list_registered_directories_truncation(basic_config, capfd):
    url, mydir = basic_config

    res = sewerrat.list_registered_directories(url, number=0)
    out, err = capfd.readouterr()
    assert "truncated" in out
    assert len(res) == 0

    with pytest.warns(UserWarning, match="truncated"):
        res = sewerrat.list_registered_directories(url, number=0, on_truncation="warning")
    assert len(res) == 0

    res = sewerrat.list_registered_directories(url, number=0, on_truncation="none")
    assert len(res) == 0

    res = sewerrat.list_registered_directories(url, number=float("inf"))
    assert len(res) > 0
