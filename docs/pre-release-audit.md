# Pre-Release Audit

Paper DOI: [https://doi.org/10.5281/zenodo.20476200](https://doi.org/10.5281/zenodo.20476200)

This repository is intended to be published as an Apache-2.0 OSS bootloader for
Abstraction Liquidity Theory. Before publication, run this audit from the
repository root.

## Required Commands

```bash
uv run ruff check .
uv run mypy src
uv run pytest
uv run pip-audit
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
- Local caches and virtual environments are excluded from content scanning and
  reported only as cleanup warnings.

## Manual Checks

- Confirm no git operation has been performed unless explicitly requested.
- Confirm the TeX paper source is not bundled.
- Confirm the project metadata contains no fake repository URL.
- Confirm `README.md` describes the bootloader accurately and does not claim
  full causal, transport, recombination, finality, or CARA certification.
- Confirm `docs/language-neutral-contract.md` is present and linked from the
  README for non-Python implementers.
- Confirm bridge and kernel-update packets are described as audit-only in v1.
- Confirm resurrection does not add capital without admission-grade current
  evidence.

## Cleanup Before Packaging

Remove local generated artifacts before creating a source archive:

```powershell
Remove-Item -Recurse -Force .venv,.mypy_cache,.pytest_cache,.ruff_cache -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
```

Only run cleanup from the repository root after confirming the current path is
the project directory.
