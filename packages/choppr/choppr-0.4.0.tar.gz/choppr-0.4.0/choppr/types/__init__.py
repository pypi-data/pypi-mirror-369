"""Package defining custom types used within Choppr."""

from __future__ import annotations

from choppr.types.choppr_config import ChopprConfig, ChopprConfigModel
from choppr.types.choppr_shares import ChopprShares
from choppr.types.deb_package_data import DebPackageData
from choppr.types.rpm_package_data import RpmPackageData


__all__ = ["ChopprConfig", "ChopprConfigModel", "ChopprShares", "DebPackageData", "RpmPackageData"]
__author__ = "Jesse Boswell <jesse.a.boswell@lmco.com>"
__copyright__ = "Copyright (C) 2024 Lockheed Martin Corporation"
__license__ = "MIT License"
