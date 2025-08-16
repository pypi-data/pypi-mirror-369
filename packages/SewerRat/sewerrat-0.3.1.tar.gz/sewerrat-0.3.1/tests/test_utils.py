from sewerrat import _utils as ut


def test_clean_path():
    x = ut.clean_path("foo/bar")
    assert x.endswith("/foo/bar")
    assert x.startswith("/")

    x = ut.clean_path("//absd//a//foo/bar")
    assert x == "/absd/a/foo/bar"

    x = ut.clean_path("//absd//a//../foo/bar")
    assert x == "/absd/foo/bar"

    x = ut.clean_path("/xxxx/bbb/../../foo/bar")
    assert x == "/foo/bar"

    x = ut.clean_path("/../absd")
    assert x == "/absd"

    x = ut.clean_path("/absd/./bar/./")
    assert x == "/absd/bar"

    x = ut.clean_path("/a/b/c/d/")
    assert x == "/a/b/c/d"
