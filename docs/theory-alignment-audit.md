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
- Audit-only bridge and kernel-update packet handling in v0.3.0.
- Public audit CLI for DOI links, examples, schemas, local-path leakage,
  paper-source leakage, env files, secret-like assignments, and placeholder
  publishing URLs.
- Language-neutral conformance documentation and golden transcript replay for
  non-Python implementations.
- Module-level certificate validators for measurement, statistics, causal
  evidence, transport, risk, authority, root/finality, portfolio, reproduction,
  and CARA target claims.
- JSON Schemas for module certificates, foundry transcripts, and conformance
  results.
- Non-reduction validators for compression, novelty, benchmark score, transfer
  score, trace volume, library size, static surplus, evidence volume, packaging,
  and generality shortcuts.
- Mechanism validators for placebo-controlled reuse, mechanism ablation,
  actor-neutrality, evaluator independence, and self-certification rejection.
- Evaluator hierarchy validator for stratified acyclic graphs and root rotation.
- Finality/PoUA validator for federated finality, weighted quorum, PoUA
  non-authority, and finality-safe settlement.
- Sequential evidence validator for adaptive horizon, settle-or-sample, EVSI
  lower-bound comparison, and finite evidence budget.
- Robust transport validator for support coverage, Wasserstein-radius bounds,
  causal-invariance record, and observable stopping.
- Certificate algebra validator for common-estimand composition, naive
  composition rejection, and negative-certificate scope propagation.
- Extended portfolio, foundry-control, and CARA process validators.
- v0.3.0 conformance fixtures for proxy-only routing, deprecation/resurrection,
  self-certification rejection, naive-composition rejection, transport
  fail-closed behavior, evaluator-cycle rejection, and CARA target failure.

## Approximated

- Packet-level predicate checks are status and field gates. Module validators
  verify certificate structure, but they are not a substitute for independent
  scientific instruments.
- Root and quorum validity are represented as status and quorum records.
  Optional Ed25519 signature verification exists, but Byzantine quorum
  governance is not implemented.
- Finality is represented as `finalized` or explicit exemption at packet level
  and as a declared finality/PoUA certificate at module level. No consensus
  protocol is implemented.
- Runtime capital witness is represented as a declared status field.
- Transport, hazard, mission, budget, capacity, refresh, rollback,
  deprecation, and viability checks are parsed, structurally validated, and
  gated; full domain certification still depends on supplied evidence.
- Resurrection can add capital only if the packet supplies admission-grade
  current evidence; otherwise it returns to candidate. The v0.3.0 checker is a
  conservative field/status approximation.
- Non-reduction, mechanism, evaluator, finality, sequential, robust transport,
  certificate-algebra, portfolio, foundry-control, and extended CARA validators
  check declared certificate records. They do not run the experiments,
  governance systems, transport estimators, or optimization procedures that
  would produce those records.

## Deferred

- Production-grade trace sufficiency, leakage, contamination, and
  hidden-resource audits beyond the module contract.
- Mission/generated/externality opportunity-law construction.
- Baseline refresh bridges and direct remeasurement.
- Proxy calibration and common-estimand bridges.
- Causal token-effect identification and off-policy evaluation.
- Finite-sample lower and upper confidence bounds, confidence sequences, and
  post-selection correction.
- Telemetry collection and formation-cost measurement.
- Causal-invariance evidence beyond declared transport certificates.
- Dynamic risk, ruin ledgers, and calibrated hazard estimation.
- Byzantine root/quorum governance, finality consensus, and PoUA weighting.
- Portfolio optimization, behavioral metric-entropy estimation, and
  equivalence quotienting beyond the provided closure/dominance/conflict
  utilities.
- Sequential experimental design and EVSI estimation beyond declared fields.
- Robust transport estimation, Wasserstein-ball construction, and causal
  invariance discovery beyond declared certificates.
- Certificate-algebra proof search beyond deterministic common-estimand and
  negative-scope checks.
- Recombination tensor identification, phase control, and production capacity
  oracles.
- Full target-valid ALT-CARA certification and ASI target crossing beyond the
  structural target-crossing checker.

## Explicitly Not Certified

A packet is not certified because it validates as JSON. Validation means the
kernel can bind fields and apply fail-closed transition rules. Scientific
validity requires evidence-producing modules that populate those fields under
declared measurement protocols.

The v0.3.0 kernel therefore does not certify causal value, transportability,
root independence, finality, recombination, portfolio optimality, or ASI
acceleration by itself. It provides the agent-operable boundary those modules
must write into.

## Current Public-Release Audit Expectations

Before publication, run:

```bash
uv run ruff check .
uv run mypy src
uv run pytest --cov=alt_foundry_kernel
uv run pip-audit
uv run altk conformance --fixtures conformance --level L5
uv run altk audit-public --strict
```

The audit must show no local paths, no downloaded paper source, no `.env*`
files, no fake repository URLs, DOI links in public docs, valid schemas, and
valid packet/certificate examples and conformance fixtures. Local build caches
and virtual environments are ignored for content scanning but reported as
cleanup warnings.
