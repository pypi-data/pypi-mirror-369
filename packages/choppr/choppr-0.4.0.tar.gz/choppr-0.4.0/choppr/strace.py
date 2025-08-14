"""Module containing functions to call strace and analyze output."""

from __future__ import annotations

import re

from pathlib import Path


__all__ = ["get_files"]
__author__ = "Jesse Boswell <jesse.a.boswell@lmco.com>"
__copyright__ = "Copyright (C) 2024 Lockheed Martin Corporation"
__license__ = "Lockheed Martin Proprietary Information"


def resolve_relative_path(path: Path | str) -> Path:
    """Resolve the given path to its absolute form.

    Arguments:
        path: The relative path

    Returns:
        Path: The absolute path
    """
    absolute_path = str(path)
    relative_path_pattern = r"[\/|\\][^\/|\\]+?[\/|\\]\.\."

    while re.search(relative_path_pattern, absolute_path):
        absolute_path = re.sub(relative_path_pattern, "", absolute_path)

    return Path(absolute_path)


def get_files(strace_location: Path) -> set[Path]:
    """Get the list of touched files from strace.

    Arguments:
        strace_location: Output file from strace

    Returns:
        set[Path]: Set of touched files
    """
    with strace_location.open(encoding="utf-8") as file:
        text = file.read()

    flags = re.MULTILINE | re.IGNORECASE

    dir_regex = (
        r"^.*?"
        r"(?:(?:mkdir).*?"
        r"(?:(?:\'|\")(?P<mkdir>.*?)(?:\'|\")))"
        r"|"
        r"(?:(?:(?:\'|\")(?P<dirname>.*?)(?:\'|\"))"
        r"(?=.*?(?:S_IFDIR|O_DIRECTORY))(?!.*(?:ENOENT|unfinished)))"
    )
    dir_matches = re.finditer(dir_regex, text, flags)
    directories: set[Path] = {
        resolve_relative_path(dm.group(g))
        for dm in dir_matches
        for g in ["dirname", "mkdir"]
        if dm.group(g) is not None
    }

    regex = r"^.*?(?:(?:\'|\")(?P<filename>.*?)(?:\'|\"))(?!.*(?:S_IFDIR|ENOENT|O_DIRECTORY|unfinished))"
    files: set[Path] = {resolve_relative_path(match.group("filename")) for match in re.finditer(regex, text, flags)}
    return files - directories
