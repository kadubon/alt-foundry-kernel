"""Installed artifact checks, independent of a source checkout and runtime network."""

from __future__ import annotations

import json
import socket
from importlib.metadata import version
from importlib.resources import files
from pathlib import Path
from typing import Any
from unittest.mock import patch

from typer.testing import CliRunner

from alt_foundry_kernel.cli import app
from alt_foundry_kernel.conformance import run_conformance
from alt_foundry_kernel.estimators import estimate_certificate
from alt_foundry_kernel.kernel import run_kernel_transition
from alt_foundry_kernel.models import KernelState
from alt_foundry_kernel.validation import validate_packet

from .checker import check_plan
from .examples import contract_example, history_example
from .integration import run as integrate
from .lifecycle import replay
from .planning import select
from .qualification import qualify


def run(native: bool = True) -> dict[str, Any]:
    def forbidden(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("runtime sockets forbidden")

    with (
        patch.object(socket.socket, "connect", forbidden),
        patch.object(socket, "create_connection", forbidden),
    ):
        root = files("alt_foundry_kernel")
        legacy = root.joinpath("legacy_examples")
        packet = json.loads(legacy.joinpath("admission_packet.json").read_text(encoding="utf-8"))
        assert validate_packet(packet).ok
        assert run_kernel_transition(KernelState(), packet).next_state.certified_capital == 6.5
        estimate = json.loads(
            legacy.joinpath("estimators", "finite_sample.json").read_text(encoding="utf-8")
        )
        assert estimate_certificate("finite-sample", estimate).ok
        conformance = run_conformance(Path(str(root.joinpath("legacy_conformance"))), "L5")
        assert conformance.ok and conformance.checked > 0
        commands = [
            ["validate", str(legacy.joinpath("admission_packet.json"))],
            [
                "certify",
                "measurement",
                str(legacy.joinpath("certificates", "measurement_spec.json")),
            ],
            ["estimate", "finite-sample", str(legacy.joinpath("estimators", "finite_sample.json"))],
            ["reuse", "example"],
            ["reuse", "example", "--history"],
        ]
        for command in commands:
            result = CliRunner().invoke(app, command)
            assert result.exit_code == 0, result.output
            assert isinstance(json.loads(result.output), dict)
        costs = []
        for count in (1, 2, 3, 4):
            contract = contract_example(count)
            plan = select(contract)
            check_plan(contract, plan)
            assert plan.score is not None
            costs.append(plan.score.lifecycle_cost)
        assert costs == ["5", "10", "15", "16"]
        expensive = select(contract_example(transfer_cost=5))
        assert expensive.selected == [f"scratch-{i}" for i in range(4)]
        missing = contract_example()
        missing.capacities["verifier"] = 0
        assert select(missing).score is None
        row = contract_example().qualifications[0]
        row.offer.receiver = "C"
        try:
            qualify(row.request, row.candidate, row.offer, 3)
        except ValueError:
            pass
        else:
            raise AssertionError("unsupported receiver admitted")
        state = replay(history_example(), 20)
        assert len(state["stock"]) == 1 and len(state["successful_uses"]) == 4
        integration = integrate() if native else None
    return {
        "package_version": version("alt-foundry-kernel"),
        "import_origin": str(root),
        "legacy_conformance_cases": conformance.checked,
        "break_even_costs": costs,
        "runtime_sockets": "blocked",
        "installed_cli_commands": len(commands),
        "integration": integration,
        "authority": None,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
