# Agent Instructions

This repository implements the ALT Foundry Kernel v0.4.0 reference kernel and
language-neutral contract. Preserve the paper-linked contract: packets and
certificates are executable records, not informal claims. Theory citation:
https://doi.org/10.5281/zenodo.20476200

## Operating Rules

- Keep packet fields explicit. Do not invent evidence or replace missing cost
  coordinates with zero.
- Preserve fail-closed behavior. Missing capital-relevant fields must reject,
  defer, suspend, or route to exploration.
- Keep proxy-only evidence out of the settlement ledger.
- Keep schemas, examples, conformance fixtures, and reports language-neutral;
  keep Python code modular and readable.
- Do not add local paths, credentials, raw private traces, or downloaded paper
  source files.
- Do not run git operations unless explicitly asked.

## Useful Commands

```bash
uv sync --dev
uv run altk validate examples/admission_packet.json
uv run altk validate transcript conformance/v0.2.0/golden_admission_transcript.json
uv run altk decide examples/admission_packet.json --state examples/kernel_state_empty.json
uv run altk certify measurement examples/certificates/measurement_spec.json
uv run altk certify causal examples/certificates/causal_certificate.json
uv run altk certify transport examples/certificates/transport_certificate.json
uv run altk certify risk examples/certificates/risk_ledger.json
uv run altk certify authority examples/certificates/authority_certificate.json
uv run altk certify root-finality examples/certificates/root_finality_record.json
uv run altk certify cara examples/certificates/cara_claim.json
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
uv run altk estimate causal-effect examples/estimators/causal_effect.json
uv run altk estimate transport-diagnostics examples/estimators/transport_diagnostics.json
uv run altk conformance --fixtures conformance --level L5
uv run altk audit-public --strict
uv run ruff check .
uv run mypy src
uv run pytest --cov=alt_foundry_kernel
```

## Repair Order

1. JSON/schema errors.
2. packet-type required fields.
3. dependency closure and dependency availability.
4. mission, baseline, opportunity law, and measurement declarations.
5. evidence status, selection status, trace view, and sample design.
6. signed value/cost/risk/transport bounds.
7. runtime witness, telemetry, transport, hazard, authority, capability, threat.
8. root/quorum, finality, budget, capacity, refresh, rollback, deprecation.
9. raw-net solvency, noncompensable hazard, and viability.
10. non-reduction shortcut guards, mechanism ablation/placebo, evaluator
    hierarchy, finality/PoUA, sequential evidence, robust transport, certificate
    algebra, portfolio conflicts, and foundry-control capacity.
11. CARA target-validity, baseline-envelope, target-membership, viability, and
    time-to-target fields, only when target crossing is claimed.
12. Estimator output artifacts. Estimators may compute generic certificate
    reports from declared data, but they must fail closed when assumptions,
    overlap, support, calibration, identification, budget, or target evidence is
    missing.

Missing evidence is undefined, not zero. Use measured evidence, a declared
worst-case charge, a narrowed claim, exploration-only status, or rejection.

## Module Handoff

- Measurement modules produce task/solver/protocol, trace sufficiency, sample,
  instrumentation, selection, firewall, and contamination certificates.
- Causal modules produce baseline, identification, effect-bound, and evidence
  mode certificates; proxy-only certificates remain exploration evidence.
- Transport modules produce support, density-ratio, drift, refresh, and
  transport-cost certificates.
- Risk modules produce reserve, hazard, irreversible-loss, raw-net solvency, and
  noncompensable-hazard certificates.
- Root/finality modules produce root, role separation, quorum, finality,
  rollback, and optional signature records.
- Reproduction and CARA modules must fail closed unless their identification,
  target-validity, baseline-envelope, membership, viability, and time-to-target
  records are explicit.
- Non-reduction, mechanism, evaluator, finality/PoUA, sequential, robust
  transport, certificate-algebra, portfolio, and foundry-control modules verify
  declared certificate records. Do not treat them as estimators.
- Estimator helpers produce certificate-shaped reports from explicit JSON
  inputs. They are deterministic builders, not scientific authority. A failed
  estimator report must not be patched into a settlement packet.

## Automatic Implementation Order

1. Read the DOI, `README.md`, `docs/theory-map.md`,
   `docs/schema-contract.md`, `docs/estimator-contract.md`, and
   `docs/language-neutral-contract.md`.
2. Generate or validate estimator inputs under `examples/estimators/`.
3. Convert successful estimator reports into certificate records only when all
   assumptions are explicit.
4. Assemble packet fields from certificates.
5. Run `altk validate`, `altk decide`, `altk conformance --level L5`, and
   `altk audit-public --strict`.
