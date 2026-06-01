"""Foundry orchestration, dashboards, and replayable transition transcripts."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from alt_foundry_kernel.kernel import run_kernel_transition
from alt_foundry_kernel.models import KernelState, TransitionResult


class DecisionTranscript(BaseModel):
    """Replayable record of a deterministic ALT kernel run."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str = "0.2.0"
    initial_state: dict[str, Any] = Field(default_factory=dict)
    packets: list[dict[str, Any]]
    transitions: list[dict[str, Any]]
    final_state: dict[str, Any]


def run_foundry_sequence(
    initial_state: KernelState | Mapping[str, Any], packets: Sequence[Mapping[str, Any]]
) -> tuple[KernelState, list[TransitionResult]]:
    """Run a deterministic sequence of kernel transitions."""

    state = (
        initial_state
        if isinstance(initial_state, KernelState)
        else KernelState.model_validate(initial_state)
    )
    transitions: list[TransitionResult] = []
    for packet in packets:
        result = run_kernel_transition(state, packet)
        transitions.append(result)
        state = result.next_state
    return state, transitions


def build_transcript(
    initial_state: KernelState | Mapping[str, Any], packets: Sequence[Mapping[str, Any]]
) -> DecisionTranscript:
    """Build a language-neutral golden transcript for conformance fixtures."""

    starting_state = (
        initial_state.model_dump(mode="json")
        if isinstance(initial_state, KernelState)
        else KernelState.model_validate(initial_state).model_dump(mode="json")
    )
    final_state, transitions = run_foundry_sequence(initial_state, packets)
    return DecisionTranscript(
        initial_state=starting_state,
        packets=[dict(packet) for packet in packets],
        transitions=[transition.model_dump(mode="json") for transition in transitions],
        final_state=final_state.model_dump(mode="json"),
    )


def replay_transcript(transcript: Mapping[str, Any]) -> bool:
    """Replay a transcript and compare decisions, capital, and token states."""

    parsed = DecisionTranscript.model_validate(transcript)
    rebuilt = build_transcript(parsed.initial_state, parsed.packets)
    expected_decisions = [
        item.get("decision") for item in parsed.transitions if isinstance(item, Mapping)
    ]
    actual_decisions = [
        item.get("decision") for item in rebuilt.transitions if isinstance(item, Mapping)
    ]
    return (
        expected_decisions == actual_decisions
        and parsed.final_state.get("certified_capital")
        == rebuilt.final_state.get("certified_capital")
        and parsed.final_state.get("token_states") == rebuilt.final_state.get("token_states")
    )


def make_dashboard(state: KernelState | Mapping[str, Any]) -> dict[str, Any]:
    """Create the paper-facing dashboard summary from a kernel state."""

    parsed = state if isinstance(state, KernelState) else KernelState.model_validate(state)
    return {
        "schema_version": "0.2.0",
        "epoch": 0,
        "kernel_state": parsed.model_dump(mode="json"),
        "mission_status": {},
        "baseline_registry": {},
        "telemetry_state": parsed.monitor_drift_state,
        "transport_status": {},
        "hazard_status": {"entries": len(parsed.hazard_ledger)},
        "root_status": parsed.root_finality_state,
        "finality_status": parsed.root_finality_state,
        "budgets": parsed.budget_state,
        "proposed_action": "monitor",
        "certified_capital": parsed.certified_capital,
        "active_tokens": len(parsed.admitted_tokens),
        "candidate_queue": len(parsed.candidate_queue),
        "exploration_entries": len(parsed.exploration_ledger),
        "settlement_entries": len(parsed.settlement_ledger),
        "hazard_entries": len(parsed.hazard_ledger),
        "negative_entries": len(parsed.negative_registry),
        "resurrection_entries": len(parsed.resurrection_queue),
        "audit_entries": len(parsed.audit_log),
        "token_states": {key: value.value for key, value in parsed.token_states.items()},
        "ledgers": {
            "exploration": [entry.model_dump(mode="json") for entry in parsed.exploration_ledger],
            "settlement": [entry.model_dump(mode="json") for entry in parsed.settlement_ledger],
            "negative_registry": [
                entry.model_dump(mode="json") for entry in parsed.negative_registry
            ],
            "audit": [entry.model_dump(mode="json") for entry in parsed.audit_log],
        },
    }
