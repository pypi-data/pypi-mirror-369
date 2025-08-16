from typing import Optional
import os
from .retrieve_directory import _local_root, _acquire_file_raw


def retrieve_file(path, url, cache: Optional[str] = None, force_remote: bool = False, overwrite: bool = False) -> str:
    """
    Retrieve the path to a single file in a registered directory. This will
    call the REST API if the caller is not on the same filesystem. 

    Args:
        path: 
            Relative path to a registered directory or its subdirectories.

        url:
            URL to the Gobbler REST API. Only used for remote queries.

        cache:
            Path to a cache directory. If None, an appropriate location is
            automatically chosen. Only used for remote access.

        force_remote:
            Whether to force remote access. This will download ``path`` via the
            REST API and cache it locally, even if ``path`` is present on the
            same filesystem.

        overwrite:
            Whether to overwrite existing files in the cache.

    Returns:
        Path to the subdirectory on the caller's filesystem. This is either
        ``path`` if it is accessible, or a path to a local copy otherwise.
    """
    if not force_remote and os.path.exists(path):
        return path
    else:
        cache = _local_root(cache, url)
        return _acquire_file_raw(cache, path, url=url, overwrite=overwrite) 
