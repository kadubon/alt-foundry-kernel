"""JSON Schema loading helpers."""

from __future__ import annotations

import json
from importlib import resources
from pathlib import Path
from typing import Any, cast

SCHEMA_FILENAMES: dict[str, str] = {
    "authority-certificate": "authority-certificate.schema.json",
    "authority_certificate": "authority-certificate.schema.json",
    "baseline-envelope": "baseline-envelope.schema.json",
    "baseline_envelope": "baseline-envelope.schema.json",
    "cara-claim": "cara-claim.schema.json",
    "cara_claim": "cara-claim.schema.json",
    "causal-certificate": "causal-certificate.schema.json",
    "causal_certificate": "causal-certificate.schema.json",
    "certificate-report": "certificate-report.schema.json",
    "certificate_report": "certificate-report.schema.json",
    "conformance-result": "conformance-result.schema.json",
    "conformance_result": "conformance-result.schema.json",
    "packet": "packet.schema.json",
    "token": "token.schema.json",
    "kernel-state": "kernel-state.schema.json",
    "kernel_state": "kernel-state.schema.json",
    "ledger-entry": "ledger-entry.schema.json",
    "ledger_entry": "ledger-entry.schema.json",
    "dashboard": "dashboard.schema.json",
    "evidence-split": "evidence-split.schema.json",
    "evidence_split": "evidence-split.schema.json",
    "foundry-transcript": "foundry-transcript.schema.json",
    "foundry_transcript": "foundry-transcript.schema.json",
    "measurement-spec": "measurement-spec.schema.json",
    "measurement_spec": "measurement-spec.schema.json",
    "opportunity-law": "opportunity-law.schema.json",
    "opportunity_law": "opportunity-law.schema.json",
    "portfolio-state": "portfolio-state.schema.json",
    "portfolio_state": "portfolio-state.schema.json",
    "reproduction-record": "reproduction-record.schema.json",
    "reproduction_record": "reproduction-record.schema.json",
    "risk-ledger": "risk-ledger.schema.json",
    "risk_ledger": "risk-ledger.schema.json",
    "root-finality-record": "root-finality-record.schema.json",
    "root_finality_record": "root-finality-record.schema.json",
    "transport-certificate": "transport-certificate.schema.json",
    "transport_certificate": "transport-certificate.schema.json",
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
