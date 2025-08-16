from typing import Dict, Any
import requests
import urllib
from . import _utils as ut


def retrieve_metadata(path: str, url: str) -> Dict[str, Any]:
    """
    Retrieve a single metadata entry in a registered directory from the
    SewerRat API.

    Args:
        path:
            Absolute path to a metadata file in a registered directory.

        url:
            URL to the SewerRat REST API.

    Returns:
        Dictionary containing:

        - ``path``, the path to the metadata file.
        - ``user``, the identity of the owning user.
        - ``time``, the Unix time at which the file was modified.
        - ``metadata``, the loaded metadata, typically another dictionary
          representing a JSON object.
    """
    res = requests.get(url + "/retrieve/metadata?path=" + urllib.parse.quote_plus(path))
    if res.status_code >= 300:
        raise ut.format_error(res)
    return res.json()
