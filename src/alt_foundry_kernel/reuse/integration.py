"""Offline developer integration with exact released companion implementations."""

from __future__ import annotations

from importlib import import_module
from importlib.metadata import version
from typing import Any

from .cait_export import export_cait
from .checker import check_plan
from .examples import contract_example, history_example
from .interchange import ccr_tasks, import_vek, pinned, vek_demand
from .planning import select


def run() -> dict[str, Any]:
    versions = {
        "collective-capability-runtime": "1.8.0",
        "verification-ecology-kit": "1.3.0",
        "cait-certificate-schema": "0.2.0",
    }
    for package, expected in versions.items():
        if version(package) != expected:
            raise ValueError("companion version mismatch: " + package)
    contract = contract_example()
    plan = select(contract)
    check_plan(contract, plan)
    tasks = ccr_tasks(contract, plan, "2026-09-20T00:00:00Z", "synthetic-original-revision")
    validator = import_module("ccr.schemas.validation")
    for task in tasks["tasks"]:
        result = validator.validate_instance("task", task)
        if not result.ok:
            raise ValueError(str(result.errors))
    report = pinned("vek-report-positive.json")
    imported = import_vek(
        report,
        report["scope"],
        report["snapshot_revision"],
        report["time_origin"],
        report["slot_seconds"],
    )
    negative = pinned("vek-report-negative.json")
    try:
        import_vek(
            negative,
            report["scope"],
            report["snapshot_revision"],
            report["time_origin"],
            report["slot_seconds"],
        )
    except ValueError:
        pass
    except Exception as exc:
        if type(exc).__module__.startswith("jsonschema"):
            pass
        else:
            raise
    else:
        raise AssertionError("forged service guarantee accepted")
    demand = vek_demand(contract, plan)
    model = import_module("verification_ecology_kit.capacity.model")
    checker = import_module("verification_ecology_kit.capacity.checker")
    checked = checker.check_schedule(
        model.Contract.from_dict(demand["native_contract"]),
        checker.Snapshot(spent=[0, 0]),
        demand["schedule"],
    )
    if not checked.mandatory_met:
        raise ValueError("mapped demand failed native schedule checking")
    projection = export_cait(history_example(), 20, "synthetic-tick", {"resource": "100"})
    native = projection["native_bundle"]
    if native is None:
        raise ValueError("unexpected incomplete history")
    cait_report = import_module("cait_schema.accounting.report").analyze(native)
    cait_check = import_module("cait_schema.accounting.checker").check_report(native, cait_report)
    if cait_check["status"] != "checked":
        raise ValueError(str(cait_check))
    assets, service = cait_report["balances"]
    if (
        assets["closing"],
        assets["unresolved"],
        service["service"],
        assets["costs"]["resource"],
    ) != ("1", "1", "4", "16"):
        raise AssertionError("native source accounting did not conserve stock/use/cost")
    return {
        "versions": versions,
        "ccr_tasks_checked": len(tasks["tasks"]),
        "vek_supplied_counters": imported,
        "vek_native_check": checked.to_dict(),
        "cait_report": cait_report,
        "cait_check": cait_check,
        "forged_guarantee_rejected": True,
        "live_host_enforcement": None,
        "execution_authority": None,
    }
