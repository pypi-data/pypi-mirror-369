from typing import Optional, Union, List, Dict, Literal
import requests
import urllib

from . import _utils as ut


def list_registered_directories(
    url: str,
    user: Optional[Union[str, bool]] = None,
    contains: Optional[str] = None,
    within: Optional[str] = None,
    prefix: Optional[str] = None,
    exists: Optional[bool] = None,
    number: int = 100, 
    on_truncation: Literal["message", "warning", "none"] = "message"
) -> List[Dict]:
    """
    List all registered directories in the SewerRat instance.

    Args:
        url:
            URL to the SewerRat REST API.

        user:
            Name of a user.
            If not ``None``, this is used to filter the returned directories based on the user who registered them.
            Alternatively, this can be set to ``True`` to automatically use the name of the current user.

        contains:
            String containing an absolute path. If not None, results are
            filtered to directories that contain this path.

        within:
            String containing an absolute path.
            If not ``None``, results are filtered to directories equal to or within this path.

        prefix:
            String containing an absolute path or a prefix thereof.
            If not ``None``, results are filtered to directories starting with this string.
            This is soft-deprecated and users should use ``within=`` instead.

        exists:
            Whether to only report directories that exist on the filesystem.
            If ``False``, only non-existent directories are reported, and if ``None``, no filtering is applied based on existence.

        number:
            Integer specifying the maximum number of results to return.
            This can also be ``float("inf")`` to retrieve all available results.

        on_truncation:
            String specifying the action to take when the number of search results is capped by ``number``.

    Returns:
        List of dictionaries where each dictionary corresponds to a registered directory and contains:

        - `path`, the path to the directory.
        - `user`, the name of the user who registered it.
        - `time`, the Unix epoch `time` of the registration.
        - `names`, a list containing the names of the metadata files to be indexed.
    """
    query = []
    if not user is None and user != False:
        if user == True:
            import getpass
            user = getpass.getuser()
        query.append("user=" + user)
    if not contains is None:
        query.append("contains_path=" + urllib.parse.quote_plus(contains))
    if not prefix is None:
        query.append("path_prefix=" + urllib.parse.quote_plus(prefix))
    if not within is None:
        query.append("within_path=" + urllib.parse.quote_plus(within))
    if exists is not None:
        if exists:
            qstr = "true"
        else:
            qstr = "false"
        query.append("exists=" + qstr)

    stub = "/registered"
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
