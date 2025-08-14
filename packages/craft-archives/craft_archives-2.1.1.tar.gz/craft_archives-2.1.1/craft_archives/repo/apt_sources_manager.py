# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2015-2023 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""Manage the host's apt source repository configuration."""

import functools
import io
import logging
import pathlib
import subprocess
from collections.abc import Sequence
from pathlib import Path
from typing import cast
from urllib.parse import urlparse

import distro
from debian.deb822 import Deb822

from craft_archives import utils
from craft_archives.repo.package_repository import (
    PocketEnum,
)

from . import apt_key_manager, apt_ppa, apt_uca, errors, gpg, package_repository

logger = logging.getLogger(__name__)

_DEFAULT_SOURCES_DIRECTORY = Path("/etc/apt/sources.list.d")
_DEFAULT_SIGNED_BY_ROOT = Path("/")
# a mapping of architectures to a list of architectures with compatible packages
_COMPATIBLE_ARCHS = {
    "amd64": ["amd64", "i386"],
    "arm64": ["arm64", "armhf"],
}


def _construct_deb822_source(
    *,
    architectures: list[str] | None = None,
    components: list[str] | None = None,
    formats: list[str] | None = None,
    suites: list[str],
    url: str,
    signed_by: pathlib.Path,
) -> str:
    """Construct deb-822 formatted sources string."""
    with io.StringIO() as deb822:
        type_text = " ".join(formats) if formats else "deb"

        print(f"Types: {type_text}", file=deb822)

        print(f"URIs: {url}", file=deb822)

        suites_text = " ".join(suites)
        print(f"Suites: {suites_text}", file=deb822)

        if components:
            components_text = " ".join(components)
            print(f"Components: {components_text}", file=deb822)

        if architectures:
            arch_text = " ".join(architectures)
        else:
            arch_text = utils.get_host_architecture()

        print(f"Architectures: {arch_text}", file=deb822)

        print(f"Signed-By: {str(signed_by)}", file=deb822)

        return deb822.getvalue()


