---
name: collective-reuse
description: Form and check bounded receiver-qualified ALT reuse proposals without granting settlement or execution authority.
---

Read `docs/collective-reuse.md`, `docs/reuse-interchange.md` and repository `AGENTS.md`.
Use the installed `altk reuse` command group or typed `alt_foundry_kernel.reuse` API.
Start with `altk reuse example` to inspect synthetic inputs and decisions.

1. Register immutable sources, training cutoff, grammar, attempt costs and receiver scope.
2. Run `form`; reconstruct the candidate against the original request.
3. Run `qualify` with source-bound checks for the exact receiver/input/evaluator.
4. Register costs, matched service alternatives, resources and joint scenarios.
5. Run `plan`, `check-plan` and `compare`; incomplete search cannot prove superiority.
6. Read-only operations do not create storage. Explicit `ingest` requires an expected revision.
7. Replay new evidence and carry forward costs before replanning. Export only supported
   native mappings; retain unmapped obligations and host admission as unresolved.

Model results are not empirical receipts. Do not construct settlement-grade legacy
packets from these examples. Do not run token text, grant leases or modify companions.
The host must serialize local writers; CCR owns concurrent admission and execution.
