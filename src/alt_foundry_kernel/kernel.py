"""Deterministic fail-closed ALT bootloader kernel."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pydantic import ValidationError

from alt_foundry_kernel.bounds import compute_signed_bounds
from alt_foundry_kernel.constants import Decision, EstimandType, LifecycleState, PacketType
from alt_foundry_kernel.models import (
    KernelState,
    LedgerEntry,
    Packet,
    SignedBoundReport,
    TransitionResult,
    ValidationIssue,
)
from alt_foundry_kernel.validation import validate_packet


def _entry(
    packet: Packet,
    ledger: str,
    decision: Decision,
    state: LifecycleState,
    reason: str,
    capital_delta: float = 0.0,
    details: dict[str, Any] | None = None,
) -> LedgerEntry:
    return LedgerEntry(
        entry_id=f"{packet.id}:{ledger}:{decision.value}",
        packet_id=packet.id,
        token_id=packet.token_id,
        ledger=ledger,  # type: ignore[arg-type]
        decision=decision,
        state=state,
        capital_delta=capital_delta,
        reason=reason,
        details=details or {},
    )


def _append_audit(state: KernelState, entry: LedgerEntry) -> None:
    state.audit_log.append(entry)


def _append_by_ledger(state: KernelState, entry: LedgerEntry) -> None:
    if entry.ledger == "candidate_queue":
        state.candidate_queue.append(entry)
    elif entry.ledger == "exploration":
        state.exploration_ledger.append(entry)
    elif entry.ledger == "settlement":
        state.settlement_ledger.append(entry)
    elif entry.ledger == "negative_registry":
        state.negative_registry.append(entry)
    _append_audit(state, entry)


def _raw_net(packet: Packet) -> float | None:
    value = packet.bounds.get("raw_net_capital_lower_bound")
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    return float(value)


def _positive_capital_delta(packet: Packet, signed: SignedBoundReport) -> float:
    raw_net = _raw_net(packet)
    candidates = [value for value in (raw_net, signed.lower_bound) if value is not None]
    if not candidates:
        return 0.0
    return max(0.0, min(candidates))


def _status(mapping: Mapping[str, Any], key: str) -> Any:
    current: Any = mapping
    for part in key.split("."):
        if not isinstance(current, Mapping):
            return None
        current = current.get(part)
    return current


def _dependencies_closed(packet: Packet, state: KernelState) -> bool:
    dependencies = packet.declaration.get("dependencies", {})
    if isinstance(dependencies, Mapping):
        closure = dependencies.get("dependency_closure", {})
        if isinstance(closure, Mapping) and closure.get("closed") is False:
            return False
        objects = dependencies.get("objects", [])
        if isinstance(objects, list):
            for item in objects:
                if not isinstance(item, Mapping):
                    return False
                object_type = item.get("object_type")
                object_id = item.get("object_id")
                if object_type == "Tok":
                    if (
                        object_id not in state.admitted_tokens
                        and item.get("available") is not True
                        and item.get("included_in_packet") is not True
                    ):
                        return False
                elif item.get("available") is not True:
                    return False
    return True


def _state_dependency_failures(packet: Packet, state: KernelState) -> list[str]:
    failures: list[str] = []
    if not _dependencies_closed(packet, state):
        failures.append("DependencyClosed")
    return failures


def _telemetry_valid(packet: Packet) -> bool:
    telemetry = packet.validity.get("telemetry", {})
    return isinstance(telemetry, Mapping) and (
        telemetry.get("status") == "valid" or telemetry.get("worst_case_charge_applied") is True
    )


def _root_quorum_valid(packet: Packet) -> bool:
    root = packet.validity.get("root", {})
    if not isinstance(root, Mapping) or root.get("status") != "valid":
        return False
    quorum = root.get("quorum")
    if quorum is None:
        return True
    return isinstance(quorum, Mapping) and (
        quorum.get("status") == "valid" or quorum.get("exempt") is True
    )


def _resurrection_settlement_ready(
    packet: Packet, state: KernelState, signed: SignedBoundReport
) -> bool:
    estimand_type = _status(packet.declaration, "estimand.estimand_type")
    finality_ok = _status(packet.validity, "finality.state") == "finalized" or (
        _status(packet.validity, "finality.exempt") is True
    )
    static_status_ok = all(
        (
            _status(packet.declaration, "mission.status") == "valid",
            _status(packet.declaration, "baseline.status") in {"live", "valid"},
            _status(packet.declaration, "opportunity_law.status") == "valid",
            _status(packet.declaration, "authority.status") == "valid",
            _status(packet.declaration, "capability.status") == "valid",
            _status(packet.declaration, "threat_model.status") == "cleared",
            _status(packet.declaration, "runtime_witness.status") == "valid",
            _status(packet.evidence, "status") in {"valid", "live"},
            _status(packet.evidence, "selection_status") in {"valid", "not_required"},
            _telemetry_valid(packet),
            _status(packet.validity, "transport.status") == "valid",
            _status(packet.validity, "hazard.status") == "valid",
            _status(packet.validity, "hazard.noncompensable_clearance") is True,
            _root_quorum_valid(packet),
            finality_ok,
            _status(packet.validity, "budget.status") == "valid",
            _status(packet.validity, "capacity.status") == "valid",
            _status(packet.validity, "refresh.status") == "valid",
            _status(packet.validity, "rollback.status") == "valid",
            _status(packet.validity, "deprecation.status") == "valid",
            _status(packet.validity, "viability.status") == "valid",
        )
    )
    return (
        estimand_type in {EstimandType.CAUSAL.value, EstimandType.CALIBRATED_PROXY.value}
        and static_status_ok
        and _dependencies_closed(packet, state)
        and signed.lower_bound is not None
        and signed.lower_bound > 0
        and (_raw_net(packet) or 0.0) > 0
    )


def _reject_result(
    state: KernelState,
    packet: Packet,
    decision: Decision,
    state_value: LifecycleState,
    reason: str,
    signed: SignedBoundReport,
    issues: list[ValidationIssue] | None = None,
) -> TransitionResult:
    next_state = state.model_copy(deep=True)
    entry = _entry(packet, "audit", decision, state_value, reason)
    next_state.token_states[packet.token_id] = state_value
    if state_value != LifecycleState.ACTIVE and packet.token_id in next_state.admitted_tokens:
        next_state.admitted_tokens.remove(packet.token_id)
    _append_audit(next_state, entry)
    validation = validate_packet(packet)
    if issues:
        validation.issues.extend(issues)
        validation.ok = False
        validation.settlement_decidable = False
        validation.can_increase_capital = False
    return TransitionResult(
        decision=decision,
        packet_id=packet.id,
        token_id=packet.token_id,
        next_state=next_state,
        ledger_entry=entry,
        validation=validation,
        signed_bounds=signed,
    )


def _failure_decision(packet_type: PacketType) -> tuple[Decision, LifecycleState, str]:
    if packet_type == PacketType.TRANSPORT_REFRESH:
        return Decision.DEFER, LifecycleState.SUSPENDED, "Transport refresh failed closed."
    if packet_type == PacketType.MONITOR_ALARM:
        return Decision.SUSPEND, LifecycleState.SUSPENDED, "Monitor alarm failed closed."
    if packet_type == PacketType.DEPRECATION:
        return Decision.SUSPEND, LifecycleState.SUSPENDED, "Deprecation failed closed."
    if packet_type == PacketType.ROLLBACK:
        return Decision.SUSPEND, LifecycleState.SUSPENDED, "Rollback failed closed."
    if packet_type == PacketType.RESURRECTION:
        return (
            Decision.REJECT,
            LifecycleState.DEPRECATED,
            "Resurrection failed closed and retained the negative certificate.",
        )
    if packet_type == PacketType.KERNEL_UPDATE:
        return Decision.REJECT, LifecycleState.ACTIVE, "Kernel update failed closed."
    return Decision.DEFER, LifecycleState.EXPLORATION, "Packet failed closed."


def _parse_packet(packet: Packet | Mapping[str, Any]) -> Packet:
    if isinstance(packet, Packet):
        return packet
    return Packet.model_validate(packet)


def run_kernel_transition(
    state: KernelState | Mapping[str, Any], packet: Packet | Mapping[str, Any]
) -> TransitionResult:
    """Run one deterministic v1 kernel transition.

    The function implements the bootloader rule, not a full ALT foundry. Missing
    capital-relevant evidence never defaults to zero; it rejects, defers, suspends,
    or routes the packet to exploration.
    """

    kernel_state = state if isinstance(state, KernelState) else KernelState.model_validate(state)
    try:
        typed_packet = _parse_packet(packet)
    except ValidationError:
        raw_packet = packet if isinstance(packet, Mapping) else packet.model_dump(mode="json")
        fallback_packet = Packet(
            id=str(raw_packet.get("id", "invalid-packet")),
            type=PacketType.CANDIDATE,
            token_id=str(raw_packet.get("token_id", "unknown-token")),
            version=str(raw_packet.get("version", "unknown")),
            state=LifecycleState.CANDIDATE,
            scope_hash=str(raw_packet.get("scope_hash", "undefined")),
            declaration={},
            evidence={},
            bounds={},
            validity={},
            monitor={},
            fallback={},
            signatures=[],
        )
        return _reject_result(
            kernel_state,
            fallback_packet,
            Decision.REJECT,
            LifecycleState.CANDIDATE,
            "Packet did not parse as the public Packet model.",
            compute_signed_bounds({}),
        )

    validation = validate_packet(typed_packet)
    signed = compute_signed_bounds(typed_packet.bounds)
    next_state = kernel_state.model_copy(deep=True)

    if typed_packet.type == PacketType.CANDIDATE:
        if not validation.ok:
            return _reject_result(
                kernel_state,
                typed_packet,
                Decision.REJECT,
                LifecycleState.CANDIDATE,
                "Candidate packet failed schema or required-field validation.",
                signed,
            )
        entry = _entry(
            typed_packet,
            "candidate_queue",
            Decision.DEFER,
            LifecycleState.CANDIDATE,
            "Candidate recorded for exploration; no certified capital was added.",
        )
        next_state.token_states[typed_packet.token_id] = LifecycleState.CANDIDATE
        _append_by_ledger(next_state, entry)
        return TransitionResult(
            decision=Decision.DEFER,
            packet_id=typed_packet.id,
            token_id=typed_packet.token_id,
            next_state=next_state,
            ledger_entry=entry,
            validation=validation,
            signed_bounds=signed,
        )

    if typed_packet.type == PacketType.ADMISSION:
        if not validation.schema_ok:
            return _reject_result(
                kernel_state,
                typed_packet,
                Decision.REJECT,
                LifecycleState.CANDIDATE,
                "Admission packet failed schema validation.",
                signed,
            )
        if validation.missing_paths():
            return _reject_result(
                kernel_state,
                typed_packet,
                Decision.DEFER,
                LifecycleState.EXPLORATION,
                "Admission packet has undefined capital-relevant fields.",
                signed,
            )
        if not validation.ok:
            return _reject_result(
                kernel_state,
                typed_packet,
                Decision.REJECT,
                LifecycleState.EXPLORATION,
                "Admission packet failed one or more ALT admission predicates.",
                signed,
            )
        estimand_type = _status(typed_packet.declaration, "estimand.estimand_type")
        if estimand_type == EstimandType.PROXY_ONLY.value:
            entry = _entry(
                typed_packet,
                "exploration",
                Decision.DEFER,
                LifecycleState.EXPLORATION,
                "Proxy-only evidence cannot increase safe certified capital.",
                details={"estimand_type": estimand_type},
            )
            next_state.token_states[typed_packet.token_id] = LifecycleState.EXPLORATION
            _append_by_ledger(next_state, entry)
            return TransitionResult(
                decision=Decision.DEFER,
                packet_id=typed_packet.id,
                token_id=typed_packet.token_id,
                next_state=next_state,
                ledger_entry=entry,
                validation=validation,
                signed_bounds=signed,
            )

        predicate_failures = _state_dependency_failures(typed_packet, next_state)
        if predicate_failures:
            return _reject_result(
                kernel_state,
                typed_packet,
                Decision.REJECT,
                LifecycleState.EXPLORATION,
                "Admission predicates failed: " + ", ".join(predicate_failures),
                signed,
            )
        capital_delta = _positive_capital_delta(typed_packet, signed)
        if capital_delta <= 0:
            return _reject_result(
                kernel_state,
                typed_packet,
                Decision.REJECT,
                LifecycleState.EXPLORATION,
                "Admission lower bound is not positive after costs, risk, and transport charges.",
                signed,
            )
        entry = _entry(
            typed_packet,
            "settlement",
            Decision.ADMIT,
            LifecycleState.ACTIVE,
            "Admission packet satisfied v1 settlement gates.",
            capital_delta=capital_delta,
            details={"signed_lower_bound": signed.lower_bound},
        )
        if typed_packet.token_id not in next_state.admitted_tokens:
            next_state.admitted_tokens.append(typed_packet.token_id)
        next_state.token_states[typed_packet.token_id] = LifecycleState.ACTIVE
        next_state.certified_capital += capital_delta
        _append_by_ledger(next_state, entry)
        return TransitionResult(
            decision=Decision.ADMIT,
            packet_id=typed_packet.id,
            token_id=typed_packet.token_id,
            next_state=next_state,
            ledger_entry=entry,
            validation=validation,
            signed_bounds=signed,
        )

    if not validation.ok:
        decision, state_value, reason = _failure_decision(typed_packet.type)
        return _reject_result(kernel_state, typed_packet, decision, state_value, reason, signed)

    if typed_packet.type == PacketType.DEPRECATION:
        current = next_state.token_states.get(typed_packet.token_id)
        if current not in {LifecycleState.ACTIVE, LifecycleState.SUSPENDED}:
            return _reject_result(
                kernel_state,
                typed_packet,
                Decision.REJECT,
                LifecycleState.DEPRECATED,
                "Deprecation requires an active or suspended token state.",
                signed,
            )
        entry = _entry(
            typed_packet,
            "negative_registry",
            Decision.DEPRECATE,
            LifecycleState.DEPRECATED,
            "Scope-limited negative or stale certificate recorded.",
        )
        next_state.token_states[typed_packet.token_id] = LifecycleState.DEPRECATED
        if typed_packet.token_id in next_state.admitted_tokens:
            next_state.admitted_tokens.remove(typed_packet.token_id)
        _append_by_ledger(next_state, entry)
        return TransitionResult(
            decision=Decision.DEPRECATE,
            packet_id=typed_packet.id,
            token_id=typed_packet.token_id,
            next_state=next_state,
            ledger_entry=entry,
            validation=validation,
            signed_bounds=signed,
        )

    if typed_packet.type == PacketType.TRANSPORT_REFRESH:
        current = next_state.token_states.get(typed_packet.token_id)
        if current not in {LifecycleState.ACTIVE, LifecycleState.SUSPENDED}:
            return _reject_result(
                kernel_state,
                typed_packet,
                Decision.DEFER,
                LifecycleState.SUSPENDED,
                "Transport refresh requires an active or suspended token state.",
                signed,
            )
        if _status(typed_packet.validity, "transport.status") != "valid":
            entry = _entry(
                typed_packet,
                "audit",
                Decision.DEFER,
                LifecycleState.SUSPENDED,
                "Transport refresh did not cover the target scope; token remains suspended.",
            )
            next_state.token_states[typed_packet.token_id] = LifecycleState.SUSPENDED
            _append_audit(next_state, entry)
            return TransitionResult(
                decision=Decision.DEFER,
                packet_id=typed_packet.id,
                token_id=typed_packet.token_id,
                next_state=next_state,
                ledger_entry=entry,
                validation=validation,
                signed_bounds=signed,
            )
        entry = _entry(
            typed_packet,
            "settlement",
            Decision.ADMIT,
            LifecycleState.ACTIVE,
            "Transport refresh restored only the covered receiver and context-law scope.",
        )
        next_state.token_states[typed_packet.token_id] = LifecycleState.ACTIVE
        if typed_packet.token_id not in next_state.admitted_tokens:
            next_state.admitted_tokens.append(typed_packet.token_id)
        _append_by_ledger(next_state, entry)
        return TransitionResult(
            decision=Decision.ADMIT,
            packet_id=typed_packet.id,
            token_id=typed_packet.token_id,
            next_state=next_state,
            ledger_entry=entry,
            validation=validation,
            signed_bounds=signed,
        )

    if typed_packet.type == PacketType.ROLLBACK:
        current = next_state.token_states.get(typed_packet.token_id)
        if current not in {LifecycleState.ACTIVE, LifecycleState.SUSPENDED}:
            return _reject_result(
                kernel_state,
                typed_packet,
                Decision.REJECT,
                LifecycleState.SUSPENDED,
                "Rollback requires an active or suspended token state.",
                signed,
        )
        charge = typed_packet.bounds.get("reserve_charge", 0.0)
        charge_value = 0.0
        if isinstance(charge, int | float) and not isinstance(charge, bool):
            charge_value = float(charge)
        next_state.certified_capital = max(0.0, next_state.certified_capital - charge_value)
        output_state = typed_packet.fallback.get("output_state", LifecycleState.SUSPENDED.value)
        lifecycle = (
            LifecycleState.ACTIVE
            if output_state == LifecycleState.ACTIVE.value
            else LifecycleState.SUSPENDED
        )
        entry = _entry(
            typed_packet,
            "audit",
            Decision.ROLLBACK,
            lifecycle,
            "Rollback applied with declared reserve charge.",
            capital_delta=-charge_value,
        )
        next_state.token_states[typed_packet.token_id] = lifecycle
        if (
            lifecycle == LifecycleState.SUSPENDED
            and typed_packet.token_id in next_state.admitted_tokens
        ):
            next_state.admitted_tokens.remove(typed_packet.token_id)
        _append_audit(next_state, entry)
        return TransitionResult(
            decision=Decision.ROLLBACK,
            packet_id=typed_packet.id,
            token_id=typed_packet.token_id,
            next_state=next_state,
            ledger_entry=entry,
            validation=validation,
            signed_bounds=signed,
        )

    if typed_packet.type == PacketType.RESURRECTION:
        current = next_state.token_states.get(typed_packet.token_id)
        if current != LifecycleState.DEPRECATED:
            return _reject_result(
                kernel_state,
                typed_packet,
                Decision.REJECT,
                LifecycleState.DEPRECATED,
                "Resurrection requires a deprecated token state.",
                signed,
            )
        capital_delta = _positive_capital_delta(typed_packet, signed)
        if _resurrection_settlement_ready(typed_packet, next_state, signed):
            lifecycle = LifecycleState.ACTIVE
            ledger = "settlement"
            if typed_packet.token_id not in next_state.admitted_tokens:
                next_state.admitted_tokens.append(typed_packet.token_id)
            next_state.certified_capital += capital_delta
        else:
            lifecycle = LifecycleState.CANDIDATE
            ledger = "candidate_queue"
            capital_delta = 0.0
        entry = _entry(
            typed_packet,
            ledger,
            Decision.RESURRECT,
            lifecycle,
            "Resurrection packet applied under current evidence.",
            capital_delta=capital_delta,
        )
        next_state.token_states[typed_packet.token_id] = lifecycle
        _append_by_ledger(next_state, entry)
        return TransitionResult(
            decision=Decision.RESURRECT,
            packet_id=typed_packet.id,
            token_id=typed_packet.token_id,
            next_state=next_state,
            ledger_entry=entry,
            validation=validation,
            signed_bounds=signed,
        )

    if typed_packet.type == PacketType.MONITOR_ALARM:
        current = next_state.token_states.get(typed_packet.token_id)
        if current not in {LifecycleState.ACTIVE, LifecycleState.PENDING_SETTLEMENT}:
            return _reject_result(
                kernel_state,
                typed_packet,
                Decision.SUSPEND,
                LifecycleState.SUSPENDED,
                "Monitor alarm requires an active or pending-settlement token state.",
                signed,
            )
        entry = _entry(
            typed_packet,
            "audit",
            Decision.SUSPEND,
            LifecycleState.SUSPENDED,
            "Monitor alarm suspended the token for new contribution.",
        )
        next_state.token_states[typed_packet.token_id] = LifecycleState.SUSPENDED
        if typed_packet.token_id in next_state.admitted_tokens:
            next_state.admitted_tokens.remove(typed_packet.token_id)
        _append_audit(next_state, entry)
        return TransitionResult(
            decision=Decision.SUSPEND,
            packet_id=typed_packet.id,
            token_id=typed_packet.token_id,
            next_state=next_state,
            ledger_entry=entry,
            validation=validation,
            signed_bounds=signed,
        )

    if typed_packet.type == PacketType.BRIDGE:
        entry = _entry(
            typed_packet,
            "audit",
            Decision.DEFER,
            typed_packet.state,
            "Bridge packet recorded; v1 bootloader does not apply bridge semantics.",
        )
        _append_audit(next_state, entry)
        return TransitionResult(
            decision=Decision.DEFER,
            packet_id=typed_packet.id,
            token_id=typed_packet.token_id,
            next_state=next_state,
            ledger_entry=entry,
            validation=validation,
            signed_bounds=signed,
        )

    if typed_packet.type == PacketType.KERNEL_UPDATE:
        entry = _entry(
            typed_packet,
            "audit",
            Decision.DEFER,
            LifecycleState.ACTIVE,
            "Kernel update packet recorded; the current kernel remains authoritative in v1.",
        )
        _append_audit(next_state, entry)
        return TransitionResult(
            decision=Decision.DEFER,
            packet_id=typed_packet.id,
            token_id=typed_packet.token_id,
            next_state=next_state,
            ledger_entry=entry,
            validation=validation,
            signed_bounds=signed,
        )

    return _reject_result(
        kernel_state,
        typed_packet,
        Decision.DEFER,
        typed_packet.state,
        "Packet type is parsed but v1 bootloader does not perform a capital-changing transition.",
        signed,
    )
