# Estimator Contract

Paper DOI: [https://doi.org/10.5281/zenodo.20476200](https://doi.org/10.5281/zenodo.20476200)

v0.4.0 adds deterministic estimator helpers. They are not a substitute for the
paper's scientific assumptions. Each helper accepts declared JSON input and
emits a `CertificateReport` with metrics and a JSON-serializable certificate
artifact. If a required assumption, overlap condition, support condition,
calibration bridge, evidence budget, or target-validity field is missing, the
report fails closed.

## CLI

```bash
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
```

## Estimator Kinds

| Kind | Output artifact | Fail-closed condition |
| --- | --- | --- |
| `finite-sample` | `confidence-accounting` | empty sample, invalid range, invalid confidence |
| `proxy-bridge` | `proxy-bridge-record` | invalid calibration or nonpositive bridged lower bound |
| `causal-effect` | causal-certificate-shaped artifact | missing identification, unsupported mode, no overlap |
| `transport-diagnostics` | `transport-diagnostics` | uncovered target support, radius above threshold, excessive dimension |
| `guard-risk` | `guard-risk-record` | invalid alpha, too little calibration data, risk above budget |
| `federated-pooling` | `federated-pooling` | invalid record, invalid correlation, nonpositive pooled lower bound |
| `portfolio-selection` | `submodular-selection-result` | malformed portfolio or budget |
| `foundry-phase` | `phase-control-record` | missing source/sink or min-cut below demand |
| `reproduction-phase` | `recombination-estimate` | invalid matrix, capacity mismatch, unidentified recombination |
| `cara-time-to-target` | CARA-process-shaped artifact | invalid target, raw-net insolvency, no time-to-target margin |
| `alpha-budget` | `evidence-budget` | exhausted finite evidence budget |

## Non-Python Rule

A non-Python implementation may use different numerical libraries, but L5
conformance requires the same input/output shape and the same fail-closed
decision on the bundled examples and conformance fixtures. Numerical values may
be represented in the host language's native floating type, but report keys,
predicate names, and artifact fields must remain stable.

## Scientific Boundary

Estimator success means the declared data passed the reference arithmetic. It
does not certify unobserved assumptions. Causal identification, transportability,
root authority, recombination structure, and ALT-CARA target validity must still
be declared and independently justified before a packet can enter settlement.

## Additive v0.5.0 profile

The opt-in receiver-qualified model workbench is documented in
[collective-reuse.md](collective-reuse.md), with version-bound adapters in
[reuse-interchange.md](reuse-interchange.md). Its closed schemas and exact arithmetic
do not replace these legacy certificate interfaces or establish settlement authority.
See [release qualification](release-v0.5.0.md) for the GitHub-only artifact gates.
