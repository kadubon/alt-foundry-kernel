# Root, Portfolio, Reproduction, And CARA

Paper DOI: [https://doi.org/10.5281/zenodo.20476200](https://doi.org/10.5281/zenodo.20476200)

This document covers v0.3.0 contracts for the paper's root/finality,
portfolio, reproduction, recombination, and target-crossing surfaces.

## Root And Finality

`root-finality-record.schema.json` and
`validate_root_finality_certificate` require root status, role separation,
quorum threshold, signed quorum count, finality status, and rollback path.
Optional Ed25519 signatures can be verified when a message and base64 public
keys/signatures are present.

`evaluator-hierarchy.schema.json` and `finality-poua-ledger.schema.json` add
v0.3.0 guards for stratified evaluator DAGs, independent root rotation,
federated finality, weighted quorum, PoUA non-authority, and finality-safe
settlement. These checkers do not implement Byzantine governance by themselves.
They verify records supplied by evaluator and finality services.

## Portfolio

`portfolio-state.schema.json` supports dependency closure and settlement-only
capital accounting. The reference utilities validate dependency availability,
reject dependency cycles, and sum only settlement-ledger capital deltas.
Exploration entries do not increase safe certified abstraction capital.

`portfolio-constraints.schema.json` and `validate_portfolio_constraints`
extend this surface with conflict graphs, breadth partitions, cherry-picking
guards, behavioral covering, and a submodular interface flag. The validator does
not solve the portfolio problem; it rejects declared selections that violate the
certificate.

## Reproduction And Recombination

`reproduction-record.schema.json` and `validate_reproduction_certificate`
require a reproduction matrix, valuation gauge, capacity record, and
identification status. Recombination claims fail closed unless they include
valid recombination identification.

The helper `capacity_capped_growth` implements non-negative matrix growth under
capacity caps. It is a deterministic calculator, not an estimator.

## CARA

`cara-claim.schema.json` and `validate_cara_certificate` check capability
acceleration and target-crossing records. When target crossing or time-to-target
comparison is claimed, the record must include target validity, capability
basis, baseline upper envelope, target membership, viability witness, and
candidate/baseline time-to-target bounds.

`cara-process.schema.json` and `validate_cara_process` add v0.3.0 guardrails for
target-valid processes, non-tradable target constraints, baseline envelopes,
viability-controlled acceleration, raw-net capital, and stopping conditions.
These checkers verify structural target-crossing conditions and time-to-target
improvement. They do not certify ASI realization.
