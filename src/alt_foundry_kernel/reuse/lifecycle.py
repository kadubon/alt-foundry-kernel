"""Append-only model history, pure as-of replay and explicitly requested local writes."""

from __future__ import annotations

import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import Field

from .contracts import Qualification
from .qualification import qualify
from .wire import Clock, Closed, Digest, Id, Q, Source, digest, encoded, loads


class Event(Closed):
    version: Literal["alt_reuse_event_v1"]
    id: Id
    scope: Id
    study: Id
    kind: Literal[
        "formation",
        "qualify",
        "transfer",
        "request",
        "result",
        "cost",
        "expire",
        "contradict",
        "withdraw",
        "refresh",
        "correct",
    ]
    previous: Digest
    time: Clock
    recorded: Clock
    artifact: Digest
    receiver: Id
    context: Id
    task: Id
    input_digest: Digest
    protocol: Id
    evaluator: Id
    offer_digest: Digest | None
    attempt: Id
    outcome: Literal["success", "failure", "unknown"]
    dependencies: list[Digest]
    required_cost_ids: list[Id]
    cost_id: Id | None
    cost_unit: Id | None
    quantity: Q
    valid_until: Clock
    target: Id | None
    origin: dict[Literal["endogenous", "external", "unresolved"], Q]
    evidence_basis: Literal["synthetic", "source-replay"]
    qualification: Qualification | None = None
    cost_stage: Literal[
        "formation", "execution", "transfer", "validation", "refresh", "maintenance", "repair"
    ] = "formation"


class Journal(Closed):
    version: Literal["alt_reuse_journal_v1"]
    scope: Id
    study: Id
    events: Annotated[list[Source], Field(max_length=256)]


def empty(scope: str, study: str) -> Journal:
    return Journal(version="alt_reuse_journal_v1", scope=scope, study=study, events=[])