class AptSourcesManager:
    """Manage apt source configuration in /etc/apt/sources.list.d.

    :param sources_list_d: Path to sources.list.d directory.
    """

    # pylint: disable=too-few-public-methods
    def __init__(
        self,
        *,
        sources_list_d: Path | None = None,
        keyrings_dir: Path | None = None,
        signed_by_root: Path | None = None,
    ) -> None:
        """Create a manager for Apt repository sources listings.

        :param sources_list_d: The path to the directory containing the sources listings.
        :param keyrings_dir: The path to the directory containing the (already installed)
          keyrings.
        :param signed_by_root: The path that should be considered as "system root" when
          filling the "Signed-By" field in the sources listings. Used to configure an
          Apt-based system that will eventually be chrooted into.
        """
        self._sources_list_d = sources_list_d or _DEFAULT_SOURCES_DIRECTORY
        self._keyrings_dir = keyrings_dir or apt_key_manager.KEYRINGS_PATH
        self._signed_by_root = signed_by_root or _DEFAULT_SIGNED_BY_ROOT

    @classmethod
    def sources_path_for_root(cls, root: Path | None = None) -> Path:
        """Get the location for Apt source listings with ``root`` as the system root.

        :param root: The optional system root to consider, or None to assume the standard
          system root "/".
        """
        if root is None:
            return _DEFAULT_SOURCES_DIRECTORY
        return root / "etc/apt/sources.list.d"

    def _install_sources(
        self,
        *,
        architectures: list[str] | None = None,
        components: list[str] | None = None,
        formats: list[str] | None = None,
        name: str,
        suites: list[str],
        url: str,
        keyring_path: pathlib.Path,
    ) -> bool:
        """Install sources list configuration.

        Write config to:
        /etc/apt/sources.list.d/craft-<name>.sources

        :returns: True if configuration was changed.
        """
        if keyring_path and not keyring_path.is_file():
            raise errors.AptGPGKeyringError(keyring_path)

        keyring_path = Path("/") / keyring_path.relative_to(self._signed_by_root)

        config = _construct_deb822_source(
            architectures=architectures,
            components=components,
            formats=formats,
            suites=suites,
            url=url,
            signed_by=keyring_path,
        )

        if name not in ["default", "default-security"]:
            name = "craft-" + name

        config_path = self._sources_list_d / f"{name}.sources"
        if config_path.exists() and config_path.read_text() == config:
            # Already installed and matches, nothing to do.
            logger.debug(f"Ignoring unchanged sources: {config_path!s}")
            return False

        config_path.write_text(config)
        logger.debug(f"Installed sources: {config_path!s}")
        return True

    def _install_sources_apt(
        self, *, package_repo: package_repository.PackageRepositoryApt
    ) -> bool:
        """Install repository configuration.

        1) First check to see if package repo is implied path,
           or "bare repository" config.  This is indicated when no
           path, components, or suites are indicated.
        2) If path is specified, convert path to a suite entry,
           ending with "/".

        Relatedly, this assumes all the error-checking has been
        done already on the package_repository object in a proper
        fashion, but do some checks here anyways.

        :returns: True if source configuration was changed.
        """
        if (
            not package_repo.path
            and not package_repo.components
            and not package_repo.suites
        ):
            suites = ["/"]
        elif package_repo.path:
            # Suites denoting exact path must end with '/'.
            path = package_repo.path
            if not path.endswith("/"):
                path += "/"
            suites = [path]
        elif package_repo.suites:
            suites = package_repo.suites
        elif package_repo.pocket:
            suites = _get_suites(package_repo.pocket, cast(str, package_repo.series))
        else:  # pragma: no cover
            raise RuntimeError("no suites or path")

        name = package_repo.name

        url = str(package_repo.url)

        logger.debug(
            "Looking for existing sources files for url '%s' and suites %s", url, suites
        )
        # Check whether this url is already listed in an existing sources file
        existing_key = _get_existing_keyring_for(
            key_id=package_repo.key_id,
            url=url,
            suites=suites,
            root=self._signed_by_root,
        )

        if existing_key:
            keyring_path = existing_key
        else:
            logger.debug("No existing sources found")
            keyring_path = apt_key_manager.get_keyring_path(
                package_repo.key_id, base_path=self._keyrings_dir
            )

        return self._install_sources(
            architectures=package_repo.architectures,
            components=package_repo.components,
            formats=cast(list[str] | None, package_repo.formats),
            name=name,
            suites=suites,
            url=url,
            keyring_path=keyring_path,
        )

    def _install_sources_ppa(
        self, *, package_repo: package_repository.PackageRepositoryAptPPA
    ) -> bool:
        """Install PPA formatted repository.

        Create a sources list config by:
        - Looking up the codename of the host OS and using it as the "suites"
          entry.
        - Formulate deb URL to point to PPA.
        - Enable only "deb" formats.

        :returns: True if source configuration was changed.
        """
        owner, name = apt_ppa.split_ppa_parts(ppa=package_repo.ppa)
        codename = distro.codename()

        key_id: str = cast(str, package_repo.key_id)
        if not key_id:
            key_id = apt_ppa.get_launchpad_ppa_key_id(ppa=package_repo.ppa)

        keyring_path = apt_key_manager.get_keyring_path(
            key_id, base_path=self._keyrings_dir
        )

        return self._install_sources(
            components=["main"],
            formats=["deb"],
            name=f"ppa-{owner}_{name}",
            suites=[codename],
            url=f"http://ppa.launchpad.net/{owner}/{name}/ubuntu",
            keyring_path=keyring_path,
        )

    def _install_sources_uca(
        self, *, package_repo: package_repository.PackageRepositoryAptUCA
    ) -> bool:
        """Install UCA formatted repository.

        Create a sources list config by:
        - Looking up the codename of the host OS and using it as the "suites"
          entry.
        - Formulate deb URL to point to UCA.
        - Enable only "deb" formats.

        :returns: True if source configuration was changed.
        """
        cloud = package_repo.cloud
        pocket = package_repo.pocket

        codename = distro.codename()
        apt_uca.check_release_compatibility(codename, cloud, pocket)

        key_id = package_repository.UCA_KEY_ID
        keyring_path = apt_key_manager.get_keyring_path(
            key_id, base_path=self._keyrings_dir
        )
        return self._install_sources(
            components=["main"],
            formats=["deb"],
            name=f"cloud-{cloud}",
            suites=[f"{codename}-{pocket}/{cloud}"],
            url=package_repository.UCA_ARCHIVE,
            keyring_path=keyring_path,
        )

    def install_package_repository_sources(
        self,
        *,
        package_repo: package_repository.PackageRepository,
    ) -> bool:
        """Install configured package repositories.

        :param package_repo: Repository to install the source configuration for.

        :returns: True if source configuration was changed.
        """
        logger.debug(f"Processing repo: {package_repo!r}")
        if isinstance(package_repo, package_repository.PackageRepositoryAptPPA):
            return self._install_sources_ppa(package_repo=package_repo)

        if isinstance(package_repo, package_repository.PackageRepositoryAptUCA):
            return self._install_sources_uca(package_repo=package_repo)

        if isinstance(package_repo, package_repository.PackageRepositoryApt):
            changed = self._install_sources_apt(package_repo=package_repo)
            architectures = package_repo.architectures
            if changed and architectures:
                _add_architecture(
                    architectures=architectures,
                    root=self._signed_by_root,
                    sources_dir=self._sources_list_d,
                )
            return changed

        raise RuntimeError(f"unhandled package repository: {package_repository!r}")


