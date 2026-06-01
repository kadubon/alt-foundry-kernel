# Theory Map

Paper:
Takahashi, K. (2026). *Abstraction Liquidity Theory*. Zenodo.
[https://doi.org/10.5281/zenodo.20476200](https://doi.org/10.5281/zenodo.20476200)

This document maps the implementation-facing objects in Abstraction Liquidity
Theory (ALT) to the bootloader. The paper remains the normative source; this
repository supplies a deterministic reference kernel and language-neutral
contract that agents can extend.

## Central Claim

ALT asks when traces from local problem solving become reusable abstraction
assets. A trace is not liquid capital merely because it looks useful. It must be
converted into an operational token, measured against a declared baseline and
opportunity law, charged for lifecycle and hazard costs, transported only under
valid evidence, and settled through an actor-neutral fail-closed kernel.

The central quantity is signed surplus: downstream search-cost reduction minus
formation, deployment, validation, certification, settlement, maintenance,
telemetry, transport, hazard, rollback, deprecation, contamination-control, and
misapplication charges.

## Paper Objects To Repo Objects

| Paper object | Meaning | Repo surface |
| --- | --- | --- |
| Abstraction token | Reusable operational object extracted from traces | `Token`, `schemas/token.schema.json` |
| Executable certificate packet | Machine-readable claim consumed by the kernel | `Packet`, `schemas/packet.schema.json` |
| Declaration layer | Claim, scope, mission, baseline, estimand, authority, capability, dependencies | `packet.declaration` |
| Evidence layer | Trace view, samples, design, selection, instrumentation | `packet.evidence` |
| Bound layer | Value, cost, risk, transport, reserve, raw-net coordinates | `packet.bounds`, `compute_signed_bounds` |
| Validity layer | Telemetry, transport, hazard, root, finality, budget, capacity, viability | `packet.validity` |
| Monitor layer | Drift, refresh, deprecation, rollback, resurrection rules | `packet.monitor` |
| Fallback layer | Executable fail-closed action | `packet.fallback` |
| Kernel state tuple | Admitted set, queue, ledgers, hazards, monitors, authority, roots, audit | `KernelState`, `schemas/kernel-state.schema.json` |
| Exploration ledger | Proxy-only or weak evidence that cannot add capital | `exploration_ledger` |
| Settlement ledger | Finalized or exempt settlement evidence | `settlement_ledger` |
| Negative registry | Scope-limited stale or harmful certificates | `negative_registry` |
| Measurement specification | Task, solver, protocol, trace view, sample, instrumentation, firewall | `measurement`, `schemas/measurement-spec.schema.json` |
| Causal certificate | Potential-outcome estimand, baseline, identification, effect lower bound | `causal`, `schemas/causal-certificate.schema.json` |
| Transport certificate | Support, density-ratio, drift, refresh, transport cost | `transport`, `schemas/transport-certificate.schema.json` |
| Risk ledger | Reserve, hazard, irreversible loss, raw-net solvency | `risk`, `schemas/risk-ledger.schema.json` |
| Root/finality record | Root, role separation, quorum, finality, rollback path | `root_finality`, `schemas/root-finality-record.schema.json` |
| Portfolio state | Dependency closure, DAG, settlement-only capital accounting | `portfolio`, `schemas/portfolio-state.schema.json` |
| Reproduction record | Matrix, gauge, capacity, identification, recombination gate | `reproduction`, `schemas/reproduction-record.schema.json` |
| CARA claim | Target validity, baseline envelope, membership, viability, time-to-target | `cara`, `schemas/cara-claim.schema.json` |
| Dashboard protocol | Agent-readable foundry state and allocation surface | `foundry`, `schemas/dashboard.schema.json` |

## Kernel Tuple Mapping

The paper defines kernel state as:

```text
X_t = (B_t, Q_t, L_t, H_t, M_t, U_t, N_t, R_t, A_t)
```

The bootloader maps this tuple as:

| Paper coordinate | Bootloader field |
| --- | --- |
| `B_t`, admitted token set | `admitted_tokens`, `token_states` |
| `Q_t`, candidate queue | `candidate_queue` |
| `L_t`, certificate and capital ledger | `exploration_ledger`, `settlement_ledger`, `certified_capital` |
| `H_t`, hazard ledger | `hazard_ledger` |
| `M_t`, monitor and drift state | `monitor_drift_state` |
| `U_t`, authority and capability state | `authority_capability_state` |
| `N_t`, negative registry and resurrection queue | `negative_registry`, `resurrection_queue` |
| `R_t`, root/quorum and finality state | `root_finality_state` |
| `A_t`, immutable audit log | `audit_log` |

## Admission Predicate Coverage

The paper's admission kernel is a conjunction of field, evidence, validity,
budget, root, finality, and viability predicates. The bootloader exposes these
predicate names in `ValidationReport.predicates`:

`SchemaOK`, `NetLowerBoundOK`, `MissionOK`, `TargetValidityOK`,
`BaselineEnvelopeOK`, `BaselineLive`, `OpportunityLawOK`, `EvidenceLive`,
`SelectionOK`, `TelemetryOK`, `TransportOK`, `HazardOK`, `AuthorityOK`,
`CapabilityOK`, `ThreatOK`, `DependencyClosed`, `RootOK`, `QuorumOK`,
`FinalityOK`, `BudgetOK`, `CapacityOK`, `RefreshOK`, `RollbackOK`,
`DeprecationOK`, `RawNetSolvencyOK`, `RuntimeWitnessOK`, `NoncompHazardOK`,
and `ViabilityOK`.

In v0.2.0, the packet kernel still exposes these as packet-level gates, and the
new certificate modules provide evidence-facing validators for measurement,
causal effect, transport, risk, authority, root/finality, portfolio,
reproduction, and CARA claims. A full domain foundry should replace status
assertions with evidence-producing instruments while preserving the same failure
semantics. If a predicate required for capital admission is false, the kernel
rejects or defers. If it is undefined because a conditional claim is not made,
it remains `null` and does not block ordinary admission.

## Deterministic Settlement Loop

An agent-operable foundry should converge on this loop:

```text
parse -> schema -> typed layers -> dependencies -> mission
-> baseline refresh -> threat model -> telemetry -> LCB/UCB
-> selection -> hazard -> transport -> root/quorum -> finality
-> ledger -> budget -> capacity -> monitor -> kernel decision
```

The v0.2.0 implementation covers the parser, schema, typed layers,
signed-bound discipline, predicate reports, dual-ledger accounting, lifecycle
transitions, deterministic transcript replay, and module-level certificate
checkers. It does not infer scientific truth from raw traces; it verifies the
declared certificate records that a measurement, causal, transport, risk,
root/finality, reproduction, or CARA module supplies.

## Module Handoff Map

| Module | Inputs | Outputs | Fail-closed boundary |
| --- | --- | --- | --- |
| `measurement` | task, solver, protocol, trace, sample, instrumentation | measurement `CertificateReport` | missing firewall, trace sufficiency, contamination, or selection |
| `statistics` | bounded samples, confidence, selection count | lower bounds and reproducible metrics | empty sample, invalid range, invalid confidence |
| `causal` | estimand, baseline, identification, effect, evidence mode | settlement-grade or exploration certificate | proxy-only or missing mode-specific evidence |
| `transport` | source/target context, support, ratio, drift, refresh | transport cost and validity report | uncovered support, unbounded ratio, stale refresh |
| `risk` | capital, reserve, hazard, irreversible loss | raw-net solvency report | noncompensable hazard or nonpositive raw net |
| `authority` | authority, capability, threat, telemetry, guard | guarded-deployment report | uncleared threat or invalid runtime witness |
| `root_finality` | root, role separation, quorum, finality, rollback | finality report and optional signature count | missing quorum or nonfinal evidence |
| `portfolio` | dependencies, available objects, ledgers | closure and capital accounting | cycles, missing dependencies, exploration capital |
| `reproduction` | matrix, gauge, capacity, identification | reproduction report | unidentified recombination claim |
| `cara` | target, basis, baseline envelope, membership, viability, time-to-target | target-crossing report | missing target evidence or no time improvement |

## Non-Reduction Boundary

This repository does not reduce ALT to JSON validation. JSON Schema means only
that the packet is parseable. Certification requires evidence modules that
populate packet and certificate fields under declared measurement protocols.
Until those modules produce typed evidence, the correct behavior is
exploration-only or fail-closed.