def replay(journal: Journal, cutoff: int, *, corrected: bool = False) -> dict[str, Any]:
    chain = empty(journal.scope, journal.study)
    seen: dict[str, Event] = {}
    events: list[Event] = []
    for source in journal.events:
        event = Event.model_validate(source.read())
        if event.id in seen:
            if seen[event.id] != event:
                raise ValueError("conflicting event retry")
            continue
        if (
            event.previous != digest(chain)
            or event.scope != journal.scope
            or (event.study != journal.study or event.recorded < event.time)
        ):
            raise ValueError("journal revision, scope or clock mismatch")
        if events and event.recorded < events[-1].recorded:
            raise ValueError("recorded times must be append ordered")
        if (
            Fraction(event.quantity) < 0
            or set(event.origin) != {"endogenous", "external", "unresolved"}
            or any(Fraction(v) < 0 for v in event.origin.values())
            or sum((Fraction(v) for v in event.origin.values()), Fraction()) != 1
        ):
            raise ValueError("invalid quantity or origin partition")
        seen[event.id] = event
        events.append(event)
        chain.events.append(source)
    visible = sorted(
        (e for e in events if e.recorded <= cutoff and e.time <= cutoff),
        key=lambda e: (e.time, e.recorded, events.index(e)),
    )
    costs: dict[str, dict[str, str]] = {}
    stock: set[str] = set()
    revoked: set[str] = set()
    eligible: dict[str, Event] = {}
    invalidated: dict[str, int] = {}
    requests: dict[str, Event] = {}
    outcomes: dict[str, str] = {}
    uses: set[tuple[str, ...]] = set()
    corrections: dict[str, Event] = {}
    unresolved: set[str] = set()
    for event in visible:
        if event.kind == "correct":
            target = seen.get(event.target or "")
            if target is None or target.kind != "cost" or target.recorded >= event.recorded:
                raise ValueError("only explicit earlier cost corrections supported")
            if event.target in corrections:
                raise ValueError("conflicting corrected interpretation")
            corrections[str(event.target)] = event
    for event in visible:
        scope_key = digest(
            [
                event.artifact,
                event.receiver,
                event.context,
                event.input_digest,
                event.protocol,
                event.evaluator,
            ]
        )
        if event.kind == "cost":
            if event.cost_id is None or event.cost_unit is None:
                raise ValueError("cost identity or unit missing")
            quantity = (
                corrections[event.id].quantity
                if corrected and event.id in corrections
                else event.quantity
            )
            charge = {"unit": event.cost_unit, "amount": quantity}
            if event.cost_id in costs and costs[event.cost_id] != charge:
                raise ValueError("conflicting physical cost identity")
            costs[event.cost_id] = charge
        elif event.kind == "formation":
            if event.outcome == "success":
                stock.add(event.artifact)
            else:
                unresolved.add(event.attempt)
        elif event.kind in {"qualify", "refresh"}:
            if event.offer_digest is None or event.outcome != "success":
                raise ValueError("qualification requires bound successful source")
            proof = event.qualification
            if proof is None:
                raise ValueError("missing reconstruction material")
            qualify(proof.request, proof.candidate, proof.offer, event.time)
            if (
                event.offer_digest != digest(proof.offer)
                or event.artifact != proof.candidate.artifact_digest
                or event.input_digest not in proof.offer.inputs
                or event.valid_until != (proof.offer.valid_until)
            ):
                raise ValueError("qualification source binding mismatch")
            for name in ("receiver", "context", "protocol", "evaluator"):
                if getattr(event, name) != getattr(proof.offer, name):
                    raise ValueError("qualification receiver mismatch")
            if set(event.dependencies) != set(proof.offer.dependencies):
                raise ValueError("qualification dependencies changed")
            if not set(proof.offer.required_cost_ids) <= set(event.required_cost_ids):
                raise ValueError("qualification cost obligations omitted")
            if proof.offer.valid_from <= invalidated.get(scope_key, -1):
                raise ValueError("refresh requires evidence after scoped invalidation")
            eligible[scope_key] = event
        elif event.kind in {"expire", "contradict"}:
            eligible.pop(scope_key, None)
            invalidated[scope_key] = event.time
        elif event.kind == "withdraw":
            revoked.add(event.artifact)
        elif event.kind in {"transfer", "request"}:
            if event.attempt in requests and requests[event.attempt] != event:
                raise ValueError("attempt identity reused")
            requests[event.attempt] = event
            unresolved.add(event.attempt)
        elif event.kind == "result":
            request = requests.get(event.attempt)
            if request is None or event.attempt in outcomes:
                raise ValueError("result without unique request")
            for name in (
                "artifact",
                "receiver",
                "context",
                "task",
                "input_digest",
                "protocol",
                "evaluator",
                "offer_digest",
            ):
                if getattr(request, name) != getattr(event, name):
                    raise ValueError("result binding mismatch")
            qualification = eligible.get(scope_key)
            if event.outcome != "unknown":
                outcomes[event.attempt] = event.outcome
                unresolved.discard(event.attempt)
            if event.outcome == "success":
                if (
                    qualification is None
                    or event.artifact not in stock
                    or event.time >= qualification.valid_until
                    or event.offer_digest != qualification.offer_digest
                    or set(event.dependencies) != set(qualification.dependencies)
                    or (event.artifact in revoked or set(event.dependencies) & revoked)
                ):
                    raise ValueError("unqualified or expired successful use")
                if not set(qualification.required_cost_ids) <= set(
                    event.required_cost_ids
                ) or not set(qualification.required_cost_ids) <= set(request.required_cost_ids):
                    raise ValueError("successful use omitted physical cost obligations")
                uses.add(
                    (
                        event.artifact,
                        event.receiver,
                        event.context,
                        event.task,
                        event.input_digest,
                        event.protocol,
                        event.evaluator,
                    )
                )
            elif event.outcome == "failure":
                eligible.pop(scope_key, None)
                invalidated[scope_key] = event.time
        for cost_id in event.required_cost_ids:
            if not any(e.kind == "cost" and e.cost_id == cost_id for e in visible):
                unresolved.add("missing-cost:" + cost_id)
    # Fixed point propagates immutable revocations without erasing earlier uses/costs.
    for _ in range(len(visible) + 1):
        before = set(revoked)
        for event in visible:
            if set(event.dependencies) & revoked:
                revoked.add(event.artifact)
        if revoked == before:
            break
    current = {
        key: event.model_dump(mode="json")
        for key, event in eligible.items()
        if event.valid_until > cutoff
        and event.artifact not in revoked
        and not set(event.dependencies) & revoked
    }
    return {
        "revision": digest(chain),
        "scope": journal.scope,
        "study": journal.study,
        "cutoff": cutoff,
        "interpretation": "corrected" if corrected else "as-of",
        "stock": sorted(stock),
        "revoked": sorted(revoked),
        "eligible": current,
        "successful_uses": sorted([list(use) for use in uses]),
        "costs": costs,
        "unresolved": sorted(unresolved),
        "historical_events": len(visible),
        "settlement": None,
        "execution_authority": None,
        "source_authentication": None,
    }


def ingest(path: Path, journal: Journal, source: Source, expected: str) -> dict[str, Any]:
    """Host must serialize writers across read/check/replace; no external execution."""
    existing = (
        Journal.model_validate(loads(path.read_text(encoding="utf-8")))
        if path.exists()
        else journal
    )
    event = Event.model_validate(source.read())
    if digest(existing) != expected:
        raise ValueError("stale expected revision")
    for old in existing.events:
        if old.read()["id"] == event.id:
            if old != source:
                raise ValueError("conflicting event retry")
            return {"revision": expected, "writes": False}
    updated = existing.model_copy(deep=True)
    updated.events.append(source)
    updated = Journal.model_validate(updated.model_dump())
    replay(updated, 1000000)
    descriptor, name = tempfile.mkstemp(prefix=".alt-reuse-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(encoded(updated) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)
    return {"revision": digest(updated), "writes": True}
