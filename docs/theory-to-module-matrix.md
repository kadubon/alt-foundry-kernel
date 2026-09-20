# Theory-To-Module Matrix

Paper DOI: [https://doi.org/10.5281/zenodo.20476200](https://doi.org/10.5281/zenodo.20476200)

This matrix is the release-facing map from major ALT theorem and proposition
classes to the v0.4.0 implementation surface. It is designed for agents and
non-Python implementers that need to know which parts are executable, which are
certificate validators, and which remain scientific work.

## Status Labels

- `implemented`: deterministic reference behavior exists and is tested.
- `estimator`: the repo computes a generic certificate report from declared JSON
  data and fails closed when assumptions are missing.
- `validator only`: the repo checks declared certificates but does not estimate
  or discover the underlying scientific fact.
- `schema only`: the repo defines the portable record shape.
- `deferred`: the paper concept is mapped but needs a future evidence engine.
- `not certified`: the repo explicitly refuses to treat the object as certified
  without external evidence.

## Matrix

| Paper class | Status | Repo surface | Boundary |
| --- | --- | --- | --- |
| Executable certificate packet | implemented | `Packet`, `schemas/packet.schema.json`, `validate_packet` | JSON validity is not scientific validity |
| Signed surplus lower/upper discipline | implemented | `bounds.compute_signed_bounds` | missing coordinates are undefined |
| Dual-ledger settlement | implemented | `KernelState`, `run_kernel_transition` | exploration cannot add capital |
| Lifecycle preservation | implemented | packet transition tests and conformance fixtures | invalid state preconditions fail closed |
| Admission predicate conjunction | implemented | `ValidationReport.predicates` | status gates do not replace evidence production |
| Non-reduction results | validator only | `non_reduction`, `non-reduction-audit.schema.json` | shortcut properties cannot certify liquidity |
| Placebo and mechanism-ablation reuse | validator only | `mechanism`, `mechanism-certificate.schema.json` | supplied certificate must carry the experiment |
| Actor-neutral intervention invariance | validator only | `mechanism` | validator checks declaration, not intervention discovery |
| Self-certification rejection | implemented as validator | `mechanism`, `evaluator`, conformance negative fixtures | cycles and self-certified value claims fail |
| Evaluator stratification | validator only | `evaluator`, `evaluator-hierarchy.schema.json` | graph acyclicity is checked; governance is external |
| Independent root rotation | validator only | `evaluator`, `root_finality` | root validity must be supplied |
| Federated finality and quorum safety | validator only | `finality`, `root_finality` | no consensus protocol is implemented |
| PoUA ledger | validator only | `finality-poua-ledger.schema.json` | PoUA weight cannot replace epistemic authority |
| Sequential evidence rule | estimator | `sequential`, `alpha-budget estimator`, `sequential-decision.schema.json` | EVSI-style fields are checked; alpha budgets can be computed |
| Finite evidence budget | validator only | `sequential` | sample action must be affordable |
| Robust estimated transport | estimator | `transport_ext`, `transport-diagnostics estimator` | support/radius certificates are computed from declared samples |
| Wasserstein-radius transport | estimator | `transport-robustness.schema.json`, `transport-diagnostics.schema.json` | empirical radius is computed; assumptions remain declared |
| Causal-invariance transport | validator only | `transport_ext` | invariance evidence is not discovered |
| Observable transport stopping | validator only | `transport_ext` | stopping record must be explicit |
| Certificate composition algebra | validator only | `certificate_algebra` | common-estimand proof is required |
| Negative-certificate scope propagation | validator only | `certificate_algebra` | propagation scope is checked, not inferred |
| Portfolio dependency closure | implemented | `portfolio.validate_dependency_closure` | unavailable dependencies fail |
| Portfolio conflict and breadth guards | estimator | `portfolio_ext`, `portfolio-selection estimator` | greedy selection is deterministic, not globally optimal |
| Cherry-picking and breadth gaming | validator only | `portfolio_ext` | declared audits are checked |
| Foundry bottleneck/min-cut control | estimator | `foundry_control`, `foundry-phase estimator` | min-cut is computed from declared network |
| Shadow price and absorption control | estimator | `foundry_control`, `phase-control-record.schema.json` | shadow signal is local to declared graph |
| Capital-conservative exploration | validator only | `foundry_control` | exploration risk must stay within budget |
| Measurement task/protocol/evaluator firewall | validator only | `measurement` | trace capture and leakage tests are external |
| Causal certificates | validator only | `causal` | randomized/paired/replay/off-policy/DR fields are checked |
| Risk and noncompensable hazard | validator only | `risk` | dynamic hazard estimation is external |
| Root/finality signatures | partial implementation | `root_finality.verify_ed25519_signature` | signature verification is optional; quorum governance is external |
| Reproduction and recombination | estimator | `reproduction`, `reproduction-phase estimator` | unidentified recombination claims fail |
| CARA target crossing | estimator | `cara`, `cara_ext`, `cara-time-to-target estimator` | target validity and time-to-target evidence must be supplied |
| ASI realization | not certified | docs and CARA guards | no real-world ASI claim is certified |

## v0.5.0 bounded additions

| Area | Status | Surface | Boundary |
| --- | --- | --- | --- |
| Finite typed abstraction formation | implemented | `reuse.formation` | Explicit literal parameterization; no unrestricted synthesis |
| Receiver qualification | implemented structural replay | `reuse.qualification` | Exact source/receiver checks; authentication and causal value unknown |
| Net reuse selection | implemented finite model | `reuse.planning`, `reuse.checker` | Exhaustive registered catalogue only; no hidden-world optimization |
| Lifecycle recomputation | implemented local model | `reuse.lifecycle`, `reuse.bridge` | Append-only evidence; no settlement authority |
| Companion mapping | implemented supported subsets | `reuse.interchange`, `reuse.cait_export` | Native acceptance is not live host enforcement |

See [collective reuse](collective-reuse.md) for bounds, costs, unsupported cases and tests.

## Implementer Rule

When in doubt, map a paper theorem to one of three public artifacts:

1. a schema field that records the claim;
2. a deterministic validator that checks the declared certificate; or
3. a fail-closed boundary documenting that the repo does not certify it.

Do not replace missing evidence with a default numeric value. Do not turn a
non-reduction signal into a liquidity certificate. Do not allow audit-only
records to increase settlement capital.
