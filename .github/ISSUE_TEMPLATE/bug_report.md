---
name: Bug report
about: Report parser, schema, validation, or fail-closed transition behavior
title: ""
labels: bug
assignees: ""
---

## Summary

Describe the observed behavior and the expected ALT bootloader behavior.

## Reproduction

```bash
uv run altk validate <packet.json>
uv run altk decide <packet.json> --state <state.json>
```

## Packet Type

candidate, admission, transport-refresh, monitor-alarm, deprecation, rollback,
resurrection, bridge, or kernel-update.

## Notes

Do not include credentials, private traces, local paths, or downloaded paper
source.
