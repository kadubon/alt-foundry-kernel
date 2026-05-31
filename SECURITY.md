# Security Policy

## Supported Versions

The project is pre-1.0. Security fixes target the current mainline release.

## Scope

Security-relevant issues include:

- packet validation accepting missing capital-relevant fields
- proxy-only evidence increasing settlement capital
- schema or parser behavior that permits silent authority expansion
- CLI behavior that writes unexpected files
- examples or docs exposing private traces, credentials, or local machine paths

## Reporting

Use the repository issue tracker for non-sensitive reports. For sensitive
reports, contact the maintainers through the private channel listed by the
repository host.

Do not include credentials, private trace content, or unpublished packet payloads
in public reports.
