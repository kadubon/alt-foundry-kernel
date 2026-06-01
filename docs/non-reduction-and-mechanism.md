# Non-Reduction And Mechanism Guards

Paper DOI: [https://doi.org/10.5281/zenodo.20476200](https://doi.org/10.5281/zenodo.20476200)

ALT's distinctive point is that liquidity is not reducible to familiar proxy
properties. A trace-derived artifact may be compact, novel, transferable in one
benchmark, frequent in a library, large in evidence volume, or easy to package,
and still fail to become safe certified abstraction capital.

## Non-Reduction Contract

The v0.4.0 `non_reduction` module makes this explicit. It rejects attempts to
use these properties as substitutes for liquidity certification:

- compression;
- novelty;
- benchmark score or transfer score;
- trace volume or evidence volume;
- library size or duplicate count;
- static surplus without lifecycle settlement;
- surface packaging or category structure;
- informal generality.

The corresponding schema is `schemas/non-reduction-audit.schema.json`. A valid
audit must declare the liquidity claim, measurement status, signed-surplus
status, transport status, hazard status, authority status, lifecycle status,
finality status, and shortcut audit. If the claim affects settlement capital,
`kernel_route.status` must be valid.

Example:

```bash
uv run altk certify non-reduction examples/certificates/non_reduction_audit.json
```

## Mechanism Contract

The `mechanism` module checks whether a reuse claim is grounded in mechanism
evidence rather than in the artifact's surface properties. It validates:

- placebo or null-token control;
- mechanism-ablation surplus;
- actor-neutral intervention invariance;
- evaluator independence;
- self-certification rejection;
- positive lower-bound mechanism effect.

Example:

```bash
uv run altk certify mechanism examples/certificates/mechanism_certificate.json
```

## Failure Semantics

If a shortcut is marked as `used_as_certification: true`, the non-reduction
audit fails. If a mechanism certificate is self-certified, the mechanism report
fails. These are hard errors because the paper treats them as invalid routes to
liquidity, not as weak evidence that can be compensated by surplus elsewhere.

The conformance fixture `conformance/v0.3.0/rejected_self_certification.json`
fixes this behavior for non-Python implementations.
