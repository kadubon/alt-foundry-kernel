# Causal, Transport, And Risk Certificates

Paper DOI: [https://doi.org/10.5281/zenodo.20476200](https://doi.org/10.5281/zenodo.20476200)

v0.4.0 provides structural validators for the paper's counterfactual value,
transport, and hazard accounting surfaces. These validators check executable
certificate records. They do not create identification assumptions or evidence.

## Causal Certificate

`causal-certificate.schema.json` and `validate_causal_certificate` require:

- estimand type;
- resource-matched baseline comparator;
- identification status;
- effect lower bound and unit;
- evidence mode.

Supported evidence modes are `randomized`, `paired`, `replay`, `off_policy`,
and `doubly_robust`. Each mode has required evidence fields. Calibrated proxy
claims require a valid calibration bridge. Proxy-only claims are accepted as
exploration evidence but are not settlement-grade.

## Transport Certificate

`transport-certificate.schema.json` and `validate_transport_certificate`
require source and target contexts, support coverage, positive overlap,
finite density-ratio upper bound, drift status, refresh status, and transport
cost upper bound.

Transport claims fail closed when support is uncovered, density ratio is
unbounded, drift is stale, refresh is missing, or transport cost is undefined.

`transport-robustness.schema.json` and `validate_transport_robustness` add the
v0.4.0 robust transport layer: support coverage, robust estimated transport,
Wasserstein-radius thresholding, causal-invariance record, and observable
stopping. This validator checks supplied robustness evidence; it does not learn
transportability from raw samples.

## Risk Ledger

`risk-ledger.schema.json` and `validate_risk_certificate` require certified
capital lower bound, reserve upper bound, hazard upper bound,
noncompensable-hazard clearance, and irreversible-loss upper bound.

The raw-net lower bound is:

```text
capital_lower_bound - reserve_upper_bound - hazard_upper_bound - irreversible_loss_upper_bound
```

Positive value cannot compensate for uncleared noncompensable hazards. Such
claims must be rejected, suspended, deprecated, or kept out of settlement.
