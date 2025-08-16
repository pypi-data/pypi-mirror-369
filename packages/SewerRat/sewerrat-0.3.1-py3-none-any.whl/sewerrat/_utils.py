import requests
import os
import time
import shutil
import warnings


def format_error(res):
    ctype = res.headers["content-type"]
    if ctype == "application/json":
        info = res.json()
        return requests.HTTPError(res.status_code, info["reason"])
    elif ctype == "text/plain":
        return requests.HTTPError(res.status_code, res.text)
    else:
        return requests.HTTPError(res.status_code)


def clean_path(path: str) -> str:
    # Don't use os.path.abspath, as this calls normpath; you would end up
    # resolving symlinks that the user wants to respect, e.g., for mounted
    # drives with aliased locations to network shares. Rather, we just do the
    # bare minimum required to obtain a clean absolute path, analogous to
    # Golang's filepath.Clean().
    if not path.startswith('/'):
        path = os.getcwd() + "/" + path

    components = path.split("/")
    keep = []
    for comp in components:
        if comp == "..":
            if len(keep):
                keep.pop()
        elif comp == "":
            # no-op, it's a redundant '//' or we're at the start.
            pass
        elif comp == ".":
            # no-op as well.
            pass
        else:
            keep.append(comp)

    keep = [""] + keep # add back the root.
    return '/'.join(keep)


def parse_remote_last_modified(res) -> time.time:
    if "last-modified" not in res.headers:
        warnings.warn("failed to extract the 'last-modified' header")
        return None
    try:
        mod_time = res.headers["last-modified"]
        return time.mktime(time.strptime(mod_time, "%a, %d %b %Y %H:%M:%S GMT")) - time.mktime(time.gmtime(0))
    except:
        warnings.warn("failed to parse the 'last-modified' header")
        return None


def download_file(url: str, dest: str):
    with requests.get(url, stream=True) as r:
        if r.status_code >= 300:
            raise format_error(r)
        with open(dest, "wb") as f:
            shutil.copyfileobj(r.raw, f)

        # Setting the correct modified time; we use the
        # current time as the access time for comparison.
        modtime = parse_remote_last_modified(r)
        if modtime is not None:
            os.utime(dest, (time.time(), modtime))


def handle_truncated_pages(on_truncation: str, original_number: int, collected: list) -> list:
    if on_truncation != "none":
        if original_number != float("inf") and len(collected) > original_number:
            msg = "truncated results to the first " + str(original_number) + " entries"
            if on_truncation == "warning":
                warnings.warn(msg)
            else:
                print(msg)
            collected = collected[:original_number]
    return collected
