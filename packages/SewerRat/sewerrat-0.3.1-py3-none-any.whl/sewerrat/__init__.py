import sys

if sys.version_info[:2] >= (3, 8):
    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.8`
    from importlib.metadata import PackageNotFoundError, version  # pragma: no cover
else:
    from importlib_metadata import PackageNotFoundError, version  # pragma: no cover

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = "SewerRat"
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

from .register import register
from .deregister import deregister
from .query import query
from .start_sewerrat import start_sewerrat, stop_sewerrat
from .list_files import list_files
from .retrieve_directory import retrieve_directory
from .retrieve_file import retrieve_file
from .retrieve_metadata import retrieve_metadata
from .list_registered_directories import list_registered_directories
from .list_tokens import list_tokens
from .list_fields import list_fields
