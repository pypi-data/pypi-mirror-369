"""Class definition for ChopprShares, a singleton class to share commonly access objects."""

from __future__ import annotations

from typing import TYPE_CHECKING

from hoppr import ComponentType, PurlType


if TYPE_CHECKING:
    from hoppr import Component, HopprContext, HopprLogger
    from typing_extensions import Self

    from choppr.types import ChopprConfig


__all__ = ["ChopprShares"]
__author__ = "Jesse Boswell <jesse.a.boswell@lmco.com>"
__copyright__ = "Copyright (C) 2024 Lockheed Martin Corporation"
__license__ = "MIT License"


class ChopprShares:
    """Singleton class to hold commonly accessed Choppr objects.

    Members:
        - components
        - config
        - context
        - log

    Methods:
        - initialized
    """

    _instance: Self | None = None

    def __new__(cls, config: ChopprConfig, context: HopprContext, log: HopprLogger) -> Self:
        """Initialize ChopprShares singleton.

        Arguments:
            config: Instance of ChopprConfig
            context: Instance of HopprContext
            log: Instance of HopprLogger

        Returns:
            Self: Singleton instance of ChopprShares
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)

            cls.purl_components: dict[PurlType, list[Component]] = {
                purl_type: [
                    component
                    for component in context.delivered_sbom.components
                    if component.purl and component.purl.lower().startswith(f"pkg:{purl_type.value.lower()}")
                ]
                for purl_type in PurlType
            }
            cls.file_components: set[Component] = {
                component
                for component in context.delivered_sbom.components
                if str(component.type) == ComponentType.FILE.value
            }
            cls.config: ChopprConfig = config
            cls.context: HopprContext = context
            cls.log: HopprLogger = log

            cls.log.debug("Purl component counts:")
            for purl_type, component_list in cls.purl_components.items():
                if component_count := len(component_list):
                    cls.log.debug(f"{purl_type.name}: {component_count}", indent_level=1)
            cls.log.debug(f"File component count: {len(cls.file_components)}")
        return cls._instance

    @classmethod
    def initialized(cls) -> bool:
        """Check if the class has been initialized.

        Returns:
            bool: True if the class is initialized, otherwise False
        """
        return cls._instance is not None
