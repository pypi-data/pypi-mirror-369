"""BinaryPackage implementation."""

from __future__ import annotations

import io
import os
import tarfile

from typing import Any

import zstandard as zstd

from pydantic import HttpUrl, parse_obj_as

from choppr.apt_api._utils import get_list, get_value
from choppr.apt_api.dependency import Dependency
from choppr.constants import DEB_HEADER_LENGTH


__all__ = ["BinaryPackage"]
__author__ = "Jesse Boswell <jesse.a.boswell@lmco.com>"
__copyright__ = "Copyright (C) 2024 Lockheed Martin Corporation"
__license__ = "MIT License"


def _flatten(matrix: list[Any]) -> list[str]:
    flat_list = []
    for element in matrix:
        if isinstance(element, list):
            flat_list.extend(_flatten(element))
        else:
            flat_list.append(element.strip())
    return flat_list


def _extract_archive(archive_file: bytes) -> dict[str, bytes]:
    archive = {}

    with io.BytesIO(archive_file) as f:
        # Read the ar file header (archive starts with "!<arch>\n")
        if f.read(8) != b"!<arch>\n":
            # Invalid ar archive
            return {}

        # Read the file metadata in the archive
        while (header := f.read(DEB_HEADER_LENGTH)) and len(header) >= DEB_HEADER_LENGTH:
            file_name = header[:16].strip().decode()
            file_size = int(header[48:58].strip())

            # Read the file content
            content = f.read(file_size)

            # Skip over any padding
            # (ar files are padded to even byte boundaries)
            if file_size % 2 != 0:
                f.seek(1, os.SEEK_CUR)

            # Write the file contents to the destination folder
            archive[file_name] = content

    return archive


def _get_deb_files(deb_file: bytes) -> list[str]:
    # Step 1: Extract the ar archive from the .deb file
    archive = _extract_archive(deb_file)

    # Step 2: Find the data.tar.gz or data.tar.xz in the extracted contents
    data_archive = None
    for filename in archive:
        if filename.startswith("data.tar"):
            data_archive = archive[filename]
            break

    # Step 3: Extract the data archive (the package contents)
    if data_archive:
        if ".zst" in filename:
            with io.BytesIO(data_archive) as f:
                dctx = zstd.ZstdDecompressor()
                with dctx.stream_reader(f) as reader:
                    buffer = io.BytesIO(reader.read())
                    buffer.seek(0)
                    fileobj = buffer
        else:
            fileobj = io.BytesIO(data_archive)

        # Extract .tar archive (either data.tar.xz or data.tar.gz)
        with tarfile.open(fileobj=fileobj) as tar:
            members = tar.getmembers()
            return [member.name[1:] for member in members if member.isfile()]
    else:
        return []


