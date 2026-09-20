"""Generate or check the closed language-neutral opt-in schemas."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from alt_foundry_kernel.reuse.contracts import Contract, Plan, Qualification
from alt_foundry_kernel.reuse.formation import Candidate, Formation, Trace
from alt_foundry_kernel.reuse.lifecycle import Event, Journal
from alt_foundry_kernel.reuse.qualification import Adapter, Check, Offer

ROOT = Path(__file__).resolve().parents[1] / "schemas" / "reuse"
MODELS = {
    "formation": Formation,
    "candidate": Candidate,
    "trace": Trace,
    "qualification": Qualification,
    "offer": Offer,
    "check": Check,
    "adapter": Adapter,
    "contract": Contract,
    "plan": Plan,
    "event": Event,
    "journal": Journal,
}


def main() -> None:
    for name, model in MODELS.items():
        schema = model.model_json_schema()
        schema.update(
            {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "$id": f"urn:alt:reuse:{name}:v1",
            }
        )
        raw = json.dumps(schema, indent=2, sort_keys=True) + "\n"
        path = ROOT / (name + ".schema.json")
        if "--check" in sys.argv:
            if not path.exists() or path.read_text(encoding="utf-8") != raw:
                raise ValueError("generated schema drift: " + name)
        else:
            ROOT.mkdir(parents=True, exist_ok=True)
            path.write_text(raw, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
