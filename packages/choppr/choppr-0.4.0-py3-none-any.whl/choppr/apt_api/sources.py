"""Sources implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from hoppr import PurlType

from choppr.types import ChopprShares


if TYPE_CHECKING:
    from pydantic import HttpUrl

    from choppr.apt_api.binary_package import BinaryPackage
    from choppr.apt_api.repository import Repository


__all__ = ["Sources"]
__author__ = "Jesse Boswell <jesse.a.boswell@lmco.com>"
__copyright__ = "Copyright (C) 2024 Lockheed Martin Corporation"
__license__ = "MIT License"


class Sources:
    """Class that represents a collection of APT repositories."""

    def __init__(self, repositories: list[Repository]) -> None:
        """Initialize an instance of APTSources.

        Arguments:
            repositories: List of Repository objects
        """
        self.__repositories = repositories
        sbom_package_names = [component.name for component in ChopprShares.purl_components[PurlType.DEB]]
        self.packages = [
            package
            for repo in self.__repositories
            for package in repo.packages()
            if package.package in sbom_package_names
        ]

    def __getitem__(self, item: str) -> set[BinaryPackage]:
        """Get packages by name.

        Arguments:
            item: The package name

        Returns:
            set[BinaryPackage]: Packages with the given name
        """
        return self.get_packages_by_name(item)

    def get_package(self, name: str, version: str) -> BinaryPackage | None:
        """Return a single binary package.

        Arguments:
            name: Name of the package
            version: Version of the package

        Returns:
            BinaryPackage | None: The package if it exists
        """
        return next(
            (package for package in self.packages if package.package == name and package.version == version), None
        )

    def get_package_url(self, name: str, version: str) -> HttpUrl | None:
        """Return the URL of a single binary package.

        Arguments:
            name: Name of the package
            version: Version of the package

        Returns:
            HttpUrl | None: The package URL if it exists
        """
        for repo in self.__repositories:
            if url := repo.get_package_url(name, version):
                return url

        return None

    def get_packages_by_name(self, name: str) -> set[BinaryPackage]:
        """Return the list of available packages for a specific package name.

        Arguments:
            name: Name of the package

        Returns:
            set[BinaryPackage]: List of packages with the given name
        """
        return {package for package in self.packages if package.package == name}

    def get_packages_that_provide(self, filename: str) -> set[BinaryPackage]:
        """Determine what package, if any provides the given filename.

        Arguments:
            filename: The file to search for

        Returns:
            set[BinaryPackage]: The packages that provide the file
        """
        providers: set[BinaryPackage] = {
            package for package in self.packages for file in package.provides if filename.endswith(file)
        }
        return providers
