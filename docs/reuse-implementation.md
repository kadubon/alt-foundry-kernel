# Collective reuse implementation record

Theory: https://doi.org/10.5281/zenodo.20476200

Baseline inspected: v0.4.0, commit b5170dbee93b9183f86570c9b2fa325be9cded51.
The checkout was clean and upstream matched. No open PR, branch protection or
ruleset was reported. The existing Wiki git repository was unavailable; do not
create one. The sole workflow runs checks on pushes and has no publication job.
The two specified DOI pages were unavailable through the research reader; paper
text was not read. Repository contracts and the scoped specification govern this
implementation, without a claim to implement either entire theory.

| Requirement | Existing surface | Additive work and verification |
| --- | --- | --- |
| A1 formation | Token is permissive; no trace reconstruction | Closed source envelopes, typed finite sequence extraction, independent reconstruction tests |
| A1 qualification | Transport validators check declarations | Receiver/input/protocol bound source checks and finite adapters |
| A2 selection | Greedy portfolio estimator and conflict validators | Exact nonadaptive subset selection, shared physical costs, slots, matched comparators, independent checker and tiny oracle |
| A3 lifecycle | Packet kernel and cumulative capital | Isolated model journal, revision checks, scoped eligibility, immutable outcomes; regression for legacy cumulative accounting |
| A3 interchange | Legacy token wire format | Released CCR 1.8.0, VEK 1.3.0, CAIT 0.2.0 read-only contracts and native checks |
| A4 delivery | L5 conformance, lint/types/audit/tests | Preserve old checks; add coverage, faults, cross-platform artifact tests and public GitHub asset verification |
| Excluded | External evidence and authority | No scientific acceleration experiment, settlement promotion, signing service, companion edits, PyPI or deployment |

Legacy characterization: admission currently increments cumulative capital even
on repeated delivery; suspension/deprecation remove the admitted token but retain
the historical capital field. The new model profile must never use that cumulative
field as currently eligible stock or send model evidence to settlement.

This is a work record, not a completion claim. Release qualification and public
asset verification must be recorded only after the corresponding checks run.
