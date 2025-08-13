from __future__ import annotations
import argparse
import os
import urllib.request
import zipfile
from pathlib import Path

from tests.integration_tests.integration_test_util import get_s3_uri

TEMP_ZIP_NAME = '_tempcache.zip'


def apply_cache(filepath: str, cache_directory: str | None = None) -> None:
    """
    Extracts cache package at `filepath` and applies to `cache_directory`.
    :param filepath: Filepath of cache package. Deleted afterwards.
    :param cache_directory: Directory of cache. None for default.
    :return:
    """
    if cache_directory is None:
        cache_directory = get_cache_directory()
    with zipfile.ZipFile(filepath, 'r') as zip_ref:
        zip_ref.extractall(cache_directory)
    os.remove(filepath)


def download_and_apply_cache(name: str, cache_directory: str | None = None, version_id: str | None = None) -> None:
    """
    :param name: Filename (including extension) of cache package to download
    :param cache_directory: Directory to unpack cache package into
    :param version_id: The S3 object version to retrieve. None for latest.
    """
    # Download ZIP from public S3 bucket.
    uri = get_s3_uri(
        f'ci/caches/{name}',
        version_id=version_id
    )
    try:
        urllib.request.urlretrieve(uri, TEMP_ZIP_NAME)
        apply_cache(TEMP_ZIP_NAME, cache_directory)
    except Exception as exc:
        raise Exception(f'Failed to download cache from {uri} and extract to {cache_directory}.') from exc


def download_taxonomy_package(name: str, download_path: str, version_id: str | None = None) -> None:
    """
    :param name: Filename (including extension) of taxonomy package to download
    :param download_path: Location to save the package
    :param version_id: The S3 object version to retrieve. None for latest.
    """
    if os.path.exists(download_path):
        return
    os.makedirs(os.path.dirname(download_path), exist_ok=True)
    uri = get_s3_uri(
        f'ci/taxonomy_packages/{name}',
        version_id=version_id
    )
    try:
        urllib.request.urlretrieve(uri, download_path)
    except Exception as exc:
        raise Exception(f'Failed to download package from {uri} to {download_path}') from exc


def download_program() -> None:
    parser = argparse.ArgumentParser(
        prog='Download Cache',
        description='Downloads a cache package from the '
                    'public arelle S3 bucket and applies '
                    'it to the local environment cache.')
    parser.add_argument('--name', '-n', action='append', required=True,
                        help='Filename (including extension) of'
                             'cache package to download. '
                             'Optionally append :[versionId] to specify version of S3 object.')
    parser.add_argument('--print', action='store_true',
                        help='Print cache directory tree structure.')

    args = parser.parse_args()
    cache_directory = get_cache_directory()
    for name_arg in args.name:
        parts = name_arg.split(':', maxsplit=2)
        name = parts[0]
        version_id = None if len(parts) < 2 else parts[1]
        download_and_apply_cache(name, cache_directory, version_id=version_id)
    if args.print:
        for path in [
            os.path.join(dirpath, f)
            for (dirpath, dirnames, filenames) in os.walk(cache_directory)
            for f in filenames
        ]:
            print(path)


def get_cache_directory() -> str:
    r"""
    Determines the default cache directory
    ubuntu: "$XDG_CONFIG_HOME/arelle/cache"
    macos: ~/Library/Caches/Arelle
    windows: "$env:LOCALAPPDATA\Arelle\cache"
    :return: Cache directory path
    """
    xdg_config_home = os.getenv('XDG_CONFIG_HOME')
    if xdg_config_home:
        return os.path.join(xdg_config_home, 'arelle', 'cache')
    local_app_data = os.getenv('LOCALAPPDATA')
    if local_app_data:
        return os.path.join(local_app_data, 'Arelle', 'cache')
    return os.path.join(os.path.expanduser('~'), 'Library', 'Caches', 'Arelle')


if __name__ == '__main__':
    download_program()
