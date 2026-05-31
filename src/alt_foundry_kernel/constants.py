"""Constants for the v1 ALT bootloader contract."""

from __future__ import annotations

from enum import StrEnum


class PacketType(StrEnum):
    CANDIDATE = "candidate"
    ADMISSION = "admission"
    TRANSPORT_REFRESH = "transport-refresh"
    MONITOR_ALARM = "monitor-alarm"
    DEPRECATION = "deprecation"
    ROLLBACK = "rollback"
    RESURRECTION = "resurrection"
    BRIDGE = "bridge"
    KERNEL_UPDATE = "kernel-update"


class LifecycleState(StrEnum):
    CANDIDATE = "candidate"
    EXPLORATION = "exploration"
    PENDING_SETTLEMENT = "pending_settlement"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEPRECATED = "deprecated"
    RESURRECTED = "resurrected"


class Decision(StrEnum):
    ADMIT = "admit"
    REJECT = "reject"
    DEFER = "defer"
    SUSPEND = "suspend"
    DEPRECATE = "deprecate"
    ROLLBACK = "rollback"
    RESURRECT = "resurrect"


class EstimandType(StrEnum):
    CAUSAL = "causal"
    CALIBRATED_PROXY = "calibrated-proxy"
    PROXY_ONLY = "proxy-only"


class IssueSeverity(StrEnum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


PACKET_TYPES = [item.value for item in PacketType]
LIFECYCLE_STATES = [item.value for item in LifecycleState]
DECISIONS = [item.value for item in Decision]
ESTIMAND_TYPES = [item.value for item in EstimandType]

PREDICATE_NAMES: tuple[str, ...] = (
    "SchemaOK",
    "NetLowerBoundOK",
    "MissionOK",
    "TargetValidityOK",
    "BaselineEnvelopeOK",
    "BaselineLive",
    "OpportunityLawOK",
    "EvidenceLive",
    "SelectionOK",
    "TelemetryOK",
    "TransportOK",
    "HazardOK",
    "AuthorityOK",
    "CapabilityOK",
    "ThreatOK",
    "DependencyClosed",
    "RootOK",
    "QuorumOK",
    "FinalityOK",
    "BudgetOK",
    "CapacityOK",
    "RefreshOK",
    "RollbackOK",
    "DeprecationOK",
    "RawNetSolvencyOK",
    "RuntimeWitnessOK",
    "NoncompHazardOK",
    "ViabilityOK",
)

BASE_PACKET_REQUIRED_PATHS: tuple[str, ...] = (
    "id",
    "type",
    "token_id",
    "version",
    "state",
    "scope_hash",
    "declaration",
    "evidence",
    "bounds",
    "validity",
    "monitor",
    "fallback",
    "signatures",
)

CANDIDATE_REQUIRED_PATHS: tuple[str, ...] = (
    "declaration.lineage",
    "declaration.dependencies",
    "declaration.dependencies.dependency_closure.closed",
    "declaration.scope",
    "declaration.grammar",
    "declaration.baseline",
    "declaration.mission",
)

ADMISSION_REQUIRED_PATHS: tuple[str, ...] = (
    *CANDIDATE_REQUIRED_PATHS,
    "declaration.estimand.estimand_type",
    "declaration.mission.status",
    "declaration.baseline.status",
    "declaration.opportunity_law.status",
    "declaration.authority.status",
    "declaration.capability.status",
    "declaration.threat_model.status",
    "declaration.runtime_witness.status",
    "evidence.design",
    "evidence.trace_view",
    "evidence.sample_size",
    "evidence.status",
    "evidence.selection_status",
    "bounds.value_lower_bound",
    "bounds.cost_upper_bound",
    "bounds.risk_upper_bound",
    "bounds.transport_upper_bound",
    "bounds.raw_net_capital_lower_bound",
    "validity.telemetry",
    "validity.transport.status",
    "validity.hazard.status",
    "validity.hazard.noncompensable_clearance",
    "validity.root.status",
    "validity.finality.state",
    "validity.budget.status",
    "validity.capacity.status",
    "validity.refresh.status",
    "validity.rollback.status",
    "validity.deprecation.status",
    "validity.viability.status",
)

CARA_CONDITIONAL_REQUIRED_PATHS: tuple[str, ...] = (
    "declaration.cara.asi_target_id",
    "declaration.cara.capability_basis_id",
    "declaration.cara.target_validity_certificate",
    "declaration.cara.baseline_upper_envelope",
    "declaration.cara.target_membership_proof",
    "declaration.cara.viability_witness",
    "declaration.cara.time_to_target_claim",
)

TRANSPORT_REFRESH_REQUIRED_PATHS: tuple[str, ...] = (
    "declaration.claim_id",
    "declaration.old_law",
    "declaration.new_law",
    "declaration.bridge",
    "monitor.deadline",
    "fallback.action",
    "validity.transport.status",
)

DEPRECATION_REQUIRED_PATHS: tuple[str, ...] = (
    "declaration.scope",
    "bounds.value_upper_bound",
    "bounds.cost_lower_bound",
    "validity.hazard.status",
    "fallback.resurrection_rule",
)

ROLLBACK_REQUIRED_PATHS: tuple[str, ...] = (
    "declaration.affected_claims",
    "declaration.restore_point",
    "bounds.reserve_charge",
    "evidence.audit_record",
)

RESURRECTION_REQUIRED_PATHS: tuple[str, ...] = (
    "declaration.old_negative_certificate_id",
    "evidence.overwriting_evidence",
    "bounds.value_lower_bound",
    "bounds.cost_upper_bound",
    "bounds.risk_upper_bound",
    "bounds.transport_upper_bound",
    "bounds.raw_net_capital_lower_bound",
    "validity.hazard.status",
    "validity.finality.state",
)

KERNEL_UPDATE_REQUIRED_PATHS: tuple[str, ...] = (
    "declaration.old_semantics",
    "declaration.new_semantics",
    "declaration.bridge",
    "validity.root.independent_root",
    "fallback.rollback_path",
)

REQUIRED_PATHS_BY_TYPE: dict[str, tuple[str, ...]] = {
    PacketType.CANDIDATE.value: CANDIDATE_REQUIRED_PATHS,
    PacketType.ADMISSION.value: ADMISSION_REQUIRED_PATHS,
    PacketType.TRANSPORT_REFRESH.value: TRANSPORT_REFRESH_REQUIRED_PATHS,
    PacketType.MONITOR_ALARM.value: (
        "declaration.claim_id",
        "evidence.alarm_statistic",
        "fallback.action",
    ),
    PacketType.DEPRECATION.value: DEPRECATION_REQUIRED_PATHS,
    PacketType.ROLLBACK.value: ROLLBACK_REQUIRED_PATHS,
    PacketType.RESURRECTION.value: RESURRECTION_REQUIRED_PATHS,
    PacketType.BRIDGE.value: ("declaration.claim_id", "declaration.bridge", "validity.root.status"),
    PacketType.KERNEL_UPDATE.value: KERNEL_UPDATE_REQUIRED_PATHS,
}