class BinaryPackage:  # noqa: PLR0904
    """Class that represents a binary Debian package."""

    def __init__(self, data: str, file_list: list[str] | None = None, package_url: str = "") -> None:
        """Initialize an instance of BinaryPackage.

        Arguments:
            data: The section of the Packages file for this specific package
            file_list: The list of files internal to this specific package (default None)
            package_url: The url of the package (default "")
        """
        if file_list is None:
            file_list = []
        self.__data = data.strip()
        self.file_list: list[str] = file_list
        self.package_url = parse_obj_as(HttpUrl, f"{package_url}/{get_value(self.__data, 'Filename')}")

        pre_depends: set[Dependency] = {Dependency(d) for d in get_list(self.__data, "Pre-Depends")}
        depends: set[Dependency] = {Dependency(d) for d in get_list(self.__data, "Depends")}
        self.depends = pre_depends.union(depends)

    @property
    def package(self) -> str:
        """Get the value of package.

        Returns:
            str: Package value
        """
        return str(get_value(self.__data, "Package"))

    @property
    def version(self) -> str:
        """Get the value of version.

        Returns:
            str: Version value
        """
        return str(get_value(self.__data, "Version"))

    @property
    def filename(self) -> str:
        """Get the value of filename.

        Returns:
            str: Filename value
        """
        return str(get_value(self.__data, "Filename"))

    @property
    def maintainer(self) -> str | None:
        """Get the value of maintainer.

        Returns:
            str | None: Maintainer value if it exists
        """
        return get_value(self.__data, "Maintainer")

    @property
    def original_maintainer(self) -> str | None:
        """Get the value of Original-Maintainer.

        Returns:
            str | None: Original-Maintainer value if it exists
        """
        return get_value(self.__data, "Original-Maintainer")

    @property
    def architecture(self) -> str | None:
        """Get the value of architecture.

        Returns:
            str | None: Architecture value if it exists
        """
        return get_value(self.__data, "Architecture")

    @property
    def multi_arch(self) -> str | None:
        """Get the value of Multi-Arch.

        Returns:
            str | None: Multi-Arch value if it exists
        """
        return get_value(self.__data, "Multi-Arch")

    @property
    def homepage(self) -> str | None:
        """Get the value of Homepage.

        Returns:
            str | None: Homepage value if it exists
        """
        return get_value(self.__data, "Homepage")

    @property
    def origin(self) -> str | None:
        """Get the value of Origin.

        Returns:
            str | None: Origin value if it exists
        """
        return get_value(self.__data, "Origin")

    @property
    def priority(self) -> str | None:
        """Get the value of Priority.

        Returns:
            str | None: Priority value if it exists
        """
        return get_value(self.__data, "Priority")

    @property
    def essential(self) -> bool | None:
        """Get the value of Essential.

        Returns:
            bool | None: Essential value if it exists
        """
        return bool((value := get_value(self.__data, "Essential")) and value.lower() == "yes")

    @property
    def build_essential(self) -> bool | None:
        """Get the value of Build-Essential.

        Returns:
            bool | None: Build-Essential value if it exists
        """
        return bool((value := get_value(self.__data, "Build-Essential")) and value.lower() == "yes")

    @property
    def section(self) -> str | None:
        """Get the value of Section.

        Returns:
            str | None: Section value if it exists
        """
        return get_value(self.__data, "Section")

    @property
    def provides(self) -> list[str]:
        """Get the value of Provides.

        Returns:
            list[str]: Provides value if it exists
        """
        from choppr.utils import HTTP  # noqa: PLC0415

        if self.file_list:
            return self.file_list
        if deb := HTTP.download_raw(self.package_url):
            self.file_list = _get_deb_files(deb)
        return self.file_list

    @property
    def replaces(self) -> list[str]:
        """Get the value of Replaces.

        Returns:
            list[str]: Replaces value if it exists
        """
        return get_list(self.__data, "Replaces")

    @property
    def breaks(self) -> list[str]:
        """Get the value of Breaks.

        Returns:
            list[str]: Breaks value if it exists
        """
        return get_list(self.__data, "Breaks")

    @property
    def recommends(self) -> list[str]:
        """Get the value of Recommends.

        Returns:
            list[str]: Recommends value if it exists
        """
        return get_list(self.__data, "Recommends")

    @property
    def suggests(self) -> list[str]:
        """Get the value of Suggests.

        Returns:
            list[str]: Suggests value if it exists
        """
        return get_list(self.__data, "Suggests")

    @property
    def conflicts(self) -> list[str]:
        """Get the value of Conflicts.

        Returns:
            list[str]: Conflicts value if it exists
        """
        return get_list(self.__data, "Conflicts")

    @property
    def installed_size(self) -> str | None:
        """Get the value of Installed-Size.

        Returns:
            str | None: Installed-Size value if it exists
        """
        return get_value(self.__data, "Installed-Size")

    @property
    def size(self) -> str | None:
        """Get the value of Size.

        Returns:
            str | None: Size value if it exists
        """
        return get_value(self.__data, "Size")

    @property
    def md5(self) -> str | None:
        """Get the value of MD5Sum.

        Returns:
            str | None: MD5Sum value if it exists
        """
        return get_value(self.__data, "MD5Sum")

    @property
    def sha1(self) -> str | None:
        """Get the value of SHA1.

        Returns:
            str | None: SHA1 value if it exists
        """
        return get_value(self.__data, "SHA1")

    @property
    def sha256(self) -> str | None:
        """Get the value of SHA256.

        Returns:
            str | None: SHA256 value if it exists
        """
        return get_value(self.__data, "SHA256")

    @property
    def description(self) -> str | None:
        """Get the value of Description.

        Returns:
            str | None: Description value if it exists
        """
        return get_value(self.__data, "Description")

    @property
    def description_md5(self) -> str | None:
        """Get the value of Description-md5.

        Returns:
            str | None: Description-md5 value if it exists
        """
        return get_value(self.__data, "Description-md5")

    @property
    def built_using(self) -> str | None:
        """Get the value of Built-Using.

        Returns:
            str | None: Built-Using value if it exists
        """
        return get_value(self.__data, "Built-Using")

    @property
    def source(self) -> str | None:
        """Get the value of Source.

        Returns:
            str | None: Source value if it exists
        """
        return get_value(self.__data, "Source")

    @property
    def task(self) -> str | None:
        """Get the value of Task.

        Returns:
            str | None: Task value if it exists
        """
        return get_value(self.__data, "Task")

    @property
    def supported(self) -> str | None:
        """Get the value of Supported.

        Returns:
            str | None: Supported value if it exists
        """
        return get_value(self.__data, "Supported")
