import csv
import itertools
import json
import pathlib

import numpy as np
import regina
import snappy
import spherogram
import sympy
from snapshot_typing import load_prelude, matrix_types, most_specific, polynomial_types

SCRIPTS = pathlib.Path(__file__).resolve().parent
IMPLEMENTATIONS = SCRIPTS / "implementations"
KNOTINFO = SCRIPTS / "seed_data" / "sources" / "knotinfo" / "knots.tsv"
OUT = SCRIPTS / "seed_data" / "sources" / "positroids" / "positroids.tsv"
EVERY_KNOT_POSITROID_UP_TO = 7
ORBITS_OF = [
    (4, 5, 6, 7, 8, 9, 10, 11),
    (3, 5, 7, 8, 9, 10, 11, 15, 13),
    (3, 5, 7, 8, 9, 10, 13, 11, 15),
    (3, 5, 8, 7, 9, 10, 11, 13, 15),
    (3, 6, 8, 7, 10, 9, 11, 13, 14),
    (4, 5, 8, 7, 9, 10, 12, 11, 15),
    (4, 6, 8, 7, 10, 9, 12, 11, 14),
    (4, 5, 7, 8, 9, 10, 11, 12, 15),
    (4, 6, 7, 8, 10, 9, 11, 12, 14),
]
SEARCH_STATES = 150_000
COLUMNS = [
    "window",
    "k",
    "rotated",
    "reflected",
    "dual",
    "knot",
    "braid",
    "quiver",
    "quiver_types",
    "seed",
    "seed_types",
    "coxeter",
    "coxeter_latex",
    "coxeter_types",
    "alexander",
    "alexander_latex",
    "alexander_types",
    "negated",
    "negated_latex",
    "negated_types",
]

PRELUDE = load_prelude()
X = sympy.Symbol("x")


def _implementation(name: str) -> dict[str, object]:
    scope = dict(PRELUDE["namespace"]())
    source = (IMPLEMENTATIONS / f"{name}.py").read_text()
    exec(compile(source, f"{name}.py", "exec"), scope)  # noqa: S102
    return scope


ROTATE, REFLECT, DUAL = (_implementation(f"{s}_positroid") for s in ("rotate", "reflect", "dual"))
BRAID = _implementation("positroid_braid")
QUIVER = _implementation("cluster_quiver")
COXETER = _implementation("coxeter_polynomial")
ALEXANDER = _implementation("closure_alexander_polynomial")
NEGATE = _implementation("negate_variable")


def _run(scope: dict[str, object], value: object) -> object:
    accepts, compute = scope["accepts"], scope["compute"]
    if not callable(accepts) or not callable(compute):
        raise TypeError("an implementation defines accepts and compute")
    return compute(value) if accepts(value) else None


def _knot_positroids(n: int) -> list[tuple[int, ...]]:
    windows = []
    for rest in itertools.permutations(range(2, n + 1)):
        cycle = (1, *rest)
        image = dict(itertools.pairwise((*cycle, 1)))
        windows.append(tuple(image[i] if image[i] > i else image[i] + n for i in range(1, n + 1)))
    return windows


def _orbit(window: tuple[int, ...]) -> set[tuple[int, ...]]:
    seen, pending = {window}, [window]
    while pending:
        current = PRELUDE["Positroid"](pending.pop())
        for scope in (ROTATE, REFLECT, DUAL):
            image = _run(scope, current)
            found = tuple(image.window)  # type: ignore[attr-defined]
            if found not in seen:
                seen.add(found)
                pending.append(found)
    return seen


def _homfly(word: list[int]) -> str:
    if not word:
        return "1"
    link = spherogram.Link(spherogram.ClosedBraid(word).PD_code())
    link.simplify("global")
    if not link.crossings:
        return "1"
    pd = [[strand + 1 for strand in crossing] for crossing in link.PD_code()]
    return str(regina.Link.fromPD(pd).homflyAZ(regina.Algorithm.Treewidth))


def _knotinfo_names() -> dict[str, str]:
    names = {"1": "0_1"}
    with KNOTINFO.open(encoding="utf-8") as source:
        for row in csv.DictReader(source, delimiter="\t"):
            words = json.loads(row["braid_notation"])
            word = words[0] if isinstance(words[0], list) else words
            names.setdefault(_homfly(word), row["name"])
    return names


def _identify(word: list[int], names: dict[str, str]) -> str:
    homfly = _homfly(word)
    if homfly in names:
        return names[homfly]
    link = spherogram.Link(spherogram.ClosedBraid(word).PD_code())
    link.simplify("global")
    exterior = snappy.Manifold(link.exterior())
    for found in exterior.identify():
        label = str(found).split("(")[0]
        if label.startswith("K") and ("a" in label or "n" in label):
            crossings, _, index = label[1:].replace("a", " a").replace("n", " n").partition(" ")
            name = f"{crossings}{index[0]}_{index[1:]}"
            names[homfly] = name
            return name
    raise ValueError(f"cannot name the closure of {word}")


