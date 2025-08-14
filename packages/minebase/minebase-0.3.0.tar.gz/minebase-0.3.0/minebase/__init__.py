import json
from enum import Enum
from pathlib import Path
from typing import Any, cast

from minebase.types.data_paths import DataPaths

DATA_SUBMODULE_PATH = Path(__file__).parent / "data"
DATA_PATH = DATA_SUBMODULE_PATH / "data"


class Edition(Enum):
    """Available minecraft-data editions."""

    PC = "pc"
    BEDROCK = "bedrock"


def _validate_data() -> None:
    """Validate that the minecraft-data submodule is present."""
    if not DATA_SUBMODULE_PATH.is_dir():
        # should never happen (unless the submodule wasn't even included in the
        # package installation)
        raise ValueError(f"minecraft-data submodule not found (missing {DATA_SUBMODULE_PATH})")

    if not DATA_PATH.is_dir():
        # This can happen, if the submodule wasn't pulled (non-recursive clone)
        raise ValueError(f"minecraft-data submodule not initialized (missing {DATA_PATH})")


def _load_data_paths() -> DataPaths:
    """Load the data paths file, containing info on where to find the resources for specific versions."""
    file = DATA_PATH / "dataPaths.json"
    if not file.is_file():
        raise ValueError(f"minecraft-data submodule didn't contain data paths manifest (missing {file})")

    with file.open("rb") as fp:
        return cast("DataPaths", json.load(fp))


def _load_version_manifest(version: str, edition: Edition = Edition.PC) -> "dict[str, str]":
    """Load the data paths manifest for given version (if it exists)."""
    manifest = _load_data_paths()
    edition_info = manifest[edition.value]
    try:
        return edition_info[version]
    except KeyError as exc:
        raise ValueError(f"Version {version} doesn't exist for edition {edition.name}") from exc


def supported_versions(edition: Edition = Edition.PC) -> list[str]:
    """Get a list of all supported minecraft versions."""
    manifest = _load_data_paths()
    edition_info = manifest[edition.value]
    return list(edition_info.keys())


def load_version(version: str, edition: Edition = Edition.PC) -> dict[str, Any]:
    """Load minecraft-data for given `version` and `edition`."""
    _validate_data()
    version_data = _load_version_manifest(version, edition)

    data: dict[str, Any] = {}
    for field, dir_suffix in version_data.items():
        dir_path = DATA_PATH.joinpath(*dir_suffix.split("/"))

        # Skip yaml files, we currently don't support loading them
        if field in {"proto", "types"}:
            continue

        file = dir_path / (field + ".json")

        if not file.is_file():
            raise ValueError(f"Unable to load {field!r} for {edition.name}/{version} (missing {file})")

        with file.open("rb") as fp:
            data[field] = json.load(fp)

    return data


def load_common_data(edition: Edition = Edition.PC) -> dict[str, Any]:
    """Load the common data from minecraft-data for given `edition`."""
    _validate_data()
    common_dir = DATA_PATH / edition.value / "common"
    if not common_dir.is_dir():
        raise ValueError(f"minecraft-data submodule didn't contain the common data for {edition.name} edition")

    data: dict[str, Any] = {}
    for file in common_dir.iterdir():
        if not file.is_file() or file.suffix != ".json":
            raise ValueError(f"Found an unexpected entry in common directory: {file}")

        with file.open("rb") as fp:
            data[file.stem] = json.load(fp)

    return data
