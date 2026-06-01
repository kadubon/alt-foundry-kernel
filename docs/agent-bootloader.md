# Agent Bootloader Guide

Paper DOI: [https://doi.org/10.5281/zenodo.20476200](https://doi.org/10.5281/zenodo.20476200)

This guide is the handoff surface for AI agents that clone this repository and
build toward a full ALT foundry. v0.2.0 provides the parser, schemas,
certificate checkers, predicate report, signed-bound discipline, dual ledgers,
deterministic state machine, dashboards, and replayable conformance fixtures.
Agents should extend those boundaries rather than bypass them.

## End-To-End Workflow

1. Capture traces: failed branches, verifier feedback, retrieved context,
   auxiliary-resource use, random seeds, hidden-resource measurements,
   telemetry, environment versions, toolchain versions, and trace projection.
2. Extract candidates: declare grammar, canonicalization, ablation design,
   leakage tests, dependency graph, minimal interface, verifier binding, and
   extractor search budget.
3. Create a candidate packet with `uv run altk init-example candidate`.
4. Validate early with `uv run altk validate <packet.json>`.
5. Gather settlement evidence with paired replay, randomized deployment,
   factorial deployment, off-policy evaluation, or another declared design.
6. Upgrade to admission only after adding mission, baseline, opportunity law,
   estimand, evidence, signed bounds, telemetry, transport, hazard, authority,
   capability, threat, root/quorum, finality, budget, capacity, refresh,
   rollback, deprecation, raw-net, runtime witness, and viability fields.
7. Run the kernel with
   `uv run altk decide <packet.json> --state <state.json>`.
8. Monitor active claims using monitor-alarm, transport-refresh, deprecation,
   rollback, resurrection, bridge, and kernel-update packets.
9. Run `uv run altk audit-public --strict` before publishing a fork or release.

For non-Python implementations, treat the CLI and `conformance/` fixtures as
oracles for v0.2.0 behavior. Implement the wire format, module certificate
reports, predicates, signed bounds, lifecycle transitions, dashboards, and
transcript replay described in `docs/language-neutral-contract.md`.

## Packet Repair Order

When validation fails, repair in this order:

1. JSON syntax and top-level schema.
2. Packet-type required fields.
3. Dependency closure and dependency availability.
4. Mission, baseline, opportunity law, and measurement declarations.
5. Evidence status, selection status, trace view, and sample design.
6. Signed value/cost/risk/transport bounds.
7. Runtime witness, telemetry, transport, hazard, authority, capability, threat.
8. Root/quorum, finality, budget, capacity, refresh, rollback, deprecation.
9. Raw-net solvency, noncompensable hazard, and viability.
10. CARA target-validity, baseline-envelope, target-membership, viability, and
    time-to-target fields, only when target crossing is claimed.

Never patch missing evidence with zero. Use measured evidence, a declared
worst-case charge, a narrowed scope, or a fail-closed transition.

## Packet-Type Use

- `candidate`: queue a possible abstraction token. No capital increase.
- `admission`: request settlement capital under all predicates.
- `monitor-alarm`: suspend an active or pending claim after drift, telemetry,
  hazard, or finality alarms.
- `transport-refresh`: restore only the receiver and context-law scope covered
  by new transport evidence.
- `deprecation`: write a scope-limited negative or stale certificate.
- `rollback`: restore state and charge the rollback reserve.
- `resurrection`: address a prior negative certificate with new evidence.
  Without admission-grade current evidence, it returns to candidate.
- `bridge`: record a proxy, baseline, opportunity, transport, or semantics
  bridge. v0.2.0 records this as audit evidence only.
- `kernel-update`: propose a conservative parser/kernel update through the old
  kernel boundary. v0.2.0 records this; the old kernel remains authoritative.

## Full Implementation Modules

A full ALT implementation should add modules that emit typed packet fields:

- trace-sufficiency and contamination audit;
- token grammar validator and canonicalizer;
- mission/generated/externality opportunity-law constructors;
- baseline registry and refresh bridge checker;
- proxy, calibrated-proxy, and causal estimand checkers;
- finite-sample LCB/UCB, confidence-sequence, e-value, and post-selection
  correction modules;
- telemetry collector and formation-cost ledger;
- transport support, density-ratio, drift, and causal-invariance monitors;
- hazard envelope, noncompensable-hazard gate, and dynamic risk ledger;
- authority/capability envelope and adversarial-token threat checker;
- root/quorum verifier, finality verifier, and audit replay;
- reproduction matrix and recombination tensor estimators;
- CARA target-validity, capability-basis, baseline-envelope, target-membership,
  raw-net, and time-to-target verifiers.

v0.2.0 includes reference validators for these module boundaries. They verify
declared certificates and reject missing evidence; production foundries should
connect them to real trace stores, measurement systems, causal estimators,
transport monitors, root services, and risk ledgers.

## Module Handoff Contract

Each full-implementation module should return one of three artifacts:

- a packet fragment that populates a declared field;
- a bridge certificate that narrows or refreshes an existing claim;
- a fail-closed finding that keeps the claim in exploration, suspension,
  deprecation, rollback, or candidate resurrection.

Modules should not directly mutate settlement capital. The kernel remains the
only boundary that can write a capital-changing transition.

## v0.2.0 Commands For Agents

```bash
uv run altk certify measurement examples/certificates/measurement_spec.json
uv run altk certify causal examples/certificates/causal_certificate.json
uv run altk certify transport examples/certificates/transport_certificate.json
uv run altk certify risk examples/certificates/risk_ledger.json
uv run altk certify root-finality examples/certificates/root_finality_record.json
uv run altk certify cara examples/certificates/cara_claim.json
uv run altk conformance --fixtures conformance
```

## Agent Rule

Agents may freely fork, clone, and modify the repository under Apache-2.0. New
modules should feed the kernel through executable certificate packets. A module
that cannot produce typed evidence for a predicate must leave the claim in
exploration or fail closed.
