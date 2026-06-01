# Language-Neutral Contract

Paper DOI: [https://doi.org/10.5281/zenodo.20476200](https://doi.org/10.5281/zenodo.20476200)

ALT Foundry Kernel is intentionally not a Python-only specification. The Python
package is the reference implementation for v0.2.0. The portable contract is
the executable certificate packet shape, module-level certificate schemas,
predicate reports, signed-bound discipline, lifecycle state machine, dual-ledger
accounting rule, and replayable conformance transcripts.

## Required Wire Surface

A conforming implementation must accept and emit packets with this top-level
shape:

```text
Packet := {id, type, token_id, version, state, scope_hash,
           declaration, evidence, bounds, validity,
           monitor, fallback, signatures}
```

The implementation may use JSON Schema, a typed DSL, protobuf, generated model
classes, or another deterministic parser, but it must expose semantically
equivalent fields to the admission kernel. When exporting interoperable packets,
use the JSON files in `schemas/` as the public wire format.

## Required Enums

Packet types:

```text
candidate | admission | transport-refresh | monitor-alarm |
deprecation | rollback | resurrection | bridge | kernel-update
```

Lifecycle states:

```text
candidate | exploration | pending_settlement |
active | suspended | deprecated | resurrected
```

Kernel decisions:

```text
admit | reject | defer | suspend | deprecate | rollback | resurrect
```

## Predicate Semantics

Predicate reports must use `true`, `false`, or `null`.

- `true`: the packet supplies the required typed evidence for the v0.2.0 gate.
- `false`: the gate is claimed or required and fails.
- `null`: the gate is not applicable to that packet type or conditional claim.

The packet-level predicate names are:

`SchemaOK`, `NetLowerBoundOK`, `MissionOK`, `TargetValidityOK`,
`BaselineEnvelopeOK`, `BaselineLive`, `OpportunityLawOK`, `EvidenceLive`,
`SelectionOK`, `TelemetryOK`, `TransportOK`, `HazardOK`, `AuthorityOK`,
`CapabilityOK`, `ThreatOK`, `DependencyClosed`, `RootOK`, `QuorumOK`,
`FinalityOK`, `BudgetOK`, `CapacityOK`, `RefreshOK`, `RollbackOK`,
`DeprecationOK`, `RawNetSolvencyOK`, `RuntimeWitnessOK`, `NoncompHazardOK`,
and `ViabilityOK`.

`TargetValidityOK` and `BaselineEnvelopeOK` are `null` unless the packet claims
CARA target crossing or a time-to-target comparison. If the claim is present,
missing target-validity, target-membership, baseline-envelope, viability, or
time-to-target fields fail closed.

## Signed-Bound Discipline

Positive settlement lower bound:

```text
value_lower_bound - cost_upper_bound - risk_upper_bound - transport_upper_bound
```

Negative or stale upper bound:

```text
value_upper_bound - cost_lower_bound - risk_lower_bound - transport_lower_bound
```

Undefined coordinates do not default to zero. A conforming implementation must
return an undecidable or fail-closed result when a capital-relevant bound is
missing.

## Dual-Ledger Rule

The exploration ledger may store proxy-only evidence, weak mechanism evidence,
sandbox trials, failed candidates, threat-model findings, and high-variance
experiments. It must not increase safe certified abstraction capital.

The settlement ledger may increase safe certified capital only when the packet
passes the value-estimand hierarchy, signed-bound discipline, telemetry,
transport, hazard, authority, capability, threat, root/quorum, finality, budget,
capacity, refresh, rollback, deprecation, raw-net, runtime-witness,
noncompensable-hazard, and viability gates that are required for the claim.

## Lifecycle Transitions

A conforming implementation must preserve these v0.2.0 transition semantics:

| Packet type | Capital effect | v0.2.0 behavior |
| --- | --- | --- |
| `candidate` | none | write candidate queue or reject invalid packet |
| `admission` | possible increase | admit only with settlement-grade evidence |
| `monitor-alarm` | none | suspend active or pending claims |
| `transport-refresh` | no new capital | restore only covered suspended or active scope |
| `deprecation` | none | write negative registry and stop contribution |
| `rollback` | possible decrease | charge reserve and restore declared state |
| `resurrection` | possible increase | add capital only with admission-grade current evidence |
| `bridge` | none | audit-only in v0.2.0 |
| `kernel-update` | none | audit-only; current kernel remains authoritative |

## Conformance Levels

| Level | Required behavior |
| --- | --- |
| L0 schema | parse all schemas and validate packet/certificate examples |
| L1 arithmetic | reproduce signed bounds, raw-net capital, and settlement-only capital accounting |
| L2 kernel | reproduce packet decisions and lifecycle transitions |
| L3 module reports | emit compatible `CertificateReport` objects for measurement, causal, transport, risk, authority, root/finality, reproduction, and CARA checks |
| L4 transcript | replay `conformance/` fixtures deterministically |
| L5 public release | pass an audit equivalent to `altk audit-public --strict` |

## Conformance Tests

Non-Python implementations should:

- validate every `examples/*_packet.json` and
  `examples/certificates/*.json` against the JSON Schemas;
- reproduce the reference decisions for packet examples;
- replay `conformance/v0.2.0/golden_admission_transcript.json`;
- reject missing required fields for every packet type;
- keep proxy-only admission in exploration;
- prevent resurrection capital without admission-grade current evidence;
- pass public-surface checks equivalent to `altk audit-public --strict`;
- keep the DOI link and avoid bundling the paper source.

## Deferred Scientific Modules

Language conformance does not imply full ALT certification. Causal inference,
finite-sample bounds, transport, root/quorum finality, dynamic risk,
recombination, reproduction, and CARA target crossing require independent
scientific modules that emit typed evidence into the same packet contract.

## Report Shape

Module checkers should emit a report equivalent to:

```json
{
  "name": "transport",
  "ok": true,
  "claim": "context transport and opportunity-law refresh certificate",
  "level": "settlement",
  "predicates": {"SupportCovered": true},
  "metrics": {"transport_cost_upper_bound": 1.0},
  "artifacts": {},
  "issues": []
}
```

Issues are structured records with `severity`, `code`, `path`, and `message`.
Capital-relevant failures use `severity: "error"` and must block settlement or
route to exploration.