def _add_architecture(
    architectures: list[str],
    root: Path,
    sources_dir: Path,
) -> None:
    """Add package repository architecture.

    For systems that who default to deb822 sources, `dpkg --add-architecture`
    works for any architecture. For systems that use the traditional sources.list,
    only compatible architectures can be added.

    :param architectures: The architectures to add.
    :param root: The root of the system to add the architectures to.
    :param sources_dir: The directory containing the sources listings.
    """
    current_arch = _get_current_architecture()

    # Sources in 'ubuntu.sources' don't list architectures, so apt assumes the default
    # repository provides packages for all architectures. These need to be restricted
    # before adding other architectures with `dpkg --add-architecture`.
    if _is_deb822_default(sources_dir):
        _update_sources_file(
            sources_file=sources_dir / "ubuntu.sources",
            field="Architectures",
            values=_COMPATIBLE_ARCHS.get(current_arch, current_arch),
        )
    else:
        logger.debug(
            "Not updating sources.list because it doesn't exist "
            "or isn't in the deb822 format."
        )

    for arch in architectures:
        if _is_deb822_default(sources_dir) or arch in _COMPATIBLE_ARCHS.get(
            current_arch, []
        ):
            logger.info(f"Adding repository architecture: {arch}")
            subprocess.run(
                # Note: the order of parameters matters here, as "--add-architecture"
                # must come last because of the way dpkg parses the command.
                ["dpkg", "--root", str(root), "--add-architecture", arch],
                check=True,
            )


def _get_current_architecture() -> str:
    """Get the "main" architecture of the running system, as reported by dpkg."""
    return (
        subprocess.check_output(["dpkg", "--print-architecture"])
        .decode("utf-8")
        .strip()
    )


@functools.lru_cache
def _is_deb822_default(sources_dir: Path) -> bool:
    """Check if the default sources are in deb822 format.

    :param sources_dir: The directory containing the sources listings.

    :return: True if the default sources are in deb822 format.
    """
    sources_file = sources_dir / "ubuntu.sources"

    if not (sources_dir / "ubuntu.sources").is_file():
        return False

    # an empty list means there are no sources
    return bool(list(Deb822.iter_paragraphs(sequence=sources_file.read_text())))


