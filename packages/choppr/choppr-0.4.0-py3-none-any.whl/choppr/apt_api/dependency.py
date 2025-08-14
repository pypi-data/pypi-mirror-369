"""Dependency implementation."""

from __future__ import annotations

import re

from hashlib import sha256


__all__ = ["Dependency"]
__author__ = "Jesse Boswell <jesse.a.boswell@lmco.com>"
__copyright__ = "Copyright (C) 2024 Lockheed Martin Corporation"
__license__ = "MIT License"


class Dependency:
    """Class that represents a Debian package dependency."""

    def __init__(self, dependencies: str) -> None:
        split_dependencies = [d.strip() for d in dependencies.split("|")]
        self.alternates: set[Dependency] = set()

        for idx, dependency in enumerate(split_dependencies):
            if idx == 0:
                dependency_match = re.match(r"(?P<name>.*)\s\((?P<version>.*)\)", dependency)
                self.name = str(dependency_match["name"]) if dependency_match else dependency
                self.version = str(dependency_match["version"]) if dependency_match else ""
            else:
                self.alternates.add(Dependency(dependency))

    def __str__(self) -> str:
        primary = f"{self.name}{' ' if self.version else ''}{self.version}"
        if self.alternates:
            return f"{primary} (Alternates: {', '.join(str(a) for a in self.alternates)})"
        return primary

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Dependency) and self.name == other.name and self.version == other.version

    def __hash__(self) -> int:
        sha = sha256()
        sha.update(self.name.encode())
        sha.update(self.version.encode())
        return int(sha.hexdigest(), 16)
