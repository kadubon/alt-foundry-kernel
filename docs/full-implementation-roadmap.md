# Full Implementation Roadmap

Paper DOI: [https://doi.org/10.5281/zenodo.20476200](https://doi.org/10.5281/zenodo.20476200)

This roadmap describes how to extend the v0.4.0 reference kernel into a fuller
Abstraction Liquidity Theory foundry while preserving the executable packet,
certificate, and transcript contracts.

## Stage 0: v0.4.0 Kernel Boundary

- Preserve the public packet schema, lifecycle states, predicate names, and
  fail-closed transition semantics.
- Preserve the language-neutral contract in `docs/language-neutral-contract.md`
  so TypeScript, Rust, Go, JVM, and other implementations can interoperate.
- Keep bridge and kernel-update packets audit-only until an independent root or
  quorum verifier is implemented.
- Run `uv run altk audit-public --strict` before publishing any fork or release.
- Replay `conformance/` fixtures after changing kernel semantics.

## Stage 1: Trace And Extraction Layer

- Implement trace capture contracts with explicit logged and unlogged variables.
- Add extraction pipeline records: segmentation, candidate mining,
  canonicalization, ablation design, leakage check, typed dependency graph,
  minimal interface, verifier binding, and search status.
- Add token grammar validators for instruction templates, patch patterns,
  theorem tactics, evaluator harnesses, and workflow policies.

## Stage 2: Measurement And Bounds

- Connect the bundled measurement validator to real trace stores and evaluator
  firewalls.
- Implement opportunity-measure constructors for static, replay, rolling
  production, and closed-loop policy-induced measures.
- Add baseline selector and baseline-refresh bridge checker.
- Extend the bundled empirical Bernstein and post-selection helpers with
  confidence sequences, e-values, and domain-specific variance accounting.
- Add FCU exchange tables, lifecycle cost bounds, and telemetry-corrected
  operating value.

## Stage 3: Validity And Safety

- Add mission/generated/externality law checkers and mission-validity bridges.
- Add authority and capability envelope enforcement.
- Add adversarial-token threat-model checks for prompt injection, evaluator
  tampering, hidden tool escalation, dependency confusion, poisoned retrieval,
  model-bearing skill backdoors, and self-certification loops.
- Add hazard-envelope, noncompensable-hazard, ruin-budget, irreversible-risk,
  and dynamic risk-ledger modules.

## Stage 4: Transport, Roots, And Finality

- Implement support coverage, density-ratio, drift, and causal-invariance
  diagnostics on top of the transport certificate surface.
- Implement robust estimated transport and Wasserstein-radius construction for
  `schemas/transport-robustness.schema.json`; keep the validator as the
  settlement gate.
- Connect root/finality validation to evaluator-root, role-separated-root,
  quorum, finality, stale-packet, and partition-alarm services.
- Connect evaluator hierarchy records to an independently operated root rotation
  service; preserve acyclicity and self-certification-cycle rejection.
- Connect PoUA ledgers to governance and finality; never let PoUA weight replace
  mission-valid evidence or evaluator independence.
- Add transport-refresh and opportunity-law refresh bridges that subtract
  declared conservative charges.

## Stage 5: Sequential Evidence, Algebra, And Portfolio

- Implement sequential sample/settle controllers that estimate EVSI and finite
  evidence budgets before emitting `sequential-decision` records.
- Implement certificate-algebra proof search for common estimands, bridge
  compatibility, and negative-certificate scope propagation.
- Extend the bundled dependency-closure and capital-accounting utilities with
  portfolio selection, conflict constraints, and behavioral-equivalence
  quotienting.
- Add cherry-picking audits, breadth partitions, behavioral covering or metric
  entropy records, and submodular selection interfaces.

## Stage 6: Reproduction And Recombination

- Add gauge compatibility for class-wise capital coordinates.
- Add causal reproduction matrix identification, capacity-capped reproduction,
  recombination tensor confidence sets, residual charges, and phase
  classification.

## Stage 7: Foundry Control

- Implement bottleneck/min-cut measurement, shadow prices, absorption-capacity
  estimates, capital-conservative exploration, and dashboard phase-control
  policies on top of `schemas/foundry-control-state.schema.json`.
- Treat foundry-control outputs as allocation records; they do not certify
  scientific validity by themselves.

## Stage 8: CARA Target Claims

- Add ASI target-set parser, capability-basis registry, target-membership
  checker, resource-matched baseline upper-envelope checker, raw-net-capital
  solvency calculator, runtime witness verifier, and time-to-target comparator.
- Keep CARA claims scoped: they are target-valid, baseline-certified,
  raw-net-solvent, viability-qualified time-to-target statements, not
  unconditional intelligence claims.

## Non-Negotiable Invariant

Every module must write through the packet, certificate, or transcript schema
and the kernel transition. A scientific module may generate evidence, bounds,
or bridge certificates, but it does not bypass fail-closed admission.
