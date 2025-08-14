"""Class definition for ChopprConfig."""

from __future__ import annotations

import re

from datetime import timedelta
from enum import Enum
from hashlib import sha256
from pathlib import Path
from typing import Any

from hoppr import Component, PurlType
from pydantic import (  # noqa: TC002
    BaseModel,
    Field,
    HttpUrl,
    PositiveFloat,
    PositiveInt,
    PrivateAttr,
    parse_obj_as,
    validator,
)

from choppr import strace
from choppr.constants import ARCHIVE_EXTENSIONS, COMPONENT_LIST_FORMATS, DEFAULT_RECURSION_LIMIT


__all__ = ["ChopprConfig", "ChopprConfigModel", "DebianDistribution", "DebianRepository", "OperatingMode"]
__author__ = "Jesse Boswell <jesse.a.boswell@lmco.com>"
__copyright__ = "Copyright (C) 2024 Lockheed Martin Corporation"
__license__ = "MIT License"


def _validate_file_path(value: Path) -> Path:
    if not value.is_file():
        raise ValueError(f"File does not exist: {value}")
    return value


def _validate_http_url(value: str) -> HttpUrl:
    return parse_obj_as(HttpUrl, value.rstrip("/"))  # type: ignore[no-any-return]


def _validate_regex(value: str) -> re.Pattern[str]:
    try:
        return re.compile(value)
    except re.error as e:
        raise ValueError(f"Invalid regular expression: {value}") from e


def _default_excluded_components() -> dict[PurlType, ExcludedComponentsFile]:
    return {
        purl_type: ExcludedComponentsFile(
            file=Path(f"choppr-excluded-components-{purl_type.name.lower()}.txt"),
            component_format=COMPONENT_LIST_FORMATS.get(purl_type, "{name}={version}"),
        )
        for purl_type in PurlType
    }


class Certificate(BaseModel):
    # Required Attributes
    url: str
    certificate: Path

    # Validators
    _validate_certificate = validator("certificate", allow_reuse=True)(_validate_file_path)


class DebianDistribution(BaseModel):
    """Class representation for a debian distribution, to include its name and components.

    Members:
        - name
        - components
    """

    name: str
    components: list[str] = ["main", "restricted", "universe", "multiverse"]


class DebianRepository(BaseModel):
    """Class representation for a debian repository, to include its URL and distributions.

    Members:
        - url
        - distributions
    """

    url: HttpUrl
    distributions: list[DebianDistribution]

    _validate_url = validator("url", pre=True, allow_reuse=True)(_validate_http_url)


class HttpRequestLimits(BaseModel):
    """Class with values to configure HTTP request limits.

    Members:
        - retries
        - retry_interval
        - timeout
    """

    retries: PositiveInt = 3
    retry_interval: PositiveFloat = 5.0
    timeout: PositiveFloat = 60.0


class ExcludedComponentsFile(BaseModel):
    """The filename to output excluded components to, and what format to write them as.

    Members:
        - file
        - format
    """

    file: Path
    component_format: str = ""


class OutputFiles(BaseModel):
    """Class with values for the output files for Choppr.

    Members:
        - cache_archive
        - excluded_components
    """

    cache_archive: Path = Field(default_factory=lambda: Path.cwd() / "choppr-cache.tar.gz")
    excluded_components: dict[PurlType, ExcludedComponentsFile] = Field(default_factory=_default_excluded_components)

    @validator("cache_archive")
    @classmethod
    def _validate_cache_archive(cls, value: Path | None) -> Path | None:
        if value and value.suffix not in ARCHIVE_EXTENSIONS:
            raise ValueError(
                f"Invalid cache_archive value: {value} - Accepted extensions: {', '.join(ARCHIVE_EXTENSIONS)}"
            )

        return value

    @validator("excluded_components", pre=True)
    @classmethod
    def _validate_excluded_components(cls, value: dict[str, dict[str, str]]) -> dict[PurlType, ExcludedComponentsFile]:
        excluded_components: dict[PurlType, ExcludedComponentsFile] = _default_excluded_components()
        try:
            for purl, file_and_format in value.items():
                purl_type = PurlType[purl.upper()]
                excluded_components_file = ExcludedComponentsFile.parse_obj(file_and_format)
                excluded_components[purl_type].file = excluded_components_file.file
                if excluded_components_file.component_format:
                    excluded_components[purl_type].component_format = excluded_components_file.component_format
        except KeyError as e:
            raise ValueError(
                f"Invalid purl type: {e} - Accpeted values: [{', '.join(m.name for m in PurlType)}]"
            ) from e
        else:
            return excluded_components


