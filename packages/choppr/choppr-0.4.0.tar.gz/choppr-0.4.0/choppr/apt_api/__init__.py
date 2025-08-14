"""Package defining an interface to handle apt packages."""

from __future__ import annotations

from choppr.apt_api.binary_package import BinaryPackage
from choppr.apt_api.dependency import Dependency
from choppr.apt_api.packages_file import PackagesFile
from choppr.apt_api.release_file import ReleaseFile
from choppr.apt_api.repository import Repository
from choppr.apt_api.sources import Sources


__all__ = ["BinaryPackage", "Dependency", "PackagesFile", "ReleaseFile", "Repository", "Sources"]
__author__ = "Jesse Boswell <jesse.a.boswell@lmco.com>"
__copyright__ = "Copyright (C) 2024 Lockheed Martin Corporation"
__license__ = "MIT License"
