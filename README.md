# ALT Foundry Kernel

**ALT Foundry Kernel is an Apache-2.0, language-neutral implementation surface
for Abstraction Liquidity Theory (ALT): a theory of when local problem-solving
traces can become reusable, certified abstraction capital.** The repository is
designed for AI agents and research engineers that need executable certificate
packets, abstraction tokens, dual-ledger settlement, conservative signed surplus
accounting, and fail-closed certification semantics that can be implemented in
Python, TypeScript, Rust, Go, JVM languages, or another runtime.

ALT's central claim is operational. A trace is not safe certified abstraction
capital because it looks useful, transfers once, or scores well on a proxy
benchmark. A trace-derived object becomes liquid only when it is represented as
an abstraction token, bound to an executable certificate packet, evaluated under
declared mission laws, baselines, opportunity laws, evidence splits, transport
claims, authority/capability envelopes, hazard controls, lifecycle costs,
root/quorum/finality records, and admitted by a kernel with positive signed
surplus. Missing capital-relevant evidence is undefined, not zero.

Source paper:
Takahashi, K. (2026). *Abstraction Liquidity Theory*. Zenodo.
[https://doi.org/10.5281/zenodo.20476200](https://doi.org/10.5281/zenodo.20476200)

Search terms accurately describing this project: Abstraction Liquidity Theory,
ALT, abstraction token, executable certificate packet, agent-operable foundry,
AI agent certification kernel, dual-ledger settlement, safe certified
abstraction capital, signed surplus, language-neutral JSON Schema, certificate
transcript, foundry conformance, causal evidence certificate, transportability
certificate, CARA target-crossing checker.

## What v0.2.0 Is

`v0.2.0` is no longer only a bootloader. It is a reference kernel plus a
portable contract for other agents:

- `schemas/` defines the language-neutral wire contract.
- `examples/` gives packets and module-level certificate examples.
- `conformance/` gives golden decision transcripts for non-Python runtimes.
- `src/alt_foundry_kernel/` is the Python reference implementation.
- `docs/` maps the paper into implementable modules and release audits.

The implementation remains scientifically bounded. It verifies supplied
certificates and conservative arithmetic; it does not infer causal effects,
transportability, recombination tensors, or ASI target crossing from raw data
unless those claims are supplied as explicit evidence-bearing certificates.

## Start Here For Agents

1. Read the DOI above and `docs/theory-map.md`.
2. Read `docs/language-neutral-contract.md` before implementing ALT outside
   Python.
3. Inspect `schemas/packet.schema.json` and
   `schemas/foundry-transcript.schema.json`.
4. Validate examples with `uv run altk validate examples/admission_packet.json`.
5. Run a transition with
   `uv run altk decide examples/admission_packet.json --state examples/kernel_state_empty.json`.
6. Run module checkers such as
   `uv run altk certify transport examples/certificates/transport_certificate.json`.
7. Replay conformance fixtures with `uv run altk conformance --fixtures conformance`.
8. Before publishing, run `uv run altk audit-public --strict`.

Repair order for failed packets: schema, packet-type fields, dependency closure,
mission/baseline/opportunity, measurement/evidence, signed bounds, telemetry,
transport, hazard, authority, capability, threat, root/quorum/finality, budget,
capacity, refresh, rollback, deprecation, raw-net solvency, noncompensable
hazard, viability, and only then CARA target-crossing fields.

## Install

```bash
uv sync --dev
```

Runtime dependencies are local libraries only: `pydantic`, `jsonschema`,
`typer`, `numpy`, `scipy`, `networkx`, and `cryptography`. There are no hosted
services, databases, telemetry callbacks, or private infrastructure
requirements.

## CLI

Backwards-compatible single-argument packet validation:

```bash
uv run altk validate examples/admission_packet.json
```

v0.2 language-neutral validation and certification:

```bash
uv run altk validate packet examples/admission_packet.json
uv run altk validate state examples/kernel_state_empty.json
uv run altk validate transcript conformance/v0.2.0/golden_admission_transcript.json
uv run altk certify measurement examples/certificates/measurement_spec.json
uv run altk certify causal examples/certificates/causal_certificate.json
uv run altk certify transport examples/certificates/transport_certificate.json
uv run altk certify risk examples/certificates/risk_ledger.json
uv run altk certify authority examples/certificates/authority_certificate.json
uv run altk certify root-finality examples/certificates/root_finality_record.json
uv run altk certify cara examples/certificates/cara_claim.json
uv run altk certify reproduction examples/certificates/reproduction_record.json
uv run altk conformance --fixtures conformance
uv run altk dashboard examples/kernel_state_empty.json
uv run altk audit-public --strict
```

## Python API

```python
from alt_foundry_kernel import (
    KernelState,
    compute_signed_bounds,
    run_kernel_transition,
    validate_transport_certificate,
)

signed = compute_signed_bounds(
    {
        "value_lower_bound": 12.0,
        "cost_upper_bound": 3.0,
        "risk_upper_bound": 1.0,
        "transport_upper_bound": 1.0,
    }
)
assert signed.lower_bound == 7.0

transport = validate_transport_certificate(
    {
        "source_context": "source",
        "target_context": "target",
        "support": {"status": "covered", "overlap_min": 0.25},
        "density_ratio": {"upper_bound": 2.0},
        "drift": {"status": "stable"},
        "refresh": {"status": "valid"},
        "transport_cost": {"upper_bound": 1.0},
    }
)
assert transport.ok

result = run_kernel_transition(KernelState(), {...})
```

## Implemented Modules

| Paper-facing area | v0.2.0 implementation |
| --- | --- |
| Executable certificate packet | JSON Schema, Pydantic model, packet validation, examples |
| Signed surplus | lower/upper conservative arithmetic and missing-coordinate rejection |
| Dual ledgers | exploration, settlement, negative, resurrection, hazard, audit surfaces |
| Lifecycle kernel | candidate, admission, monitor-alarm, transport-refresh, deprecation, rollback, resurrection, bridge, kernel-update |
| Measurement | task/solver/protocol, trace sufficiency, sample design, instrumentation, evaluator firewall, contamination, selection |
| Statistical bounds | t-intervals, empirical-Bernstein lower bound, post-selection confidence adjustment |
| Causal certificates | randomized, paired, replay, off-policy, doubly robust, calibrated-proxy, proxy-only gates |
| Transport | support coverage, density-ratio bound, drift, refresh, transport cost |
| Risk | reserve, hazard, irreversible loss, raw-net solvency, noncompensable hazard |
| Authority | authority, capability, threat, guarded deployment, telemetry, runtime witness |
| Root/finality | root status, role separation, quorum, finality, rollback path, optional Ed25519 verification |
| Portfolio | dependency closure, DAG check, settlement-only capital accounting, dominance check |
| Reproduction | matrix, gauge, capacity, identification, recombination fail-closed gate |
| CARA | target validity, baseline envelope, target membership, viability, time-to-target improvement |
| Foundry conformance | deterministic transcript replay and dashboard summary |
| Public release | strict audit for DOI links, local paths, paper source, secrets, schemas, examples, conformance |

## Scientific Limits

The kernel does not convert weak evidence into capital. These claims require
external evidence and remain fail-closed unless supplied through typed
certificates:

- causal effect identification;
- mission-valid value bridges;
- proxy-to-gold calibration;
- transportability and causal invariance;
- evaluator-root soundness beyond declared root/quorum records;
- proof-of-useful-abstraction weighting;
- dynamic hazard estimation;
- reproduction-matrix identification;
- recombination tensor estimation;
- capability-basis target membership;
- ASI target realization or acceleration.

This repository provides the executable contract for those modules. It does not
replace the scientific work required to produce their evidence.

## Non-Python Implementers

A compatible non-Python implementation should:

- consume every schema in `schemas/`;
- preserve packet type, lifecycle, decision, predicate, and ledger names;
- produce the same signed-bound arithmetic;
- keep proxy-only and failed evidence out of settlement capital;
- emit the same JSON shape for validation reports, certificate reports,
  transitions, dashboards, and conformance results;
- replay `conformance/` fixtures deterministically;
- reject missing capital-relevant evidence instead of defaulting it to zero.

See `docs/language-neutral-contract.md` for the conformance levels.

## Repository Map

- `schemas/`: language-neutral JSON Schemas.
- `examples/`: packet and certificate examples.
- `conformance/`: golden deterministic transcripts.
- `src/alt_foundry_kernel/`: Python reference implementation.
- `docs/theory-map.md`: paper object to implementation map.
- `docs/schema-contract.md`: field dictionary and packet contract.
- `docs/agent-bootloader.md`: trace-to-token workflow.
- `docs/full-implementation-roadmap.md`: path beyond v0.2.0.
- `docs/theory-alignment-audit.md`: implemented, approximate, deferred, not certified.
- `docs/pre-release-audit.md`: reproducible public audit checklist.
- `docs/measurement-and-evidence.md`: measurement and evidence handoff.
- `docs/causal-transport-risk.md`: causal, transport, and risk contracts.
- `docs/root-portfolio-cara.md`: root, portfolio, reproduction, and CARA contracts.

## Verification

```bash
uv run ruff check .
uv run mypy src
uv run pytest --cov=alt_foundry_kernel
uv run pip-audit
uv run altk conformance --fixtures conformance
uv run altk audit-public --strict
```

Validate all bundled packet examples on POSIX shells:

```bash
for f in examples/*_packet.json; do uv run altk validate "$f"; done
```

On Windows PowerShell:

```powershell
Get-ChildItem examples\*_packet.json | ForEach-Object { uv run altk validate $_.FullName }
```

## Citation

Use `CITATION.cff`. If citing the theory, cite:

Takahashi, K. (2026). *Abstraction Liquidity Theory*. Zenodo.
[https://doi.org/10.5281/zenodo.20476200](https://doi.org/10.5281/zenodo.20476200)

## License

Apache License 2.0.
