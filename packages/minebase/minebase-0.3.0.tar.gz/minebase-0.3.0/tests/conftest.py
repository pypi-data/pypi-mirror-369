import pytest

from minebase import Edition, _load_data_paths  # pyright: ignore[reportPrivateUsage]


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    """Dynamically generate pytest parameter sets for tests requesting 'edition' and 'version' fixtures.

    This hook loads the data paths manifest using `_load_data_paths()` and extracts all available
    versions for both Edition.PC and Edition.BEDROCK. It then parametrizes tests with every
    (edition, version) pair, so each combination runs as a separate test case.

    If loading the manifest fails or no versions are found for a given edition, the test
    collection will be skipped with an appropriate message.
    """
    if {"edition", "version"} <= set(metafunc.fixturenames):  # subset check
        try:
            manifest = _load_data_paths()
        except Exception as exc:  # noqa: BLE001
            pytest.skip(f"Could not load data paths manifest: {exc}")

        params: list[tuple[Edition, str]] = []
        for edition in Edition.__members__.values():
            versions = manifest[edition.value]
            if not versions:
                pytest.skip(f"No versions found for edition {edition}")
            params.extend((edition, version) for version in versions)

        metafunc.parametrize(
            ("edition", "version"),
            params,
            ids=[f"{edition.name}-{version}" for edition, version in params],
        )
