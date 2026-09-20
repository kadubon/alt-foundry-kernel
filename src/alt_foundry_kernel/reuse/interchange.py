"""Version-pinned local JSON interchange. No network, leases or external writes."""

from __future__ import annotations

import hashlib
from fractions import Fraction
from importlib.resources import files
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry

from .checker import check_plan
from .contracts import Contract, Plan
from .premises import identity
from .wire import digest, loads


def pinned(name: str) -> Any:
    root = files("alt_foundry_kernel.reuse").joinpath("fixtures", "companions")
    manifest = loads(root.joinpath("manifest.json").read_text(encoding="utf-8"))
    record = next((row for row in manifest if row["file"] == name), None)
    if record is None:
        raise ValueError("unknown pinned resource")
    raw = root.joinpath(name).read_bytes()
    if hashlib.sha256(raw).hexdigest() != record["sha256"]:
        raise ValueError("pinned resource altered")
    return loads(raw.decode("utf-8"))


def validate_native(schema_name: str, value: Any) -> None:
    Draft202012Validator(pinned(schema_name), registry=Registry()).validate(value)


def import_vek(
    report: dict[str, Any], scope: str, revision: int, time_origin: str, slot_seconds: str
) -> dict[str, Any]:
    validate_native("vek-capacity-report.schema.json", report)
    if (
        report["producer_version"] != "1.3.0"
        or report["scope"] != scope
        or (
            report["snapshot_revision"] != revision
            or report["time_origin"] != time_origin
            or Fraction(report["slot_seconds"]) != Fraction(slot_seconds)
        )
    ):
        raise ValueError("VEK version, scope, revision or clock mismatch")
    if (
        report["service_guaranteed_lower_envelope"] is not None
        or report["observed_service"] is not None
    ):
        raise ValueError("unsupported empirical or guaranteed service")
    work = report["work"]
    accounting = report["local_accounting"]
    if len({item["work_id"] for item in work}) != len(work) or (
        accounting["completed"] + accounting["unfinished"] != len(work)
    ):
        raise ValueError("VEK workload conservation")
    return {
        "version": "alt_reuse_vek_import_v1",
        "source_digest": digest(report),
        "native_report": report,
        "counters_replayed": False,
        "remaining_work": accounting["unfinished"],
        "guaranteed_rate": None,
        "host_admission": None,
        "execution_authority": None,
    }


def ccr_tasks(contract: Contract, plan: Plan, created_at: str, revision: str) -> dict[str, Any]:
    check_plan(contract, plan)
    tasks = []
    options = {item.id: item for item in contract.options}
    for name in plan.selected:
        item = options[name]
        task = pinned("ccr-task.json")
        task.update(
            task_id="alt." + name,
            created_at=created_at,
            title="Review ALT " + item.kind + " proposal",
            objective="Check immutable receiver/source bindings and full lifecycle costs.",
        )
        task["inputs"] = [
            {
                "kind": "artifact",
                "ref": "sha256:" + identity(contract),
                "required": True,
                "notes": "Reference grants no permission to fetch.",
            }
        ]
        task["pic_interop"]["enabled"] = False
        task["pic_interop"]["recommended_pic_commands"] = []
        task["verifier_plan"] = {
            "required_verifiers": ["alt-reuse-host-adapter"],
            "optional_verifiers": [],
            "failure_route": "residual",
            "promotion_gate": "custom",
        }
        task["expected_outputs"] = [
            {
                "kind": "json",
                "destination": "review/alt",
                "schema_ref": "urn:alt:reuse:plan:v1",
                "acceptance_criteria": [
                    "Reconstruct source qualification for the exact receiver, input and evaluator.",
                    "Independently check costs, prerequisites, capacity and original revision.",
                    "Keep host admission unresolved until the custom adapter is registered.",
                ],
            }
        ]
        task["extensions"] = {
            "x_alt_reuse": {
                "version": "alt_reuse_ccr_sidecar_v1",
                "contract_digest": identity(contract),
                "plan_digest": digest(plan),
                "original_revision": revision,
                "option": item.model_dump(),
                "costs": [cost.model_dump() for cost in contract.costs if cost.id in item.costs],
                "qualification": next(
                    (q.model_dump() for q in contract.qualifications if q.id == item.offer), None
                ),
                "host_admission": None,
                "execution_authority": None,
            }
        }
        validate_native("ccr-task.schema.json", task)
        tasks.append(task)
    return {
        "version": "alt_reuse_ccr_export_v1",
        "tasks": tasks,
        "legacy_token": None,
        "missing_admission": ["CCR 1.8.0 importer pins ALT 0.4.0; new sidecar needs host adapter"],
        "writes": False,
        "settlement": None,
        "execution_authority": None,
    }


