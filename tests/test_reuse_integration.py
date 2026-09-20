from __future__ import annotations

import socket

import pytest

from alt_foundry_kernel.reuse.integration import run


def test_native_pinned_companions_offline(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("cait_schema")
    pytest.importorskip("verification_ecology_kit")
    pytest.importorskip("ccr")

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("runtime network forbidden")

    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    result = run()
    assert result["cait_check"]["status"] == "checked"
    assert result["forged_guarantee_rejected"]