def _update_sources_file(
    *, sources_file: Path, field: str, values: Sequence[str] | str
) -> None:
    """Update a field in a deb822 sources file.

    :param sources_file: The file to update.
    :param field: The field to update.
    :param values: The new values for the field. If the field doesn't exist, it is added.
      The existing value is overwritten. Sequences are joined with a space. If the value
      is falsey (empty string or empty list), the field is removed.
    """
    if not sources_file.is_file():
        logger.debug("Sources file %r doesn't exist.", sources_file)
        return

    logger.debug("Reading sources from %r.", str(sources_file))
    sources = list(Deb822.iter_paragraphs(sequence=sources_file.read_text()))

    # convert sequence to a space-delimited string
    value = values if isinstance(values, str) else " ".join(values)
    logger.debug("Updating field %r to %r", field, value)

    if not sources:
        logger.debug(
            "Not updating %r because it doesn't contain any deb822 sources.",
            str(sources_file),
        )
        return

    for source in sources:
        logger.debug("Updating source %r.", source.get("URIs"))
        if value:
            source[field] = value
        else:
            source.pop(field, None)

    with sources_file.open("w") as f:
        for source in sources:
            logger.debug("Writing updated sources to %r.", str(sources_file))
            f.write(str(source) + "\n")


def _get_suites(pocket: PocketEnum, series: str) -> list[str]:
    """Get a list of suites from a pocket and a series."""
    suites = [series]
    if not pocket or pocket == PocketEnum.RELEASE:
        return suites

    if pocket == PocketEnum.UPDATES:
        suites.append(f"{series}-{pocket}")
    if pocket == PocketEnum.PROPOSED:
        suites.extend(
            [f"{series}-{p}" for p in [PocketEnum.UPDATES, PocketEnum.PROPOSED]]
        )
    if pocket == PocketEnum.SECURITY:
        suites = [f"{series}-{pocket}"]

    return suites


def _normalize_archive_url(url: str) -> str:
    parsed = urlparse(url)
    # Disregard the scheme: Apt considers both http and https the same for
    # resolving the archive.
    url = parsed.netloc + parsed.path
    # Apt urls are always directories.
    if not url.endswith("/"):
        return url + "/"
    return url


def _get_existing_keyring_for(
    *, key_id: str, url: str, suites: Sequence[str], root: Path
) -> Path | None:
    """Look for an existing source that matches a key id, url and suites.

    :param key_id: The ID of the key we want to find.
    :param url: The source url to look for.
    :param suites: The suites of interest. Needed because Apt sources are signed
      at an "url + suite"-level, so the existing sources are parsed to find one
      that matches ``url`` and at least one of the ``suites``.

    :return: The full path to the signing keyfile, if a matching source is found.
    """
    suites_set = set(suites)

    sources_dir = root / "etc/apt/sources.list.d"
    # Note: this current implementation only looks for official sources in
    # "ubuntu.sources", present since Noble.
    sources_file = sources_dir / "ubuntu.sources"

    if not sources_file.is_file():
        return None

    original_url = url
    url = _normalize_archive_url(url)

    logger.debug("Reading sources in '%s' looking for '%s'", sources_file, url)

    for source_dict in Deb822.iter_paragraphs(
        sequence=sources_file.read_text(), fields=["URIs", "Suites", "Signed-By"]
    ):
        try:
            source_url = _normalize_archive_url(source_dict["URIs"])
            source_suites = set(source_dict.get("Suites", "").split())
            source_signed = source_dict["Signed-By"]
        except KeyError:
            # Source does not have a Signed-By or URIs - not relevant here.
            continue

        if url != source_url:
            logger.debug(
                "Source does not have a matching url: %s",
                source_url,
            )
            continue

        logger.debug("Source has these suites: %s", sorted(source_suites))
        if suites_set.intersection(source_suites):
            logger.debug("Suites match - Signed-By is '%s'", source_signed)
            full_key_path = root / Path(source_signed).relative_to("/")

            # Check whether the requested key-id matches the existing
            # Signed-By key.
            if not gpg.is_key_in_keyring(key_id, full_key_path):
                # This is impossible to recover: user asked for a specific ID,
                # and an Apt repository cannot be signed by different keys at
                # the moment.
                raise errors.SourcesKeyConflictError(
                    requested_key_id=key_id,
                    requested_url=original_url,
                    conflict_keyring=source_signed,
                    conflicting_source=sources_file,
                )
            return full_key_path

    return None
