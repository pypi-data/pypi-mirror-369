"""Module for handling DEB packages."""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from debian.debian_support import Version
from hoppr.models.manifest import Repository
from hoppr.models.types import PurlType
from pydantic import HttpUrl, parse_obj_as

from choppr import apt_api
from choppr.decorators import limit_recursion
from choppr.types import ChopprShares, DebPackageData
from choppr.utils import get_auth_and_verify, log_repo_pulls


if TYPE_CHECKING:
    from pathlib import Path

    from hoppr import Component

    from choppr.apt_api import BinaryPackage


__all__ = ["DebHandler"]
__author__ = "Jesse Boswell <jesse.a.boswell@lmco.com>"
__copyright__ = "Copyright (C) 2024 Lockheed Martin Corporation"
__license__ = "MIT License"


def _is_package_essential(package: BinaryPackage, build_essential: bool = False) -> bool:
    return bool(
        package.essential
        or (build_essential and package.build_essential)
        or (package.priority and package.priority.lower() == "required")
    )


class DebHandler:
    """Class to handle all DEB repository processing."""

    def __init__(self) -> None:
        self.allow_version_mismatch = ChopprShares.config.allow_version_mismatch
        self.cache_dir = ChopprShares.config.cache_dir / "deb"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.file_provided_by: dict[Path, str] = {}
        self.repositories: apt_api.Sources | None = None
        self.potential_packages: set[DebPackageData] = set()
        self.required_packages: set[DebPackageData] = set()
        self.nested_dependencies: set[DebPackageData] = set()

    ####################################################################################################
    # Exported Methods
    ####################################################################################################

    def cache_repositories(self) -> bool:
        """Pull all of the metadata for DEB repositories provided in the config.

        Returns:
            bool: True when any repository was successfully pulled
        """
        if not (
            deb_repository_urls := [
                str(repo.url)
                for repo in parse_obj_as(list[Repository], ChopprShares.context.repositories[PurlType.DEB])
            ]
        ):
            return False

        config_deb_repository_urls = [str(repo.url) for repo in ChopprShares.config.deb_repositories]

        if set(deb_repository_urls) != set(config_deb_repository_urls):
            ChopprShares.log.error(
                "DEB repository mismatch: All repository URLs in the `manifest.yml` file should also be in the "
                "`transfer.yml` file"
            )

            for url in deb_repository_urls:
                ChopprShares.log.debug(f"Manifest Repository URL: {url}")
            for url in config_deb_repository_urls:
                ChopprShares.log.debug(f"Transfer Repository URL: {url}")

            return False

        repositories: list[apt_api.Repository] = []
        expected = sum(len(repo.distributions) for repo in ChopprShares.config.deb_repositories)
        ChopprShares.log.info(f"Pulling {expected} DEB repositories...")

        repositories_dir: Final[Path] = self.cache_dir / "repositories"
        repositories_dir.mkdir(parents=True, exist_ok=True)

        for repo in ChopprShares.config.deb_repositories:
            repo_url = parse_obj_as(HttpUrl, repo.url)
            for distribution in repo.distributions:
                auth, verify = get_auth_and_verify(repo_url)
                repositories.append(
                    apt_api.Repository(
                        repo_url,
                        distribution.name,
                        distribution.components,
                        repositories_dir,
                        auth,
                        verify,
                    )
                )

        self.repositories = apt_api.Sources(repositories)

        log_repo_pulls(expected, len(repositories), PurlType.DEB)

        return bool(repositories)

    def populate_potential_packages(self, file: Path) -> None:
        """Get all potential packages that provide the given file.

        Arguments:
            file: Filename to search for
        """
        ChopprShares.log.debug(f"Getting Deb package associated with file: {file}")

        if self.repositories and (
            packages := {DebPackageData(package) for package in self.repositories.get_packages_that_provide(str(file))}
        ):
            for package in packages:
                ChopprShares.log.debug(f"Successfully found DEB: {package.name}")

                self.potential_packages.add(package)
                self.file_provided_by[file] = str(package)

    def populate_required_components(self) -> None:
        """Get the packages that provide components in the SBOM."""
        for component in ChopprShares.purl_components[PurlType.DEB]:
            if package := (
                ChopprShares.config.keep_essential_os_components and self._get_essential_package(component)
            ) or self._get_required_package(component):
                ChopprShares.log.debug(f"Package required: {package}")
                self.required_packages.add(package)

        ChopprShares.log.info(f"Found {len(self.required_packages)} required DEB packages")

        with self.cache_dir.joinpath("required-packages.txt").open("w", encoding="utf-8") as output:
            output.writelines([f"{pkg}\n" for pkg in sorted(self.required_packages, key=lambda p: p.name)])

    def populate_all_nested_dependencies(self) -> None:
        """Get all nested dependenceis of the required packages."""
        for package in self.required_packages:
            ChopprShares.log.info(f"Populating nested DEB dependencies for {package.name}")
            amount_before = len(self.nested_dependencies)
            self._populate_nested_dependencies(package)
            ChopprShares.log.info(
                f"Found {len(self.nested_dependencies) - amount_before} new nested DEB dependencies for {package.name}"
            )

        ChopprShares.log.info(f"Found {len(self.nested_dependencies)} nested DEB dependencies")

        with self.cache_dir.joinpath("nested-dependencies.txt").open("w", encoding="utf-8") as file:
            file.writelines([f"{pkg}\n" for pkg in sorted(self.nested_dependencies, key=lambda p: p.name)])

    ####################################################################################################
    # Utility Methods
    ####################################################################################################

    def _get_essential_package(self, component: Component) -> DebPackageData | None:
        if self.allow_version_mismatch:
            return next(
                (
                    DebPackageData(package)
                    for package in (
                        self.repositories.get_packages_by_name(component.name) if self.repositories else set()
                    )
                    if _is_package_essential(package)
                ),
                None,
            )

        if component.version and (
            self.repositories
            and (package := self.repositories.get_package(component.name, component.version))
            and _is_package_essential(package)
        ):
            return DebPackageData(package)

        return None

    def _get_required_package(self, component: Component) -> DebPackageData | None:
        if self.allow_version_mismatch:
            return next(
                (package for package in self.potential_packages if str(package).startswith(component.name)),
                None,
            )

        if component.version:
            return next(
                (
                    package
                    for package in self.potential_packages
                    if str(package) == f"{component.name}-{component.version}"
                ),
                None,
            )

        return None

    def _get_new_packages_by_name(self, name: str) -> set[DebPackageData]:
        return {
            DebPackageData(p)
            for p in (self.repositories.get_packages_by_name(name) if self.repositories else set())
            if p not in self.required_packages and p not in self.nested_dependencies
        }

    def _evaluate_potential_nested_dependencies(
        self, potential_packages: set[DebPackageData], version: str, dependency_stack: set[str]
    ) -> bool:
        success = False
        for package in potential_packages:
            if DebHandler._is_package_version_valid(package, version):
                self.nested_dependencies.add(package)
                dependency_stack.add(package.name)
                self._populate_nested_dependencies(package, dependency_stack)
                success = True

        return success

    @limit_recursion()
    def _populate_nested_dependencies(self, data: DebPackageData, dependency_stack: set[str] | None = None) -> None:
        ChopprShares.log.debug(f"Dependencies for {data.name}: {', '.join([str(d) for d in data.package.depends])}")
        if not dependency_stack:
            dependency_stack = {data.name}

        for dependency in [d for d in data.package.depends if d.name not in dependency_stack]:
            if not self._evaluate_potential_nested_dependencies(
                self._get_new_packages_by_name(dependency.name), dependency.version, dependency_stack
            ):
                any(
                    self._evaluate_potential_nested_dependencies(
                        self._get_new_packages_by_name(alternate.name), alternate.version, dependency_stack
                    )
                    for alternate in dependency.alternates
                )

    @staticmethod
    def _get_max_version(versions: list[str]) -> tuple[bool, Version | None]:
        return next(
            (("=" in v, Version(v.replace("<", "").replace("=", "").strip())) for v in versions if "<" in v),
            (False, None),
        )

    @staticmethod
    def _get_min_version(versions: list[str]) -> tuple[bool, Version | None]:
        return next(
            (("=" in v, Version(v.replace(">", "").replace("=", "").strip())) for v in versions if ">" in v),
            (False, None),
        )

    @staticmethod
    def _package_version_within_max(package: DebPackageData, versions: list[str]) -> bool:
        can_be_equal, max_version = DebHandler._get_max_version(versions)

        if max_version is None:
            ChopprShares.log.debug(f"No valid maximum version: {', '.join(versions)}")
            return False

        return (can_be_equal and Version(package.version) <= max_version) or (
            not can_be_equal and Version(package.version) < max_version
        )

    @staticmethod
    def _package_version_within_min(package: DebPackageData, versions: list[str]) -> bool:
        can_be_equal, min_version = DebHandler._get_min_version(versions)

        if min_version is None:
            ChopprShares.log.debug(f"No valid minimum version: {', '.join(versions)}")
            return False

        return (can_be_equal and Version(package.version) >= min_version) or (
            not can_be_equal and Version(package.version) > min_version
        )

    @staticmethod
    def _package_version_within_range(package: DebPackageData, versions: list[str]) -> bool:
        within_max = DebHandler._package_version_within_max(package, versions)
        within_min = DebHandler._package_version_within_min(package, versions)

        return within_max and within_min

    @staticmethod
    def _is_package_version_valid(package: DebPackageData, version: str) -> bool:
        if version.startswith("="):
            exact_version = Version(version.replace("=", "").strip())
            return Version(package.version) == exact_version
        if all(sign in version for sign in ["<", ">"]):
            return DebHandler._package_version_within_range(package, version.split(","))
        if version.startswith("<"):
            return DebHandler._package_version_within_max(package, [version])
        if version.startswith(">"):
            return DebHandler._package_version_within_min(package, [version])

        return True
