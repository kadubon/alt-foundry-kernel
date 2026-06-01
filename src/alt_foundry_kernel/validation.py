"""Fail-closed packet validation."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from jsonschema import Draft202012Validator
from pydantic import ValidationError

from alt_foundry_kernel.bounds import compute_signed_bounds
from alt_foundry_kernel.constants import (
    ADMISSION_REQUIRED_PATHS,
    BASE_PACKET_REQUIRED_PATHS,
    CARA_CONDITIONAL_REQUIRED_PATHS,
    PREDICATE_NAMES,
    REQUIRED_PATHS_BY_TYPE,
    EstimandType,
    IssueSeverity,
    PacketType,
)
from alt_foundry_kernel.models import Packet, ValidationIssue, ValidationReport
from alt_foundry_kernel.schemas import load_schema


def _get_path(data: Mapping[str, Any], path: str) -> Any:
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            return None
        current = current[part]
    return current


def _issue(severity: IssueSeverity, code: str, path: str, message: str) -> ValidationIssue:
    return ValidationIssue(severity=severity, code=code, path=path, message=message)


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return bool(isinstance(value, dict) and not value)


def _status_is(raw_packet: Mapping[str, Any], path: str, *valid_values: object) -> bool:
    return _get_path(raw_packet, path) in valid_values


def _positive_number(raw_packet: Mapping[str, Any], path: str) -> bool:
    value = _get_path(raw_packet, path)
    return isinstance(value, int | float) and not isinstance(value, bool) and value > 0


def _present(raw_packet: Mapping[str, Any], path: str) -> bool:
    return not _is_missing(_get_path(raw_packet, path))


def _telemetry_ok(raw_packet: Mapping[str, Any]) -> bool:
    telemetry = _get_path(raw_packet, "validity.telemetry")
    return (
        isinstance(telemetry, Mapping)
        and (
            telemetry.get("status") == "valid"
            or telemetry.get("worst_case_charge_applied") is True
        )
    )


def _finality_ok(raw_packet: Mapping[str, Any]) -> bool:
    return _status_is(raw_packet, "validity.finality.state", "finalized") or (
        _get_path(raw_packet, "validity.finality.exempt") is True
    )


def _dependency_closed(raw_packet: Mapping[str, Any]) -> bool:
    return _get_path(raw_packet, "declaration.dependencies.dependency_closure.closed") is True


def _cara_claims_target_crossing(raw_packet: Mapping[str, Any]) -> bool:
    return _get_path(raw_packet, "declaration.cara.claims_target_crossing") is True


def _cara_claims_time_to_target(raw_packet: Mapping[str, Any]) -> bool:
    return _cara_claims_target_crossing(raw_packet) or (
        _get_path(raw_packet, "declaration.cara.claims_time_to_target_comparison") is True
    )


def _quorum_ok(raw_packet: Mapping[str, Any]) -> bool:
    root = _get_path(raw_packet, "validity.root")
    if not isinstance(root, Mapping):
        return False
    if root.get("status") != "valid":
        return False
    quorum = root.get("quorum")
    if quorum is None:
        return True
    return isinstance(quorum, Mapping) and (
        quorum.get("status") == "valid" or quorum.get("exempt") is True
    )


def _predicate_report(raw_packet: Mapping[str, Any], schema_ok: bool) -> dict[str, bool | None]:
    predicates: dict[str, bool | None] = {name: None for name in PREDICATE_NAMES}
    predicates["SchemaOK"] = schema_ok

    if raw_packet.get("type") != PacketType.ADMISSION.value:
        return predicates

    signed = compute_signed_bounds(raw_packet.get("bounds", {}))
    target_claimed = _cara_claims_target_crossing(raw_packet)
    time_claimed = _cara_claims_time_to_target(raw_packet)

    predicates.update(
        {
            "NetLowerBoundOK": signed.lower_bound is not None and signed.lower_bound > 0,
            "MissionOK": _status_is(raw_packet, "declaration.mission.status", "valid"),
            "TargetValidityOK": (
                (
                    _present(raw_packet, "declaration.cara.target_validity_certificate")
                    and _present(raw_packet, "declaration.cara.target_membership_proof")
                )
                if target_claimed
                else None
            ),
            "BaselineEnvelopeOK": (
                (
                    _present(raw_packet, "declaration.cara.baseline_upper_envelope")
                    and _present(raw_packet, "declaration.cara.time_to_target_claim")
                )
                if time_claimed
                else None
            ),
            "BaselineLive": _status_is(
                raw_packet, "declaration.baseline.status", "live", "valid"
            ),
            "OpportunityLawOK": _status_is(
                raw_packet, "declaration.opportunity_law.status", "valid"
            ),
            "EvidenceLive": _status_is(raw_packet, "evidence.status", "valid", "live"),
            "SelectionOK": _status_is(
                raw_packet, "evidence.selection_status", "valid", "not_required"
            ),
            "TelemetryOK": _telemetry_ok(raw_packet),
            "TransportOK": _status_is(raw_packet, "validity.transport.status", "valid"),
            "HazardOK": _status_is(raw_packet, "validity.hazard.status", "valid"),
            "AuthorityOK": _status_is(raw_packet, "declaration.authority.status", "valid"),
            "CapabilityOK": _status_is(raw_packet, "declaration.capability.status", "valid"),
            "ThreatOK": _status_is(raw_packet, "declaration.threat_model.status", "cleared"),
            "DependencyClosed": _dependency_closed(raw_packet),
            "RootOK": _status_is(raw_packet, "validity.root.status", "valid"),
            "QuorumOK": _quorum_ok(raw_packet),
            "FinalityOK": _finality_ok(raw_packet),
            "BudgetOK": _status_is(raw_packet, "validity.budget.status", "valid"),
            "CapacityOK": _status_is(raw_packet, "validity.capacity.status", "valid"),
            "RefreshOK": _status_is(raw_packet, "validity.refresh.status", "valid"),
            "RollbackOK": _status_is(raw_packet, "validity.rollback.status", "valid"),
            "DeprecationOK": _status_is(raw_packet, "validity.deprecation.status", "valid"),
            "RawNetSolvencyOK": _positive_number(
                raw_packet, "bounds.raw_net_capital_lower_bound"
            ),
            "RuntimeWitnessOK": _status_is(
                raw_packet, "declaration.runtime_witness.status", "valid"
            ),
            "NoncompHazardOK": (
                _get_path(raw_packet, "validity.hazard.noncompensable_clearance") is True
            ),
            "ViabilityOK": _status_is(raw_packet, "validity.viability.status", "valid"),
        }
    )
    return predicates


def _schema_issues(raw_packet: Mapping[str, Any]) -> list[ValidationIssue]:
    validator = Draft202012Validator(load_schema("packet"))
    issues: list[ValidationIssue] = []
    for error in sorted(validator.iter_errors(raw_packet), key=lambda err: list(err.path)):
        path = ".".join(str(item) for item in error.path) or "<root>"
        issues.append(_issue(IssueSeverity.ERROR, "schema-error", path, error.message))
    return issues


def _model_issues(raw_packet: Mapping[str, Any]) -> list[ValidationIssue]:
    try:
        Packet.model_validate(raw_packet)
    except ValidationError as exc:
        return [
            _issue(
                IssueSeverity.ERROR,
                "model-error",
                ".".join(str(item) for item in error["loc"]),
                str(error["msg"]),
            )
            for error in exc.errors()
        ]
    return []


def _required_path_issues(raw_packet: Mapping[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for path in BASE_PACKET_REQUIRED_PATHS:
        if _is_missing(_get_path(raw_packet, path)):
            issues.append(
                _issue(
                    IssueSeverity.ERROR,
                    "required-field-missing",
                    path,
                    "Required top-level packet field is missing or empty.",
                )
            )

    packet_type = raw_packet.get("type")
    if not isinstance(packet_type, str):
        return issues

    for path in REQUIRED_PATHS_BY_TYPE.get(packet_type, ()):
        if _is_missing(_get_path(raw_packet, path)):
            issues.append(
                _issue(
                    IssueSeverity.ERROR,
                    "required-field-missing",
                    path,
                    f"Required field for {packet_type!r} packet is missing or empty.",
                )
            )
    if packet_type == PacketType.ADMISSION.value and _cara_claims_target_crossing(raw_packet):
        for path in CARA_CONDITIONAL_REQUIRED_PATHS:
            if _is_missing(_get_path(raw_packet, path)):
                issues.append(
                    _issue(
                        IssueSeverity.ERROR,
                        "cara-required-field-missing",
                        path,
                        "CARA target-crossing claims require this field.",
                    )
                )
    return issues


def _semantic_issues(
    raw_packet: Mapping[str, Any], predicates: Mapping[str, bool | None]
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    packet_type = raw_packet.get("type")

    if packet_type == PacketType.ADMISSION.value:
        estimand_type = _get_path(raw_packet, "declaration.estimand.estimand_type")
        if estimand_type == EstimandType.PROXY_ONLY.value:
            issues.append(
                _issue(
                    IssueSeverity.INFO,
                    "proxy-only-exploration",
                    "declaration.estimand.estimand_type",
                    "Proxy-only evidence is exploration evidence and cannot increase safe capital.",
                )
            )
        elif estimand_type not in {EstimandType.CAUSAL.value, EstimandType.CALIBRATED_PROXY.value}:
            issues.append(
                _issue(
                    IssueSeverity.ERROR,
                    "estimand-not-settlement-grade",
                    "declaration.estimand.estimand_type",
                    "Settlement requires causal or calibrated-proxy estimand evidence.",
                )
            )

        signed = compute_signed_bounds(raw_packet.get("bounds", {}))
        for missing in signed.missing_for_lower:
            issues.append(
                _issue(
                    IssueSeverity.ERROR,
                    "signed-lower-bound-undefined",
                    f"bounds.{missing}",
                    "Positive settlement cannot use an undefined signed lower-bound coordinate.",
                )
            )

        if not _telemetry_ok(raw_packet):
            issues.append(
                _issue(
                    IssueSeverity.ERROR,
                    "telemetry-not-valid",
                    "validity.telemetry",
                    "Telemetry must be valid or a worst-case telemetry charge must be applied.",
                )
            )

    requires_finality = packet_type in {
        PacketType.ADMISSION.value,
        PacketType.RESURRECTION.value,
    }
    if requires_finality and not _finality_ok(raw_packet):
        issues.append(
            _issue(
                IssueSeverity.ERROR,
                "finality-not-valid",
                "validity.finality.state",
                "Capital-increasing transitions require finalized evidence "
                "or a narrow exemption.",
            )
        )

    if packet_type == PacketType.ADMISSION.value:
        for name, value in predicates.items():
            if name == "SchemaOK" or value is not False:
                continue
            issues.append(
                _issue(
                    IssueSeverity.ERROR,
                    "predicate-failed",
                    name,
                    f"{name} is false for this admission packet.",
                )
            )

    return issues


def _admission_predicates_satisfied(predicates: Mapping[str, bool | None]) -> bool:
    return predicates.get("SchemaOK") is True and all(
        value is not False for name, value in predicates.items() if name != "SchemaOK"
    )


def validate_packet(packet: Packet | Mapping[str, Any]) -> ValidationReport:
    """Validate a packet against JSON Schema, Pydantic types, and ALT gates."""

    raw_packet: Mapping[str, Any] = (
        packet.model_dump(mode="json") if isinstance(packet, Packet) else packet
    )

    issues = _schema_issues(raw_packet)
    schema_ok = not any(issue.code == "schema-error" for issue in issues)
    predicates = _predicate_report(raw_packet, schema_ok)
    issues.extend(_model_issues(raw_packet))
    issues.extend(_required_path_issues(raw_packet))
    issues.extend(_semantic_issues(raw_packet, predicates))

    hard_error = any(issue.severity == IssueSeverity.ERROR for issue in issues)
    packet_type = raw_packet.get("type")
    settlement_decidable = schema_ok and not hard_error
    can_increase_capital = False

    if packet_type == PacketType.ADMISSION.value and schema_ok:
        missing = [
            path for path in ADMISSION_REQUIRED_PATHS if _is_missing(_get_path(raw_packet, path))
        ]
        estimand_type = _get_path(raw_packet, "declaration.estimand.estimand_type")
        raw_net = _get_path(raw_packet, "bounds.raw_net_capital_lower_bound")
        raw_net_positive = (
            isinstance(raw_net, int | float) and not isinstance(raw_net, bool) and raw_net > 0
        )
        can_increase_capital = (
            not missing
            and not hard_error
            and raw_net_positive
            and _admission_predicates_satisfied(predicates)
            and estimand_type in {EstimandType.CAUSAL.value, EstimandType.CALIBRATED_PROXY.value}
        )

    return ValidationReport(
        ok=not hard_error,
        schema_ok=schema_ok,
        settlement_decidable=settlement_decidable,
        can_increase_capital=can_increase_capital,
        issues=issues,
        predicates=predicates,
    )
