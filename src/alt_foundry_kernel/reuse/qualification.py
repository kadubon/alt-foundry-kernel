"""Finite receiver checks and explicit loss-accounted field/unit mappings."""

from __future__ import annotations

from fractions import Fraction
from typing import Annotated, Literal

from pydantic import Field

from .formation import Candidate, Formation, reconstruct
from .wire import Clock, Closed, Digest, Id, Q, Source, digest, unique


class Check(Closed):
    version: Literal["alt_reuse_check_v1"]
    candidate: Digest
    receiver: Id
    mission: Id
    context: Id
    task_family: Id
    input_digest: Digest
    protocol: Id
    evaluator: Id
    time: Clock
    result: Literal["pass", "fail", "unknown"]
    restrictions: list[Id]
    dependencies: list[Digest]
    defeaters: list[Id]
    evidence_basis: Literal["synthetic", "source-replay"]
    quality: Id
    estimand: Id
    valuation: Id
    preconditions: list[Id]
    postconditions: list[Id]


class Offer(Closed):
    version: Literal["alt_reuse_offer_v1"]
    candidate: Digest
    receiver: Id
    mission: Id
    context: Id
    task_family: Id
    inputs: Annotated[list[Digest], Field(min_length=1, max_length=24)]
    opportunities: Annotated[list[Id], Field(min_length=1, max_length=24)]
    protocol: Id
    evaluator: Id
    valid_from: Clock
    valid_until: Clock
    restrictions: list[Id]
    dependencies: list[Digest]
    preconditions: list[Id]
    postconditions: list[Id]
    checks: Annotated[list[Source], Field(min_length=1, max_length=24)]
    required_cost_ids: Annotated[list[Id], Field(min_length=1, max_length=24)]
    comparator: Id
    estimand: Id
    quality: Id
    valuation: Id
    evidence_basis: Literal["synthetic", "source-replay"]


def qualify(request: Formation, candidate: Candidate, offer: Offer, at: int) -> bool:
    reconstruct(request, candidate)
    if candidate.qualification != "candidate" or offer.candidate != digest(candidate):
        raise ValueError("missing candidate qualification")
    if offer.mission != candidate.scope or not offer.valid_from <= at < offer.valid_until:
        raise ValueError("mission mismatch or expired offer")
    for values in (offer.inputs, offer.opportunities, offer.required_cost_ids):
        unique(values)
    if not set(candidate.dependencies) <= set(offer.dependencies) or not set(
        candidate.guards
    ) <= set(offer.preconditions):
        raise ValueError("dependency or guard dropped")
    if request.cost_id not in offer.required_cost_ids or not set(candidate.source_cost_ids) <= set(
        offer.required_cost_ids
    ):
        raise ValueError("formation cost omitted")
    checks = [Check.model_validate(source.read()) for source in offer.checks]
    matched: set[str] = set()
    for check in checks:
        for key in (
            "candidate",
            "receiver",
            "mission",
            "context",
            "task_family",
            "protocol",
            "evaluator",
            "evidence_basis",
            "quality",
            "estimand",
            "valuation",
        ):
            if getattr(check, key) != getattr(offer, key):
                raise ValueError("receiver or evaluator evidence mismatch")
        if set(check.preconditions) != set(offer.preconditions) or set(check.postconditions) != set(
            offer.postconditions
        ):
            raise ValueError("unsupported precondition or postcondition")
        if check.time > at or check.time < offer.valid_from or check.result != "pass":
            raise ValueError("missing timely successful receiver check")
        if (
            check.defeaters
            or set(check.dependencies) != set(offer.dependencies)
            or not set(check.restrictions) <= set(offer.restrictions)
        ):
            raise ValueError("defeater or dropped access/dependency obligation")
        matched.add(check.input_digest)
    if not set(offer.inputs) <= matched:
        raise ValueError("unsupported input domain")
    return True


class MappingField(Closed):
    source: Id
    target: Id
    source_unit: Id
    target_unit: Id
    scale: Q


class Adapter(Closed):
    version: Literal["alt_reuse_adapter_v1"]
    fields: Annotated[list[MappingField], Field(min_length=1, max_length=8)]
    allowed_units: list[Id]


def adapt(adapter: Adapter, values: dict[str, str]) -> dict[str, object]:
    """Only exact declared numerical selection/rename/unit conversion; no code."""
    unique([field.target for field in adapter.fields])
    result: dict[str, str] = {}
    for field in adapter.fields:
        if (
            field.source not in values
            or field.source_unit not in adapter.allowed_units
            or (field.target_unit not in adapter.allowed_units)
        ):
            raise ValueError("unsupported adapter field or unit")
        if Fraction(field.scale) <= 0:
            raise ValueError("nonpositive unit conversion")
        from .wire import rational

        result[field.target] = str(Fraction(rational(values[field.source])) * Fraction(field.scale))
    return {
        "values": result,
        "unmapped_fields": sorted(set(values) - {field.source for field in adapter.fields}),
        "semantic_transfer": None,
        "adapter_digest": digest(adapter),
        "source_digest": digest(values),
    }
