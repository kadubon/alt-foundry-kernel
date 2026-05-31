from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

import alt_foundry_kernel.validation as validation_module
from alt_foundry_kernel import KernelState, Packet, load_schema, validate_packet

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


def _load(name: str) -> dict[str, object]:
    return json.loads((EXAMPLES / name).read_text(encoding="utf-8"))


def test_packet_examples_validate_with_json_schema_and_python_model() -> None:
    validator = Draft202012Validator(load_schema("packet"))
    for path in sorted(EXAMPLES.glob("*_packet.json")):
        packet = json.loads(path.read_text(encoding="utf-8"))
        validator.validate(packet)
        Packet.model_validate(packet)
        report = validate_packet(packet)
        assert report.schema_ok, path.name
        assert report.ok, path.name


def test_empty_kernel_state_example_matches_python_model() -> None:
    state = _load("kernel_state_empty.json")
    parsed = KernelState.model_validate(state)
    assert parsed.certified_capital == 0.0
    assert parsed.admitted_tokens == []


def test_all_public_schemas_are_valid_and_refs_resolve() -> None:
    schema_dir = ROOT / "schemas"
    for path in sorted(schema_dir.glob("*.schema.json")):
        schema = json.loads(path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        for ref in _refs(schema):
            if ref.startswith("#"):
                continue
            assert (schema_dir / ref).exists(), f"{path.name} has unresolved ref {ref}"


def test_packet_validation_runs_schema_validation_once(monkeypatch: object) -> None:
    call_count = 0
    original = validation_module._schema_issues

    def wrapped(packet: object) -> object:
        nonlocal call_count
        call_count += 1
        return original(packet)  # type: ignore[arg-type]

    monkeypatch.setattr(validation_module, "_schema_issues", wrapped)  # type: ignore[attr-defined]

    validate_packet(_load("admission_packet.json"))

    assert call_count == 1


def _refs(value: object) -> list[str]:
    refs: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "$ref" and isinstance(item, str):
                refs.append(item)
            else:
                refs.extend(_refs(item))
    elif isinstance(value, list):
        for item in value:
            refs.extend(_refs(item))
    return refs