class PackagePattern(BaseModel):
    """Class with the name, version, and purl type for a package.

    Members:
        - name
        - version
    """

    name: re.Pattern  # type: ignore[type-arg] # Pydantic v1 doesn't properly support re.Pattern
    version: re.Pattern  # type: ignore[type-arg] # Pydantic v1 doesn't properly support re.Pattern

    _validate_patterns = validator("name", "version", pre=True, allow_reuse=True)(_validate_regex)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, PackagePattern):
            return self.name == other.name and self.version == other.version
        if isinstance(other, Component):
            return bool(
                self.name.match(other.name)
                and (
                    (other.version is None and self.version.match(""))
                    or (other.version and self.version.match(other.version))
                )
            )
        return False

    def __hash__(self) -> int:
        sha = sha256()
        sha.update(str(self.name).encode())
        sha.update(str(self.version).encode())
        return int(sha.hexdigest(), 16)


class OperatingMode(str, Enum):
    """Modes to change the behavior of Choppr."""

    RUN = "run"
    """Run choppr normally, and filter the SBOM"""
    CACHE = "cache"
    """Only create the cache for Choppr, and export it as an archive."""


class ChopprConfigModel(BaseModel):
    """Class to validate and parse the configuration values provided to ChopprPlugin.

    Members:
        - strace_results
        - allow_version_mismatch
        - allowlist
        - archive_cache
        - cache_dir
        - cache_input
        - cache_timeout
        - certificates
        - clear_cache
        - deb_repositories
        - delete_excluded
        - denylist
        - http_limits
        - keep_essential_os_components
        - mode
        - output_files
        - recursion_limit
        - strace_regex_excludes

    Methods:
        - strace_files
    """

    HttpRequestLimits.update_forward_refs()

    # Operating mode
    mode: OperatingMode = OperatingMode.RUN

    # Required Attributes [RUN]
    strace_results: Path | None = None
    # Optional Attributes
    allow_version_mismatch: bool = False
    allowlist: dict[PurlType, set[PackagePattern]] = Field(default={})
    archive_cache: bool = False
    cache_dir: Path = Field(default_factory=lambda: Path.cwd() / ".cache" / "choppr")
    cache_input: Path | None = None
    cache_timeout: timedelta | bool = Field(default=timedelta(days=7))
    certificates: dict[str, Path] = Field(default={})
    clear_cache: bool = False
    deb_repositories: list[DebianRepository] = Field(default=[])
    delete_excluded: bool = True
    denylist: dict[PurlType, set[PackagePattern]] = Field(default={})
    http_limits: HttpRequestLimits = Field(default=HttpRequestLimits())
    keep_essential_os_components: bool = False
    output_files: OutputFiles = Field(default=OutputFiles())
    recursion_limit: PositiveInt = DEFAULT_RECURSION_LIMIT
    strace_regex_excludes: list[re.Pattern] = Field(default=[])  # type: ignore[type-arg] # Pydantic v1 doesn't properly support re.Pattern
    # Private Attributes
    _strace_files: set[Path] = PrivateAttr(default=set())

    # Validators
    _validate_strace_regex_excludes = validator("strace_regex_excludes", pre=True, each_item=True, allow_reuse=True)(
        _validate_regex
    )

    @validator("strace_results")
    @classmethod
    def _validate_strace_results(cls, value: Path, values: dict[str, Any]) -> Path | None:
        match values.get("mode"):
            case OperatingMode.RUN:
                if value is None:
                    raise ValueError("Invalid configuration: 'strace_results' is required in run mode")
                return _validate_file_path(value)
            case OperatingMode.CACHE:
                return None
        return None

    @validator("cache_input")
    @classmethod
    def _validate_cache_input(cls, value: Path | None) -> Path | None:
        if value:
            if value.suffix in ARCHIVE_EXTENSIONS:
                return _validate_file_path(value)
            raise ValueError(
                f"Invalid cache_input value: {value} - Accepted extensions: {', '.join(ARCHIVE_EXTENSIONS)}"
            )
        return value

    @validator("cache_timeout", pre=True)
    @classmethod
    def _validate_cache_timeout(cls, cache_timeout: str) -> timedelta | bool:
        timedelta_pattern = re.compile(r"^(?P<duration>\d+)\s?(?P<unit>d|h|m|s)$", re.IGNORECASE)
        boolean_pattern = re.compile(r"^(?P<true>true)|(?P<false>false)$", re.IGNORECASE)

        timeout_match = timedelta_pattern.match(cache_timeout)
        boolean_match = boolean_pattern.match(cache_timeout)

        error_message = "Invalid 'cache_timeout' value: Expected a number followed by a unit (d, h, m, s) or boolean"

        if not (timeout_match or boolean_match):
            raise ValueError(error_message)

        if boolean_match:
            return False if boolean_match["false"] else timedelta()

        timeout_duration = int(timeout_match["duration"])  # type: ignore[index]
        timeout_unit = timeout_match["unit"].lower()  # type: ignore[index]

        unit_map = {
            "d": "days",
            "h": "hours",
            "m": "minutes",
            "s": "seconds",
        }

        if timeout_unit not in unit_map:
            raise ValueError(error_message)

        return timedelta(**{unit_map[timeout_unit]: timeout_duration})

    @validator("certificates", pre=True)
    @classmethod
    def _validate_certificates(cls, certificates: list[dict[str, str]]) -> dict[str, Path]:
        certificate_map: dict[str, Path] = {}

        for certificate in certificates:
            c = Certificate.parse_obj(certificate)
            certificate_map[c.url] = c.certificate

        return certificate_map

    @validator("allowlist", "denylist", pre=True)
    @classmethod
    def _validate_exception_list(cls, value: dict[str, set[PackagePattern]]) -> dict[PurlType, set[PackagePattern]]:
        try:
            return {PurlType[purl_type.upper()]: packages for purl_type, packages in value.items()}
        except KeyError as e:
            raise ValueError(
                f"Invalid purl type: {e} - Accpeted values: [{', '.join(m.name for m in PurlType)}]"
            ) from e

    @validator("denylist")
    @classmethod
    def _validate_exception_overlap(
        cls, denylist: dict[PurlType, set[PackagePattern]], values: dict[str, Any]
    ) -> dict[PurlType, set[PackagePattern]]:
        allowlist: dict[PurlType, set[PackagePattern]] = parse_obj_as(
            dict[PurlType, set[PackagePattern]], values.get("allowlist")
        )

        for purl_type in PurlType:
            if allowlist.get(purl_type, set()) & denylist.get(purl_type, set()):
                raise ValueError(f"The allowlist and denylist have at least one overlapping {purl_type.name} package")

        return denylist

    def strace_files(self) -> set[Path]:
        """List of files parsed from the provided strace results.

        Returns:
            set[Path]: List of files found from strace
        """
        if self.strace_results and not self._strace_files:
            parsed_strace_files = strace.get_files(self.strace_results)

            if self.strace_regex_excludes:
                self._strace_files = {
                    file
                    for file in parsed_strace_files
                    if not any(bool(re.search(exclude, str(file))) for exclude in self.strace_regex_excludes)
                }
                self.cache_dir.mkdir(parents=True, exist_ok=True)
                with self.cache_dir.joinpath("filtered-strace-results.txt").open("w") as output:
                    output.writelines([f"{file}\n" for file in self._strace_files])
            else:
                self._strace_files = parsed_strace_files

        return self._strace_files


