# Theory Map

Paper:
Takahashi, K. (2026). *Abstraction Liquidity Theory*. Zenodo.
[https://doi.org/10.5281/zenodo.20476200](https://doi.org/10.5281/zenodo.20476200)

This document maps the implementation-facing objects in Abstraction Liquidity
Theory (ALT) to the bootloader. The paper remains the normative source; this
repository supplies a deterministic entry kernel that agents can extend.

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
| Dashboard protocol | Agent-readable foundry state and allocation surface | `schemas/dashboard.schema.json` |

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

In v1, these are status and field gates. A full implementation should replace
each status gate with an evidence-producing verifier while preserving the same
failure semantics. If a predicate required for capital admission is false, the
kernel rejects or defers. If it is undefined because a conditional claim is not
made, it remains `null` and does not block ordinary admission.

## Deterministic Settlement Loop

An agent-operable foundry should converge on this loop:

```text
parse -> schema -> typed layers -> dependencies -> mission
-> baseline refresh -> threat model -> telemetry -> LCB/UCB
-> selection -> hazard -> transport -> root/quorum -> finality
-> ledger -> budget -> capacity -> monitor -> kernel decision
```

The bootloader implements the parser, schema, typed-layer, signed-bound,
predicate-report, dual-ledger, and lifecycle portions. The scientific modules
for mission validity, causal inference, transport, root/quorum, finality,
dynamic risk, recombination, and CARA target crossing remain deferred.

## Non-Reduction Boundary

This repository does not reduce ALT to JSON validation. JSON Schema means only
that the packet is parseable. Certification requires evidence modules that
populate the packet fields under declared measurement protocols. Until those
modules exist, the correct behavior is exploration-only or fail-closed.
