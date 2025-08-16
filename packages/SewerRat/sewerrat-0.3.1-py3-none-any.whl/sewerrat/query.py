from typing import Optional, List, Dict, Literal
import requests

from . import _utils as ut


def query(
    url: str,
    text: Optional[str] = None, 
    user: Optional[str] = None, 
    path: Optional[str] = None, 
    after: Optional[int] = None, 
    before: Optional[int] = None, 
    metadata: bool = True,
    number: int = 100, 
    on_truncation: Literal["message", "warning", "none"] = "message"
) -> List[Dict]:
    """
    Query the metadata in the SewerRat backend based on free text, the owner,
    creation time, etc. This function does not require filesystem access.

    Args:
        url:
            String containing the URL to the SewerRat REST API.

        text:
            String containing a free-text query, following the syntax described
            `here <https://github.com/ArtifactDB/SewerRat#Using-a-human-readable-text-query-syntax>`_.
            If None, no filtering is applied based on the metadata text.

        user:
            String containing the name of the user who generated the metadata.
            If None, no filtering is applied based on the user.

        path:
            String containing any component of the path to the metadata file.
            If None, no filtering is applied based on the path.

        after:
            Integer containing a Unix time in seconds, where only files newer
            than ``after`` will be retained. If None, no filtering is applied
            to remove old files.

        before:
            Integer containing a Unix time in seconds, where only files older
            than ``before`` will be retained. If None, no filtering is applied
            to remove new files.

        metadata:
            Whether to return the metadata of each file.
            This can be set to ``False`` for better performance if only the path is of interest.

        number:
            Integer specifying the maximum number of results to return.
            This can also be ``float("inf")`` to retrieve all available results.

        on_truncation:
            String specifying the action to take when the number of search results is capped by ``number``.

    Returns:
        List of dictionaries where each dictionary corresponds to a metadata file and contains:

        - ``path``, a string containing the path to the file.
        - ``user``, the identity of the file owner.
        - ``time``, the Unix time of most recent file modification.
        - ``metadata``, a list representing the JSON contents of the file.
          Only reported if ``metadata=True`` in the function call.
    """
    conditions = []

    if text is not None:
        conditions.append({ "type": "text", "text": text })

    if user is not None:
        conditions.append({ "type": "user", "user": user })

    if path is not None:
        conditions.append({ "type": "path", "path": path })

    if after is not None:
        conditions.append({ "type": "time", "time": int(after), "after": True })

    if before is not None:
        conditions.append({ "type": "time", "time": int(before) })

    if len(conditions) > 1:
        query = { "type": "and", "children": conditions }
    elif len(conditions) == 1:
        query = conditions[0]
    else:
        raise ValueError("at least one search filter must be present")

    original_number = number
    if on_truncation != "none":
        number += 1

    stub = "/query?translate=true"
    if not metadata:
        stub += "&metadata=false"

    collected = []
    while len(collected) < number:
        current_url = url + stub
        if number != float("inf"):
            current_url += "&limit=" + str(number - len(collected))

        res = requests.post(current_url, json=query)
        if res.status_code >= 300:
            raise ut.format_error(res)

        payload = res.json()
        collected += payload["results"]
        if "next" not in payload:
            break
        stub = payload["next"]

    return ut.handle_truncated_pages(on_truncation, original_number, collected)
