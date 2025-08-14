"""Class definition for DebPackageData."""

from __future__ import annotations

from hashlib import sha256

from choppr.apt_api import BinaryPackage


__all__ = ["DebPackageData"]
__author__ = "Jesse Boswell <jesse.a.boswell@lmco.com>"
__copyright__ = "Copyright (C) 2024 Lockheed Martin Corporation"
__license__ = "MIT License"


class DebPackageData:
    """Class containing frequently accessed information and the originating package.

    Members:
        - name
        - package
        - version
    """

    def __init__(self, package: BinaryPackage) -> None:
        """Create an instance of DebPackageData.

        Arguments:
            package: The originating binary package
        """
        self.package = package
        self.name: str = package.package
        self.version: str = package.version
        self.provides: list[str] = package.provides

    def __eq__(self, other: object) -> bool:
        match other:
            case DebPackageData():
                return self.name == other.name and self.version == other.version
            case BinaryPackage():
                return self.name == str(other.package) and self.version == str(other.version)
            case _:
                return False

    def __hash__(self) -> int:
        sha = sha256()
        sha.update(self.name.encode())
        sha.update(self.version.encode())
        return int(sha.hexdigest(), 16)

    def __str__(self) -> str:
        return f"{self.name}-{self.version}"
