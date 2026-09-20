# v0.5.0 qualification and publication record

Theory: https://doi.org/10.5281/zenodo.20476200

This additive Alpha release preserves v0.4.0 packet/schema identities, public
commands, numeric interfaces and conformance goldens. The opt-in collective-reuse
profile is described in [collective-reuse.md](collective-reuse.md).

Before editing, the clean upstream HEAD was
`b5170dbee93b9183f86570c9b2fa325be9cded51`; v0.5.0 was unused. No open PR or active
branch rule was reported. The existing Wiki setting was enabled but its separate
git repository did not exist: Wiki is **NOT_APPLICABLE**, not updated or created.
Only GitHub distribution is requested; PyPI/TestPyPI and deployment are
**NOT_REQUESTED**. No prior waiver applies.

The baseline had 55 passing tests on Windows/Python 3.14. The original lint, types,
examples, dependency audit, L5 conformance and strict public audit are retained.
The development suite currently has 191 tests, including a separate tiny exact
oracle and seven selected implementation faults, all detected by semantic assertions.
The measured new-profile coverage was 97.23% statement and 93.91% branch (96.29%
combined); the final workflow results are authoritative for the release commit.
Additional CI measures every new profile module without exclusions, requiring
95% statement and 90% branch coverage separately, and tests Linux Python 3.11–3.14.
The targeted dependency refresh upgrades cryptography, msgpack and pip to remove
the known vulnerabilities detected during this work. Runtime minimum remains 3.11.

The distribution workflow builds wheel and sdist once for its source commit,
inspects archives, checks metadata and hashes, then tests those same wheel bytes
on Linux, Windows and macOS with Python 3.11 and 3.14. A separate Linux/Python 3.13
job installs from the sdist. These checks use fresh environments outside the
checkout, legacy CLI/fixtures, new scenarios, actual companion parsers/checkers,
package dependency checks and blocked runtime sockets. No workflow uploads to PyPI
or deploys a service. The artifact workflow does not trigger on tags.

`validation-manifest.json` identifies source commit and artifact hashes; its build
record alone does not claim that subsequent checks passed. The qualifying workflow
and publication record must establish that separately. Hashes are integrity checks,
not provenance attestations; no attestation is claimed.

Publication remains pending until required CI, normal-policy merge, annotated tag,
public Release assets and fresh download/install verification are recorded. Do not
interpret this preparation record as a successful public-asset check. Release
completion evidence will identify exact commits, run IDs and downloaded hashes.
