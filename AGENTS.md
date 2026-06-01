# Agent Instructions

This repository implements the ALT Foundry Kernel v0.2.0 reference kernel and
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
uv run altk conformance --fixtures conformance
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
10. CARA target-validity, baseline-envelope, target-membership, viability, and
    time-to-target fields, only when target crossing is claimed.

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
