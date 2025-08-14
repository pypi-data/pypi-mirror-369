"""Constants used in Choppr."""

from __future__ import annotations

from typing import Final

from hoppr import PurlType


__all__ = [
    "ARCHIVE_EXTENSIONS",
    "COMPONENT_LIST_FORMATS",
    "DEB_HEADER_LENGTH",
    "DEFAULT_ARCH_DEB",
    "DEFAULT_ARCH_RPM",
    "DEFAULT_RECURSION_LIMIT",
    "LOG_HEADER_LENGTH",
]
__author__ = "Jesse Boswell <jesse.a.boswell@lmco.com>"
__copyright__ = "Copyright (C) 2024 Lockheed Martin Corporation"
__license__ = "MIT License"


ARCHIVE_EXTENSIONS: Final[list[str]] = [".bz2", ".gz", ".tgz", ".xz", ".zip"]
"""Supported extensions for output archive files."""

COMPONENT_LIST_FORMATS: Final[dict[PurlType, str]] = {
    PurlType.DEB: "{name}={version}",
    PurlType.NPM: "{name}@{version}",
    PurlType.RPM: "{name}-{version}",
}
"""Format for packages in component list output files."""

DEB_HEADER_LENGTH: Final[int] = 60
"""Length of headers in DEB package files."""

DEFAULT_ARCH_DEB: Final[str] = "amd64"
"""Default architecture for Debian repositories."""

DEFAULT_ARCH_RPM: Final[str] = "x86_64"
"""Default architecture for RPM repositories."""

DEFAULT_RECURSION_LIMIT: Final[int] = 10
"""Default depth to limit recursive functions to when used alongside the `limit_recursion` decorator."""

LOG_HEADER_LENGTH: Final[int] = 100
"""Length of headers in logs."""
