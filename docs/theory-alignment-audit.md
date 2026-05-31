# Theory Alignment Audit

Paper DOI: [https://doi.org/10.5281/zenodo.20476200](https://doi.org/10.5281/zenodo.20476200)

This audit records how the repository aligns with Abstraction Liquidity Theory
and where it intentionally stops. It is a public engineering audit, not a
substitute for the paper.

## Implemented

- Machine-readable packet contract:
  `id`, `type`, `token_id`, `version`, `state`, `scope_hash`, `declaration`,
  `evidence`, `bounds`, `validity`, `monitor`, `fallback`, `signatures`.
- Nine packet types: candidate, admission, transport-refresh, monitor-alarm,
  deprecation, rollback, resurrection, bridge, and kernel-update.
- Lifecycle states: candidate, exploration, pending settlement, active,
  suspended, deprecated, resurrected.
- Six typed packet layers: declaration, evidence, bounds, validity, monitor,
  fallback.
- Conservative signed lower and upper bound calculation.
- Dual-ledger separation between exploration evidence and settlement capital.
- Kernel state tuple coverage for admitted set, candidate queue, ledgers,
  hazard, monitor/drift, authority/capability, negative/resurrection,
  root/finality, budget, and audit state.
- Predicate-level admission report with paper-aligned predicate names,
  including net lower bound, target validity, baseline envelope, quorum, runtime
  witness, raw-net solvency, noncompensable hazard, and viability.
- Conditional CARA required fields for target-crossing claims.
- Fail-closed required-field validation for every packet type.
- Lifecycle preconditions for monitor-alarm, transport-refresh, deprecation,
  rollback, and resurrection.
- Audit-only bridge and kernel-update packet handling in v1.
- Public audit CLI for DOI links, examples, schemas, local-path leakage,
  paper-source leakage, env files, secret-like assignments, and placeholder
  publishing URLs.
- Language-neutral conformance documentation for non-Python implementations.

## Approximated

- Predicate checks are status and field gates. They are not independent
  scientific verifiers.
- Root and quorum validity are represented as status records. No cryptographic
  or Byzantine quorum verification is performed.
- Finality is represented as `finalized` or explicit exemption. No consensus or
  PoUA implementation is present.
- Runtime capital witness is represented as a declared status field.
- Transport, hazard, mission, budget, capacity, refresh, rollback, deprecation,
  and viability checks are parsed and gated, not statistically or formally
  certified.
- Resurrection can add capital only if the packet supplies admission-grade
  current evidence; otherwise it returns to candidate. The v1 checker is a
  conservative field/status approximation.

## Deferred

- Trace sufficiency, leakage, contamination, and hidden-resource audits.
- Mission/generated/externality opportunity-law construction.
- Baseline refresh bridges and direct remeasurement.
- Proxy calibration and common-estimand bridges.
- Causal token-effect identification and off-policy evaluation.
- Finite-sample lower and upper confidence bounds, confidence sequences, and
  post-selection correction.
- Telemetry collection and formation-cost measurement.
- Transport support, density-ratio, drift, and causal-invariance evidence.
- Dynamic risk, irreversible-risk, hazard, and ruin ledgers.
- Root/quorum cryptographic verification, finality, and PoUA weighting.
- Portfolio optimization, equivalence quotienting, and dominance checks.
- Reproduction matrices, recombination tensors, phase control, and capacity
  oracles.
- Full target-valid ALT-CARA certification and ASI target crossing.

## Explicitly Not Certified

A packet is not certified because it validates as JSON. Validation means the
kernel can bind fields and apply fail-closed transition rules. Scientific
validity requires evidence-producing modules that populate those fields under
declared measurement protocols.

The v1 bootloader therefore does not certify causal value, transportability,
root independence, finality, recombination, or ASI acceleration. It provides the
agent-operable boundary those modules must write into.

## Current Public-Release Audit Expectations

Before publication, run:

```bash
uv run ruff check .
uv run mypy src
uv run pytest
uv run pip-audit
uv run altk audit-public --strict
```

The audit must show no local paths, no downloaded paper source, no `.env*`
files, no fake repository URLs, DOI links in public docs, valid schemas, and
valid examples. Local build caches and virtual environments are ignored for
content scanning but reported as cleanup warnings.
