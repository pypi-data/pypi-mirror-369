"""Test loading of the actual minecraft-data repository.

This suite essentially acts as integration tests, as it just blindly runs
the load functions without checking the expected results, simply testing
whether the loading succeeded.
"""

import pytest

from minebase import (
    Edition,
    _validate_data,  # pyright: ignore[reportPrivateUsage]
    load_common_data,
    load_version,
)


def test_data_submodule_is_initialized() -> None:
    """Ensure the minecraft-data submodule is present and initialized."""
    _validate_data()


@pytest.mark.parametrize("edition", Edition.__members__.values())
def test_load_common_data_for_each_edition(edition: Edition) -> None:
    """Ensure common data exists and is loadable for each edition."""
    data = load_common_data(edition)
    assert isinstance(data, dict)
    assert data, f"No common data found for edition {edition}"


def test_all_versions_loadable(edition: Edition, version: str) -> None:  # parametrized from conftest
    """Ensure that a specific version for an edition can be loaded."""
    result = load_version(version, edition)
    assert isinstance(result, dict)
