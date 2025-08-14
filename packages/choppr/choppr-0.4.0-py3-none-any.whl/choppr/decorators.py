"""Module with decorator functions."""

from __future__ import annotations

import functools

from typing import TYPE_CHECKING, Any, TypeVar

from choppr.types import ChopprShares


if TYPE_CHECKING:
    from collections.abc import Callable


__all__ = ["limit_recursion"]
__author__ = "Jesse Boswell <jesse.a.boswell@lmco.com>"
__copyright__ = "Copyright (C) 2024 Lockheed Martin Corporation"
__license__ = "MIT License"

T = TypeVar("T")


def limit_recursion(max_depth: int | None = None) -> Callable[[Callable[..., T]], Callable[..., T | None]]:
    """Limit the recursion depth of a function.

    Returns None instead of the function result if the limit is reached.

    Arguments:
        max_depth: The maximum allowed recursion depth (default None)

    Returns:
        A decorator function that wraps the original function
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T | None]:
        depth = 0

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T | None:  # noqa: ANN401
            nonlocal max_depth
            if max_depth is None:
                max_depth = ChopprShares.config.recursion_limit

            nonlocal depth
            depth += 1
            result = None if depth > max_depth else func(*args, **kwargs)
            depth -= 1
            return result

        return wrapper

    return decorator
