"""Seven selected implementation faults; count only semantic assertion failures."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cases = [
    (
        "duplicate-credit",
        "lifecycle.py",
        "stock.add(event.artifact)",
        "stock.add(event.artifact); stock.add(event.id)",
        "test_reuse_history.py::test_unique_uses_stock_and_source_round_trip",
    ),
    (
        "omitted-formation-cost",
        "planning.py",
        "cost_ids.update(option.costs)",
        'cost_ids.update(name for name in option.costs if name != "formation")',
        "test_reuse.py::test_matched_break_even",
    ),
    (
        "wrong-receiver",
        "qualification.py",
        '            "receiver",\n',
        "",
        "test_reuse.py::test_receiver_cannot_inherit_a",
    ),
    (
        "expired-qualification",
        "planning.py",
        "if qualification.offer.valid_until <= contract.checkpoint + option.end:",
        "if False:",
        "test_reuse_guards.py::test_independent_checker_rejects_infeasible_changes",
    ),
    (
        "overlap",
        "planning.py",
        "if len(providers) > 1:",
        "if len(providers) > 999:",
        "test_reuse_guards.py::test_overlap_and_and_bundle_are_joint",
    ),
    (
        "incomplete-comparator",
        "planning.py",
        "complete=expanded == 2 ** len(options),",
        "complete=True,",
        "test_reuse.py::test_joint_capacity_and_incomplete_search",
    ),
    (
        "synthetic-authority-promotion",
        "checker.py",
        "    Plan.model_validate(plan.model_dump())\n",
        "",
        "test_reuse_guards.py::test_checker_does_not_authenticate_search_or_settlement",
    ),
]
scratch = Path(tempfile.mkdtemp(prefix="alt-faults-"))
for name in ("src", "tests", "examples", "conformance"):
    shutil.copytree(root / name, scratch / name, ignore=shutil.ignore_patterns("__pycache__"))
results = []
for name, filename, before, after, test in cases:
    path = scratch / "src/alt_foundry_kernel/reuse" / filename
    source = path.read_text(encoding="utf-8")
    assert source.count(before) == 1, (name, "fault anchor changed")
    path.write_text(source.replace(before, after), encoding="utf-8", newline="\n")
    environment = dict(os.environ, PYTHONPATH=str(scratch / "src"), PYTHONDONTWRITEBYTECODE="1")
    run = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--no-cov", str(scratch / "tests" / test)],
        cwd=scratch,
        env=environment,
        capture_output=True,
        text=True,
        timeout=60,
    )
    killed = run.returncode == 1 and (
        "AssertionError" in run.stdout or "DID NOT RAISE" in run.stdout
    )
    results.append({"fault": name, "semantic_assertion_failed": killed})
    path.write_text(source, encoding="utf-8", newline="\n")
print(json.dumps({"selected_faults": results, "complete_mutation_score": None}, indent=2))
if not all(row["semantic_assertion_failed"] for row in results):
    raise SystemExit("Selected fault survived or failed without a semantic assertion")
