"""Utility functions used within the Choppr plugin.

Functions:
    - append_slash
    - http_get
    - remove_parenthesis

Classes:
    - RPM
"""

from __future__ import annotations

import bz2
import contextlib
import gzip
import lzma
import re
import tarfile
import time
import zipfile

from datetime import datetime
from http.client import RemoteDisconnected
from typing import TYPE_CHECKING

import requests

from hoppr import Credentials, PurlType
from pydantic import HttpUrl, SecretStr, parse_obj_as
from requests.auth import HTTPBasicAuth
from requests.exceptions import ProxyError

from choppr.constants import LOG_HEADER_LENGTH
from choppr.types import ChopprShares
from choppr.types.choppr_config import OperatingMode


if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from hoppr import Component
    from requests import Response


__all__ = [
    "HTTP",
    "cache_file_outdated",
    "compress_directory",
    "extract_archive",
    "get_auth_and_verify",
    "get_purl_type",
    "log_header",
    "log_repo_pulls",
    "output_list",
    "prepend_slash",
    "remove_parenthesis",
]
__author__ = "Jesse Boswell <jesse.a.boswell@lmco.com>"
__copyright__ = "Copyright (C) 2024 Lockheed Martin Corporation"
__license__ = "MIT License"


class HTTP:
    """Utility methods to handle HTTP requests."""

    @staticmethod
    def get(url: HttpUrl, auth: HTTPBasicAuth | None = None, verify: str | bool = True) -> Response:
        """Perform an HTTP get request with the provided parameters.

        Arguments:
            url: The URL to access
            auth: The credentials needed to access the URL (default None)
            verify: The certificate needed to access the URL (default True)

        Returns:
            Response: The response from the request
        """
        limits = ChopprShares.config.http_limits

        for attempt in range(limits.retries):
            if attempt > 0:
                time.sleep(limits.retry_interval)

            with contextlib.suppress(RemoteDisconnected):
                response = requests.get(
                    url,
                    auth=auth,
                    stream=True,
                    verify=verify,
                    timeout=limits.timeout,
                )
                if response.ok:
                    return response
        return response

    @staticmethod
    def download_raw(url: HttpUrl, auth: HTTPBasicAuth | None = None, verify: str | bool = True) -> bytes | None:
        """Download the raw content with the provided parameters.

        Arguments:
            url: The URL to access
            auth: The credentials needed to access the URL (default None)
            verify: The certificate needed to access the URL (default True)

        Returns:
            bytes | None: The raw content if the request is successful
        """
        response = HTTP.get(url, auth, verify)

        return response.content if response.ok else None

    @staticmethod
    def download(
        url: HttpUrl,
        auth: HTTPBasicAuth | None = None,
        verify: str | bool = True,
        encoding: str = "utf-8",
    ) -> str | None:
        """Download the content and decode with the provided parameters.

        Arguments:
            url: The URL to access
            auth: The credentials needed to access the URL (default None)
            verify: The certificate needed to access the URL (default True)
            encoding: The encoding to use when decoding the content (default "utf-8")

        Returns:
            str | None: The decoded content if the request is successful
        """
        with contextlib.suppress(ProxyError):
            if raw := HTTP.download_raw(url, auth, verify):
                return raw.decode(encoding)

        return None

    @staticmethod
    def download_compressed(
        url: HttpUrl,
        auth: HTTPBasicAuth | None = None,
        verify: str | bool = True,
        encoding: str = "utf-8",
    ) -> str | None:
        """Download the content, then decoompress and decode it with the provided parameters.

        Arguments:
            url: The URL to access
            auth: The credentials needed to access the URL (default None)
            verify: The certificate needed to access the URL (default True)
            encoding: The encoding to use when decoding the content (default "utf-8")

        Returns:
            str | None: The decompressed and decoded content if the request is successful
        """
        decompress: dict[str, Callable[[bytes], bytes]] = {
            "": lambda c: c,
            ".xz": lzma.decompress,
            ".gz": gzip.decompress,
            ".tgz": gzip.decompress,
            ".bzip2": bz2.decompress,
        }

        for suffix, method in decompress.items():
            with contextlib.suppress(ProxyError):
                if (raw := HTTP.download_raw(parse_obj_as(HttpUrl, f"{url}{suffix}"), auth, verify)) and (
                    output := method(raw).decode(encoding)
                ):
                    return output

        return None


def cache_file_outdated(file: Path) -> bool:
    """Check if the provided file is outdated.

    Arguments:
        file: File to check

    Returns:
        bool: True if the file is outdated, otherwise, false
    """
    if ChopprShares.config.mode == OperatingMode.CACHE:
        ChopprShares.log.debug(
            f"Running in cache mode. Refreshing file: {file.relative_to(ChopprShares.config.cache_dir)}"
        )
        return True

    if not file.is_file():
        ChopprShares.log.debug(
            f"Missing cache file will be downloaded: {file.relative_to(ChopprShares.config.cache_dir)}"
        )
        return True

    if isinstance(ChopprShares.config.cache_timeout, bool):
        ChopprShares.log.debug(f"Cache timeout is {'enabled' if ChopprShares.config.cache_timeout else 'disabled'}")
        return ChopprShares.config.cache_timeout

    tz = datetime.now().astimezone().tzinfo
    expiration_time = datetime.fromtimestamp(file.stat().st_mtime, tz) + ChopprShares.config.cache_timeout

    if outdated := expiration_time < datetime.now(tz):
        ChopprShares.log.debug(
            f"Outdated cache file will be refreshed: {file.relative_to(ChopprShares.config.cache_dir)}"
        )

    return outdated


