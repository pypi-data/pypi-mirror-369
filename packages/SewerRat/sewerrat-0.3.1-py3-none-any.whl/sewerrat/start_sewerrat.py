from typing import Optional, Tuple
import requests
import os
import time
from . import _utils as ut


test_api_process = None
test_api_port = None


def start_sewerrat(db: Optional[str] = None, port: Optional[int] = None, wait: float = 1, version: str = "1.3.1", whitelist: Optional[list] = None, overwrite: bool = False) -> Tuple[bool, int]:
    """
    Start a test SewerRat service.

    Args:
        db: 
            Path to a SQLite database. If None, one is automatically created.

        port:
            An available port. If None, one is automatically chosen.

        wait:
            Number of seconds to wait for the service to initialize before use.

        version:
            Version of the service to run.

        whitelist:
            List of users who can create symbolic links that will be followed by the SewerRat service.
            If None, this defaults to the current user and the owner of the temporary directory.

        overwrite:
            Whether to overwrite the existing Gobbler binary.

    Returns:
        A tuple indicating whether a new test service was created (or an
        existing instance was re-used) and its URL. If a service is already
        running, this function is a no-op and the configuration details of the
        existing service will be returned.
    """
    global test_api_port

    if test_api_process is not None:
        return False, "http://0.0.0.0:" + str(test_api_port)

    exe = _acquire_sewerrat_binary(version, overwrite)
    _initialize_sewerrat_process(exe, db, port, whitelist)

    time.sleep(1) # give it some time to spin up.
    return True, "http://0.0.0.0:" + str(test_api_port)


def _acquire_sewerrat_binary(version: str, overwrite: bool):
    import platform
    sysname = platform.system()
    if sysname == "Darwin":
        OS = "darwin"
    elif sysname == "Linux":
        OS = "linux"
    else:
        raise ValueError("unsupported operating system '" + sysname + "'")

    sysmachine = platform.machine()
    if sysmachine == "arm64":
        arch = "arm64"
    elif sysmachine == "x86_64":
        arch = "amd64"
    else:
        raise ValueError("unsupported architecture '" + sysmachine + "'")

    import appdirs
    cache = appdirs.user_data_dir("SewerRat", "aaron")
    desired = "SewerRat-" + OS + "-" + arch
    exe = os.path.join(cache, desired + "-" + version)

    if not os.path.exists(exe) or overwrite:
        url = "https://github.com/ArtifactDB/SewerRat/releases/download/" + version + "/" + desired

        import shutil
        os.makedirs(cache, exist_ok=True)
        tmp = exe + ".tmp"
        ut.download_file(url, tmp)
        os.chmod(tmp, 0o755)

        # Using a write-and-rename paradigm to provide some atomicity. Note
        # that renaming doesn't work across different filesystems so in that
        # case we just fall back to copying.
        try:
            shutil.move(tmp, exe)
        except:
            shutil.copy(tmp, exe)

    return exe
   

def _initialize_sewerrat_process(exe: str, db: Optional[str], port: Optional[int], whitelist: Optional[list]):
    if whitelist is None:
        import getpass
        whitelist = set([getpass.getuser()])
        import tempfile
        import pathlib
        tmp = pathlib.Path(tempfile.gettempdir())
        while True:
            whitelist.add(tmp.owner())
            parent = tmp.parent
            if parent == tmp:
                break
            tmp = parent
        whitelist = list(whitelist)

    if db is None:
        import tempfile
        host = tempfile.mkdtemp()
        db = os.path.join(host, "index.sqlite3")

    if port is None:
        import socket
        with socket.socket(socket.AF_INET) as s:
            s.bind(('0.0.0.0', 0))
            port = s.getsockname()[1]

    global test_api_port
    global test_api_process
    test_api_port = port

    import subprocess
    test_api_process = subprocess.Popen([ exe, "-db", db, "-port", str(port), "-whitelist", ",".join(whitelist) ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    import atexit
    atexit.register(stop_sewerrat)
    return


def stop_sewerrat():
    """
    Stop the SewerRat test service started by :py:func:`~.start_sewerrat`. If
    no test service was running, this function is a no-op.
    """
    global test_api_process
    global test_api_port

    if test_api_process is not None:
        test_api_process.terminate()
        test_api_process = None
        test_api_port = None
    return
