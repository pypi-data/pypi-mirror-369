from typing import Optional, Literal, List, Dict
import requests
import urllib

from . import _utils as ut


def list_fields(
    url: str,
    pattern: Optional[str] = None,
    count: bool = False,
    number: int = 100, 
    on_truncation: Literal["message", "warning", "none"] = "message"
) -> List[Dict]:
    """
    List available fields in the SewerRat database.

    Args:
        url:
            URL to the SewerRat REST API.

        pattern:
            Pattern for filtering fields, using the usual ``*`` and ``?`` wildcards.
            Only fields matching to the pattern will be returned. 
            If ``None``, no filtering is performed.

        count:
            Whether to count the number of metadata files associated with each field.

        number:
            Integer specifying the maximum number of results to return.
            This can also be ``float("inf")`` to retrieve all available results.

        on_truncation:
            String specifying the action to take when the number of search results is capped by ``number``.

    Returns:
        List of dictionaries where each dictionary corresponds to a field and contains:

        - ``field``, string containing the field.
        - ``count``, integer specifying the number of files associated with the field.
          This is only present if ``count=True`` in the function call.
    """
    query = []
    if pattern is not None:
        query.append("pattern=" + urllib.parse.quote_plus(pattern))
    if count:
        query.append("count=true")

    stub = "/fields"
    use_question = True
    if len(query) > 0:
        stub += "?" + "&".join(query)
        use_question = False

    original_number = number
    if on_truncation != "none":
        number += 1

    collected = []
    while len(collected) < number:
        current_url = url + stub
        if number != float("inf"):
            sep = "&"
            if use_question:
                sep = "?"
            current_url += sep + "limit=" + str(number - len(collected))

        res = requests.get(current_url)
        if res.status_code >= 300:
            raise ut.format_error(res)
        payload = res.json()
        collected += payload["results"]

        if "next" not in payload:
            break
        stub = payload["next"]
        use_question = False

    return ut.handle_truncated_pages(on_truncation, original_number, collected)
