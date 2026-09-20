"""Bounded inert JSON and exact arithmetic shared by the opt-in profile."""

from __future__ import annotations

import hashlib
import json
import re
from fractions import Fraction
from typing import Annotated, Any

from pydantic import AfterValidator, BaseModel, ConfigDict, Field


def rational(value: str) -> str:
    if not re.fullmatch(r"-?(0|[1-9][0-9]*)(/[1-9][0-9]*)?", value) or len(value) > 81:
        raise ValueError("expected canonical bounded rational string")
    number = Fraction(value)
    if (
        str(number) != value
        or max(abs(number.numerator).bit_length(), number.denominator.bit_length()) > 128
    ):
        raise ValueError("rational must be reduced and at most 128 bits")
    return value


Q = Annotated[
    str,
    Field(max_length=81, pattern=r"^-?(0|[1-9][0-9]*)(/[1-9][0-9]*)?$"),
    AfterValidator(rational),
]
Id = Annotated[str, Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_.:-]+$")]
Digest = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
Clock = Annotated[int, Field(ge=0, le=1000000)]


class Closed(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, validate_default=True)


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _reject(value: str) -> Any:
    raise ValueError("floating and nonfinite JSON numbers are unsupported")


def loads(raw: str) -> Any:
    if len(raw.encode("utf-8")) > 2000000:
        raise ValueError("JSON byte bound")
    try:
        result = json.loads(
            raw, object_pairs_hook=_pairs, parse_float=_reject, parse_constant=_reject
        )
    except RecursionError as exc:
        raise ValueError("JSON depth bound") from exc
    pending = [(result, 0)]
    nodes = 0
    while pending:
        item, depth = pending.pop()
        nodes += 1
        if depth > 24 or nodes > 50000:
            raise ValueError("JSON structural bound")
        if isinstance(item, dict):
            pending.extend((value, depth + 1) for value in item.values())
        elif isinstance(item, list):
            pending.extend((value, depth + 1) for value in item)
        elif type(item) is int and abs(item).bit_length() > 128:
            raise ValueError("integer bound")
    return result


def encoded(value: Any) -> str:
    if isinstance(value, BaseModel):
        value = value.model_dump(mode="json")
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    )


def sha(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def digest(value: Any) -> str:
    return sha(encoded(value))


class Source(Closed):
    sha256: Digest
    content: Annotated[str, Field(max_length=100000)]

    def read(self) -> Any:
        if sha(self.content) != self.sha256:
            raise ValueError("source digest mismatch")
        return loads(self.content)


def envelope(value: Any) -> Source:
    raw = encoded(value)
    return Source(sha256=sha(raw), content=raw)


def unique(values: list[str]) -> None:
    if len(values) != len(set(values)):
        raise ValueError("duplicate semantic identity")


def nonnegative(values: list[str]) -> None:
    if any(Fraction(value) < 0 for value in values):
        raise ValueError("negative resource coordinate")
