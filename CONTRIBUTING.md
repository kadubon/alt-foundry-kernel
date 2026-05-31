# Contributing

Contributions should preserve the ALT bootloader boundary: this project validates
and routes executable certificate packets. It does not silently certify evidence
that the packet did not provide.

## Development

```bash
uv sync --dev
uv run ruff check .
uv run mypy src
uv run pytest
```

## Design Constraints

- Keep public JSON Schemas language-neutral.
- Keep Python modules small and loosely coupled.
- Add tests for every new transition or predicate.
- Prefer explicit field names over inference.
- Preserve fail-closed semantics for missing or malformed evidence.
- Keep documentation linked to the paper DOI:
  [10.5281/zenodo.20476200](https://doi.org/10.5281/zenodo.20476200)

## Pull Requests

Explain which packet field, predicate, or lifecycle transition changed. Include
example packets when a public interface changes.
