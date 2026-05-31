# ALT Foundry Kernel

**ALT Foundry Kernel is an Apache-2.0, language-neutral bootloader for
Abstraction Liquidity Theory (ALT): a theory of when local problem-solving
traces can become reusable, certified abstraction capital.** The Python/uv
package in this repository is the reference implementation; the public contract
is the JSON Schema, packet semantics, lifecycle state machine, predicate names,
and fail-closed ledger behavior that other languages can implement directly.

ALT does not treat an artifact as valuable because it is plausible, elegant, or
useful on one benchmark. Its core claim is operational: a trace-derived object
becomes a liquid abstraction only when it is represented as an abstraction token,
bound to an executable certificate packet, evaluated against declared baselines
and opportunity laws, charged for formation, telemetry, transport, hazard,
rollback, refresh, and deprecation costs, and admitted by a fail-closed kernel
with positive signed surplus. Proxy-only evidence and weak sandbox results may
guide exploration, but they do not increase safe certified abstraction capital.

Source paper:
Takahashi, K. (2026). *Abstraction Liquidity Theory*. Zenodo.
[https://doi.org/10.5281/zenodo.20476200](https://doi.org/10.5281/zenodo.20476200)

This repository is not the full scientific implementation. It is the public
entry kernel for AI agents, research engineers, and automated foundry systems
that want to build toward the full paper in any programming language:
language-neutral schemas, packet examples, deterministic validation,
conservative signed-bound accounting, dual-ledger settlement, lifecycle
transitions, conformance expectations, and public-release audit tooling.

Search terms that describe the intended surface: Abstraction Liquidity Theory,
ALT, abstraction token, executable certificate packet, agent-operable foundry,
AI agent certification kernel, dual-ledger settlement, safe certified
abstraction capital, signed surplus, certified abstraction capital.

## Start Here For Agents

1. Read the paper DOI above and `docs/theory-map.md` to understand what the
   bootloader implements and what remains scientific work.
2. Inspect `schemas/packet.schema.json`; it is the language-neutral contract
   for executable certificate packets.
3. Read `docs/language-neutral-contract.md` before implementing the contract in
   TypeScript, Rust, Go, JVM languages, or another runtime.
4. Generate a packet with `uv run altk init-example candidate` or copy one from
   `examples/`.
5. Validate early with `uv run altk validate <packet.json>`.
6. Run one transition with
   `uv run altk decide <packet.json> --state examples/kernel_state_empty.json`.
7. Use `docs/full-implementation-roadmap.md` to add evidence-producing modules
   for causal value, transport, roots, finality, risk, recombination, and CARA.
8. Before publishing changes, run `uv run altk audit-public --strict`.

The repair rule is fail-closed: missing capital-relevant fields are undefined.
Do not fill missing cost, risk, telemetry, transport, or hazard fields with zero.
Provide measured evidence, declare a conservative charge, narrow the claim, keep
the packet in exploration, or reject the transition.

## Core Concepts

**Abstraction token**: an operational object extracted from traces with a stable
signature, representation, adapter, verifier contract, guard, cost/risk model,
provenance, and typed dependencies. A token can be a proof tactic, patch
pattern, evaluator harness, workflow policy, diagnostic rule, interface, or
governance constraint.

**Executable certificate packet**: the machine-readable record consumed by the
kernel. It separates declaration, evidence, bounds, validity, monitor, and
fallback layers so every capital-relevant claim is bound to typed fields.

**Signed surplus**: the central economic quantity. For positive settlement, the
bootloader uses the conservative lower-bound discipline:

```text
value_lower_bound - cost_upper_bound - risk_upper_bound - transport_upper_bound
```

Negative or stale certificates use the opposite upper-bound direction. Undefined
coordinates do not default to zero.

**Dual-ledger settlement**: exploration evidence and settlement evidence are
separate. Proxy-only evidence, weak mechanism evidence, sandbox trials, failed
candidates, threat findings, and high-variance experiments stay in the
exploration ledger. Safe certified capital is computed only from settlement
entries.

**Fail-closed certification kernel**: the kernel returns admit, reject, defer,
suspend, deprecate, rollback, or resurrect. It never admits a packet because a
free-text argument is persuasive.

## What This Bootloader Implements

| Area | Status | Public surface |
| --- | --- | --- |
| Packet schema and examples | Implemented | `schemas/`, `examples/` |
| Python models and CLI | Implemented | `Packet`, `KernelState`, `altk` |
| Signed lower and upper bounds | Implemented | `compute_signed_bounds` |
| Dual ledgers and lifecycle transitions | Implemented | `run_kernel_transition` |
| Admission predicate names | Implemented as status gates | `ValidationReport.predicates` |
| CARA target-crossing fields | Parseable and fail-closed | conditional validation |
| Bridge and kernel update packets | Parsed and audit-only in v1 | old kernel remains authoritative |
| Causal value, transport, roots, finality | Deferred | interfaces only |
| Reproduction, recombination, ASI target crossing | Deferred | fail-closed placeholders |

The v1 predicate report includes the paper-aligned gates:

`SchemaOK`, `NetLowerBoundOK`, `MissionOK`, `TargetValidityOK`,
`BaselineEnvelopeOK`, `BaselineLive`, `OpportunityLawOK`, `EvidenceLive`,
`SelectionOK`, `TelemetryOK`, `TransportOK`, `HazardOK`, `AuthorityOK`,
`CapabilityOK`, `ThreatOK`, `DependencyClosed`, `RootOK`, `QuorumOK`,
`FinalityOK`, `BudgetOK`, `CapacityOK`, `RefreshOK`, `RollbackOK`,
`DeprecationOK`, `RawNetSolvencyOK`, `RuntimeWitnessOK`, `NoncompHazardOK`,
and `ViabilityOK`.

In v1 these are field and status predicates. A full ALT foundry should replace
status assertions with evidence-producing modules while preserving the same
field names, failure semantics, and ledger discipline.

## Non-Python Implementers

Use Python as an executable reference, not as a dependency requirement. A
compatible TypeScript, Rust, Go, JVM, or other implementation should:

- consume the JSON Schemas in `schemas/`;
- preserve packet type and lifecycle enums exactly;
- expose the same predicate names and `true`/`false`/`null` semantics;
- compute signed lower and upper bounds with the same conservative direction;
- keep proxy-only evidence out of settlement capital;
- implement the same fail-closed lifecycle transitions;
- write every state-changing decision to an audit surface;
- pass the example packet suite and public conformance checks.

See `docs/language-neutral-contract.md` for the wire contract and conformance
expectations.

## What Is Deliberately Deferred

The bootloader does not certify:

- causal token-effect identification
- mission-validity bridges
- proxy-to-gold calibration
- finite-sample LCB/UCB or anytime-valid inference
- density-ratio, drift, or causal-invariance transport
- root/quorum cryptographic verification
- finality and PoUA weighting
- dynamic hazard and irreversible-risk ledgers
- reproduction matrices and recombination tensors
- capability-basis target membership
- certified ASI realization acceleration claims

Those modules should emit executable certificate packets rather than bypassing
the kernel. Until they supply typed evidence, their claims remain exploration
evidence or fail closed.

## Install

```bash
uv sync --dev
```

## CLI

```bash
uv run altk validate examples/admission_packet.json
uv run altk decide examples/admission_packet.json --state examples/kernel_state_empty.json
uv run altk schema packet
uv run altk init-example admission
uv run altk audit-public --strict
```

## Python API

```python
from alt_foundry_kernel import KernelState, compute_signed_bounds, run_kernel_transition

state = KernelState()
packet = {
    "id": "pkt-example",
    "type": "candidate",
    "token_id": "tok-example",
    "version": "0.1.0",
    "state": "candidate",
    "scope_hash": "sha256:scope",
    "declaration": {
        "lineage": {"source": "trace-derived"},
        "dependencies": {"objects": [], "dependency_closure": {"closed": True}},
        "scope": {"receiver_class": "example-agent"},
        "grammar": {"class": "WorkflowPolicyToken"},
        "baseline": {"policy_id": "baseline-policy"},
        "mission": {"mission_id": "example-mission"},
    },
    "evidence": {"status": "not-yet-collected"},
    "bounds": {"status": "not-yet-estimated"},
    "validity": {"status": "candidate-only"},
    "monitor": {"deprecation_rule": "declare before settlement"},
    "fallback": {"action": "keep-in-candidate-queue"},
    "signatures": [],
}

result = run_kernel_transition(state, packet)
assert result.decision == "defer"

bounds = compute_signed_bounds(
    {
        "value_lower_bound": 12,
        "cost_upper_bound": 3,
        "risk_upper_bound": 1,
        "transport_upper_bound": 1,
    }
)
assert bounds.lower_bound == 7
```

## Repository Map

- `schemas/`: language-neutral JSON Schemas for external agents and other
  runtimes.
- `src/alt_foundry_kernel/`: Python models, validation, signed-bound logic,
  public audit, and kernel transitions.
- `examples/`: candidate, proxy-only admission, positive admission,
  monitor-alarm, transport-refresh, deprecation, rollback, resurrection,
  bridge, and kernel-update packets.
- `docs/theory-map.md`: paper objects mapped to repo APIs and schemas.
- `docs/schema-contract.md`: paper-to-JSON packet field dictionary.
- `docs/language-neutral-contract.md`: conformance contract for non-Python
  implementations.
- `docs/agent-bootloader.md`: end-to-end workflow for agents.
- `docs/full-implementation-roadmap.md`: path from v1 bootloader to full ALT
  foundry.
- `docs/theory-alignment-audit.md`: implemented, approximated, deferred, and not
  certified theory claims.
- `docs/pre-release-audit.md`: reproducible public-release audit checklist.

## Validation And CI

```bash
uv run ruff check .
uv run mypy src
uv run pytest
uv run pip-audit
uv run altk audit-public --strict
```

Validate all bundled examples:

```bash
for f in examples/*_packet.json; do uv run altk validate "$f"; done
```

On Windows PowerShell:

```powershell
Get-ChildItem examples\*_packet.json | ForEach-Object { uv run altk validate $_.FullName }
```

## Building Toward Full ALT

A full implementation should add modules for trace instrumentation, token
grammar validation, opportunity-measure construction, mission validity, baseline
refresh, finite-sample lower and upper bounds, causal identification, proxy
calibration, telemetry collection, transport monitors, root/quorum finality,
dynamic risk, reproduction estimates, recombination confidence sets, and CARA
target-crossing checks.

The invariant is simple: until those modules emit typed evidence through an
executable certificate packet, they do not increase safe certified capital.

## Citation

Use `CITATION.cff`. If citing the theory, cite:

Takahashi, K. (2026). *Abstraction Liquidity Theory*. Zenodo.
[https://doi.org/10.5281/zenodo.20476200](https://doi.org/10.5281/zenodo.20476200)

## License

Apache License 2.0.
