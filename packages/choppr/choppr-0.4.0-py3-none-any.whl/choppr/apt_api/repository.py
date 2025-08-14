"""Repository implementation."""

from __future__ import annotations

import json
import posixpath

from collections import defaultdict
from typing import TYPE_CHECKING

from pydantic import HttpUrl, parse_obj_as

from choppr.apt_api.packages_file import PackagesFile
from choppr.apt_api.release_file import ReleaseFile
from choppr.constants import DEFAULT_ARCH_DEB
from choppr.types.choppr_config import OperatingMode
from choppr.types.choppr_shares import ChopprShares
from choppr.utils import HTTP, cache_file_outdated


if TYPE_CHECKING:
    from pathlib import Path

    from requests.auth import HTTPBasicAuth

    from choppr.apt_api.binary_package import BinaryPackage


__all__ = ["Repository"]
__author__ = "Jesse Boswell <jesse.a.boswell@lmco.com>"
__copyright__ = "Copyright (C) 2024 Lockheed Martin Corporation"
__license__ = "MIT License"


class Repository:
    """Class that represents a single APT repository.

    Examples:
    ```python
    APTRepository("http://archive.ubuntu.com/ubuntu", "bionic", "main")
    APTRepository("https://pkg.jenkins.io/debian/", "binary")
    ```
    """

    repositories: list[str]

    def __init__(  # noqa: PLR0913, PLR0917
        self,
        url: HttpUrl,
        dist: str,
        components: list[str],
        cache_dir: Path,
        auth: HTTPBasicAuth | None = None,
        verify: str | bool = True,
        arch: str = DEFAULT_ARCH_DEB,
    ) -> None:
        """Initialize an instance of APTRepository.

        Arguments:
            url: The base URL of the repository
            dist: The target distribution
            components: The target components
            cache_dir: The cache directory to store cache files in
            auth: The credentials needed to access the URL (default None)
            verify: The certificate needed to access the URL (default True)
            arch: The CPU archetecture of the target (default DEFAULT_DEB_ARCH)
        """
        self.url = url
        self.auth = auth
        self.verify = verify
        self.dist = dist
        self.components = components

        self.repository_dir = cache_dir / f"{self.url.host}/dists/{self.dist}"
        self.repository_dir.mkdir(parents=True, exist_ok=True)

        self._cache_content_file = self.repository_dir / f"contents-{arch}.json"
        self._cache_release_file = self.repository_dir / "release"

        self._release_file: ReleaseFile | None = None
        self._packages: dict[str, list[BinaryPackage]] = {}

        if cache_file_outdated(self._cache_content_file):
            obj = None
            content_file_url = parse_obj_as(
                HttpUrl,
                posixpath.join(self.url, "dists", self.dist, f"Contents-{arch}"),
            )

            if obj := HTTP.download_compressed(content_file_url, self.auth, self.verify):
                content_file_data = obj
            else:
                content_file_url = parse_obj_as(HttpUrl, posixpath.join(self.url, f"Contents-{arch}"))
                content_file_data = (
                    obj if (obj := HTTP.download_compressed(content_file_url, self.auth, self.verify)) else ""
                )

            file_list: dict[str, list[str]] = defaultdict(list[str])

            if content_file_data:
                for v, k in [
                    (file.split()[0], file.split()[1].split("/")[-1]) for file in content_file_data.strip().split("\n")
                ]:
                    file_list[k].append(v)

            with self._cache_content_file.open("w") as f:
                json.dump(file_list, f, cls=json.JSONEncoder, indent=2)

        # Populate additional cache files
        if ChopprShares.config.mode == OperatingMode.CACHE:
            _ = self.release_file
            _ = self.packages()

    def __getitem__(self, item: str) -> list[BinaryPackage]:
        """Get packages by name.

        Arguments:
            item: The package name

        Returns:
            list[BinaryPackage]: Packages with the given name
        """
        return self.get_packages_by_name(item)

    @property
    def all_components(self) -> list[str]:
        """Returns the all components of this repository.

        Returns:
            list[str]: List of components in the repository
        """
        return self.release_file.components if self.release_file else []

    @property
    def release_file(self) -> ReleaseFile | None:
        """Returns the Release file of this repository.

        Returns:
            ReleaseFile | None: The release file if it exists
        """
        if cache_file_outdated(self._cache_release_file):
            url = parse_obj_as(HttpUrl, posixpath.join(self.url, "dists", self.dist, "Release"))
            if release_content := HTTP.download(url, self.auth, self.verify):
                with self._cache_release_file.open("w", encoding="utf-8") as f:
                    f.write(release_content)
                self._release_file = ReleaseFile(release_content)
        elif not self._release_file:
            with self._cache_release_file.open(encoding="utf-8") as f:
                self._release_file = ReleaseFile(f.read())

        return self._release_file

    def packages(self, arch: str = DEFAULT_ARCH_DEB) -> list[BinaryPackage]:
        """Return all binary packages of this repository.

        Arguments:
            arch: The architecture to return packages for (default DEFAULT_DEB_ARCH)

        Returns:
            list[BinaryPackage]: List of BinaryPackages for given architecture
        """
        if not self._packages.get(arch):
            self._packages[arch] = []

            for component in self.components:
                cache_package_file = self.repository_dir / f"{component}-packages-{arch}"

                if cache_file_outdated(cache_package_file):
                    package_file_url = parse_obj_as(
                        HttpUrl,
                        posixpath.join(
                            self.url,
                            "dists",
                            self.dist,
                            component,
                            f"binary-{arch}",
                            "Packages",
                        ),
                    )

                    if package_file_content := HTTP.download_compressed(package_file_url, self.auth, self.verify):
                        with cache_package_file.open("w", encoding="utf-16") as file:
                            file.write(package_file_content.strip())

                self._packages[arch].extend(
                    PackagesFile(cache_package_file, self._cache_content_file, self.url).packages
                )

        return self._packages[arch]

    def get_package(self, name: str, version: str) -> BinaryPackage | None:
        """Return a single binary package.

        Arguments:
            name: Name of the package
            version: Version of the package

        Returns:
            BinaryPackage | None: Package with the given name and version
        """
        return next(
            (package for package in self.packages() if package.package == name and package.version == version),
            None,
        )

    def get_package_url(self, name: str, version: str) -> HttpUrl | None:
        """Return the URL for a single binary package.

        Arguments:
            name: Name of the package
            version: Version of the package

        Returns:
            HttpUrl | None: URL for package
        """
        if package := self.get_package(name, version):
            url: HttpUrl = parse_obj_as(HttpUrl, posixpath.join(self.url, package.filename))
            return url

        return None

    def get_packages_by_name(self, name: str) -> list[BinaryPackage]:
        """Return the list of available packages for a specific package name.

        Arguments:
            name: Name of the package

        Returns:
            list[BinaryPackage]: List of packages that match the given name
        """
        return [package for package in self.packages() if package.package == name]

    def get_common_packages(self, packages: list[str]) -> list[str]:
        """Return the list of packages that are in the repository and given list.

        Arguments:
            packages: String list of packages in SBOM

        Returns:
            list[str]: List of packages that are in common with the provided list
        """
        return list(set(packages) & {package.package for package in self.packages()})
