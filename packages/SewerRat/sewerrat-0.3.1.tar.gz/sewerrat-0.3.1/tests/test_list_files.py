import sewerrat
import os
import tempfile
import time


def test_list_files(basic_config):
    url, mydir = basic_config

    out = sewerrat.list_files(mydir, url=url)
    assert sorted(out) == [ "diet/metadata.json", "metadata.json" ]

    out = sewerrat.list_files(mydir, url=url, recursive=False)
    assert sorted(out) == [ "diet/", "metadata.json" ]

    out = sewerrat.list_files(mydir + "/diet", url=url)
    assert sorted(out) == [ "metadata.json" ]

    out = sewerrat.list_files(mydir, url=url, force_remote=True)
    assert sorted(out) == [ "diet/metadata.json", "metadata.json" ]
