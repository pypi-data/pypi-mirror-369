"""Module for handling RPM packages."""

from __future__ import annotations

import gzip
import json
import lzma

from copy import deepcopy
from http import HTTPStatus
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final, cast

import jmespath
import xmltodict

from hoppr.models.manifest import Repository
from hoppr.models.types import PurlType
from pydantic import HttpUrl, parse_obj_as

from choppr.constants import DEFAULT_ARCH_RPM
from choppr.decorators import limit_recursion
from choppr.types import ChopprShares, RpmPackageData
from choppr.utils import HTTP, cache_file_outdated, get_auth_and_verify, log_repo_pulls, remove_parenthesis


if TYPE_CHECKING:
    from collections import OrderedDict

    from hoppr import Component


__all__ = ["RpmHandler"]
__author__ = "Jesse Boswell <jesse.a.boswell@lmco.com>"
__copyright__ = "Copyright (C) 2024 Lockheed Martin Corporation"
__license__ = "MIT License"


class RpmHandler:
    """Class to handle all RPM repository processing."""

    def __init__(self) -> None:
        self.allow_version_mismatch = ChopprShares.config.allow_version_mismatch
        self.cache_dir = ChopprShares.config.cache_dir / "rpm"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.file_provided_by: dict[Path, str] = {}
        self.repositories: dict[str, OrderedDict[str, Any]] = {}
        self.potential_packages: set[RpmPackageData] = set()
        self.required_packages: set[RpmPackageData] = set()
        self.nested_dependencies: set[RpmPackageData] = set()

    ####################################################################################################
    # Exported Methods
    ####################################################################################################

    def cache_repositories(self) -> bool:
        """Pull all of the metadata for RPM repositories provided in the config.

        Returns:
            bool: True when any repository was successfully pulled
        """
        if rpm_repository_urls := [
            parse_obj_as(HttpUrl, str(repo.url))
            for repo in parse_obj_as(list[Repository], ChopprShares.context.repositories[PurlType.RPM])
        ]:
            expected = len(rpm_repository_urls)
            ChopprShares.log.info(f"Caching {expected} RPM repositories...")

            for repo_url in rpm_repository_urls:
                if repo_return := self._get_remote_repo(repo_url):
                    repo_checksum, repo_data = repo_return
                    self.repositories[repo_checksum] = repo_data
            log_repo_pulls(expected, len(self.repositories), PurlType.RPM)

        return bool(len(self.repositories))

    def populate_potential_packages(self, file: Path, search_files: bool) -> None:
        """Get all potential packages that provide the given file.

        Arguments:
            file: Filename to search for
            search_files: Enable searching the files section of RPM repo metadata
        """
        ChopprShares.log.debug(f"Getting RPM associated with file: {file}")

        if packages := self._rpm_provides(file, search_files):
            for package in packages:
                ChopprShares.log.debug(f"Successfully found RPM: {package.name}")

                self.potential_packages.add(package)
                self.file_provided_by[file] = str(package)

    def populate_required_components(self) -> None:
        """Get the packages that provide components in the SBOM."""
        for component in ChopprShares.purl_components[PurlType.RPM]:
            if package := self._get_component_package(component):
                ChopprShares.log.debug(f"Package required: {package}")
                self.required_packages.add(package)

        ChopprShares.log.info(f"Found {len(self.required_packages)} required rpm packages")

        with self.cache_dir.joinpath("required-packages.txt").open("w", encoding="utf-8") as output:
            output.writelines([f"{pkg}\n" for pkg in sorted(self.required_packages, key=lambda p: p.name)])

    def populate_all_nested_dependencies(self) -> None:
        """Get all nested dependenceis of the required packages."""
        for package in deepcopy(self.required_packages):
            if package_requires := self._rpm_requires(package):
                ChopprShares.log.debug(f"Getting nested rpm dependencies for {package}")
                amount_before = len(self.nested_dependencies)
                self._populate_nested_dependencies(package_requires)
                ChopprShares.log.debug(
                    f"Found {len(self.nested_dependencies) - amount_before} new nested rpm dependencies"
                )

        ChopprShares.log.info(f"Found {len(self.nested_dependencies)} nested rpm dependencies")

        with self.cache_dir.joinpath("nested-dependencies.txt").open("w", encoding="utf-8") as file:
            file.writelines([f"{pkg}\n" for pkg in sorted(self.nested_dependencies, key=lambda p: p.name)])

    ####################################################################################################
    # Utility Methods
    ####################################################################################################

    def _get_remote_repo(self, repo_url: HttpUrl) -> tuple[str, OrderedDict[str, Any]] | None:
        repository_dir: Final[Path] = self.cache_dir.joinpath("repositories", f"{repo_url.host}{repo_url.path or ''}")
        repository_dir.mkdir(parents=True, exist_ok=True)

        cache_repomd = repository_dir / "repomd.json"
        repomd_url = parse_obj_as(HttpUrl, f"{repo_url}/repodata/repomd.xml")
        basic_auth, verify = get_auth_and_verify(repomd_url)

        if not cache_file_outdated(cache_repomd):
            ChopprShares.log.info(f"Loading repository data from {cache_repomd}...")
            with cache_repomd.open() as file:
                repomd_data = cast("OrderedDict[str, Any]", json.load(file))
        else:
            ChopprShares.log.info(f"Pulling repository data from {repomd_url}...")
            with HTTP.get(repomd_url, basic_auth, verify) as response:
                if response.status_code > HTTPStatus.MULTIPLE_CHOICES:
                    ChopprShares.log.error(f"Failed to pull repository: {response.content.decode()}")
                    return None

                repomd_data = xmltodict.parse(response.content)

                with cache_repomd.open("w") as file:
                    json.dump(repomd_data, file, indent=2)

        primary_checksum = jmespath.search(
            expression='[?"@type"==\'primary\'].checksum."#text"',
            data=repomd_data["repomd"]["data"],
        )
        primary_location = jmespath.search(
            expression='[?"@type"==\'primary\'].location."@href"',
            data=repomd_data["repomd"]["data"],
        )

        if isinstance(primary_checksum, list) and len(primary_checksum) == 1:
            cache_repository_file = repository_dir / f"{primary_checksum[0]}.json"

            # Use cached repository
            if cache_repository_file.is_file():
                with cache_repository_file.open() as file:
                    ChopprShares.log.info("Successfully loaded repository from cache")
                    return (primary_checksum[0], cast("OrderedDict[str, Any]", json.load(file)))
            # Pull repository
            elif isinstance(primary_location, list) and len(primary_location) == 1:
                primary_url = parse_obj_as(HttpUrl, f"{repo_url}/{primary_location[0]}")
                with HTTP.get(primary_url, basic_auth, verify) as primary_response:
                    if primary_response.status_code > HTTPStatus.MULTIPLE_CHOICES:
                        ChopprShares.log.error(f"Failed to pull repository: {response.content.decode()}")
                        return None

                    match primary_url:
                        case _ if primary_url.endswith(".gz"):
                            primary_xml = gzip.decompress(primary_response.content)
                        case _ if primary_url.endswith(".xz"):
                            primary_xml = lzma.decompress(primary_response.content)
                        case _ if primary_url.endswith(".xml"):
                            primary_xml = primary_response.content
                        case _:
                            ChopprShares.log.error(f"Unsupported file type found for primary repository: {primary_url}")
                            return None

                    ChopprShares.log.info("Successfully pulled repository data")

                    repo_data = xmltodict.parse(primary_xml)
                    # Write repository data to cache
                    with cache_repository_file.open("w") as file:
                        json.dump(repo_data, file, indent=2)
                    return (primary_checksum[0], repo_data)

        ChopprShares.log.error("Failed to get `location` and/or `checksum` from repository")
        return None

    def _rpm_provides(
        self, file: Path, search_files: bool = False, arch: str = DEFAULT_ARCH_RPM
    ) -> set[RpmPackageData]:
        if file in self.file_provided_by:
            return set()

        providers: set[RpmPackageData] = set()

        for repo in self.repositories.values():
            package_data: set[RpmPackageData] = {
                RpmPackageData(package)
                for package in jmespath.search(
                    expression=f"metadata.package[?arch == '{arch}' || arch == 'noarch']", data=repo
                )
            }
            if search_files:
                providers.update(self._search_files_section(file, package_data))

            if not providers:
                providers.update(self._search_rpm_provides_section(file, package_data))

        return providers

    def _get_component_package(self, component: Component) -> RpmPackageData | None:
        if not self.allow_version_mismatch:
            if not component.version:
                return None
            return next(
                (
                    package
                    for package in self.potential_packages
                    if str(package) == f"{component.name}-{component.version}"
                ),
                None,
            )
        return next(
            (package for package in self.potential_packages if str(package).startswith(component.name)),
            None,
        )

    @limit_recursion()
    def _populate_nested_dependencies(self, required_files: set[Path]) -> None:
        for file in required_files:
            if packages := {
                package
                for package in self._rpm_provides(file)
                if package not in self.required_packages | self.nested_dependencies
            }:
                for package in packages:
                    self.nested_dependencies.add(package)

                    if package_requires := self._rpm_requires(package):
                        self._populate_nested_dependencies(package_requires)

    @staticmethod
    def _rpm_requires(data: RpmPackageData) -> set[Path] | None:
        if requirements := jmespath.search(
            expression='format."rpm:requires"."rpm:entry"[*]."@name"',
            data=data.package,
        ):
            return {Path(requirement) for requirement in requirements if requirement}

        return None

    @staticmethod
    def _search_files_section(file: Path, package_data: set[RpmPackageData]) -> set[RpmPackageData]:
        """Search the files secetion of a given package for a given file.

        It will search files for an exact match, and for directories, it will check if the given
        file path starts with the directory path.

        Arguments:
            file: The file to search for
            package_data: The package to search

        Returns:
            set[RpmPackageData]: Packages containing the file
        """
        # Search files
        providers: set[RpmPackageData] = {
            data
            for data in package_data
            if jmespath.search(
                expression=(f"format.file[?type(@) == 'string' && @ == '{file}']"),
                data=data.package,
            )
        }
        if not providers:
            # Search directories
            for data in package_data:
                directories: list[str] | None = jmespath.search(
                    expression='format."file"[?"@type" == \'dir\']."#text"',
                    data=data.package,
                )
                if directories and any(file.is_relative_to(directory) for directory in directories):
                    providers.add(data)

        return providers

    @staticmethod
    def _search_rpm_provides_section(file: Path, package_data: set[RpmPackageData]) -> set[RpmPackageData]:
        """Search the rpm:provides secetion of a given package for a given file.

        Arguments:
            file: The file to search for
            package_data: The package to search

        Returns:
            set[RpmPackageData]: Packages containing the file
        """
        providers: set[RpmPackageData] = set()

        for data in package_data:
            # Search provides section
            package_provides: list[str] | None = jmespath.search(
                expression=('format."rpm:provides"."rpm:entry"[*]."@name"'),
                data=data.package,
            )
            if package_provides and any(remove_parenthesis(provides) == file.name for provides in package_provides):
                providers.add(data)

        return providers
