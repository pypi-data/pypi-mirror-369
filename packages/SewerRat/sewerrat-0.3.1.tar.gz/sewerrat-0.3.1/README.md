<!-- These are examples of badges you might want to add to your README:
     please update the URLs accordingly

[![Built Status](https://api.cirrus-ci.com/github/<USER>/SewerRat.svg?branch=main)](https://cirrus-ci.com/github/<USER>/SewerRat)
[![ReadTheDocs](https://readthedocs.org/projects/SewerRat/badge/?version=latest)](https://SewerRat.readthedocs.io/en/stable/)
[![Coveralls](https://img.shields.io/coveralls/github/<USER>/SewerRat/main.svg)](https://coveralls.io/r/<USER>/SewerRat)
[![Conda-Forge](https://img.shields.io/conda/vn/conda-forge/SewerRat.svg)](https://anaconda.org/conda-forge/SewerRat)
[![Monthly Downloads](https://pepy.tech/badge/SewerRat/month)](https://pepy.tech/project/SewerRat)
[![Twitter](https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter)](https://twitter.com/SewerRat)
-->

# Python interface to the SewerRat API

![Unit tests](https://github.com/ArtifactDB/SewerRat-py/actions/workflows/run-tests.yaml/badge.svg)
![Documentation](https://github.com/ArtifactDB/SewerRat-py/actions/workflows/build-docs.yaml/badge.svg)
[![PyPI-Server](https://img.shields.io/pypi/v/SewerRat.svg)](https://pypi.org/project/SewerRat/)

Pretty much as it says on the tin: provides a Python client for the [API of the same name](https://github.com/ArtifactDB/SewerRat).
It is assumed that the users of the **sewerrat** client and the SewerRat API itself are accessing the same shared filesystem;
this is typically the case for high-performance computing clusters in scientific institutions.
To demonstrate, let's spin up a mock SewerRat instance:

```python
import sewerrat as sr
_, url = sr.start_sewerrat()
```

Let's mock up a directory of metadata files:

```python
import tempfile
import os

mydir = tempfile.mkdtemp()
with open(os.path.join(mydir, "metadata.json"), "w") as handle:
    handle.write('{ "first": "foo", "last": "bar" }')

os.mkdir(os.path.join(mydir, "diet"))
with open(os.path.join(mydir, "diet", "metadata.json"), "w") as handle:
    handle.write('{ "fish": "barramundi" }')
```

We can then easily register it via the `register()` function.
Similarly, we can deregister this directory with `deregister(mydir)`.

```python
# Only indexing metadata files named 'metadata.json'.
sr.register(mydir, names=["metadata.json"], url=url)
```

To search the index, we use the `query()` function to perform free-text searches.
This does not require filesystem access and can be done remotely.

```python
sr.query(url, "foo")
sr.query(url, "bar*") # partial match to 'bar...'
sr.query(url, "bar* AND foo") # boolean operations
sr.query(url, "fish:bar*") # match in the 'fish' field
```

We can also search on the user, path components, and time of creation:

```python
sr.query(url, user="LTLA") # created by myself
sr.query(url, path="diet/") # path has 'diet/' in it

import time
sr.query(url, after=time.time() - 3600) # created less than 1 hour ago
```

Once we find a file of interest from a registered directory, we can retrieve its metadata, or other files in the same directory, or the entire directory itself:

```python
sr.retrieve_metadata(mydir + "/metadata.json", url)
sr.list_files(mydir, url)
sr.retrieve_file(mydir + "/diet/metadata.json", url)
sr.retrieve_directory(mydir, url)
```

Check out the [API documentation](https://artifactdb.github.io/SewerRat-py/) for more details on each function.
For the concepts underlying the SewerRat itself, check out the [repository](https://github.com/ArtifactDB/SewerRat) for a detailed explanation.
