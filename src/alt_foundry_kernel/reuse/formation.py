"""Finite whole-sequence anti-unification with explicitly permitted literal slots."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field

from .wire import Clock, Closed, Digest, Id, Q, Source, digest, nonnegative, unique


class Atom(Closed):
    kind: Literal["integer", "string", "reference", "parameter"]
    value: int | str


class Primitive(Closed):
    id: Id
    implementation: Digest
    inputs: list[Literal["integer", "string"]]
    output: Literal["integer", "string"]


class Step(Closed):
    primitive: Id
    arguments: Annotated[list[Atom], Field(max_length=8)]


class Trace(Closed):
    version: Literal["alt_reuse_trace_v1"]
    episode: Id
    task: Id
    input_digest: Digest
    source_version: Id
    time: Clock
    split: Literal["training", "holdout"]
    complete: bool
    checked_artifact: Digest
    steps: Annotated[list[Step], Field(min_length=1, max_length=8)]
    outcome: Literal["success", "failure", "unknown"]
    check_results: Annotated[list[Literal["pass", "fail", "unknown"]], Field(min_length=1)]
    costs: Annotated[list[Id], Field(min_length=1, max_length=16)]
    guards: list[Id]
    dependencies: list[Digest]
    unresolved: list[Id]
    secret_taint: bool


class Parameter(Closed):
    name: Id
    step: Annotated[int, Field(ge=0, le=7)]
    argument: Annotated[int, Field(ge=0, le=7)]


class Formation(Closed):
    version: Literal["alt_reuse_formation_v1"]
    mode: Literal["package", "sequence"]
    scope: Id
    cutoff: Clock
    sources: Annotated[list[Source], Field(min_length=1, max_length=8)]
    library: Annotated[list[Primitive], Field(min_length=1, max_length=16)]
    parameters: Annotated[list[Parameter], Field(max_length=16)]
    attempt_id: Id
    cost_id: Id
    cost_unit: Id
    cost: Q
    expansion_limit: Annotated[int, Field(ge=1, le=1024)]


class Candidate(Closed):
    version: Literal["alt_reuse_candidate_v1"]
    request_digest: Digest
    extractor: Literal["whole-sequence-1"]
    artifact_digest: Digest
    scope: Id
    source_digests: list[Digest]
    representation: list[Step]
    implementation_digests: list[Digest]
    guards: list[Id]
    dependencies: list[Digest]
    unresolved: list[Id]
    formation_cost_id: Id
    source_cost_ids: list[Id]
    qualification: Literal["candidate", "unqualified"]
    source_authentication: None
    settlement: None
    execution_authority: None


def request_identity(request: Formation) -> str:
    value = request.model_dump(mode="json")
    for key, field in (("sources", "sha256"), ("library", "id")):
        value[key] = sorted(value[key], key=lambda item: item[field])
    value["parameters"] = sorted(
        value["parameters"], key=lambda item: (item["step"], item["argument"], item["name"])
    )
    return digest(value)


def trace_inputs(request: Formation) -> list[Trace]:
    unique([source.sha256 for source in request.sources])
    unique([primitive.id for primitive in request.library])
    nonnegative([request.cost])
    traces = [Trace.model_validate(source.read()) for source in request.sources]
    unique([trace.episode for trace in traces])
    if any(trace.split != "training" or trace.time > request.cutoff for trace in traces):
        raise ValueError("holdout or post-cutoff source cannot be mined")
    if request.mode == "sequence" and len(traces) < 2:
        raise ValueError("recurrence requires independent declared episodes")
    if request.mode == "package" and (len(traces) != 1 or request.parameters):
        raise ValueError("packaging requires one exact artifact without parameterization")
    library = {primitive.id: primitive for primitive in request.library}
    for trace in traces:
        if not set(trace.dependencies) <= {p.implementation for p in request.library}:
            raise ValueError("unresolved primitive dependency closure")
        outputs: list[str] = []
        for step in trace.steps:
            primitive = library.get(step.primitive)
            if primitive is None or len(primitive.inputs) != len(step.arguments):
                raise ValueError("unknown interface or arity")
            for atom, expected in zip(step.arguments, primitive.inputs, strict=True):
                if atom.kind == "reference":
                    if type(atom.value) is not int or not 0 <= atom.value < len(outputs):
                        raise ValueError("forward or invalid dataflow reference")
                    actual = outputs[atom.value]
                else:
                    actual = atom.kind
                    if (actual == "integer" and type(atom.value) is not int) or (
                        actual == "string" and type(atom.value) is not str
                    ):
                        raise ValueError("literal type mismatch")
                if actual != expected:
                    raise ValueError("typed dataflow mismatch")
            outputs.append(primitive.output)
    return traces


def form(request: Formation) -> Candidate:
    traces = trace_inputs(request)
    if sum(len(trace.steps) for trace in traces) > request.expansion_limit:
        raise ValueError("extraction budget exhausted; attempt cost remains payable")
    positions = {(item.step, item.argument): item.name for item in request.parameters}
    if len(positions) != len(request.parameters):
        raise ValueError("duplicate parameter slot")
    patterns: list[list[Step]] = []
    for trace in traces:
        pattern = [step.model_copy(deep=True) for step in trace.steps]
        bindings: dict[str, Atom] = {}
        for (step_index, argument_index), name in positions.items():
            if step_index >= len(pattern) or argument_index >= len(pattern[step_index].arguments):
                raise ValueError("parameter outside sequence")
            atom = pattern[step_index].arguments[argument_index]
            if atom.kind not in {"integer", "string"}:
                raise ValueError("only literal inputs may be parameterized")
            if name in bindings and bindings[name] != atom:
                raise ValueError("repeated-variable equality violated")
            bindings[name] = atom
            pattern[step_index].arguments[argument_index] = Atom(kind="parameter", value=name)
        patterns.append(pattern)
    if any(pattern != patterns[0] for pattern in patterns):
        raise ValueError("no recurring typed sequence; attempt cost remains payable")
    return Candidate(
        version="alt_reuse_candidate_v1",
        request_digest=request_identity(request),
        extractor="whole-sequence-1",
        artifact_digest=artifact_identity(request, patterns[0]),
        scope=request.scope,
        source_digests=sorted(source.sha256 for source in request.sources),
        representation=patterns[0],
        implementation_digests=sorted({item.implementation for item in request.library}),
        guards=sorted({guard for trace in traces for guard in trace.guards}),
        dependencies=sorted({dep for trace in traces for dep in trace.dependencies}),
        unresolved=sorted({item for trace in traces for item in trace.unresolved}),
        formation_cost_id=request.cost_id,
        source_cost_ids=sorted({cost for trace in traces for cost in trace.costs}),
        qualification="candidate"
        if all(
            trace.complete
            and trace.outcome == "success"
            and all(result == "pass" for result in trace.check_results)
            and not trace.secret_taint
            and not trace.unresolved
            for trace in traces
        )
        else "unqualified",
        source_authentication=None,
        settlement=None,
        execution_authority=None,
    )


def reconstruct(request: Formation, candidate: Candidate) -> bool:
    """Check each substitution against original bytes without invoking extraction."""
    traces = trace_inputs(request)
    if sum(len(trace.steps) for trace in traces) > request.expansion_limit:
        raise ValueError("reconstruction exceeds declared extraction work")
    positions = [(p.step, p.argument) for p in request.parameters]
    if len(set(positions)) != len(positions) or any(
        i >= len(trace.steps) or j >= len(trace.steps[i].arguments)
        for trace in traces
        for i, j in positions
    ):
        raise ValueError("invalid declared parameter positions")
    if candidate.request_digest != request_identity(request) or candidate.scope != request.scope:
        raise ValueError("candidate registration mismatch")
    if candidate.source_digests != sorted(source.sha256 for source in request.sources):
        raise ValueError("candidate source set mismatch")
    allowed = {(p.step, p.argument): p.name for p in request.parameters}
    for trace in traces:
        if len(trace.steps) != len(candidate.representation):
            raise ValueError("sequence truncation")
        bindings: dict[str, Atom] = {}
        for i, (actual, projected) in enumerate(
            zip(trace.steps, candidate.representation, strict=True)
        ):
            if actual.primitive != projected.primitive or len(actual.arguments) != len(
                projected.arguments
            ):
                raise ValueError("implementation or arity changed")
            for j, (original, item) in enumerate(
                zip(actual.arguments, projected.arguments, strict=True)
            ):
                name = allowed.get((i, j))
                if name is None:
                    if original != item:
                        raise ValueError("unpermitted projection")
                elif (
                    item.kind != "parameter"
                    or item.value != name
                    or original.kind not in {"integer", "string"}
                ):
                    raise ValueError("invalid parameter projection")
                elif name in bindings and bindings[name] != original:
                    raise ValueError("parameter equality lost")
                else:
                    bindings[name] = original
    if candidate.implementation_digests != sorted({p.implementation for p in request.library}):
        raise ValueError("implementation digest changed")
    if candidate.artifact_digest != artifact_identity(request, candidate.representation):
        raise ValueError("immutable artifact identity changed")
    for name in ("guards", "dependencies", "unresolved"):
        if getattr(candidate, name) != sorted(
            {item for trace in traces for item in getattr(trace, name)}
        ):
            raise ValueError("source obligation omitted")
    if candidate.source_cost_ids != sorted({cost for trace in traces for cost in trace.costs}):
        raise ValueError("source cost omitted")
    eligible = all(
        t.complete
        and t.outcome == "success"
        and not t.secret_taint
        and not t.unresolved
        and set(t.check_results) == {"pass"}
        for t in traces
    )
    if (candidate.qualification == "candidate") != eligible or (
        candidate.formation_cost_id != request.cost_id
    ):
        raise ValueError("unsupported qualification or omitted formation cost")
    return True


def artifact_identity(request: Formation, representation: list[Step]) -> str:
    """Finite equivalence: primitive bytes/types, dataflow and alpha-renamed parameters."""
    library = {primitive.id: primitive for primitive in request.library}
    names: dict[str, int] = {}
    rows = []
    for step in representation:
        primitive = library[step.primitive]
        arguments = []
        for atom in step.arguments:
            value = atom.value
            if atom.kind == "parameter":
                name = str(value)
                if name not in names:
                    names[name] = len(names)
                value = names[name]
            arguments.append([atom.kind, value])
        rows.append([primitive.implementation, primitive.inputs, primitive.output, arguments])
    return digest(rows)
