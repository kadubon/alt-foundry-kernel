# ALT Foundry Kernel

When is a checked procedure worth reusing instead of solving the task again?
ALT Foundry Kernel provides a legacy packet/certificate kernel and a separate,
experimental finite receiver-qualified reuse profile for that question. ALT expands
to **Abstraction Liquidity Theory**. The software checks declared evidence and
costs; it does not manufacture scientific validity, settlement or execution authority.

Current source and [GitHub release](https://github.com/kadubon/alt-foundry-kernel/releases/tag/v0.5.0):
**0.5.0**, Python 3.11+, Apache-2.0. Package maturity remains **Alpha**.
The legacy v0.4.0 wire/API surface remains available. The v0.5.0 reuse profile is
opt-in; a newer package version does not replace legacy schema identities.
The verified distribution route is the GitHub wheel, not an ALT PyPI release.

Start with [installation](#install), then choose the
[finite reuse contract](docs/collective-reuse.md) or
[legacy language-neutral contract](docs/language-neutral-contract.md).
For theory, see Takahashi (2026), *Abstraction Liquidity Theory*,
[DOI 10.5281/zenodo.20476200](https://doi.org/10.5281/zenodo.20476200).

## v0.5.0: experimental collective reuse

The additive Alpha profile forms bounded typed candidates from immutable sources,
qualifies them for named receivers, selects costed reuse portfolios, and replays
local lifecycle evidence. `altk reuse example` demonstrates a shared formation
cost of 12, reuse cost 1, and matched from-scratch cost 5: four uses cost 16 versus
20; adding transfer cost 5 removes the advantage. These are finite model results,
not empirical acceleration evidence or settlement/execution authorization.

See [the installed quickstart and contract](docs/collective-reuse.md),
[version-pinned interoperability](docs/reuse-interchange.md), and
[qualification/publication record](docs/release-v0.5.0.md). Legacy commands,
0.4.0 schema identities and goldens remain unchanged. GitHub Release assets are
the requested distribution channel; ALT PyPI publication is not requested.

## What v0.4.0 Is

`v0.4.0` is the first v1.0.0-equivalent reference surface: a packet kernel,
certificate validators, raw-data estimator helpers, language-neutral schemas,
examples, conformance fixtures, and public-release audit in one repository. It
is still scientifically bounded: estimators compute generic certificates from
declared data, but the kernel does not fabricate causal identification,
transportability, root authority, recombination evidence, or ASI target
realization.

The public contract is language-neutral:

- `schemas/` defines wire formats for packets, kernel state, ledgers,
  dashboards, module certificates, estimator artifacts, robust transport,
  finality/PoUA, certificate composition, extended CARA, and conformance
  results.
- `examples/` gives valid packet, certificate, and estimator-input examples.
- `conformance/` gives deterministic golden transcripts and negative fixtures
  for non-Python implementations.
- `src/alt_foundry_kernel/` is the Python reference implementation.
- `docs/` maps theory objects and non-reduction results to modules, validators,
  schemas, and known limits.

## Start Here For Agents

Choose a profile before supplying evidence. New reuse accepts source-bound finite
`Formation`, `Offer`, `Contract` and `Journal` records from [schemas/reuse](schemas/reuse/).
Legacy packets use [packet schemas](schemas/) and preserve their existing numeric
and declaration semantics. A legacy `status=valid` does not satisfy source replay.

Machine readers should use the [language-neutral contract](docs/language-neutral-contract.md)
for predicate/issue meanings and L0–L5 conformance, the
[schema contract](docs/schema-contract.md), and the
[implementation map](docs/theory-to-module-matrix.md). Missing evidence is undefined,
not zero; rejection, deferral and unresolved work must remain visible.

## Install

Download `alt_foundry_kernel-0.5.0-py3-none-any.whl` and `SHA256SUMS` from the
[0.5.0 release](https://github.com/kadubon/alt-foundry-kernel/releases/tag/v0.5.0).
Verify the wheel against its checksum entry before installing it into an isolated
Python environment. From the download directory, with that environment active
(POSIX shell or PowerShell):

```sh
python -m pip install ./alt_foundry_kernel-0.5.0-py3-none-any.whl
altk --help
```

Installation may fetch dependencies. Base use does not need any companion project.
For source development instead, run `uv sync --dev` from the checkout root and use
`uv run altk`. `uv run` may install dependencies if the environment is not prepared.
Optional native checks use the exact pairs in [reuse interchange](docs/reuse-interchange.md);
they are not required for the minimal offline path.

## CLI Surface

After installation, this finite synthetic example computes a report to stdout;
it does not ingest a journal, contact a model, dispatch work or settle capital:

```sh
altk reuse example
```

Inspect the reported model comparisons and failures, not just process completion.
The declared 12/1/5 costs above are neither GPU/token measurements nor monetary savings.
Commands here are source-checked, not newly execution-verified by this documentation update.

The [reuse command/API contract](docs/collective-reuse.md) covers `form`, `qualify`,
`plan`, `check-plan`, `compare`, `ingest` and `replay` with actual argument names.
Calculations are read-only unless a named `--out` file is requested. `ingest` is an
explicit journal write requiring the expected digest; the host serializes writers.
Independent plan checking establishes feasibility/score, not global optimality;
incomplete comparison search establishes no superiority claim.

For legacy validation, from a prepared source checkout root:

```sh
uv run altk validate examples/admission_packet.json
```

This reads an existing synthetic fixture and emits validation output. Installed
users should not assume repository-relative `examples/` paths exist in their cwd.
Full certificate/estimator families are documented in the
[language-neutral contract](docs/language-neutral-contract.md) and
[estimator contract](docs/estimator-contract.md).

## Python API

The following is the **legacy v0.4.0 API surface**, retained in 0.5.0. Its floating
values and declared `status` flags are not new-profile source-replay qualifications.
The final call reads the complete existing synthetic packet from a source checkout
root; it computes a transition in memory, not external execution permission.

```python
from alt_foundry_kernel import (
    KernelState,
    compute_signed_bounds,
    run_kernel_transition,
    validate_certificate_composition,
    validate_non_reduction_audit,
)

signed = compute_signed_bounds(
    {
        "value_lower_bound": 12.0,
        "cost_upper_bound": 3.0,
        "risk_upper_bound": 1.0,
        "transport_upper_bound": 1.0,
    }
)
assert signed.lower_bound == 7.0

non_reduction = validate_non_reduction_audit(
    {
        "liquidity_claim": {"status": "explicit"},
        "measurement": {"status": "valid"},
        "signed_surplus": {"status": "valid"},
        "transport": {"status": "valid"},
        "hazard": {"status": "bounded"},
        "authority": {"status": "valid"},
        "lifecycle": {"status": "valid"},
        "finality": {"status": "finalized"},
        "capital_effect": {"claims_settlement": False},
        "shortcuts": [{"name": "compression", "used_as_certification": False}],
    }
)
assert non_reduction.ok

import json
from pathlib import Path

packet = json.loads(Path("examples/admission_packet.json").read_text(encoding="utf-8"))
result = run_kernel_transition(KernelState(), packet)
```

## Implemented Modules

The [theory-to-module matrix](docs/theory-to-module-matrix.md) distinguishes
implemented modules, validators, schemas and deferred scientific obligations.
The [language-neutral reference](docs/language-neutral-contract.md) retains the
certificate inventories and conformance levels; the [estimator contract](docs/estimator-contract.md)
defines raw-data input/output reports. These references do not upgrade supplied
causal, transport or authority declarations into independently established facts.

## Scientific Limits

This repository verifies declared artifacts. It does not turn weak evidence into
capital. The following remain outside automatic certification unless supplied as
typed evidence-bearing certificates:

- causal effect identification and off-policy validity;
- mission-valid value bridges and proxy-to-gold calibration;
- transportability, robust transport, and causal invariance;
- evaluator-root soundness beyond declared hierarchy, quorum, and finality
  records;
- proof-of-useful-abstraction weighting as epistemic authority;
- dynamic hazard estimation and irreversible-loss modeling;
- reproduction-matrix identification and recombination tensor estimation;
- portfolio optimality beyond declared conflict and breadth constraints;
- capability-basis target membership;
- ASI target realization or viability-controlled acceleration.

## Non-Python Implementers

A compatible implementation in another language should:

- consume every schema in `schemas/`;
- preserve packet type, lifecycle, decision, predicate, and ledger names;
- reproduce signed-bound arithmetic and raw-net capital gates;
- keep proxy-only and failed evidence out of settlement capital;
- reject missing capital-relevant evidence instead of defaulting it to zero;
- emit compatible validation reports, certificate reports, transitions,
  dashboards, conformance results, and public-audit results;
- replay `conformance/` fixtures deterministically at the claimed level;
- implement negative fixtures as hard failures, not warnings.
- match estimator report shape and fail-closed behavior for `examples/estimators/`
  if claiming v0.4.0 L5 conformance.

See [docs/language-neutral-contract.md](docs/language-neutral-contract.md) for
L0-L5 conformance levels and report shapes.

## Repository Map

- `schemas/`: language-neutral JSON Schemas.
- `examples/`: packet and certificate examples.
- `examples/estimators/`: declared estimator inputs for certificate builders.
- `conformance/`: golden deterministic transcripts and negative fixtures.
- `src/alt_foundry_kernel/`: Python reference implementation.
- [docs/theory-map.md](docs/theory-map.md): paper object to implementation map.
- [docs/theory-to-module-matrix.md](docs/theory-to-module-matrix.md): theorem/proposition-class coverage.
- [docs/schema-contract.md](docs/schema-contract.md): field dictionary and packet contract.
- [docs/language-neutral-contract.md](docs/language-neutral-contract.md): non-Python conformance.
- [docs/estimator-contract.md](docs/estimator-contract.md): estimator input/output contracts.
- [docs/non-reduction-and-mechanism.md](docs/non-reduction-and-mechanism.md): non-reduction and mechanism guards.
- [docs/evaluator-finality-and-poua.md](docs/evaluator-finality-and-poua.md): evaluator hierarchy, roots, quorum, finality, PoUA.
- [docs/sequential-transport-and-control.md](docs/sequential-transport-and-control.md): sequential evidence, robust transport, foundry control.
- [docs/agent-bootloader.md](docs/agent-bootloader.md): trace-to-token workflow.
- [docs/full-implementation-roadmap.md](docs/full-implementation-roadmap.md): path beyond this release.
- [docs/theory-alignment-audit.md](docs/theory-alignment-audit.md): implemented, approximate, deferred, not certified.
- [docs/pre-release-audit.md](docs/pre-release-audit.md): reproducible public audit checklist.

## Verification

Contributor checks below require a prepared source checkout; they are not installation steps.

```bash
uv run ruff check .
uv run mypy src
uv run pytest --cov=alt_foundry_kernel
uv run pip-audit
uv run altk conformance --fixtures conformance --level L5
uv run altk audit-public --strict
```

Validate bundled packet examples on POSIX shells:

```bash
for f in examples/*_packet.json; do uv run altk validate "$f"; done
```

On Windows PowerShell:

```powershell
Get-ChildItem examples\*_packet.json | ForEach-Object { uv run altk validate $_.FullName }
```

## Citation

Use `CITATION.cff`. If citing the theory, cite:

Takahashi, K. (2026). *Abstraction Liquidity Theory*. Zenodo.
[https://doi.org/10.5281/zenodo.20476200](https://doi.org/10.5281/zenodo.20476200)

## License

Apache License 2.0.

## Research navigation

For related theory and neighboring tools, use the
[Collective Intelligence Research and OSS Index](https://kadubon.github.io/github.io/collective-intelligence-index.html),
especially [reuse versus scratch](https://kadubon.github.io/github.io/collective-intelligence-index.html#problem-reuse)
and [distribution shift](https://kadubon.github.io/github.io/collective-intelligence-index.html#problem-distribution-shift).
The index is a discovery map; versioned contracts and host admission remain authoritative.
