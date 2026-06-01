# Schema Contract

Paper DOI: [https://doi.org/10.5281/zenodo.20476200](https://doi.org/10.5281/zenodo.20476200)

The public schema is the language-neutral contract for executable ALT
certificate packets. It is normative only up to semantic equivalence: another
language may use another parser or DSL, but it must expose the same typed
information and fail-closed semantics to the kernel.

For implementation conformance outside Python, see
`docs/language-neutral-contract.md`.

v0.2.0 separates the public contract into packet schemas and module-level
certificate schemas. Packets remain the kernel input. Certificate schemas are
the portable records emitted by measurement, causal, transport, risk,
root/finality, reproduction, and CARA modules before their results are copied
into packet `declaration`, `evidence`, `bounds`, and `validity` fields.

## Top-Level Packet

```text
Packet := {id, type, token_id, version, state, scope_hash,
           declaration, evidence, bounds, validity,
           monitor, fallback, signatures}
```

Supported packet types:

`candidate`, `admission`, `transport-refresh`, `monitor-alarm`, `deprecation`,
`rollback`, `resurrection`, `bridge`, `kernel-update`.

Lifecycle states:

`candidate`, `exploration`, `pending_settlement`, `active`, `suspended`,
`deprecated`, `resurrected`.

## Paper Field Groups

| Paper group | JSON location | Required meaning |
| --- | --- | --- |
| identity and scope | top-level, `declaration.lineage`, `declaration.scope` | stable token and packet handle, version, scope hash, receiver class |
| dependencies | `declaration.dependencies` | typed object closure and availability |
| authority and capability | `declaration.authority`, `declaration.capability` | allowed action and deployment envelope |
| baseline and opportunity law | `declaration.baseline`, `declaration.opportunity_law` | current counterfactual comparison and finite evaluation measure |
| utility estimand | `declaration.estimand` | proxy-only, calibrated-proxy, or causal claim |
| evidence and uncertainty | `evidence` | trace view, split, design, sample, selection, contamination, uncertainty method |
| telemetry | `validity.telemetry` | observed telemetry or worst-case charge |
| signed bounds | `bounds` | value, cost, risk, transport, reserve, raw-net coordinates |
| transport and hazard | `validity.transport`, `validity.hazard` | scope coverage and noncompensable-hazard clearance |
| root and finality | `validity.root`, `validity.finality` | role-separated root/quorum and finalized or exempt status |
| lifecycle control | `monitor`, `fallback`, `validity.refresh`, `validity.rollback`, `validity.deprecation` | executable monitor and fail-closed action |
| CARA target fields | `declaration.cara` | target validity, capability basis, baseline envelope, membership, viability, time-to-target |

## Packet-Type Requirements

Python validation applies semantic requirements on top of JSON Schema:

- `candidate`: lineage, dependency closure, scope, grammar, baseline, mission.
- `admission`: candidate fields plus estimand, mission, baseline,
  opportunity-law, evidence, selection, signed bounds, telemetry, transport,
  hazard, authority, capability, threat, root, finality, budget, capacity,
  refresh, rollback, deprecation, raw-net solvency, runtime witness,
  noncompensable hazard, and viability.
- `monitor-alarm`: claim id, alarm statistic, fallback action.
- `transport-refresh`: claim id, old law, new law, bridge, deadline, fallback,
  and transport status.
- `deprecation`: scope, value upper bound, cost lower bound, hazard status, and
  resurrection rule.
- `rollback`: affected claims, restore point, reserve charge, and audit record.
- `resurrection`: old negative certificate, overwriting evidence, new signed
  bounds, raw-net lower bound, hazard, and finality. Capital addition also
  requires admission-grade current evidence at transition time.
- `bridge`: claim id, bridge object, and root status. v0.2.0 records it as
  audit evidence only.
- `kernel-update`: old semantics, new semantics, bridge, independent root, and
  rollback path. v0.2.0 records it; the current kernel remains authoritative.

## Conditional CARA Fields

When an admission packet sets `declaration.cara.claims_target_crossing` to
`true`, the packet must include:

- `asi_target_id`
- `capability_basis_id`
- `target_validity_certificate`
- `baseline_upper_envelope`
- `target_membership_proof`
- `viability_witness`
- `time_to_target_claim`

`TargetValidityOK` and `BaselineEnvelopeOK` are `null` unless target crossing or
time-to-target comparison is claimed. When such a claim is made, missing fields
fail closed.

## Signed-Bound Direction

Positive settlement lower bound:

```text
value_lower_bound - cost_upper_bound - risk_upper_bound - transport_upper_bound
```

Negative or stale upper bound:

```text
value_upper_bound - cost_lower_bound - risk_lower_bound - transport_lower_bound
```

Missing coordinates are undefined. They must not be interpreted as zero.

## Compatibility Requirements

A compatible implementation must preserve:

- packet-type enums and lifecycle states;
- fail-closed missing-data semantics;
- value-estimand hierarchy, where proxy-only evidence cannot increase capital;
- dual-ledger separation;
- signed lower/upper bound direction;
- predicate-level reporting;
- CARA conditional fields;
- auditability of every state-changing packet.

## v0.2.0 Module Schemas

| Schema | Purpose | Typical producer |
| --- | --- | --- |
| `measurement-spec.schema.json` | task/solver/protocol, trace view, sample, instrumentation, firewall, contamination | trace instrumentation and evaluator harness |
| `evidence-split.schema.json` | train, candidate, proxy, gold, held-out, audit split declarations | evidence scheduler |
| `causal-certificate.schema.json` | estimand, baseline, identification, effect lower bound, mode-specific evidence | causal estimator or calibrated proxy bridge |
| `baseline-envelope.schema.json` | resource-matched baseline and refresh contract | baseline monitor |
| `opportunity-law.schema.json` | mission/generated/externality opportunity law | opportunity-measure constructor |
| `transport-certificate.schema.json` | support, density ratio, drift, refresh, transport cost | transport monitor |
| `risk-ledger.schema.json` | reserve, hazard, irreversible loss, raw-net solvency | risk ledger |
| `authority-certificate.schema.json` | authority, capability, threat, runtime witness, telemetry, guard | guarded-deployment controller |
| `root-finality-record.schema.json` | root, role separation, quorum, finality, rollback, optional signatures | evaluator root service |
| `portfolio-state.schema.json` | available objects, dependencies, settlement ledgers | portfolio accountant |
| `reproduction-record.schema.json` | reproduction matrix, gauge, capacity, identification, recombination | foundry growth estimator |
| `cara-claim.schema.json` | target validity, baseline envelope, target membership, viability, time-to-target | CARA target checker |
| `foundry-transcript.schema.json` | replayable deterministic transition transcript | conformance runner |
| `conformance-result.schema.json` | portable replay result | CI or release audit |

The module schemas are deliberately not hidden Python internals. They are
intended for agents implementing the paper in any programming language. A
non-Python implementation can emit these records, replay the transcripts, and
then feed packet-level claims into its own kernel.
