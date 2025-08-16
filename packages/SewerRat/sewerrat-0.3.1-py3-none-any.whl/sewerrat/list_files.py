from typing import Optional, List
import os
import requests
from . import _utils as ut


def list_files(path: str, url: str, recursive: bool = True, force_remote: bool = False) -> List[str]:
    """
    List the contents of a registered directory or a subdirectory thereof.

    Args:
        path:
            Absolute path of the directory to list.

        url:
            URL to the SewerRat REST API. Only used for remote access.

        recursive:
            Whether to list the contents recursively. If False, the contents of
            subdirectories are not listed, and the names of directories are
            suffxed with ``/`` in the returned list.

        force_remote:
            Whether to force remote access via the API, even if ``path`` is
            on the same filesystem as the caller. 

    Returns:
        List of strings containing the relative paths of files in ``path``.
    """
    if not force_remote and os.path.exists(path):
        listing = []
        for root, dirs, files in os.walk(path):
            rel = os.path.relpath(root, path)
            for f in files:
                if rel != ".":
                    listing.append(os.path.join(rel, f))
                else:
                    listing.append(f)
            if not recursive:
                for d in dirs:
                    listing.append(d + "/")
                break

        return listing

    else:
        import urllib
        res = requests.get(url + "/list?path=" + urllib.parse.quote_plus(path) + "&recursive=" + str(recursive).lower())
        if res.status_code >= 300:
            raise ut.format_error(res)
        return res.json()
