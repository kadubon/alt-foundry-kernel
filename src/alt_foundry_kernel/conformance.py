"""Language-neutral conformance fixture runner."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from alt_foundry_kernel.authority import validate_authority_certificate
from alt_foundry_kernel.cara import validate_cara_certificate
from alt_foundry_kernel.cara_ext import validate_cara_process
from alt_foundry_kernel.causal import validate_causal_certificate
from alt_foundry_kernel.certificate_algebra import validate_certificate_composition
from alt_foundry_kernel.estimators import estimate_certificate
from alt_foundry_kernel.evaluator import validate_evaluator_hierarchy
from alt_foundry_kernel.finality import validate_finality_poua_ledger
from alt_foundry_kernel.foundry import replay_transcript
from alt_foundry_kernel.foundry_control import validate_foundry_control_state
from alt_foundry_kernel.measurement import validate_measurement_spec
from alt_foundry_kernel.mechanism import validate_mechanism_certificate
from alt_foundry_kernel.non_reduction import validate_non_reduction_audit
from alt_foundry_kernel.portfolio_ext import validate_portfolio_constraints
from alt_foundry_kernel.reproduction import validate_reproduction_certificate
from alt_foundry_kernel.risk import validate_risk_certificate
from alt_foundry_kernel.root_finality import validate_root_finality_certificate
from alt_foundry_kernel.sequential import validate_sequential_decision
from alt_foundry_kernel.transport import validate_transport_certificate
from alt_foundry_kernel.transport_ext import validate_transport_robustness

CONFORMANCE_LEVELS = {"L0", "L1", "L2", "L3", "L4", "L5"}
CERTIFICATE_CHECKERS = {
    "measurement": validate_measurement_spec,
    "transport": validate_transport_certificate,
    "risk": validate_risk_certificate,
    "authority": validate_authority_certificate,
    "root-finality": validate_root_finality_certificate,
    "causal": validate_causal_certificate,
    "cara": validate_cara_certificate,
    "reproduction": validate_reproduction_certificate,
    "non-reduction": validate_non_reduction_audit,
    "mechanism": validate_mechanism_certificate,
    "evaluator": validate_evaluator_hierarchy,
    "finality": validate_finality_poua_ledger,
    "sequential": validate_sequential_decision,
    "transport-ext": validate_transport_robustness,
    "certificate-algebra": validate_certificate_composition,
    "portfolio-ext": validate_portfolio_constraints,
    "foundry-control": validate_foundry_control_state,
    "cara-ext": validate_cara_process,
}


@dataclass(frozen=True)
class ConformanceFinding:
    path: str
    message: str


@dataclass(frozen=True)
class ConformanceReport:
    ok: bool
    checked: int
    level: str = "L5"
    findings: list[ConformanceFinding] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, sort_keys=True)


def run_conformance(fixtures: Path, level: str = "L5") -> ConformanceReport:
    """Run language-neutral conformance fixtures under a directory."""

    findings: list[ConformanceFinding] = []
    if level not in CONFORMANCE_LEVELS:
        return ConformanceReport(
            ok=False,
            checked=0,
            level=level,
            findings=[ConformanceFinding(str(fixtures), f"Unknown conformance level {level!r}.")],
        )
    checked = 0
    for path in sorted(fixtures.rglob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            checked += 1
            if level == "L0":
                continue
            _check_fixture(path, payload, level, findings)
        except Exception as exc:
            findings.append(ConformanceFinding(str(path), str(exc)))
    return ConformanceReport(ok=not findings, checked=checked, level=level, findings=findings)


def _check_fixture(
    path: Path, payload: dict[str, Any], level: str, findings: list[ConformanceFinding]
) -> None:
    fixture_type = payload.get("fixture_type")
    if fixture_type == "certificate":
        if level in {"L1", "L2"}:
            return
        kind = payload.get("kind")
        checker = CERTIFICATE_CHECKERS.get(kind) if isinstance(kind, str) else None
        if checker is None:
            findings.append(ConformanceFinding(str(path), f"Unknown certificate kind {kind!r}."))
            return
        report = checker(payload.get("payload", {}))
        expected_ok = payload.get("expected_ok", True)
        if report.ok is not expected_ok:
            findings.append(
                ConformanceFinding(
                    str(path),
                    f"Certificate fixture expected ok={expected_ok!r}, got ok={report.ok!r}.",
                )
            )
        return

    if fixture_type == "estimator":
        if level in {"L1", "L2"}:
            return
        kind = payload.get("kind")
        if not isinstance(kind, str):
            findings.append(ConformanceFinding(str(path), "Estimator fixture missing kind."))
            return
        report = estimate_certificate(kind, payload.get("payload", {}))
        expected_ok = payload.get("expected_ok", True)
        if report.ok is not expected_ok:
            findings.append(
                ConformanceFinding(
                    str(path),
                    f"Estimator fixture expected ok={expected_ok!r}, got ok={report.ok!r}.",
                )
            )
            return
        expected_metrics = payload.get("expected_metrics", {})
        if isinstance(expected_metrics, dict):
            for key, expected in expected_metrics.items():
                actual = report.metrics.get(str(key))
                if actual != expected:
                    findings.append(
                        ConformanceFinding(
                            str(path),
                            f"Estimator metric {key!r} expected {expected!r}, got {actual!r}.",
                        )
                    )
        return

    if level in {"L1", "L2", "L4", "L5"} and not replay_transcript(payload):
        findings.append(
            ConformanceFinding(str(path), "Transcript replay did not match expected state.")
        )
