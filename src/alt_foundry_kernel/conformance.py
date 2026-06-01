"""Language-neutral conformance fixture runner."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from alt_foundry_kernel.foundry import replay_transcript


@dataclass(frozen=True)
class ConformanceFinding:
    path: str
    message: str


@dataclass(frozen=True)
class ConformanceReport:
    ok: bool
    checked: int
    findings: list[ConformanceFinding] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, sort_keys=True)


def run_conformance(fixtures: Path) -> ConformanceReport:
    """Replay every JSON transcript fixture under a directory."""

    findings: list[ConformanceFinding] = []
    checked = 0
    for path in sorted(fixtures.rglob("*.json")):
        checked += 1
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if not replay_transcript(payload):
                findings.append(
                    ConformanceFinding(str(path), "Transcript replay did not match expected state.")
                )
        except Exception as exc:
            findings.append(ConformanceFinding(str(path), str(exc)))
    return ConformanceReport(ok=not findings, checked=checked, findings=findings)
