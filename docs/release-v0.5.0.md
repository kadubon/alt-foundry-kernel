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

## Verified public delivery

[PR #1](https://github.com/kadubon/alt-foundry-kernel/pull/1) was merged through the
normal merge API, without an administrator bypass. The annotated `v0.5.0` tag peels
to `cdb5c7d845364f0bec42ebe5e865871b2bde2e91`. Its source tree matches the checked PR
head. The public [GitHub Release](https://github.com/kadubon/alt-foundry-kernel/releases/tag/v0.5.0)
was published on 2026-09-20 after all of these runs passed:

- [Merged source CI, 35488945874](https://github.com/kadubon/alt-foundry-kernel/actions/runs/35488945874):
  191 tests on each Python 3.11–3.14 job, retained gates and all seven selected faults detected.
- [Distribution qualification, 35488945936](https://github.com/kadubon/alt-foundry-kernel/actions/runs/35488945936):
  six wheel installations and the sdist installation described above.
- [Tag CI, 35489094085](https://github.com/kadubon/alt-foundry-kernel/actions/runs/35489094085):
  all jobs passed at the same release commit.

The final Python 3.13 source run measured 97.24% statement and 93.91% branch
coverage across every module under `alt_foundry_kernel/reuse`, with no exclusions.
The intentional forged-model test emits one Pydantic serialization warning.

| Public artifact | SHA-256 |
| --- | --- |
| `alt_foundry_kernel-0.5.0-py3-none-any.whl` | `cd6755db6d97f978300d978695dc70c19d64fdd11c58e0c6dc4c1fcb7db9f487` |
| `alt_foundry_kernel-0.5.0.tar.gz` | `2da03b30e278c6cd824a045eb8e5ea382d1941b5500340bc88d6336c6a618785` |

Both distributions, `validation-manifest.json`, `qualification-manifest.json` and
`SHA256SUMS` were downloaded from unauthenticated public GitHub URLs after
publication and matched the prepublication qualified bytes. The wheel and sdist
were then installed separately into fresh Windows/Python 3.13.3 environments
outside every checkout. Both passed metadata/import-origin checks, the installed
`altk` entry-point check, literal `pip check`, five legacy/new CLI calls, all 17 L5
cases, break-even/transfer/capacity/receiver scenarios, lifecycle replay and actual
pinned CCR/VEK/CAIT checks with runtime sockets blocked. This is verification of
GitHub assets; it is not a public-PyPI installation of ALT.

An additional installed-package check explicitly ingested the synthetic use history
with a failed fourth use and a subsequent scoped expiry. Replanning selected only
`scratch-3`, and the independent plan checker accepted the history-bound contract.
Withdrawal then removed all current eligibility while retaining one historical
stock item, three successful uses and every recorded cost. This passed against
both public wheel and public sdist installations, outside the checkout with sockets
blocked.

The attached qualification manifest records prepublication CI and deliberately
does not predict this later public download result. This document and the Release
notes record that subsequent result; the already published assets remain unchanged.

| Deliverable | Status |
| --- | --- |
| A1–A4 implementation | IMPLEMENTED |
| Local tests and checks | LOCAL_CHECKS passed |
| Required existing quality gates and added CI | REQUIRED_CI passed |
| Feature branch | BRANCH_PUSHED |
| Implementation PR | PR_OPENED, MERGED |
| Canonical documentation | DOCS_UPDATED |
| Existing Wiki | NOT_APPLICABLE |
| Annotated version tag | TAG_PUSHED |
| Public Release | GITHUB_RELEASED |
| Public asset fresh installation | PUBLIC_GITHUB_ASSET_INSTALL_VERIFIED |
| PyPI/TestPyPI and deployment | NOT_REQUESTED |

No external empirical collective-intelligence acceleration experiment was
performed. Finite synthetic results do not establish causal abstraction value,
authenticated real-world observations without external trust material, AGI/ASI,
universal transferability, indefinite growth or execution authority. Supported
native mappings and their remaining host-admission, source-authentication and
partial-conversion boundaries are detailed in [reuse-interchange.md](reuse-interchange.md).
