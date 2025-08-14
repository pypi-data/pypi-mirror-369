"""Class definition for RpmPackageData."""

from __future__ import annotations

from hashlib import sha256
from typing import Any


__all__ = ["RpmPackageData"]
__author__ = "Jesse Boswell <jesse.a.boswell@lmco.com>"
__copyright__ = "Copyright (C) 2024 Lockheed Martin Corporation"
__license__ = "MIT License"


class RpmPackageData:
    """Class containing frequently accessed information and the originating package.

    Members:
        - name
        - package
        - version
        - release_version
    """

    def __init__(self, package: dict[str, Any]) -> None:
        """Create an instance of PackageDetails.

        Arguments:
            package: The originating package dictionary
        """
        self.package = package
        self.name: str = package["name"]
        self.version: str = package["version"]["@ver"]
        self.release: str = package["version"]["@rel"]
        self.release_version = f"{self.version}-{self.release}"

    def __eq__(self, other: object) -> bool:
        match other:
            case RpmPackageData():
                return self.name == other.name and self.version == other.version
            case {"name": _, "version": {"@ver": _}}:
                return self.name == str(other["name"]) and self.version == str(other["version"]["@ver"])  # type: ignore[index]
            case _:
                return False

    def __hash__(self) -> int:
        sha = sha256()
        sha.update(self.name.encode())
        sha.update(self.version.encode())
        return int(sha.hexdigest(), 16)

    def __str__(self) -> str:
        return f"{self.name}-{self.release_version}"
