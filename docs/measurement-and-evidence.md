# Measurement And Evidence

Paper DOI: [https://doi.org/10.5281/zenodo.20476200](https://doi.org/10.5281/zenodo.20476200)

This document describes how v0.2.0 turns the paper's task, solver, protocol,
trace, value-estimand, and evaluator-firewall requirements into reusable
implementation contracts.

## Contract

Measurement modules emit `measurement-spec.schema.json` records. The reference
checker is `validate_measurement_spec`. A settlement-grade record must declare:

- task, solver, and protocol identifiers;
- estimand type: `causal`, `calibrated-proxy`, or `proxy-only`;
- observed trace projection and trace-sufficiency status;
- sample design and positive sample size;
- instrumentation status;
- selection status;
- evaluator-firewall status;
- contamination status.

Proxy-only measurement is allowed in exploration. It does not increase
settlement capital.

## Evidence Flow

1. Trace capture records observations, actions, tool calls, verifier results,
   costs, runtime context, and unobserved-variable declarations.
2. Measurement specification binds those traces to a task, solver, protocol,
   sample design, and estimand.
3. Statistical helpers compute conservative bounds, but do not decide
   settlement.
4. Causal or calibrated-proxy modules produce certificate records.
5. The packet copies the relevant declarations, evidence, bounds, and validity
   outputs into `declaration`, `evidence`, `bounds`, and `validity`.
6. The kernel decides capital movement.

## Fail-Closed Conditions

The checker fails when firewall, instrumentation, trace sufficiency, selection,
contamination, or sample size is missing or invalid. Missing fields cannot be
treated as zero-cost evidence. Agents should narrow the claim, add a
conservative charge, or keep the token in exploration.
