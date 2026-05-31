# Full Implementation Roadmap

Paper DOI: [https://doi.org/10.5281/zenodo.20476200](https://doi.org/10.5281/zenodo.20476200)

This roadmap describes how to extend the v1 bootloader into a fuller
Abstraction Liquidity Theory foundry while preserving the executable packet
contract.

## Stage 0: Bootloader Boundary

- Preserve the public packet schema, lifecycle states, predicate names, and
  fail-closed transition semantics.
- Preserve the language-neutral contract in `docs/language-neutral-contract.md`
  so TypeScript, Rust, Go, JVM, and other implementations can interoperate.
- Keep bridge and kernel-update packets audit-only until an independent root or
  quorum verifier is implemented.
- Run `uv run altk audit-public --strict` before publishing any fork or release.

## Stage 1: Trace And Extraction Layer

- Implement trace capture contracts with explicit logged and unlogged variables.
- Add extraction pipeline records: segmentation, candidate mining,
  canonicalization, ablation design, leakage check, typed dependency graph,
  minimal interface, verifier binding, and search status.
- Add token grammar validators for instruction templates, patch patterns,
  theorem tactics, evaluator harnesses, and workflow policies.

## Stage 2: Measurement And Bounds

- Implement opportunity-measure constructors for static, replay, rolling
  production, and closed-loop policy-induced measures.
- Add baseline selector and baseline-refresh bridge checker.
- Add empirical Bernstein, confidence-sequence, e-value, and post-selection
  correction modules.
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
  diagnostics.
- Add evaluator-root, role-separated-root, quorum, finality, stale-packet, and
  partition-alarm validators.
- Add transport-refresh and opportunity-law refresh bridges that subtract
  declared conservative charges.

## Stage 5: Portfolio, Reproduction, And Recombination

- Add dependency-closed portfolio selection, conflict constraints, dominance
  checks, and behavioral-equivalence quotienting.
- Add gauge compatibility for class-wise capital coordinates.
- Add causal reproduction matrix identification, capacity-capped reproduction,
  recombination tensor confidence sets, residual charges, and phase
  classification.

## Stage 6: CARA Target Claims

- Add ASI target-set parser, capability-basis registry, target-membership
  checker, resource-matched baseline upper-envelope checker, raw-net-capital
  solvency calculator, runtime witness verifier, and time-to-target comparator.
- Keep CARA claims scoped: they are target-valid, baseline-certified,
  raw-net-solvent, viability-qualified time-to-target statements, not
  unconditional intelligence claims.

## Non-Negotiable Invariant

Every module must write through the packet schema and kernel transition. A
scientific module may generate evidence, bounds, or bridge certificates, but it
does not bypass fail-closed admission.
