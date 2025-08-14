from typing import TypedDict


class DataPaths(TypedDict):
    """Strucutre of the `dataPaths.json` manifest file."""

    pc: dict[str, dict[str, str]]
    bedrock: dict[str, dict[str, str]]
