# Evaluator, Finality, And PoUA Guards

Paper DOI: [https://doi.org/10.5281/zenodo.20476200](https://doi.org/10.5281/zenodo.20476200)

ALT separates useful-use evidence from epistemic authority. Proof-of-useful
abstraction records can support governance and finality, but PoUA weight cannot
replace independent evaluation, root rotation, or evidence of the mission-valid
claim.

## Evaluator Hierarchy

The v0.4.0 `evaluator` module validates a stratified evaluator graph:

- evaluator IDs and strata are explicit;
- evaluation edges form a directed acyclic graph;
- edges point from higher strata to lower strata;
- self-certification edges are rejected;
- root status and root rotation are valid.

Schema: `schemas/evaluator-hierarchy.schema.json`.

Example:

```bash
uv run altk certify evaluator examples/certificates/evaluator_hierarchy.json
```

The negative fixture `conformance/v0.3.0/evaluator_cycle_rejection.json` fixes
cycle rejection as a portable requirement.

## Finality And PoUA

The v0.4.0 `finality` module checks:

- federated finality is finalized;
- root status is valid;
- signed quorum weight meets the declared threshold;
- PoUA is not used as epistemic authority;
- settlement is explicitly finality-safe.

Schema: `schemas/finality-poua-ledger.schema.json`.

Example:

```bash
uv run altk certify finality examples/certificates/finality_poua_ledger.json
```

## Implementation Boundary

This repository does not implement a distributed consensus system or a real
root-governance process. It validates the declared finality and evaluator
records consumed by the packet kernel. If an implementation has a stronger root
system, it should emit the same language-neutral records and preserve the same
fail-closed behavior.
