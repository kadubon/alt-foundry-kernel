"""Public-release surface audit for the ALT bootloader repository."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal

from jsonschema import Draft202012Validator

from alt_foundry_kernel.models import Packet
from alt_foundry_kernel.schemas import load_schema
from alt_foundry_kernel.validation import validate_packet

DOI = "https://doi.org/10.5281/zenodo.20476200"

IGNORED_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
}


@dataclass(frozen=True)
class AuditFinding:
    severity: Literal["error", "warning"]
    code: str
    path: str
    message: str


@dataclass(frozen=True)
class PublicAuditReport:
    ok: bool
    strict: bool
    root: str
    findings: list[AuditFinding] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


def _is_ignored(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    return any(part in IGNORED_DIRS for part in relative.parts)


def _public_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if _is_ignored(path, root) or path.name == "uv.lock":
            continue
        if path.is_file():
            files.append(path)
    return files


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _finding(
    severity: Literal["error", "warning"], code: str, path: Path | str, message: str
) -> AuditFinding:
    return AuditFinding(severity=severity, code=code, path=str(path), message=message)


def _check_public_text(root: Path, findings: list[AuditFinding]) -> None:
    local_markers = (
        "C:" + "\\" + "Users",
        "C:" + "/" + "Users",
        "Desk" + "top",
        "Down" + "loads",
        "Abstraction Liquidity Theory" + ".tex",
    )
    secret_markers = (
        "BEGIN " + "PRIVATE KEY",
        "OPENAI_" + "API" + "_KEY=",
        "AWS_" + "SECRET_ACCESS_KEY",
        "api" + "_key =",
        "token" + " =",
    )
    fake_url_markers = (
        "github.com/" + "alt-foundry-kernel/alt-foundry-kernel",
        "alt-foundry-kernel" + ".example",
    )

    for path in _public_files(root):
        relative = path.relative_to(root)
        text = _text(path)
        for marker in local_markers:
            if marker in text:
                findings.append(
                    _finding("error", "local-marker", relative, f"Local marker {marker!r} found.")
                )
        for marker in secret_markers:
            if marker in text and path.name not in {".gitignore", "public_audit.py"}:
                findings.append(
                    _finding("error", "secret-marker", relative, f"Secret marker {marker!r} found.")
                )
        for marker in fake_url_markers:
            if marker in text:
                findings.append(
                    _finding(
                        "error",
                        "placeholder-url",
                        relative,
                        f"Placeholder publishing URL {marker!r} found.",
                    )
                )


def _check_docs(root: Path, findings: list[AuditFinding]) -> None:
    readme_ja = root / "README.ja.md"
    if readme_ja.exists():
        findings.append(_finding("error", "japanese-readme-present", readme_ja.name, "Remove it."))

    public_docs = [root / "README.md", *sorted((root / "docs").glob("*.md"))]
    for path in public_docs:
        if not path.exists():
            findings.append(
                _finding("error", "doc-missing", path.relative_to(root), "File missing.")
            )
            continue
        if DOI not in _text(path):
            findings.append(
                _finding("error", "doi-missing", path.relative_to(root), "Paper DOI is missing.")
            )

    citation = root / "CITATION.cff"
    if not citation.exists() or "10.5281/zenodo.20476200" not in _text(citation):
        findings.append(
            _finding("error", "citation-doi-missing", "CITATION.cff", "Paper DOI is missing.")
        )


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


def _check_schemas(root: Path, findings: list[AuditFinding]) -> None:
    schema_dir = root / "schemas"
    for path in sorted(schema_dir.glob("*.schema.json")):
        relative = path.relative_to(root)
        try:
            schema = json.loads(_text(path))
            Draft202012Validator.check_schema(schema)
        except Exception as exc:
            findings.append(_finding("error", "schema-invalid", relative, str(exc)))
            continue
        for ref in _refs(schema):
            if ref.startswith("#"):
                continue
            if not (schema_dir / ref).exists():
                findings.append(
                    _finding("error", "schema-ref-unresolved", relative, f"Missing ref {ref!r}.")
                )


def _check_examples(root: Path, findings: list[AuditFinding]) -> None:
    validator = Draft202012Validator(load_schema("packet"))
    for path in sorted((root / "examples").glob("*_packet.json")):
        relative = path.relative_to(root)
        try:
            packet = json.loads(_text(path))
            validator.validate(packet)
            Packet.model_validate(packet)
            report = validate_packet(packet)
        except Exception as exc:
            findings.append(_finding("error", "example-invalid", relative, str(exc)))
            continue
        if not report.ok:
            findings.append(
                _finding(
                    "error",
                    "example-fails-alt-validation",
                    relative,
                    "; ".join(issue.message for issue in report.issues),
                )
            )


def _check_local_artifacts(root: Path, findings: list[AuditFinding]) -> None:
    for path in sorted(root.iterdir()):
        if path.is_dir() and path.name in IGNORED_DIRS:
            findings.append(
                _finding(
                    "warning",
                    "generated-local-artifact",
                    path.name,
                    "Ignored local artifact exists; remove before publishing an archive.",
                )
            )
    for path in root.rglob(".env*"):
        if not _is_ignored(path, root) and path.is_file():
            findings.append(
                _finding(
                    "error",
                    "env-file-present",
                    path.relative_to(root),
                    "Local env file found.",
                )
            )
    for path in root.rglob("*.tex"):
        if not _is_ignored(path, root) and path.is_file():
            findings.append(
                _finding(
                    "error",
                    "paper-source-present",
                    path.relative_to(root),
                    "TeX source found.",
                )
            )


def run_public_audit(root: Path | None = None, strict: bool = False) -> PublicAuditReport:
    """Audit the repository surface intended for public OSS release."""

    audit_root = (root or Path.cwd()).resolve()
    findings: list[AuditFinding] = []
    _check_public_text(audit_root, findings)
    _check_docs(audit_root, findings)
    _check_schemas(audit_root, findings)
    _check_examples(audit_root, findings)
    _check_local_artifacts(audit_root, findings)
    ok = not any(finding.severity == "error" for finding in findings)
    return PublicAuditReport(ok=ok, strict=strict, root=str(audit_root), findings=findings)
