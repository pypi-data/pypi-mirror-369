import requests
import os
import time

from . import _utils as ut


def deregister(path: str, url: str, retry: int = 3, wait: float = 1, block: bool = True):
    """
    Deregister a directory from the SewerRat search index.

    Args:
        path: 
            Path to the directory to be deregistered.
            The directory should either be readable by the SewerRat API and the caller should have write access;
            or the directory should not exist.

        url:
            URL to the SewerRat REST API. 

        retry:
            Deprecated, ignored.

        wait:
            Deprecated, ignored.

        block:
            Whether to block on successful deregistration.

    Returns:
        On success, the directory is deregistered. 

        If ``block = False``, the function returns before confirmation of successful deregistration from the SewerRat API.
        This can be useful for asynchronous processing of directories with many files.
    """
    path = ut.clean_path(path)
    res = requests.post(url + "/deregister/start", json = { "path": path, "block": block }, allow_redirects=True)
    if res.status_code >= 300:
        raise ut.format_error(res)

    # If it succeeded on start, we don't need to do verification.
    body = res.json()
    if body["status"] == "SUCCESS":
        return

    code = body["code"]
    target = os.path.join(path, code)
    with open(target, "w") as handle:
        pass

    try:
        res = requests.post(url + "/deregister/finish", json = { "path": path, "block": block }, allow_redirects=True)
        if res.status_code >= 300:
            raise ut.format_error(res)
    finally:
        os.unlink(target)

    return
