from typing import Optional
import os
import tempfile
import urllib
import time
import requests
from . import _utils as ut


def _local_root(cache: Optional[str], url: str) -> str:
    if cache is None:
        import appdirs
        cache = appdirs.user_data_dir("sewerrat", "aaron")
    return os.path.join(cache, urllib.parse.quote_plus(url))


def _full_file_url(url: str, path: str) -> str:
    return url + "/retrieve/file?path=" + urllib.parse.quote_plus(path)


def _acquire_file_raw(cache: str, path: str, url: str, overwrite: bool) -> str:
    target = os.path.join(cache, "LOCAL" + path) # os.path.join behaves poorly when 'path' is an absolute path.

    if not overwrite:
        if not os.path.exists(target):
            overwrite = True
        else:
            with requests.head(_full_file_url(url, path)) as r:
                if r.status_code < 300:
                    last_mod = os.path.getmtime(target)
                    modtime = ut.parse_remote_last_modified(r)
                    if modtime is not None and modtime > last_mod:
                        overwrite = True

    if overwrite: 
        tempdir = os.path.join(cache, "TEMP")
        os.makedirs(tempdir, exist_ok=True)
        os.makedirs(os.path.dirname(target), exist_ok=True)

        _, temppath = tempfile.mkstemp(dir=tempdir)
        try:
            ut.download_file(_full_file_url(url, path), temppath)
            os.rename(temppath, target) # this should be more or less atomic, so no need for locks.
        finally:
            if os.path.exists(temppath):
                os.remove(temppath)

    return target


def _acquire_file(cache: str, path: str, name: str, url: str, overwrite: bool) -> str:
    return _acquire_file_raw(cache, path + "/" + name, url, overwrite)


def retrieve_directory(path: str, url: str, cache: Optional[str] = None, force_remote: bool = False, overwrite: bool = False, concurrent: int = 1, update_delay: int = 3600) -> str:
    """
    Obtain the path to a registered directory or one of its subdirectories.
    This may create a local copy of the directory's contents if the caller
    is not on the same filesystem. 

    Args:
        path: 
            Relative path to a registered directory or its subdirectories.

        url:
            URL to the Gobbler REST API. Only used for remote queries.

        cache:
            Path to a cache directory. If None, an appropriate location is
            automatically chosen. Only used for remote access.

        force_remote:
            Whether to force remote access. This will download all files in the
            ``path`` via the REST API and cache them locally, even if
            ``path`` is present on the same filesystem.

        overwrite:
            Whether to overwrite existing files in the cache.

        concurrent:
            Number of concurrent downloads.

        update_delay: 
            Delay interval before checking for updates in a cached directory,
            seconds. Only used for remote access.

    Returns:
        Path to the subdirectory on the caller's filesystem.  This is either
        ``path`` if it is accessible, or a path to a local cache of the
        directory's contents otherwise.
    """
    if not force_remote and os.path.exists(path):
        return path

    cache = _local_root(cache, url)
    final = os.path.join(cache, "LOCAL" + path) # os.path.join doesn't like joining of absolute paths.
    ok = os.path.join(cache, "SUCCESS" + path, "....OK")

    if not overwrite and os.path.exists(ok) and os.path.exists(final):
        # Only check for updates every 'update_delay' since the last check, so
        # as to avoid excessive queries to the API.
        if os.path.getmtime(ok) + update_delay >= time.time():
            return final

    res = requests.get(url + "/list?path=" + urllib.parse.quote_plus(path) + "&recursive=true")
    if res.status_code >= 300:
        raise ut.format_error(res)
    listing = res.json()

    # Delete all files that aren't in the listing.
    ok_files = set(listing)
    for root, dirs, filenames in os.walk(final):
        for f in filenames:
            full = os.path.join(root, f)
            if os.path.relpath(full, final) not in ok_files:
                os.remove(full)

    if concurrent == 1:
        for y in listing:
            _acquire_file(cache, name=y, path=path, url=url, overwrite=overwrite)
    else:
        import multiprocessing
        import functools
        with multiprocessing.Pool(concurrent) as p:
            p.map(functools.partial(_acquire_file, cache, path, url=url, overwrite=overwrite), listing)

    # We use a directory-level OK file to avoid having to scan through all 
    # the directory contents to indicate that it's complete.
    os.makedirs(os.path.dirname(ok), exist_ok=True)
    with open(ok, "w") as handle:
        handle.write("")
    return final
