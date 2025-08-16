import sewerrat
import os
import tempfile
import time


def test_basic():
    mydir = tempfile.mkdtemp()
    with open(os.path.join(mydir, "metadata.json"), "w") as handle:
        handle.write('{ "first": "Aaron", "last": "Lun" }')

    os.mkdir(os.path.join(mydir, "diet"))
    with open(os.path.join(mydir, "diet", "metadata.json"), "w") as handle:
        handle.write('{ "meal": "lunch", "ingredients": "water" }')

    # Checking that registration works as expected.
    _, url = sewerrat.start_sewerrat()
    sewerrat.register(mydir, ["metadata.json"], url=url)

    try:
        res = sewerrat.query(url, "aaron")
        assert len(res) == 1

        # Successfully deregistered:
        sewerrat.deregister(mydir, url=url)
        res = sewerrat.query(url, "aaron")
        assert len(res) == 0

        # We can also register a string.
        sewerrat.register(mydir, "metadata.json", url=url)
        res = sewerrat.query(url, "aaron")
        assert len(res) == 1

    finally:
        sewerrat.deregister(mydir, url=url)


def test_unblocked():
    mydir = tempfile.mkdtemp()
    with open(os.path.join(mydir, "metadata.json"), "w") as handle:
        handle.write('{ "first": "Aaron", "last": "Lun" }')

    os.mkdir(os.path.join(mydir, "diet"))
    with open(os.path.join(mydir, "diet", "metadata.json"), "w") as handle:
        handle.write('{ "meal": "lunch", "ingredients": "water" }')

    _, url = sewerrat.start_sewerrat()
    res = sewerrat.query(url, "aaron")
    assert len(res) == 0

    try:
        sewerrat.register(mydir, ["metadata.json"], url=url, block=False)
        for i in range(10):
            time.sleep(0.1)
            res = sewerrat.query(url, "aaron")
            if len(res) == 1:
                break
        assert len(res) == 1

        sewerrat.deregister(mydir, url=url, block=False)
        for i in range(10):
            time.sleep(0.1)
            res = sewerrat.query(url, "aaron")
            if len(res) == 0:
                break
        assert len(res) == 0 
    finally:
        sewerrat.deregister(mydir, url=url)
