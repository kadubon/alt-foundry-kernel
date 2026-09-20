"""Separate statement/branch gates for every new profile module, without exclusions."""

import json
import sys
from pathlib import Path

report = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
groups = {
    name: row for name, row in report["files"].items() if "/reuse/" in name.replace("\\", "/")
}
if not groups:
    raise SystemExit("No reuse coverage collected")
totals = {
    key: sum(row["summary"][key] for row in groups.values())
    for key in ("num_statements", "covered_lines", "num_branches", "covered_branches")
}
statement = 100 * totals["covered_lines"] / totals["num_statements"]
branch = 100 * totals["covered_branches"] / totals["num_branches"]
combined = (
    100
    * (totals["covered_lines"] + totals["covered_branches"])
    / (totals["num_statements"] + totals["num_branches"])
)
print(
    json.dumps(
        {
            **totals,
            "statement_percent": statement,
            "branch_percent": branch,
            "combined_percent": combined,
        },
        indent=2,
    )
)
if statement < 95 or branch < 90:
    raise SystemExit("New-profile coverage below 95% statement / 90% branch")
