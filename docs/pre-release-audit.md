# Pre-Release Audit

Paper DOI: [https://doi.org/10.5281/zenodo.20476200](https://doi.org/10.5281/zenodo.20476200)

This repository is intended to be published as an Apache-2.0 OSS reference
kernel and language-neutral implementation surface for Abstraction Liquidity
Theory. Before publication, run this audit from the repository root.

## Required Commands

```bash
uv run ruff check .
uv run mypy src
uv run pytest --cov=alt_foundry_kernel
uv run pip-audit
uv run altk conformance --fixtures conformance --level L5
uv run altk audit-public --strict
```

Validate every example packet:

```bash
for f in examples/*_packet.json; do uv run altk validate "$f"; done
```

On Windows PowerShell:

```powershell
Get-ChildItem examples\*_packet.json | ForEach-Object { uv run altk validate $_.FullName }
```

Certify every module example:

```bash
uv run altk certify measurement examples/certificates/measurement_spec.json
uv run altk certify causal examples/certificates/causal_certificate.json
uv run altk certify transport examples/certificates/transport_certificate.json
uv run altk certify risk examples/certificates/risk_ledger.json
uv run altk certify authority examples/certificates/authority_certificate.json
uv run altk certify root-finality examples/certificates/root_finality_record.json
uv run altk certify reproduction examples/certificates/reproduction_record.json
uv run altk certify non-reduction examples/certificates/non_reduction_audit.json
uv run altk certify mechanism examples/certificates/mechanism_certificate.json
uv run altk certify evaluator examples/certificates/evaluator_hierarchy.json
uv run altk certify finality examples/certificates/finality_poua_ledger.json
uv run altk certify sequential examples/certificates/sequential_decision.json
uv run altk certify transport-ext examples/certificates/transport_robustness.json
uv run altk certify certificate-algebra examples/certificates/certificate_composition.json
uv run altk certify portfolio-ext examples/certificates/portfolio_constraints.json
uv run altk certify foundry-control examples/certificates/foundry_control_state.json
uv run altk certify cara-ext examples/certificates/cara_process.json
```

## What `altk audit-public --strict` Checks

- `README.ja.md` is absent.
- Public docs link to the paper DOI.
- `CITATION.cff` cites the paper DOI.
- No downloaded paper source is present.
- No local workstation paths are present.
- No `.env*` file is present.
- No obvious private-key, API-key, or cloud-secret assignment is present.
- No placeholder publishing URLs are present.
- All JSON Schemas are valid and local `$ref` links resolve.
- Every `examples/*_packet.json` validates through JSON Schema, the Python
  `Packet` model, and ALT semantic validation.
- Every `examples/certificates/*.json` validates through its JSON Schema and
  module-level certificate checker.
- Every `conformance/*.json` transcript replays deterministically or, for
  certificate fixtures, produces the declared expected result.
- Local caches and virtual environments are excluded from content scanning and
  reported only as cleanup warnings.

## Manual Checks

- Confirm no git operation has been performed unless explicitly requested.
- Confirm the TeX paper source is not bundled.
- Confirm the project metadata contains no fake repository URL.
- Confirm `README.md` describes the reference kernel accurately and does not claim
  full causal, transport, recombination, finality, or CARA certification.
- Confirm `docs/language-neutral-contract.md` is present and linked from the
  README for non-Python implementers.
- Confirm bridge and kernel-update packets are described as audit-only in
  v0.3.0.
- Confirm resurrection does not add capital without admission-grade current
  evidence.
- Confirm non-reduction shortcuts, self-certification, evaluator cycles, naive
  certificate composition, transport radius failures, and CARA target failures
  are represented as hard negative conformance fixtures.

## Cleanup Before Packaging

Remove local generated artifacts before creating a source archive:

```powershell
Remove-Item -Recurse -Force .venv,.mypy_cache,.pytest_cache,.ruff_cache -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
```

Only run cleanup from the repository root after confirming the current path is
the project directory.
