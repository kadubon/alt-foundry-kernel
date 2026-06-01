"""Reusable certificate reports for ALT validator modules."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from alt_foundry_kernel.constants import IssueSeverity


class CertificateIssue(BaseModel):
    """A machine-readable issue emitted by a module-level ALT checker."""

    severity: IssueSeverity
    code: str
    path: str
    message: str


class CertificateReport(BaseModel):
    """Language-neutral result object for a deterministic ALT certificate check."""

    model_config = ConfigDict(extra="forbid")

    name: str
    ok: bool = True
    claim: str | None = None
    level: Literal["syntax", "evidence", "settlement", "audit"] = "evidence"
    predicates: dict[str, bool | None] = Field(default_factory=dict)
    metrics: dict[str, float | int | str | bool | None] = Field(default_factory=dict)
    artifacts: dict[str, Any] = Field(default_factory=dict)
    issues: list[CertificateIssue] = Field(default_factory=list)

    def add_issue(
        self, severity: IssueSeverity, code: str, path: str, message: str
    ) -> None:
        self.issues.append(
            CertificateIssue(severity=severity, code=code, path=path, message=message)
        )
        if severity == IssueSeverity.ERROR:
            self.ok = False

    def require(self, predicate: str, value: bool, path: str, message: str) -> None:
        self.predicates[predicate] = value
        if not value:
            self.add_issue(IssueSeverity.ERROR, "predicate-failed", path, message)


def value_at(payload: Any, path: str) -> Any:
    """Return a dotted-path value from a mapping-like JSON payload."""

    current = payload
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def present(payload: Any, path: str) -> bool:
    value = value_at(payload, path)
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, dict):
        return bool(value)
    if isinstance(value, list):
        return bool(value)
    return True


def status_is(payload: Any, path: str, *allowed: object) -> bool:
    return value_at(payload, path) in allowed


def numeric(payload: Any, path: str) -> float | None:
    value = value_at(payload, path)
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    return float(value)
