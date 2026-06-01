from __future__ import annotations

import json
from pathlib import Path

from alt_foundry_kernel import build_transcript, replay_transcript, run_conformance
from alt_foundry_kernel.foundry import make_dashboard

ROOT = Path(__file__).resolve().parents[1]


def test_golden_transcript_replays_deterministically() -> None:
    fixture = json.loads(
        (ROOT / "conformance" / "v0.2.0" / "golden_admission_transcript.json").read_text(
            encoding="utf-8"
        )
    )

    assert replay_transcript(fixture)


def test_conformance_runner_checks_fixture_directory() -> None:
    report = run_conformance(ROOT / "conformance")

    assert report.ok
    assert report.checked >= 1


def test_build_transcript_and_dashboard_are_language_neutral_json() -> None:
    packet = json.loads((ROOT / "examples" / "admission_packet.json").read_text(encoding="utf-8"))
    transcript = build_transcript({}, [packet])
    dashboard = make_dashboard(transcript.final_state)

    assert transcript.transitions[0]["decision"] == "admit"
    assert transcript.final_state["certified_capital"] == 6.5
    assert dashboard["certified_capital"] == 6.5
    assert dashboard["active_tokens"] == 1
