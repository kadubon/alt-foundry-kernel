# Language-Neutral Contract

Paper DOI: [https://doi.org/10.5281/zenodo.20476200](https://doi.org/10.5281/zenodo.20476200)

ALT Foundry Kernel is intentionally not a Python-only specification. The Python
package is the reference implementation for v0.4.0. The portable contract is
the executable packet shape, module certificate schemas, predicate semantics,
signed-bound discipline, lifecycle state machine, dual-ledger accounting rule,
certificate report shape, estimator report shape, and replayable conformance
fixtures.

## Required Wire Surface

A conforming implementation must accept and emit packets with this top-level
shape:

```text
Packet := {id, type, token_id, version, state, scope_hash,
           declaration, evidence, bounds, validity,
           monitor, fallback, signatures}
```

The implementation may use JSON Schema, generated model classes, a typed DSL,
protobuf, or another deterministic parser internally. Interoperability requires
exporting JSON compatible with `schemas/*.schema.json`.

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

## Packet Predicate Semantics

Predicate reports must use `true`, `false`, or `null`.

- `true`: the packet supplies the required typed evidence for the gate.
- `false`: the gate is claimed or required and fails.
- `null`: the gate is not applicable to that packet type or conditional claim.

Packet-level predicate names are:

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

## v0.4.0 Certificate Predicates

Module checkers use the same report shape but different predicate namespaces.
Conforming implementations should preserve these names when implementing the
corresponding modules:

| Module kind | Representative predicates |
| --- | --- |
| `non-reduction` | `LiquidityClaimExplicit`, `ShortcutFree`, `KernelRouteDeclared` |
| `mechanism` | `PlaceboControlled`, `AblationOK`, `ActorNeutralOK`, `SelfCertificationFree` |
| `evaluator` | `RootOK`, `RootRotationOK`, `EvaluatorGraphAcyclic`, `StratifiedEdgesOK` |
| `finality` | `FederatedFinalityOK`, `WeightedQuorumOK`, `PoUANotEpistemicAuthority` |
| `sequential` | `FiniteEvidenceBudgetOK`, `HorizonOK`, `SettleOrSampleOK` |
| `transport-ext` | `SupportCoverageOK`, `RobustEstimateOK`, `WassersteinRadiusOK` |
| `certificate-algebra` | `NaiveCompositionRejected`, `CommonEstimandOK`, `NegativeScopePropagationOK` |
| `portfolio-ext` | `ConflictFreeSelection`, `BreadthPartitionOK`, `CherryPickingCleared` |
| `foundry-control` | `BottleneckCapacityOK`, `AbsorptionCapacityOK`, `CapitalConservativeExploration` |
| `cara-ext` | `TargetValidityOK`, `NonTradableConstraintsOK`, `ViabilityControlledOK` |

These validators check declared certificates. Estimator helpers add deterministic
builders for selected generic certificate artifacts, but a false predicate still
blocks settlement or keeps the record audit-only.

## v0.4.0 Estimator Reports

Estimator commands use the same `CertificateReport` shape as validators. The
stable kinds are `finite-sample`, `proxy-bridge`, `causal-effect`,
`transport-diagnostics`, `guard-risk`, `federated-pooling`,
`portfolio-selection`, `foundry-phase`, `reproduction-phase`,
`cara-time-to-target`, and `alpha-budget`. Their output artifacts are described
in `docs/estimator-contract.md`.

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
return an undecidable or fail-closed result when a capital-relevant coordinate is
missing.

## Dual-Ledger Rule

The exploration ledger may store proxy-only evidence, weak mechanism evidence,
sandbox trials, failed candidates, threat-model findings, and high-variance
experiments. It must not increase safe certified abstraction capital.

The settlement ledger may increase safe certified capital only when the packet
passes the value-estimand hierarchy, signed-bound discipline, telemetry,
transport, hazard, authority, capability, threat, root/quorum, finality, budget,
capacity, refresh, rollback, deprecation, raw-net, runtime-witness,
noncompensable-hazard, and viability gates required for the claim.

## Lifecycle Transitions

| Packet type | Capital effect | Required behavior |
| --- | --- | --- |
| `candidate` | none | write candidate queue or reject invalid packet |
| `admission` | possible increase | admit only with settlement-grade evidence |
| `monitor-alarm` | none | suspend active or pending claims |
| `transport-refresh` | no new capital | restore only covered suspended or active scope |
| `deprecation` | none | write negative registry and stop contribution |
| `rollback` | possible decrease | charge reserve and restore declared state |
| `resurrection` | possible increase | add capital only with admission-grade current evidence |
| `bridge` | none | audit-only in this reference kernel |
| `kernel-update` | none | audit-only; current kernel remains authoritative |

## Conformance Levels

| Level | Required behavior |
| --- | --- |
| L0 schema | parse all schemas and validate packet/certificate examples |
| L1 arithmetic | reproduce signed bounds, raw-net capital, and settlement-only accounting |
| L2 kernel | reproduce packet decisions and lifecycle transitions |
| L3 module reports | emit compatible `CertificateReport` objects for all certificate and estimator modules |
| L4 transcript | replay `conformance/` fixtures deterministically |
| L5 public release | pass an audit equivalent to `altk audit-public --strict` |

`altk conformance --fixtures conformance --level L5` is the reference command.
The runner includes historical v0.2.0 admission replay, v0.3.0 packet and
certificate fixtures, and v0.4.0 estimator fixtures for no trace sufficiency,
no off-policy overlap, invalid proxy bridge, high-dimensional transport failure,
PoUA-as-authority failure, unidentified recombination, guard calibration
failure, unsafe CARA target timing, and exhausted evidence budget.

## Report Shape

Module checkers should emit a report equivalent to:

```json
{
  "name": "transport_ext",
  "ok": true,
  "claim": "robust transportability certificate",
  "level": "settlement",
  "predicates": {"SupportCoverageOK": true},
  "metrics": {"wasserstein_radius_upper_bound": 0.1},
  "artifacts": {},
  "issues": []
}
```

Issues are structured records with `severity`, `code`, `path`, and `message`.
Capital-relevant failures use `severity: "error"` and must block settlement or
route to exploration.

## Deferred Scientific Modules

Language conformance does not imply full ALT certification. Causal inference,
finite-sample bounds, transportability, root/quorum finality, dynamic risk,
recombination, reproduction, and CARA target crossing require independent
scientific modules that emit typed evidence into the same packet contract.
