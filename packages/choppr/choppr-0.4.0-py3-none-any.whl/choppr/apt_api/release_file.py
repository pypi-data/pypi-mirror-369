"""ReleaseFile implementation."""

from __future__ import annotations

from choppr.apt_api._utils import get_value


__all__ = ["ReleaseFile"]
__author__ = "Jesse Boswell <jesse.a.boswell@lmco.com>"
__copyright__ = "Copyright (C) 2024 Lockheed Martin Corporation"
__license__ = "MIT License"


class ReleaseFile:
    """Class that represents a Release file.

    # Arguments
    content (str): the content of the Release file
    """

    def __init__(self, content: str) -> None:
        """Initialize an instance of ReleaseFile.

        Arguments:
            content: _description_
        """
        self.__content = content.strip()

    @property
    def origin(self) -> str:
        """Get the value of Origin.

        Returns:
            str: Origin value
        """
        return str(get_value(self.__content, "Origin"))

    @property
    def label(self) -> str:
        """Get the value of Label.

        Returns:
            str: Label value
        """
        return str(get_value(self.__content, "Label"))

    @property
    def suite(self) -> str:
        """Get the value of Suite.

        Returns:
            str: Suite value
        """
        return str(get_value(self.__content, "Suite"))

    @property
    def version(self) -> str:
        """Get the value of Version.

        Returns:
            str: Version value
        """
        return str(get_value(self.__content, "Version"))

    @property
    def codename(self) -> str:
        """Get the value of Codename.

        Returns:
            str: Codename value
        """
        return str(get_value(self.__content, "Codename"))

    @property
    def date(self) -> str:
        """Get the value of Date.

        Returns:
            str: Date value
        """
        return str(get_value(self.__content, "Date"))

    @property
    def architectures(self) -> list[str]:
        """Get the value of Architectures.

        Returns:
            str: Architectures value
        """
        return str(get_value(self.__content, "Architectures")).split()

    @property
    def components(self) -> list[str]:
        """Get the value of Components.

        Returns:
            str: Components value
        """
        return str(get_value(self.__content, "Components")).split()

    @property
    def description(self) -> str:
        """Get the value of Description.

        Returns:
            str: Description value
        """
        return str(get_value(self.__content, "Description"))
