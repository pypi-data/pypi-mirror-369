# Changelog

## Version 0.3.0

- Added pagination options (`number=`, `on_truncation=`) to `list_registered_directories()`.
- Added a `metadata=` option to `query()` for improved performance when metadata is not required.
- Added the `list_fields()` and `list_tokens()` functions to provide the database's known vocabulary.

## Version 0.2.8

- Added `within=` to `list_registered_directories()` to search for directories within a specified path.
  This is more correct than `prefix=` and should be used in the vast majority of cases.

## Version 0.2.7

- Added `exists=` to `list_registered_directories()` to filter to (non-)existent directories.

## Version 0.2.6

- Support `number=float("inf")` to get all results in `query()`.

## Version 0.2.5

- Support non-blocking calls to the SewerRat API in `register()` and `deregister()`.

## Version 0.2.4

- Support more filters in `list_registered_directories()`.
- Improved synchronization of cache with the remote in `retrieve_file()`, `retrieve_directory()`.
- Emit diagnostics when the number of query results is truncated in `query()`.
- Added option for non-recursive listing of directory contents in `list_files()`.

## Version 0.2.3

- Added `list_registered_directories()` to list the registered directories.

## Version 0.2.2

- Check for updated files in the backend when doing remote calls in `retrieve_file()`, `retrieve_directory()`.
  If detected, a new download into the cache will be performed.

## Version 0.2.1

- Deprecated the retry loop for (de)registration as the backend is now responsible for polling.

## Version 0.2.0

- Added function to list files in a directory.
- Added helper functions to retrieve metadata, files, and directory contents.
- Added a retry loop for (de)registration on slow network shares.
- Clean path manually to avoid resolution of symlinks via normpath.

## Version 0.1.0

- New release of this package.
