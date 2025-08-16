import sewerrat
from sewerrat.retrieve_directory import _local_root
import os
import tempfile
import json
import time


def test_retrieve_file(basic_config):
    url, mydir = basic_config

    p = sewerrat.retrieve_file(mydir + "/metadata.json", url=url)
    with open(p, "r") as f:
        meta = json.load(f)
        assert meta["first"] == "Aaron"

    # Caching of remotes works as expected.
    cache = tempfile.mkdtemp()
    p = sewerrat.retrieve_file(mydir + "/metadata.json", url=url, cache=cache, force_remote=True)
    assert p.startswith(cache)
    with open(p, "r") as f:
        meta = json.load(f)
        assert meta["first"] == "Aaron"

    # Subsequent requests are no-ops.
    with open(p, "w") as f:
        f.write('{ "first": "Erika" }')
    p2 = sewerrat.retrieve_file(mydir + "/metadata.json", url=url, cache=cache, force_remote=True)
    assert p == p2 
    with open(p2, "r") as f:
        meta = json.load(f)
        assert meta["first"] == "Erika"

    # Overwritten successfully:
    p2 = sewerrat.retrieve_file(mydir + "/metadata.json", url=url, cache=cache, force_remote=True, overwrite=True)
    assert p == p2 
    with open(p2, "r") as f:
        meta = json.load(f)
        assert meta["first"] == "Aaron"

    # We also get an update if the cached file is too old.
    with open(p, "w") as f:
        f.write('{ "first": "Erika" }')
    os.utime(p, (time.time(), time.time() - 4000))
    p2 = sewerrat.retrieve_file(mydir + "/metadata.json", url=url, cache=cache, force_remote=True)
    assert p == p2 
    with open(p2, "r") as f:
        meta = json.load(f)
        assert meta["first"] == "Aaron"


def test_retrieve_metadata(basic_config):
    url, mydir = basic_config

    fpath = mydir + "/diet/metadata.json"
    meta = sewerrat.retrieve_metadata(fpath, url=url)
    assert os.path.normpath(fpath) == os.path.normpath(meta["path"])
    assert meta["metadata"]["meal"] == "lunch"


def test_retrieve_directory(basic_config):
    url, mydir = basic_config

    dir = sewerrat.retrieve_directory(mydir, url=url)
    with open(os.path.join(dir, "metadata.json"), "r") as f:
        meta = json.load(f)
        assert meta["first"] == "Aaron"

    subpath = os.path.join(mydir, "diet")
    cache = tempfile.mkdtemp()
    rdir = sewerrat.retrieve_directory(subpath, url=url, cache=cache, force_remote=True)
    assert rdir.startswith(cache)
    with open(os.path.join(rdir, "metadata.json"), "r") as f:
        meta = json.load(f)
        assert meta["meal"] == "lunch"

    # Subsequent requests are no-ops.
    with open(os.path.join(rdir, "metadata.json"), "w") as f:
        f.write('{ "meal": "dinner" }')
    rdir2 = sewerrat.retrieve_directory(subpath, url=url, cache=cache, force_remote=True)
    assert rdir == rdir2
    with open(os.path.join(rdir2, "metadata.json"), "r") as f:
        meta = json.load(f)
        assert meta["meal"] == "dinner"

    # Unless we force an overwrite.
    rdir2 == sewerrat.retrieve_directory(subpath, url=url, cache=cache, force_remote=True, overwrite=True)
    assert rdir == rdir2
    with open(os.path.join(rdir2, "metadata.json"), "r") as f:
        meta = json.load(f)
        assert meta["meal"] == "lunch"

    # Or the cached file AND the success file are both too old, in which case they get updated.
    with open(os.path.join(rdir, "metadata.json"), "w") as f:
        f.write('{ "meal": "dinner" }')
    os.utime(os.path.join(rdir, "metadata.json"), (time.time(), time.time() - 4000))
    os.utime(os.path.join(_local_root(cache, url), "SUCCESS" + subpath, "....OK"), (time.time(), time.time() - 4000))

    rdir2 = sewerrat.retrieve_directory(subpath, url=url, cache=cache, force_remote=True)
    assert rdir == rdir2
    with open(os.path.join(rdir2, "metadata.json"), "r") as f:
        meta = json.load(f)
        assert meta["meal"] == "lunch"

    # Trying with multiple cores.
    cache = tempfile.mkdtemp()
    rdir2 = sewerrat.retrieve_directory(mydir, url=url, cache=cache, force_remote=True, concurrent=2)
    with open(os.path.join(rdir2, "diet", "metadata.json"), "r") as f:
        meta = json.load(f)
        assert meta["meal"] == "lunch"


def test_retrieve_directory_with_updates():
    mydir2 = tempfile.mkdtemp()
    with open(os.path.join(mydir2, "metadata.json"), "w") as handle:
        handle.write('{ "first": "Kanon", "last": "Shibuya" }')

    os.mkdir(os.path.join(mydir2, "2"))
    with open(os.path.join(mydir2, "2", "metadata.json"), "w") as handle:
        handle.write('{ "first": "Kinako", "last": "Sakurakouji" }')

    os.mkdir(os.path.join(mydir2, "3"))
    with open(os.path.join(mydir2, "3", "metadata.json"), "w") as handle:
        handle.write('{ "first": "Margarete", "last": "Wien" }')

    _, url = sewerrat.start_sewerrat()
    sewerrat.register(mydir2, ["metadata.json"], url=url)

    cache = tempfile.mkdtemp()
    dir = sewerrat.retrieve_directory(mydir2, url=url, cache=cache, force_remote=True)
    with open(os.path.join(dir, "2", "metadata.json"), "r") as f:
        meta = json.load(f)
        assert meta["first"] == "Kinako"
    assert os.path.exists(os.path.join(dir, "3", "metadata.json"))

    # Checking if it responds correctly to remote updates.
    time.sleep(1.5)
    import shutil
    shutil.rmtree(os.path.join(mydir2, "3"))
    with open(os.path.join(mydir2, "2", "metadata.json"), "w") as handle:
        handle.write('{ "first": "Mei", "last": "Yoneme" }')
    time.sleep(1.5)

    dir2 = sewerrat.retrieve_directory(mydir2, url=url, cache=cache, force_remote=True, update_delay=0)
    assert dir == dir2
    with open(os.path.join(dir, "2", "metadata.json"), "r") as f:
        meta = json.load(f)
        assert meta["first"] == "Mei"
    assert not os.path.exists(os.path.join(dir, "3", "metadata.json"))
