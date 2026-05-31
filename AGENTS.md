# Agent Instructions

This repository implements the ALT Foundry Kernel bootloader. Preserve the
paper-linked contract: packets are executable records, not informal claims.

## Operating Rules

- Keep packet fields explicit. Do not invent evidence or replace missing cost
  coordinates with zero.
- Preserve fail-closed behavior. Missing capital-relevant fields must reject,
  defer, suspend, or route to exploration.
- Keep proxy-only evidence out of the settlement ledger.
- Keep schemas language-neutral and Python code modular.
- Do not add local paths, credentials, raw private traces, or downloaded paper
  source files.
- Do not run git operations unless explicitly asked.

## Useful Commands

```bash
uv sync --dev
uv run altk validate examples/admission_packet.json
uv run altk decide examples/admission_packet.json --state examples/kernel_state_empty.json
uv run altk audit-public --strict
uv run ruff check .
uv run mypy src
uv run pytest
```

## Repair Order

1. JSON/schema errors.
2. packet-type required fields.
3. dependency closure and dependency availability.
4. mission, baseline, opportunity law, and measurement declarations.
5. evidence status, selection status, trace view, and sample design.
6. signed value/cost/risk/transport bounds.
7. runtime witness, telemetry, transport, hazard, authority, capability, threat.
8. root/quorum, finality, budget, capacity, refresh, rollback, deprecation.
9. raw-net solvency, noncompensable hazard, and viability.
10. CARA target-validity, baseline-envelope, target-membership, viability, and
    time-to-target fields, only when target crossing is claimed.

Missing evidence is undefined, not zero. Use measured evidence, a declared
worst-case charge, a narrowed claim, exploration-only status, or rejection.
