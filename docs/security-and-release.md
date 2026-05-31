# Security And Release Notes

Paper DOI: [https://doi.org/10.5281/zenodo.20476200](https://doi.org/10.5281/zenodo.20476200)

ALT Foundry Kernel treats security status as part of packet admission. A token
with positive measured value is not settlement-grade if it expands authority,
changes the evaluator, hides resources, or bypasses telemetry outside the
declared envelope.

## Public Surface Rules

- Do not commit credentials, local state, private datasets, or raw traces with
  identifying content.
- Do not include local machine paths in examples, docs, schemas, or tests.
- Do not include downloaded paper source files. Link to the DOI instead.
- Keep `.env` files, caches, coverage, builds, and local scratch files outside
  the public surface.
- Treat generated packets as data artifacts; review them before publication.

## Release Checklist

Before publishing a release:

```bash
uv sync --dev
uv run ruff check .
uv run mypy src
uv run pytest
uv run pip-audit
uv run altk audit-public --strict
```

Also validate examples:

```bash
uv run altk validate examples/candidate_packet.json
uv run altk validate examples/proxy_only_packet.json
uv run altk validate examples/admission_packet.json
uv run altk validate examples/deprecation_packet.json
uv run altk validate examples/transport_refresh_packet.json
uv run altk validate examples/monitor_alarm_packet.json
uv run altk validate examples/rollback_packet.json
uv run altk validate examples/resurrection_packet.json
uv run altk validate examples/bridge_packet.json
uv run altk validate examples/kernel_update_packet.json
```

`altk audit-public --strict` checks DOI links, schema validity, example packet
validity, local path leakage, `.env*` files, downloaded paper source, obvious
secret assignments, and placeholder publishing URLs. Local virtual environments
and caches are reported as cleanup warnings and excluded from content scanning.

## Reporting Issues

Report parser, schema, or fail-closed behavior issues through the repository's
public issue tracker after the real publishing location is configured. Do not
include credentials or private trace payloads in reports.
