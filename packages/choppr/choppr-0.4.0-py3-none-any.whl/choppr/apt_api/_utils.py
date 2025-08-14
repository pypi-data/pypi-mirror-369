from __future__ import annotations

import re


__all__ = ["get_list", "get_value"]
__author__ = "Jesse Boswell <jesse.a.boswell@lmco.com>"
__copyright__ = "Copyright (C) 2024 Lockheed Martin Corporation"
__license__ = "MIT License"


def get_value(content: str, key: str, default: str | None = None) -> str | None:
    """Extract a value from a Packages or Release file.

    Arguments:
        content: The content of the Packages/Release file
        key: The key to return the value for
        default: The default value to return if the key is not found

    Returns:
        str | None: Value for a given key
    """
    pattern = key + ": (.*)\n"
    return match[1] if (match := re.search(pattern, content)) else default


def get_list(content: str, key: str) -> list[str]:
    """Extract a list of values from a Packages or Release file.

    Arguments:
        content: The content of the Packages/Release file
        key: The key to return the value for

    Returns:
        list[str]: List of values for a given key
    """
    if field := get_value(content, key):
        return [d.strip() for d in field.split(",")]

    return []
