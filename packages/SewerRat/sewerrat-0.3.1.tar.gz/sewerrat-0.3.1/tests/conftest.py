import pytest
import sewerrat
import tempfile
import os

@pytest.fixture(scope="module")
def basic_config():
    _, url = sewerrat.start_sewerrat()

    mydir = tempfile.mkdtemp()
    with open(os.path.join(mydir, "metadata.json"), "w") as handle:
        handle.write('{ "first": "Aaron", "last": "Lun" }')

    os.mkdir(os.path.join(mydir, "diet"))
    with open(os.path.join(mydir, "diet", "metadata.json"), "w") as handle:
        handle.write('{ "meal": "lunch", "ingredients": "water" }')

    sewerrat.register(mydir, ["metadata.json"], url=url)
    yield (url, mydir)
    sewerrat.deregister(mydir, url=url)