def vek_demand(contract: Contract, plan: Plan) -> dict[str, Any]:
    """Complete finite check-demand mapping; synthetic residual registration remains local."""
    check_plan(contract, plan)
    names = [*plan.selected, "calibration", "counter-check"]
    if len(names) > 12 or Fraction(contract.slot_seconds).denominator > 1000000:
        raise ValueError("VEK finite mapping bound")
    # One registered check per selected option plus calibration and independent counter-check.
    # Demand duration is separately registered here, never inferred from average throughput.
    horizon = len(names)
    work, actions = [], []
    for name in names:
        work.append(
            {
                "work_id": name,
                "residual_id": "alt-demand-" + name,
                "subject_digest": digest(plan),
                "input_digest": identity(contract),
                "rule_version": "alt-reuse-check-v1",
                "check": "reconstruct",
                "domain": "alt-reuse",
                "bundle": "alt",
                "arrival": 0,
                "deadline": horizon,
                "protected": True,
                "required": True,
                "predecessors": [],
                "separate_from": [],
            }
        )
        actions.append(
            {
                "action_id": name,
                "work_id": name,
                "service_id": "local-checker",
                "kind": "check",
                "duration": 1,
                "costs": [1, 1],
                "requires_success": [],
                "requires_negative": [],
            }
        )
    native = {
        "schema_version": "vek.capacity.contract.v1",
        "contract_id": "alt-" + digest(plan)[:16],
        "scope": contract.scope,
        "time_origin": contract.time_origin,
        "slot_seconds": contract.slot_seconds,
        "horizon": horizon,
        "max_candidates": 10000,
        "max_events": 256,
        "semantics": "nonpreemptive-integer-slots",
        "work_unit": "registered-check",
        "observation_policy": "replan-after-admitted-result",
        "resources": [
            {
                "resource_id": "reviewer",
                "unit": "reviewer-slot",
                "kind": "pool",
                "capacity": [1] * horizon,
            },
            {
                "resource_id": "budget",
                "unit": "check-work",
                "kind": "budget",
                "capacity": [horizon],
            },
        ],
        "services": [
            {
                "service_id": "local-checker",
                "version": "1",
                "domain": "alt-reuse",
                "checks": ["reconstruct"],
                "interface": "inert-json-v1",
                "valid_until": horizon,
                "exposures": ["synthetic-local"],
                "dependence_known": False,
                "support_refs": [identity(contract)],
                "assumptions": ["finite synthetic checks"],
                "evidence_basis": "synthetic",
            }
        ],
        "work": work,
        "actions": actions,
        "scenarios": [
            {
                "scenario_id": "declared",
                "outcomes": ["positive"] * horizon,
                "assumption": "declared check completion",
            }
        ],
    }
    validate_native("vek-capacity-contract.schema.json", native)
    return {
        "version": "alt_reuse_vek_demand_v1",
        "native_contract": native,
        "schedule": {name: i for i, name in enumerate(names)},
        "host_residual_registration": None,
        "observed_service": None,
        "source_digest": identity(contract),
        "execution_authority": None,
    }