def get_auth_and_verify(url: HttpUrl) -> tuple[HTTPBasicAuth | None, str | bool]:
    """Get the authentication credentials and certificate.

    Arguments:
        url: URL to get the credentials and certificate for

    Returns:
        tuple[HTTPBasicAuth | None, str | bool]: Credentials and certificate
    """
    if not url.host:
        return (None, True)

    auth = None
    credentials = Credentials.find(url.host)
    certificate = ChopprShares.config.certificates.get(url.host)
    if credentials and isinstance(credentials.password, SecretStr):
        ChopprShares.log.debug(f"Found credentials for host: {url.host}")
        auth = HTTPBasicAuth(username=credentials.username, password=credentials.password.get_secret_value())
    else:
        ChopprShares.log.debug(f"No credentials for host: {url.host}")

    return (auth, str(certificate) if certificate else True)


def get_purl_type(component: Component) -> PurlType | None:
    """Get the purl type for the provided component.

    Arguments:
        component: SBOM component

    Returns:
        PurlType | None: The purl type for the component
    """
    if component.purl and (match := re.match(r"pkg:(?P<type>.*?)/", component.purl)):
        with contextlib.suppress(KeyError):
            return PurlType(match["type"].upper())
    return None


def log_header(title: str) -> None:
    """Output a header to the log with the provided title, and padded with equal signs.

    Arguments:
        title: The header title
    """
    ChopprShares.log.info(f" {title} ".center(LOG_HEADER_LENGTH, "="))


def log_repo_pulls(expected: int, actual: int, purl_type: PurlType) -> None:
    """Log the success or failure of pulling a repository.

    Arguments:
        expected: The expected number of repositories
        actual: The number of repositories actually pulled
        purl_type: They repository type
    """
    match actual:
        case 0:
            ChopprShares.log.error(f"Failed to pull any {purl_type} repositories")
        case _ if actual == expected:
            ChopprShares.log.info(f"Successfully pulled all {purl_type} repositories")
        case _:
            ChopprShares.log.error(f"Failed to pull {expected - actual}/{expected} {purl_type} repositories")


def output_list(output_file: Path, items: list[str]) -> None:
    """Output list to the provided file.

    Arguments:
        output_file: Output file path
        items: List of strings to write to the file
    """
    with output_file.open("w", encoding="utf-8") as file:
        file.writelines([f"{item}\n" for item in items])


def prepend_slash(text: str) -> str:
    """Prepend a slash to a string that doesn't have one.

    Arguments:
        text: A string to prepend a slash to

    Returns:
        str: The string with a prepended slash
    """
    return f"/{text.removeprefix('/')}"


def remove_parenthesis(text: str) -> str:
    """Remove text within parenthesis, to include empty parenthesis.

    Arguments:
        text: Text to remove parenthesis from

    Returns:
        str: Text with parenthesis removed
    """
    return re.sub(r"\(.*?\)", "", text)


def compress_directory(archive: Path, input_dir: Path) -> None:
    """Compress all files in a given directory.

    Arguments:
        archive: The archive file to create
        input_dir: The directory to traverse and compress
    """
    match archive.suffix:
        case ".bz2":
            with tarfile.open(archive, "w:bz2") as archive_file:
                for file in input_dir.rglob("*"):
                    archive_file.add(file, file.relative_to(input_dir), False)
        case ".gz" | ".tgz":
            with tarfile.open(archive, "w:gz") as archive_file:
                for file in input_dir.rglob("*"):
                    archive_file.add(file, file.relative_to(input_dir), False)
        case ".xz":
            with tarfile.open(archive, "w:xz") as archive_file:
                for file in input_dir.rglob("*"):
                    archive_file.add(file, file.relative_to(input_dir), False)
        case ".zip":
            with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as archive_file:
                for file in input_dir.rglob("*"):
                    archive_file.write(file, file.relative_to(input_dir))


def _is_safe_to_extract(info: tarfile.TarInfo | zipfile.ZipInfo, output_dir: Path) -> bool:
    archived_file = info.name if isinstance(info, tarfile.TarInfo) else info.filename

    return output_dir.joinpath(archived_file).resolve().is_relative_to(output_dir.resolve())


def extract_archive(archive: Path, output_dir: Path) -> None:
    """Extract the contents of the given archive to the output directory.

    Arguments:
        archive: The archive to extract
        output_dir: The output directory
    """
    match archive.suffix:
        case ".bz2":
            with tarfile.open(archive, "r:bz2") as archive_file:
                tar_members = [
                    member for member in archive_file.getmembers() if _is_safe_to_extract(member, output_dir)
                ]
                archive_file.extractall(output_dir, tar_members)  # noqa: S202
        case ".gz" | ".tgz":
            with tarfile.open(archive, "r:gz") as archive_file:
                tar_members = [
                    member for member in archive_file.getmembers() if _is_safe_to_extract(member, output_dir)
                ]
                archive_file.extractall(output_dir, tar_members)  # noqa: S202
        case ".xz":
            with tarfile.open(archive, "r:xz") as archive_file:
                tar_members = [
                    member for member in archive_file.getmembers() if _is_safe_to_extract(member, output_dir)
                ]
                archive_file.extractall(output_dir, tar_members)  # noqa: S202
        case ".zip":
            with zipfile.ZipFile(archive, "r", zipfile.ZIP_DEFLATED) as archive_file:
                zip_members = [member for member in archive_file.filelist if _is_safe_to_extract(member, output_dir)]
                archive_file.extractall(output_dir, zip_members)  # noqa: S202
