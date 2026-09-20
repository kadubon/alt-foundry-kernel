"""Install tested/downloaded bytes outside checkout and exercise them without sockets."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("dist", type=Path)
parser.add_argument("--python", default="3.13")
parser.add_argument("--sdist", action="store_true")
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
dist = args.dist.resolve()
manifest = json.loads((dist / "validation-manifest.json").read_text(encoding="utf-8"))
for line in (dist / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
    expected, name = line.split("  ", 1)
    if Path(name).name != name:
        raise ValueError("invalid manifest path")
    assert hashlib.sha256((dist / name).read_bytes()).hexdigest() == expected
for name, expected in manifest["artifacts"].items():
    assert hashlib.sha256((dist / name).read_bytes()).hexdigest() == expected
scratch = Path(tempfile.mkdtemp(prefix="alt-installed-"))
env = scratch / "env"
subprocess.run(["uv", "venv", "--python", args.python, str(env)], check=True)
python = env / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
artifact = next(dist.glob("*.tar.gz" if args.sdist else "*.whl"))
subprocess.run(
    [
        "uv",
        "pip",
        "install",
        "--python",
        str(python),
        "--index-url",
        "https://pypi.org/simple",
        str(artifact),
        "cait-certificate-schema==0.2.0",
        "verification-ecology-kit==1.3.0",
        "https://github.com/kadubon/collective-capability-runtime/releases/download/v1.8.0/"
        "collective_capability_runtime-1.8.0-py3-none-any.whl"
        "#sha256=97b2f3dc1f675c78246c362d211b71452b721b001e25dd2711263f34874f8b25",
    ],
    cwd=scratch,
    check=True,
)
subprocess.run(["uv", "pip", "check", "--python", str(python)], cwd=scratch, check=True)
result = subprocess.run(
    [str(python), "-I", "-m", "alt_foundry_kernel.reuse.installed_check"],
    cwd=scratch,
    capture_output=True,
    text=True,
    check=True,
)
report = json.loads(result.stdout)
assert report["package_version"] == manifest["version"]
assert str(env.resolve()) in str(Path(report["import_origin"]).resolve())
report.update(
    artifact=artifact.name,
    artifact_sha256=hashlib.sha256(artifact.read_bytes()).hexdigest(),
    commit=manifest["commit"],
    fresh_environment=str(env),
)
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"artifact": artifact.name, "status": "verified", "commit": manifest["commit"]}))
