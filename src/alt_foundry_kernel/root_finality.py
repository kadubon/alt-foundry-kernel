"""Root-of-trust, quorum, signature, finality, and rollback checks."""

from __future__ import annotations

import base64
import binascii
from collections.abc import Mapping, Sequence
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from alt_foundry_kernel.constants import IssueSeverity
from alt_foundry_kernel.reports import CertificateReport, numeric, present, status_is, value_at


def verify_ed25519_signature(message: bytes, signature_b64: str, public_key_b64: str) -> bool:
    """Verify an Ed25519 signature encoded as base64 strings."""

    try:
        public_key = Ed25519PublicKey.from_public_bytes(base64.b64decode(public_key_b64))
        public_key.verify(base64.b64decode(signature_b64), message)
    except (ValueError, binascii.Error, InvalidSignature):
        return False
    return True


def validate_root_finality_certificate(certificate: Mapping[str, Any]) -> CertificateReport:
    """Validate evaluator root, quorum, role separation, and finality records."""

    report = CertificateReport(
        name="root_finality",
        claim="root/quorum/finality/rollback certificate",
        level="settlement",
    )
    required = (
        "root.status",
        "root.role_separation",
        "quorum.threshold",
        "quorum.signed",
        "finality.state",
        "rollback.path",
    )
    for path in required:
        if not present(certificate, path):
            report.add_issue(
                IssueSeverity.ERROR,
                "required-field-missing",
                path,
                "Root/finality certification requires this field.",
            )

    threshold = numeric(certificate, "quorum.threshold")
    signed = numeric(certificate, "quorum.signed")
    quorum_ok = (
        threshold is not None and signed is not None and threshold > 0 and signed >= threshold
    )
    report.require(
        "RootOK",
        status_is(certificate, "root.status", "valid"),
        "root.status",
        "Evaluator root must be valid.",
    )
    report.require(
        "RoleSeparationOK",
        value_at(certificate, "root.role_separation") is True,
        "root.role_separation",
        "Root roles must be separated for evaluator soundness.",
    )
    report.require(
        "QuorumOK",
        quorum_ok,
        "quorum",
        "Quorum must meet or exceed the declared threshold.",
    )
    report.require(
        "FinalityOK",
        status_is(certificate, "finality.state", "finalized")
        or value_at(certificate, "finality.exempt") is True,
        "finality.state",
        "Capital transitions require finality or a narrow exemption.",
    )
    report.require(
        "RollbackPathOK",
        present(certificate, "rollback.path"),
        "rollback.path",
        "A rollback path must be declared.",
    )

    signatures = value_at(certificate, "signatures")
    message = value_at(certificate, "message")
    if (
        isinstance(signatures, Sequence)
        and not isinstance(signatures, str)
        and isinstance(message, str)
    ):
        valid_count = 0
        for item in signatures:
            if not isinstance(item, Mapping):
                continue
            signature = item.get("signature_b64")
            public_key = item.get("public_key_b64")
            if isinstance(signature, str) and isinstance(public_key, str):
                valid_count += int(
                    verify_ed25519_signature(message.encode(), signature, public_key)
                )
        report.metrics["valid_signature_count"] = valid_count
        if threshold is not None:
            report.require(
                "SignatureQuorumOK",
                valid_count >= threshold,
                "signatures",
                "Valid signature count must satisfy the declared quorum.",
            )
    return report
