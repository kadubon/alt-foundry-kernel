"""Explicit ALT source projection into the released CAIT 0.2.0 finite vocabulary."""

from __future__ import annotations

import json
from copy import deepcopy
from typing import Any

from .interchange import pinned, validate_native
from .lifecycle import Event, Journal, replay
from .wire import digest, envelope, sha


def export_cait(
    journal: Journal, cutoff: int, time_unit: str, resource_limits: dict[str, str]
) -> dict[str, Any]:
    state = replay(journal, cutoff)
    rows = [Event.model_validate(source.read()) for source in journal.events]
    obligations = list(state["unresolved"])
    unsupported = {e.kind for e in rows} - {
        "cost",
        "formation",
        "qualify",
        "request",
        "result",
        "withdraw",
    }
    obligations.extend("unmapped-event:" + kind for kind in sorted(unsupported))
    if any(e.recorded > cutoff for e in rows):
        obligations.append("post-cutoff-history")
    qualifications = [e for e in rows if e.kind == "qualify"]
    if not qualifications:
        obligations.append("missing-qualified-creation-source")
    units = {str(e.cost_unit) for e in rows if e.kind == "cost"}
    if units != resource_limits.keys():
        obligations.append("missing-resource-bound")
    base: dict[str, Any] = {
        "version": "alt_reuse_cait_projection_v1",
        "source_journal": journal.model_dump(),
        "source_digest": digest(journal),
        "native_bundle": None,
        "unmapped_obligations": obligations,
        "source_authentication": None,
        "causal_attribution": None,
        "arrival": None,
        "settlement": None,
        "execution_authority": None,
    }
    if obligations:
        return base
    template = pinned("cait-positive.json")["contract"]
    contract = deepcopy(template)
    receivers: dict[str, dict[str, Any]] = {}
    evidence: list[dict[str, Any]] = []
    for row in qualifications:
        receiver = {
            "id": row.receiver,
            "context": row.context,
            "task": row.task,
            "evaluator": row.evaluator,
            "protocol": row.protocol,
            "checks": ["source-check"],
        }
        if row.receiver in receivers and receivers[row.receiver] != receiver:
            base["unmapped_obligations"].append("receiver-has-multiple-task-bindings")
            return base
        receivers[row.receiver] = receiver
        evidence.append(
            {
                "id": row.id,
                "scope": journal.scope,
                "arm": "candidate",
                "artifact": row.artifact,
                "receiver": row.receiver,
                "context": row.context,
                "evaluator": row.evaluator,
                "protocol": row.protocol,
                "check": "source-check",
                "outcome": "pass",
                "valid_from": row.time,
                "valid_until": row.valid_until,
                "dependencies": [],
                "blocking_defeaters": [],
                "cost_ids": row.required_cost_ids,
            }
        )
    events: list[dict[str, Any]] = []
    created: dict[str, str] = {}
    mappings: dict[str, str | None] = {}
    for row in rows:
        kind: str | None = None
        data: dict[str, Any] = {}
        evidence_ids: list[str] = []
        dependencies: list[str] = []
        if row.kind == "cost":
            kind = "cost"
            data = {
                "cost_id": row.cost_id,
                "unit": row.cost_unit,
                "quantity": {"joint": row.quantity},
                "stage": row.cost_stage,
            }
        elif row.kind == "formation" and row.outcome == "success" and row.artifact not in created:
            eligible = [
                q for q in qualifications if q.artifact == row.artifact and q.time <= row.time
            ]
            if not eligible or row.dependencies:
                base["unmapped_obligations"].append(
                    "creation-needs-current-evidence-and-parent-mapping"
                )
                return base
            evidence_ids = [eligible[0].id]
            kind = "create"
            created[row.artifact] = row.id
            data = {
                "artifact": row.artifact,
                "coordinate": "assets",
                "quantity": {"joint": "1"},
                "shares": row.origin,
                "parents": [],
                "parent_shares": {},
                "expires": eligible[0].valid_until,
            }
        elif row.kind == "result":
            matches = [q for q in qualifications if q.offer_digest == row.offer_digest]
            if not matches or row.artifact not in created:
                base["unmapped_obligations"].append("use-missing-native-creation-or-receiver")
                return base
            kind = "use"
            evidence_ids = [matches[-1].id]
            dependencies = [created[row.artifact]]
            data = {
                "artifact": row.artifact,
                "coordinate": "service",
                "quantity": {"joint": "1"},
                "receiver": row.receiver,
                "context": row.context,
                "task": row.task,
                "input": row.input_digest,
                "evaluator": row.evaluator,
                "protocol": row.protocol,
                "outcome": "pending" if row.outcome == "unknown" else row.outcome,
            }
        elif row.kind == "withdraw":
            kind = "withdraw"
            data = {"artifact": row.artifact, "reason": "source-withdrawal"}
        mappings[row.id] = row.id if kind is not None else None
        if kind is not None:
            events.append(
                {
                    "id": row.id,
                    "kind": kind,
                    "time": row.time,
                    "recorded": row.recorded,
                    "arm": "candidate",
                    "stream": "journal",
                    "study": journal.study,
                    "dependencies": dependencies,
                    "evidence": evidence_ids,
                    "costs": row.required_cost_ids,
                    "data": data,
                }
            )
    contract.update(
        scope=journal.scope,
        episode="alt-source-history",
        study=journal.study,
        time_unit=time_unit,
        start=0,
        end=cutoff,
        cutoff=cutoff,
        checkpoint_time=0,
        basis="synthetic"
        if all(e.evidence_basis == "synthetic" for e in rows)
        else "source-replay",
        interpretation="as_of",
        receivers=list(receivers.values()),
        arms=["candidate"],
        scenarios=["joint"],
        opening=[],
        mandatory_events=[e["id"] for e in events],
        mandatory_costs=[str(e.cost_id) for e in rows if e.kind == "cost"],
        negative_terms_complete=True,
        allocations={},
        cost_units=sorted(units),
        resource_limits={unit: {"joint": amount} for unit, amount in resource_limits.items()},
        valuation={"version": "no-cross-unit-valuation", "target": "assets", "rates": {}},
        streams=[
            {
                "id": "journal",
                "arm": "candidate",
                "checkpoint": digest(journal),
                "first": 1,
                "last": len(events),
                "terminal": "0" * 64,
            }
        ],
    )
    # CAIT canonical encoding is ASCII escaped; terminals alone are omitted for registration.
    registration = sha(
        json.dumps(contract, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    )
    wrapped = []
    previous = contract["streams"][0]["checkpoint"]
    for sequence, event in enumerate(events, 1):
        event.update(
            scope=journal.scope,
            episode=contract["episode"],
            contract=registration,
            sequence=sequence,
            previous=previous,
        )
        source = envelope(event)
        wrapped.append(source.model_dump())
        previous = source.sha256
    contract["streams"][0]["terminal"] = previous
    bundle = {
        "record_type": "cait_source_bundle_v1",
        "contract": contract,
        "events": wrapped,
        "evidence": [envelope(e).model_dump() for e in evidence],
        "models": [],
    }
    validate_native("cait-bundle.schema.json", bundle)
    base.update(
        native_bundle=bundle,
        event_mapping=mappings,
        ignored_as_stock=["qualification", "request", "copies"],
        origin_interpretation="declared bookkeeping shares, not causal identification",
    )
    return base