class ChopprConfig:
    """A class to store the Choppr configuration.

    Members:
        - allow_version_mismatch
        - allowlist
        - archive_cache
        - cache_dir
        - cache_input
        - cache_timeout
        - certificates
        - clear_cache
        - deb_repositories
        - delete_excluded
        - denylist
        - http_limits
        - keep_essential_os_components
        - mode
        - output_files
        - recursion_limit
        - strace_files
    """

    def __init__(self, model: ChopprConfigModel) -> None:
        self.allow_version_mismatch: bool = model.allow_version_mismatch
        self.allowlist: dict[PurlType, set[PackagePattern]] = model.allowlist
        self.archive_cache: bool = model.archive_cache
        self.cache_dir: Path = model.cache_dir
        self.cache_input: Path | None = model.cache_input
        self.cache_timeout: timedelta | bool = model.cache_timeout
        self.certificates: dict[str, Path] = model.certificates
        self.clear_cache: bool = model.clear_cache
        self.deb_repositories: list[DebianRepository] = model.deb_repositories
        self.delete_excluded: bool = model.delete_excluded
        self.denylist: dict[PurlType, set[PackagePattern]] = model.denylist
        self.http_limits: HttpRequestLimits = model.http_limits
        self.keep_essential_os_components: bool = model.keep_essential_os_components
        self.mode: OperatingMode = model.mode
        self.output_files: OutputFiles = model.output_files
        self.recursion_limit: PositiveInt = model.recursion_limit
        self.strace_files: set[Path] = model.strace_files()