def _mutate(b: np.ndarray, k: int) -> np.ndarray:
    column, row = b[:, k], b[k, :]
    c = b + (np.abs(column)[:, None] * row[None, :] + column[:, None] * np.abs(row)[None, :]) // 2
    c[k, :], c[:, k] = -b[k, :], -b[:, k]
    np.fill_diagonal(c, 0)
    return c


def _is_acyclic(b: np.ndarray) -> bool:
    arrows = b > 0
    indegree = arrows.sum(0).copy()
    ready = [int(j) for j in np.where(indegree == 0)[0]]
    seen = 0
    while ready:
        v = ready.pop()
        seen += 1
        for j in np.where(arrows[v])[0]:
            indegree[j] -= 1
            if indegree[j] == 0:
                ready.append(int(j))
    return seen == len(b)


def _shape(b: np.ndarray) -> tuple[int, ...]:
    labels = [0] * len(b)
    for _ in range(3):
        labels = [
            hash((labels[i], tuple(sorted((int(b[i][j]), labels[j]) for j in np.nonzero(b[i])[0]))))
            for i in range(len(b))
        ]
    return tuple(sorted(labels))


def _three_cycles(b: np.ndarray) -> int:
    arrows = (b > 0).astype(np.int64)
    return int(np.trace(arrows @ arrows @ arrows))


def _acyclic_seed(rows: list[list[int]]) -> list[list[int]] | None:
    start = np.array(rows, dtype=np.int64)
    if _is_acyclic(start):
        return rows
    beam, seen = [start], {_shape(start)}
    for _ in range(60):
        candidates = []
        for q in beam:
            for k in range(len(q)):
                c = _mutate(q, k)
                if np.abs(c).max() > 5 or _shape(c) in seen:
                    continue
                seen.add(_shape(c))
                if _is_acyclic(c):
                    return c.tolist()
                weight = 100 * _three_cycles(c) + int(np.abs(c).sum())
                candidates.append((weight, c))
            if len(seen) > SEARCH_STATES:
                return None
        if not candidates:
            return None
        candidates.sort(key=lambda item: item[0])
        beam = [c for _, c in candidates[:800]]
    return None


def _polynomial_columns(value: object, prefix: str) -> dict[str, str]:
    if value is None:
        return {prefix: "", f"{prefix}_latex": "", f"{prefix}_types": ""}
    expression = sympy.expand(value)
    return {
        prefix: json.dumps(PRELUDE["to_data"](expression)),
        f"{prefix}_latex": sympy.latex(expression),
        f"{prefix}_types": ",".join(polynomial_types(expression, X)),
    }


def _matrix_types(rows: list[list[int]], kind: str) -> str:
    return ",".join(most_specific({*matrix_types(rows), kind}))


def _row(window: tuple[int, ...], names: dict[str, str]) -> dict[str, str]:
    positroid = PRELUDE["Positroid"](window)
    braid = _run(BRAID, positroid)
    word = list(braid.word)  # type: ignore[attr-defined]
    images = [_run(scope, positroid) for scope in (ROTATE, REFLECT, DUAL)]
    row = {
        "window": json.dumps(list(window)),
        "k": str(sum(1 for x in window if x > len(window))),
        "rotated": json.dumps(list(images[0].window)),  # type: ignore[attr-defined]
        "reflected": json.dumps(list(images[1].window)),  # type: ignore[attr-defined]
        "dual": json.dumps(list(images[2].window)),  # type: ignore[attr-defined]
        "knot": _identify(word, names),
        "braid": json.dumps(word),
        "quiver": "",
        "quiver_types": "",
        "seed": "",
        "seed_types": "",
    }
    quiver = _run(QUIVER, positroid)
    coxeter = None
    if quiver is not None:
        rows = [[int(x) for x in r] for r in quiver.tolist()]  # type: ignore[attr-defined]
        acyclic = _is_acyclic(np.array(rows, dtype=np.int64))
        row["quiver"] = json.dumps(rows)
        row["quiver_types"] = _matrix_types(
            rows, "AcyclicExchangeMatrices" if acyclic else "ExchangeMatrices"
        )
        seed = _acyclic_seed(rows)
        if seed is not None:
            row["seed"] = json.dumps(seed)
            row["seed_types"] = _matrix_types(seed, "AcyclicExchangeMatrices")
            coxeter = _run(COXETER, PRELUDE["Matrix"](seed))
    alexander = _run(ALEXANDER, braid)
    negated = _run(NEGATE, alexander) if alexander is not None else None
    row |= _polynomial_columns(coxeter, "coxeter")
    row |= _polynomial_columns(alexander, "alexander")
    row |= _polynomial_columns(negated, "negated")
    return row


def main() -> None:
    windows = set()
    for n in range(2, EVERY_KNOT_POSITROID_UP_TO + 1):
        windows |= set(_knot_positroids(n))
    for window in ORBITS_OF:
        windows |= _orbit(window)
    names = _knotinfo_names()
    rows = [_row(window, names) for window in sorted(windows, key=lambda w: (len(w), w))]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, COLUMNS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} positroids to {OUT}")


if __name__ == "__main__":
    main()
