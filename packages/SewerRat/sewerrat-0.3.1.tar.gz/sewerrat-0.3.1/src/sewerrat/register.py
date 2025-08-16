from typing import List, Optional, Union
import requests
import os
import warnings
import time

from . import _utils as ut


def register(path: str, names: Union[str, List[str]], url: str, retry: int = 3, wait: int = 1, block: bool = True):
    """
    Register a directory into the SewerRat search index.

    Args:
        path: 
            Path to the directory to be registered.
            The directory should be readable by the SewerRat API and the caller should have write access.

        names: 
            List of strings containing the base names of metadata files inside ``path`` to be indexed.
            Alternatively, a single string containing the base name for a single metadata file.

        url:
            URL to the SewerRat REST API.

        retry:
            Deprecated, ignored.

        wait:
            Deprecated, ignored.

        block:
            Whether to block on successful registration.

    Returns:
        On success, the directory is registered. 
        If a metadata file cannot be indexed (e.g., due to incorrect formatting, insufficient permissions), a warning will be printed but the function will not throw an error.

        If ``block = False``, the function returns before confirmation of successful registration from the SewerRat API.
        This can be useful for asynchronous processing of directories with many files. 
    """
    if isinstance(names, str):
        names = [names]
    elif len(names) == 0:
        raise ValueError("expected at least one entry in 'names'")

    path = ut.clean_path(path)
    res = requests.post(url + "/register/start", json = { "path": path }, allow_redirects=True)
    if res.status_code >= 300:
        raise ut.format_error(res)

    body = res.json()
    code = body["code"]
    target = os.path.join(path, code)
    with open(target, "w") as handle:
        handle.write("")

    try:
        res = requests.post(url + "/register/finish", json = { "path": path, "base": names, "block": block }, allow_redirects=True)
        if res.status_code >= 300:
            raise ut.format_error(res)
        body = res.json()
    finally:
        os.unlink(target)

    if block:
        for comment in body["comments"]:
            warnings.warn(comment)
    return
