# ALT Foundry Kernel

**ALT Foundry Kernel is an Apache-2.0, language-neutral reference kernel for
Abstraction Liquidity Theory (ALT): the claim that traces become reusable
abstraction capital only after they are converted into certified abstraction
tokens with positive signed surplus under explicit measurement, baseline,
opportunity, transport, hazard, authority, lifecycle, and finality rules.**

ALT is not a synonym for compression, novelty, benchmark transfer, trace volume,
library size, static surplus, or packaging. Those properties may be useful
signals, but the theory treats them as non-sufficient. Liquidity is an
operational settlement condition: a trace-derived object must be represented as
an abstraction token, bound to an executable certificate packet, checked against
declared mission and opportunity laws, charged for formation and lifecycle
costs, constrained by transport and hazard evidence, authorized by capability
and threat gates, finalized by roots/quorums, and admitted to a settlement
ledger only when conservative lower-bound signed surplus is positive. Missing
capital-relevant evidence is undefined, not zero.

Source paper:
Takahashi, K. (2026). *Abstraction Liquidity Theory*. Zenodo.
[https://doi.org/10.5281/zenodo.20476200](https://doi.org/10.5281/zenodo.20476200)

Accurate search terms for this project: Abstraction Liquidity Theory, ALT,
abstraction token, executable certificate packet, agent-operable foundry, AI
agent certification kernel, dual-ledger settlement, safe certified abstraction
capital, signed surplus, non-reduction guards, evaluator hierarchy, proof of
useful abstraction, PoUA finality, certificate algebra, sequential evidence,
transport robustness, CARA target-crossing guard, language-neutral JSON Schema,
and conformance fixtures.

## What v0.4.0 Is

`v0.4.0` is the first v1.0.0-equivalent reference surface: a packet kernel,
certificate validators, raw-data estimator helpers, language-neutral schemas,
examples, conformance fixtures, and public-release audit in one repository. It
is still scientifically bounded: estimators compute generic certificates from
declared data, but the kernel does not fabricate causal identification,
transportability, root authority, recombination evidence, or ASI target
realization.

The public contract is language-neutral:

- `schemas/` defines wire formats for packets, kernel state, ledgers,
  dashboards, module certificates, estimator artifacts, robust transport,
  finality/PoUA, certificate composition, extended CARA, and conformance
  results.
- `examples/` gives valid packet, certificate, and estimator-input examples.
- `conformance/` gives deterministic golden transcripts and negative fixtures
  for non-Python implementations.
- `src/alt_foundry_kernel/` is the Python reference implementation.
- `docs/` maps theory objects and non-reduction results to modules, validators,
  schemas, and known limits.

## Start Here For Agents

1. Read the paper DOI above and [docs/theory-map.md](docs/theory-map.md).
2. Read [docs/theory-to-module-matrix.md](docs/theory-to-module-matrix.md) to
   see what is implemented, validator-only, schema-only, deferred, or not
   certified.
3. Read [docs/language-neutral-contract.md](docs/language-neutral-contract.md)
   before implementing ALT in TypeScript, Rust, Go, JVM languages, or another
   runtime.
4. Inspect `schemas/packet.schema.json`,
   `schemas/foundry-transcript.schema.json`, and the v0.4.0 certificate and
   estimator schemas.
5. Validate a packet:

   ```bash
   uv run altk validate examples/admission_packet.json
   ```

6. Run a deterministic transition:

   ```bash
   uv run altk decide examples/admission_packet.json --state examples/kernel_state_empty.json
   ```

7. Certify module artifacts:

   ```bash
   uv run altk certify non-reduction examples/certificates/non_reduction_audit.json
   uv run altk certify mechanism examples/certificates/mechanism_certificate.json
   uv run altk certify transport-ext examples/certificates/transport_robustness.json
   uv run altk certify certificate-algebra examples/certificates/certificate_composition.json
   uv run altk certify cara-ext examples/certificates/cara_process.json
   ```

8. Generate estimator-backed certificate reports from declared data:

   ```bash
   uv run altk estimate finite-sample examples/estimators/finite_sample.json
   uv run altk estimate causal-effect examples/estimators/causal_effect.json
   uv run altk estimate transport-diagnostics examples/estimators/transport_diagnostics.json
   ```

9. Replay the portable contract:

   ```bash
   uv run altk conformance --fixtures conformance --level L5
   ```

10. Before publication or redistribution:

   ```bash
   uv run altk audit-public --strict
   ```

Packet repair order is deliberate: schema, packet-type fields, dependency
closure, mission/baseline/opportunity, measurement/evidence, signed bounds,
runtime witness, telemetry, transport, hazard, authority, capability, threat,
root/quorum/finality, budget, capacity, refresh, rollback, deprecation, raw-net
solvency, noncompensable hazard, viability, and then CARA target fields only
when target crossing is claimed.

## Install

```bash
uv sync --dev
```

Runtime dependencies are local libraries only: `pydantic`, `jsonschema`,
`typer`, `numpy`, `scipy`, `networkx`, and `cryptography`. There are no hosted
services, databases, telemetry callbacks, or private infrastructure
requirements. Heavier estimator ecosystem packages are optional under the
`estimators` extra; the reference estimators in this release run with the core
dependencies.

## CLI Surface

Backwards-compatible packet validation:

```bash
uv run altk validate examples/admission_packet.json
```

Language-neutral validation, certification, replay, dashboard, and audit:

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
uv run altk certify reproduction examples/certificates/reproduction_record.json
uv run altk certify non-reduction examples/certificates/non_reduction_audit.json
uv run altk certify mechanism examples/certificates/mechanism_certificate.json
uv run altk certify evaluator examples/certificates/evaluator_hierarchy.json
uv run altk certify finality examples/certificates/finality_poua_ledger.json
uv run altk certify sequential examples/certificates/sequential_decision.json
uv run altk certify transport-ext examples/certificates/transport_robustness.json
uv run altk certify certificate-algebra examples/certificates/certificate_composition.json
uv run altk certify portfolio-ext examples/certificates/portfolio_constraints.json
uv run altk certify foundry-control examples/certificates/foundry_control_state.json
uv run altk certify cara-ext examples/certificates/cara_process.json
uv run altk estimate finite-sample examples/estimators/finite_sample.json
uv run altk estimate proxy-bridge examples/estimators/proxy_bridge.json
uv run altk estimate causal-effect examples/estimators/causal_effect.json
uv run altk estimate transport-diagnostics examples/estimators/transport_diagnostics.json
uv run altk estimate guard-risk examples/estimators/guard_risk.json
uv run altk estimate federated-pooling examples/estimators/federated_pooling.json
uv run altk estimate portfolio-selection examples/estimators/portfolio_selection.json
uv run altk estimate foundry-phase examples/estimators/foundry_phase.json
uv run altk estimate reproduction-phase examples/estimators/reproduction_phase.json
uv run altk estimate cara-time-to-target examples/estimators/cara_time_to_target.json
uv run altk estimate alpha-budget examples/estimators/alpha_budget.json
uv run altk conformance --fixtures conformance --level L5
uv run altk dashboard examples/kernel_state_empty.json
uv run altk audit-public --strict
```

## Python API

```python
from alt_foundry_kernel import (
    KernelState,
    compute_signed_bounds,
    run_kernel_transition,
    validate_certificate_composition,
    validate_non_reduction_audit,
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

non_reduction = validate_non_reduction_audit(
    {
        "liquidity_claim": {"status": "explicit"},
        "measurement": {"status": "valid"},
        "signed_surplus": {"status": "valid"},
        "transport": {"status": "valid"},
        "hazard": {"status": "bounded"},
        "authority": {"status": "valid"},
        "lifecycle": {"status": "valid"},
        "finality": {"status": "finalized"},
        "capital_effect": {"claims_settlement": False},
        "shortcuts": [{"name": "compression", "used_as_certification": False}],
    }
)
assert non_reduction.ok

result = run_kernel_transition(KernelState(), {...})
```

## Implemented Modules

| Paper-facing area | v0.4.0 implementation |
| --- | --- |
| Executable certificate packet | JSON Schema, Pydantic model, packet validation, examples |
| Signed surplus | lower/upper conservative arithmetic and missing-coordinate rejection |
| Dual ledgers | exploration, settlement, negative, resurrection, hazard, audit surfaces |
| Lifecycle kernel | candidate, admission, monitor-alarm, transport-refresh, deprecation, rollback, resurrection, bridge, kernel-update |
| Measurement | task/solver/protocol, trace sufficiency, sample design, instrumentation, evaluator firewall, contamination, selection |
| Statistical bounds | t-intervals, empirical-Bernstein lower bound, post-selection confidence adjustment |
| Causal certificates | randomized, paired, replay, off-policy, doubly robust, calibrated-proxy, proxy-only gates |
| Transport | support coverage, density-ratio bound, drift, refresh, transport cost |
| Transport robustness | robust estimate, Wasserstein radius, causal invariance, observable stopping |
| Non-reduction | rejects compression, novelty, benchmark score, trace volume, static surplus, and packaging as substitutes for liquidity |
| Mechanism | placebo control, mechanism ablation, actor-neutrality, evaluator independence, self-certification rejection |
| Evaluator hierarchy | stratified acyclic graph, root rotation, self-certification-cycle rejection |
| Finality and PoUA | federated finality, weighted quorum, PoUA-not-authority guard, finality-safe settlement |
| Sequential evidence | adaptive horizon, settle-or-sample, EVSI-style gate, finite evidence budget |
| Certificate algebra | common-estimand composition, naive-composition rejection, negative-scope propagation |
| Portfolio constraints | conflict graph, breadth partition, cherry-picking guard, behavioral cover, submodular interface |
| Foundry control | bottleneck/min-cut, shadow price, absorption capacity, conservative exploration, phase control |
| Risk | reserve, hazard, irreversible loss, raw-net solvency, noncompensable hazard |
| Authority | authority, capability, threat, guarded deployment, telemetry, runtime witness |
| Root/finality | root status, role separation, quorum, finality, rollback path, optional Ed25519 verification |
| Reproduction | matrix, gauge, capacity, identification, recombination fail-closed gate |
| CARA | target validity, baseline envelope, target membership, viability, time-to-target improvement |
| Extended CARA | target-valid process, non-tradable target constraints, viability-controlled acceleration preconditions |
| Estimator helpers | finite-sample, proxy bridge, causal modes, transport diagnostics, guard risk, federated pooling, portfolio selection, foundry phase, reproduction phase, CARA time-to-target, alpha budget |
| Foundry conformance | deterministic transcript replay, negative certificate fixtures, conformance levels L0-L5 |
| Public release | strict audit for DOI links, local paths, paper source, secrets, schemas, examples, conformance |

## Scientific Limits

This repository verifies declared artifacts. It does not turn weak evidence into
capital. The following remain outside automatic certification unless supplied as
typed evidence-bearing certificates:

- causal effect identification and off-policy validity;
- mission-valid value bridges and proxy-to-gold calibration;
- transportability, robust transport, and causal invariance;
- evaluator-root soundness beyond declared hierarchy, quorum, and finality
  records;
- proof-of-useful-abstraction weighting as epistemic authority;
- dynamic hazard estimation and irreversible-loss modeling;
- reproduction-matrix identification and recombination tensor estimation;
- portfolio optimality beyond declared conflict and breadth constraints;
- capability-basis target membership;
- ASI target realization or viability-controlled acceleration.

## Non-Python Implementers

A compatible implementation in another language should:

- consume every schema in `schemas/`;
- preserve packet type, lifecycle, decision, predicate, and ledger names;
- reproduce signed-bound arithmetic and raw-net capital gates;
- keep proxy-only and failed evidence out of settlement capital;
- reject missing capital-relevant evidence instead of defaulting it to zero;
- emit compatible validation reports, certificate reports, transitions,
  dashboards, conformance results, and public-audit results;
- replay `conformance/` fixtures deterministically at the claimed level;
- implement negative fixtures as hard failures, not warnings.
- match estimator report shape and fail-closed behavior for `examples/estimators/`
  if claiming v0.4.0 L5 conformance.

See [docs/language-neutral-contract.md](docs/language-neutral-contract.md) for
L0-L5 conformance levels and report shapes.

## Repository Map

- `schemas/`: language-neutral JSON Schemas.
- `examples/`: packet and certificate examples.
- `examples/estimators/`: declared estimator inputs for certificate builders.
- `conformance/`: golden deterministic transcripts and negative fixtures.
- `src/alt_foundry_kernel/`: Python reference implementation.
- [docs/theory-map.md](docs/theory-map.md): paper object to implementation map.
- [docs/theory-to-module-matrix.md](docs/theory-to-module-matrix.md): theorem/proposition-class coverage.
- [docs/schema-contract.md](docs/schema-contract.md): field dictionary and packet contract.
- [docs/language-neutral-contract.md](docs/language-neutral-contract.md): non-Python conformance.
- [docs/estimator-contract.md](docs/estimator-contract.md): estimator input/output contracts.
- [docs/non-reduction-and-mechanism.md](docs/non-reduction-and-mechanism.md): non-reduction and mechanism guards.
- [docs/evaluator-finality-and-poua.md](docs/evaluator-finality-and-poua.md): evaluator hierarchy, roots, quorum, finality, PoUA.
- [docs/sequential-transport-and-control.md](docs/sequential-transport-and-control.md): sequential evidence, robust transport, foundry control.
- [docs/agent-bootloader.md](docs/agent-bootloader.md): trace-to-token workflow.
- [docs/full-implementation-roadmap.md](docs/full-implementation-roadmap.md): path beyond this release.
- [docs/theory-alignment-audit.md](docs/theory-alignment-audit.md): implemented, approximate, deferred, not certified.
- [docs/pre-release-audit.md](docs/pre-release-audit.md): reproducible public audit checklist.

## Verification

```bash
uv run ruff check .
uv run mypy src
uv run pytest --cov=alt_foundry_kernel
uv run pip-audit
uv run altk conformance --fixtures conformance --level L5
uv run altk audit-public --strict
```

Validate bundled packet examples on POSIX shells:

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
