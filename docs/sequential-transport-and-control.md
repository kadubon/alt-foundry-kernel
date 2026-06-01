# Sequential Evidence, Robust Transport, And Foundry Control

Paper DOI: [https://doi.org/10.5281/zenodo.20476200](https://doi.org/10.5281/zenodo.20476200)

v0.4.0 adds deterministic validators for three paper-facing control surfaces:
sequential evidence decisions, robust transport boundaries, and foundry phase
control. They are certificate checkers, not data-generating estimators.

## Sequential Evidence

The `sequential` module checks a settle-or-sample decision:

- finite evidence budget is declared;
- remaining horizon is non-negative;
- `settle` requires positive surplus lower bound;
- `sample` requires EVSI lower bound greater than sampling cost and affordable
  within the finite budget;
- `defer` is valid only when the horizon is exhausted.

Schema: `schemas/sequential-decision.schema.json`.

Example:

```bash
uv run altk certify sequential examples/certificates/sequential_decision.json
```

## Robust Transport

The `transport_ext` module checks:

- support coverage;
- valid robust estimated transport record;
- Wasserstein radius upper bound within the accepted threshold;
- causal-invariance evidence or an explicit `not_required` status;
- observable stopping rule.

Schema: `schemas/transport-robustness.schema.json`.

Example:

```bash
uv run altk certify transport-ext examples/certificates/transport_robustness.json
```

The negative fixture `conformance/v0.3.0/transport_fail_closed.json` fixes the
behavior when the robust transport radius exceeds the declared threshold.

## Foundry Control

The `foundry_control` module checks:

- bottleneck/min-cut capacity covers demand;
- shadow-price record is valid or explicitly not required;
- absorption capacity covers demand;
- exploration capital at risk stays inside the risk budget;
- phase-control and conservative-exploration records are valid.

Schema: `schemas/foundry-control-state.schema.json`.

Example:

```bash
uv run altk certify foundry-control examples/certificates/foundry_control_state.json
```

## Certificate Algebra

The `certificate_algebra` module prevents naive composition. Positive
composition requires a common-estimand proof. Negative-certificate propagation
requires scope-safe propagation evidence. The fixture
`conformance/v0.3.0/invalid_naive_composition.json` fixes rejection of
unadjusted certificate addition.

```bash
uv run altk certify certificate-algebra examples/certificates/certificate_composition.json
```
