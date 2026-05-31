"""JSON Schema loading helpers."""

from __future__ import annotations

import json
from importlib import resources
from pathlib import Path
from typing import Any, cast

SCHEMA_FILENAMES: dict[str, str] = {
    "packet": "packet.schema.json",
    "token": "token.schema.json",
    "kernel-state": "kernel-state.schema.json",
    "kernel_state": "kernel-state.schema.json",
    "ledger-entry": "ledger-entry.schema.json",
    "ledger_entry": "ledger-entry.schema.json",
    "dashboard": "dashboard.schema.json",
}


def _repo_schema_path(filename: str) -> Path:
    return Path(__file__).resolve().parents[2] / "schemas" / filename


def load_schema(name: str) -> dict[str, Any]:
    """Load a public JSON Schema by stable name.

    In editable/source checkouts this reads the repository-level ``schemas/`` directory.
    In built wheels it falls back to packaged schema resources.
    """

    filename = SCHEMA_FILENAMES.get(name, name)
    if not filename.endswith(".json"):
        filename = f"{filename}.schema.json"

    source_path = _repo_schema_path(filename)
    if source_path.exists():
        return cast(dict[str, Any], json.loads(source_path.read_text(encoding="utf-8")))

    package_files = resources.files("alt_foundry_kernel").joinpath("schemas", filename)
    return cast(dict[str, Any], json.loads(package_files.read_text(encoding="utf-8")))
