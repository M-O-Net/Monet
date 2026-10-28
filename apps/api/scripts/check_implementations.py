import json
import multiprocessing
import pathlib
import sys
import time
from typing import Any

from seed_data.catalogue import TYPES
from seed_data.dataset import (
    ASSERTED,
    IMPLEMENTATIONS,
    INSTANCES,
    OBJECTS,
    OPERATORS,
    RELATIONS,
    SIGNATURES,
    fingerprint,
)

SANDBOX = pathlib.Path(__file__).resolve().parents[2] / "web" / "src" / "sandbox"
IMPLEMENTATION_DIR = pathlib.Path(__file__).resolve().parent / "implementations"
SLOW_PROBE_SECONDS = 2.0

_scope: dict[str, Any] = {}


def _load_sandbox() -> None:
    _scope["__name__"] = "__main__"
    for name in ("prelude.py", "runner.py"):
        exec(compile((SANDBOX / name).read_text(), name, "exec"), _scope)  # noqa: S102


def _ancestors(type_key: str) -> set[str]:
    found = {type_key}
    for supertype in TYPES[type_key][3]:
        found |= _ancestors(supertype)
    return found


def _types_of(key: str) -> set[str]:
    if key not in INSTANCES:
        return set()
    return set().union(*(_ancestors(type_key) for type_key, _ in INSTANCES[key][2]))


def _item(key: str) -> dict[str, Any]:
    facets = INSTANCES[key][2] if key in INSTANCES else []
    return {"latex": OBJECTS[key][0], "facets": [data for _, data in facets]}


def _fingerprints(key: str) -> set[str]:
    return {fingerprint(data) for _, data in INSTANCES[key][2]} if key in INSTANCES else set()


CODE = {
    operator: (IMPLEMENTATION_DIR / f"{filename}.py").read_text()
    for operator, filename in IMPLEMENTATIONS.items()
}
DOMAINS: dict[str, set[str]] = {}
for _operator, _domain, _ in SIGNATURES:
    DOMAINS.setdefault(_operator, set()).add(_domain)


def _probe(key: str) -> tuple[str, list[str], float]:
    implementations = [{"id": operator, "code": code} for operator, code in CODE.items()]
    started = time.process_time()
    applicable = json.loads(_scope["probe"](json.dumps(_item(key)), json.dumps(implementations)))
    return key, applicable["applicable"], time.process_time() - started


def _check_relation(index: int) -> list[str]:
    operator, inputs, outputs = RELATIONS[index]
    label = f"{operator}({', '.join(inputs)}) = {', '.join(outputs)}"
    code = CODE[operator]
    accepted = json.loads(
        _scope["probe"](json.dumps(_item(inputs[0])), json.dumps([{"id": operator, "code": code}]))
    )["applicable"]
    if operator not in accepted:
        return [] if index in ASSERTED else [f"{label}: accepts() rejects {inputs[0]}"]
    try:
        computed = json.loads(_scope["run"](code, json.dumps([_item(key) for key in inputs])))
    except Exception as error:
        return [f"{label}: compute() raised {type(error).__name__}: {error}"]
    produced = computed["outputs"]
    if len(produced) != len(outputs):
        return [f"{label}: computed {len(produced)} outputs, seeded {len(outputs)}"]
    return [
        f"{label}: output {position} computed {value['data']} ({value['latex']})"
        for position, (key, value) in enumerate(zip(outputs, produced, strict=True))
        if value["data"] is None or fingerprint(value["data"]) not in _fingerprints(key)
    ]


def _typing_failures() -> list[str]:
    failures = []
    for operator, inputs, outputs in RELATIONS:
        held = _types_of(inputs[0])
        typed = inputs[0] in INSTANCES
        codomains = {c for o, d, c in SIGNATURES if o == operator and (d in held or not typed)}
        label = f"{operator}({', '.join(inputs)})"
        if not typed and not codomains:
            continue
        if not codomains:
            failures.append(f"{label}: no signature of {operator} has {inputs[0]} in its domain")
            continue
        failures.extend(
            f"{label}: output {key} lies in no codomain of {operator} on {inputs[0]}"
            for key in outputs
            if not _types_of(key) & codomains
        )
    return failures


def main() -> int:
    failures = _typing_failures()
    failures.extend(
        f"{operator} has an implementation but no signature"
        for operator in IMPLEMENTATIONS
        if operator not in DOMAINS
    )
    tested = [i for i, (operator, _, _) in enumerate(RELATIONS) if operator in CODE]
    untested = sorted(set(CODE) - {RELATIONS[i][0] for i in tested if i not in ASSERTED})
    failures.extend(f"{name} has an implementation but no seeded relation" for name in untested)

    with multiprocessing.Pool(initializer=_load_sandbox) as pool:
        for found in pool.imap(_check_relation, tested):
            failures.extend(found)
        probes = list(pool.imap_unordered(_probe, list(OBJECTS)))

    slowest = max(probes, key=lambda probe: probe[2])
    for key, applicable, seconds in probes:
        if seconds > SLOW_PROBE_SECONDS:
            failures.append(f"probing {key} against every implementation took {seconds:.1f}s")
        held = _types_of(key)
        failures.extend(
            f"{operator} accepts {key}, which lies outside its domain"
            for operator in applicable
            if not held & DOMAINS.get(operator, set())
        )

    for failure in failures:
        print(f"FAIL {failure}")
    print(
        f"{len(tested)} seeded relations run through {len(CODE)} implementations; "
        f"{len(probes)} objects probed (slowest {slowest[0]}, {slowest[2]:.2f}s); "
        f"{len(failures)} failures; operators without an implementation: "
        f"{len(OPERATORS) - len(CODE)}"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
