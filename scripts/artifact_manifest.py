"""Inspect archives and bind the one release build to its exact commit and file hashes."""

import hashlib
import json
import os
import subprocess
import tarfile
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
dist = root / "dist"
artifacts = sorted([*dist.glob("*.whl"), *dist.glob("*.tar.gz")])
assert len(artifacts) == 2, "One wheel and one sdist required"
for artifact in artifacts:
    if artifact.suffix == ".whl":
        with zipfile.ZipFile(artifact) as archive:
            names = archive.namelist()
    else:
        with tarfile.open(artifact) as archive:
            names = archive.getnames()
    assert any(name.endswith("reuse/formation.py") for name in names)
    assert any(name.endswith("reuse/contract.schema.json") for name in names)
    assert any(name.endswith("companions/manifest.json") for name in names)
    assert all(not Path(name).is_absolute() and ".." not in Path(name).parts for name in names)
    assert not any(
        part in {".git", ".venv", ".hypothesis", "__pycache__"}
        for name in names
        for part in Path(name).parts
    )
hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in artifacts}
commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
manifest = {
    "package": "alt-foundry-kernel",
    "version": "0.5.0",
    "commit": commit,
    "workflow_run": os.environ.get("GITHUB_RUN_ID"),
    "artifacts": dict(hashes),
    "source_dirty": bool(
        subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True).strip()
    ),
    "required_install_matrix": ["Linux 3.11/3.14", "Windows 3.11/3.14", "macOS 3.11/3.14"],
    "companion_versions": {"CCR": "1.8.0", "VEK": "1.3.0", "CAIT": "0.2.0"},
    "status": "build-record; consult qualifying workflow for installation results",
    "classification": "Alpha",
    "pypi": "NOT_REQUESTED",
    "empirical_acceleration": None,
}
path = dist / "validation-manifest.json"
path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
(dist / "SHA256SUMS").write_text(
    "".join(f"{value}  {name}\n" for name, value in hashes.items()), encoding="utf-8", newline="\n"
)
print(json.dumps(manifest, indent=2))
