"""Closed bounded planning contracts; units and comparison premises are explicit."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field

from .formation import Candidate, Formation
from .qualification import Offer
from .wire import Clock, Closed, Digest, Id, Q


class Cost(Closed):
    id: Id
    stage: Literal[
        "formation",
        "transfer",
        "execution",
        "checking",
        "refresh",
        "maintenance",
        "failure",
        "retirement",
    ]
    unit: Id
    amount: Q
    allocations: dict[Id, Q]


class Occupancy(Closed):
    resource: Id
    slot: Annotated[int, Field(ge=0, le=15)]
    quantity: Annotated[int, Field(ge=1, le=1000)]


class Opportunity(Closed):
    id: Id
    receiver: Id
    context: Id
    input_digest: Digest
    task_family: Id
    task: Id
    quality: Id
    estimand: Id
    deadline: Annotated[int, Field(ge=0, le=15)]
    required: bool
    value: dict[Id, Q]


class Option(Closed):
    id: Id
    kind: Literal["scratch", "available", "formation", "transfer", "refresh", "reuse"]
    prerequisites: Annotated[list[Id], Field(max_length=12)]
    offer: Id | None
    opportunities: Annotated[list[Id], Field(max_length=24)]
    costs: Annotated[list[Id], Field(max_length=32)]
    occupancy: Annotated[list[Occupancy], Field(max_length=128)]
    start: Annotated[int, Field(ge=0, le=15)]
    end: Annotated[int, Field(ge=0, le=16)]
    succeeds: dict[Id, bool]
    hazard_cleared: bool
    conflicts: list[Id]


class Bundle(Closed):
    opportunity: Id
    options: Annotated[list[Id], Field(min_length=1, max_length=12)]


class Qualification(Closed):
    id: Id
    request: Formation
    candidate: Candidate
    offer: Offer


class Contract(Closed):
    version: Literal["alt_reuse_contract_v1"]
    scope: Id
    study: Id
    split: Literal["training", "holdout"]
    checkpoint: Clock
    evidence_cutoff: Clock
    initial_revision: Digest
    time_origin: Id
    slot_seconds: Q
    horizon: Annotated[int, Field(ge=1, le=16)]
    valuation: Id
    value_unit: Id
    cost_rates: dict[Id, Q]
    budgets: dict[Id, Q]
    capacities: dict[Id, Annotated[int, Field(ge=0, le=1000)]]
    scenarios: Annotated[list[Id], Field(min_length=1, max_length=8)]
    opportunities: Annotated[list[Opportunity], Field(max_length=24)]
    options: Annotated[list[Option], Field(max_length=12)]
    bundles: Annotated[list[Bundle], Field(max_length=24)]
    qualifications: Annotated[list[Qualification], Field(max_length=12)]
    costs: Annotated[list[Cost], Field(max_length=64)]
    sunk_cost_ids: Annotated[list[Id], Field(max_length=64)]
    objective: Literal["worst-net-value-then-cost"]
    joint_model: Literal["registered-separable-opportunities"]
    expansion_limit: Annotated[int, Field(ge=1, le=4096)]
    execution_authority: None
    completed_opportunities: Annotated[list[Id], Field(max_length=24)] = []
    unresolved_work: Annotated[list[Id], Field(max_length=256)] = []
    checker_work_limit: Annotated[int, Field(ge=1, le=100000)] = 100000


class Score(Closed):
    feasible: bool
    reasons: list[str]
    costs: dict[Id, Q]
    incremental_cost: Q
    lifecycle_cost: Q
    scenario_net: dict[Id, Q]
    scenario_coverage: dict[Id, list[Id]]


class Plan(Closed):
    version: Literal["alt_reuse_plan_v1"]
    contract_digest: Digest
    state_digest: Digest
    selected: list[Id]
    score: Score | None
    expanded: Annotated[int, Field(ge=0, le=4096)]
    complete: bool
    catalogue: Literal["all", "scratch", "available", "no-transfer"]
    evidence_basis: Literal["declared-model"]
    source_authentication: None
    statistical_coverage: None
    causal_attribution: None
    settlement: None
    execution_authority: None
