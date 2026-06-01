"""Typed records for ALT packets, ledgers, and kernel transitions."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from alt_foundry_kernel.constants import Decision, IssueSeverity, LifecycleState, PacketType

JsonObject = dict[str, Any]


class Packet(BaseModel):
    """Machine-readable executable ALT certificate packet."""

    model_config = ConfigDict(extra="forbid")

    id: str
    type: PacketType
    token_id: str
    version: str
    state: LifecycleState
    scope_hash: str
    declaration: JsonObject
    evidence: JsonObject
    bounds: JsonObject
    validity: JsonObject
    monitor: JsonObject
    fallback: JsonObject
    signatures: list[JsonObject] = Field(default_factory=list)


class Token(BaseModel):
    """Language-neutral ALT abstraction-token surface."""

    model_config = ConfigDict(extra="allow")

    token_id: str
    version: str
    signature: JsonObject
    representation: JsonObject
    adapter: JsonObject
    verifier_contract: JsonObject
    guard: JsonObject
    cost_risk_model: JsonObject
    provenance: JsonObject
    dependencies: list[JsonObject] = Field(default_factory=list)


class ValidationIssue(BaseModel):
    severity: IssueSeverity
    code: str
    path: str
    message: str


class ValidationReport(BaseModel):
    ok: bool
    schema_ok: bool
    settlement_decidable: bool
    can_increase_capital: bool
    predicates: dict[str, bool | None] = Field(default_factory=dict)
    issues: list[ValidationIssue] = Field(default_factory=list)

    def has_errors(self) -> bool:
        return any(issue.severity == IssueSeverity.ERROR for issue in self.issues)

    def missing_paths(self) -> list[str]:
        return [issue.path for issue in self.issues if issue.code == "required-field-missing"]


class SignedBoundReport(BaseModel):
    lower_bound: float | None
    upper_bound: float | None
    missing_for_lower: list[str] = Field(default_factory=list)
    missing_for_upper: list[str] = Field(default_factory=list)

    @property
    def lower_decidable(self) -> bool:
        return self.lower_bound is not None and not self.missing_for_lower


class LedgerEntry(BaseModel):
    entry_id: str
    packet_id: str
    token_id: str
    ledger: Literal[
        "candidate_queue",
        "exploration",
        "settlement",
        "hazard",
        "negative_registry",
        "resurrection",
        "audit",
    ]
    decision: Decision
    state: LifecycleState
    capital_delta: float = 0.0
    reason: str
    details: JsonObject = Field(default_factory=dict)


class KernelState(BaseModel):
    """Dual-ledger ALT kernel state."""

    admitted_tokens: list[str] = Field(default_factory=list)
    candidate_queue: list[LedgerEntry] = Field(default_factory=list)
    exploration_ledger: list[LedgerEntry] = Field(default_factory=list)
    settlement_ledger: list[LedgerEntry] = Field(default_factory=list)
    hazard_ledger: list[LedgerEntry] = Field(default_factory=list)
    negative_registry: list[LedgerEntry] = Field(default_factory=list)
    resurrection_queue: list[LedgerEntry] = Field(default_factory=list)
    monitor_drift_state: JsonObject = Field(default_factory=dict)
    authority_capability_state: JsonObject = Field(default_factory=dict)
    root_finality_state: JsonObject = Field(default_factory=dict)
    budget_state: JsonObject = Field(default_factory=dict)
    audit_log: list[LedgerEntry] = Field(default_factory=list)
    token_states: dict[str, LifecycleState] = Field(default_factory=dict)
    certified_capital: float = 0.0


class TransitionResult(BaseModel):
    decision: Decision
    packet_id: str
    token_id: str
    next_state: KernelState
    ledger_entry: LedgerEntry
    validation: ValidationReport
    signed_bounds: SignedBoundReport
