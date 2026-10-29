import csv
import functools
import itertools
import json
import pathlib
import sys
from collections.abc import Iterator

import sympy
from snapshot_typing import load_prelude, matrix_types, most_specific, polynomial_types

Edge = tuple[int, int]
ALL_GRAPHS = ["graph2.g6", "graph3.g6", "graph4.g6", "graph5.g6"]
TREES = [f"tree{order}.{diameter}.txt" for order in (6, 7, 8) for diameter in range(2, order)]
CONNECTED_6 = "graph6c.g6"
PLANAR_CONNECTED = {5: "planar_conn.5.g6", 6: "planar_conn.6.g6"}
MAX_ADJACENCY_ORDER = 4
COLUMNS = [
    "file",
    "index",
    "line",
    "order",
    "edges",
    "types",
    "spanning_trees",
    "chromatic_data",
    "chromatic_latex",
    "chromatic_types",
    "planar",
    "planarity_file",
    "adjacency_types",
]
OUT = pathlib.Path(__file__).resolve().parent / "seed_data" / "sources" / "mckay" / "graphs.tsv"

X = sympy.Symbol("x")
PRELUDE = load_prelude()


def decode(line: str) -> tuple[int, list[Edge]]:
    if " " in line:
        ends = [int(v) for v in line.split()]
        pairs = zip(ends[::2], ends[1::2], strict=True)
        return max(ends) + 1, sorted((min(u, v), max(u, v)) for u, v in pairs)
    order = ord(line[0]) - 63
    bits = [(ord(c) - 63) >> shift & 1 for c in line[1:] for shift in range(5, -1, -1)]
    pairs = [(i, j) for j in range(1, order) for i in range(j)]
    return order, sorted(pair for pair, bit in zip(pairs, bits, strict=False) if bit)


def _canonical(order: int, edges: list[Edge]) -> tuple[Edge, ...]:
    return min(
        tuple(sorted((min(p[u], p[v]), max(p[u], p[v])) for u, v in edges))
        for p in itertools.permutations(range(order))
    )


def _components(order: int, edges: list[Edge]) -> list[set[int]]:
    parent = list(range(order))

    def find(v: int) -> int:
        while parent[v] != v:
            v = parent[v]
        return v

    for u, v in edges:
        parent[find(u)] = find(v)
    groups: dict[int, set[int]] = {}
    for v in range(order):
        groups.setdefault(find(v), set()).add(v)
    return list(groups.values())


def _is_bipartite(order: int, edges: list[Edge]) -> bool:
    colour: dict[int, int] = {}
    neighbours: dict[int, list[int]] = {v: [] for v in range(order)}
    for u, v in edges:
        neighbours[u].append(v)
        neighbours[v].append(u)
    for start in range(order):
        if start in colour:
            continue
        colour[start] = 0
        stack = [start]
        while stack:
            v = stack.pop()
            for w in neighbours[v]:
                if w not in colour:
                    colour[w] = 1 - colour[v]
                    stack.append(w)
                elif colour[w] == colour[v]:
                    return False
    return True


def _spanning_trees(order: int, edges: list[Edge]) -> int:
    return sum(
        1
        for chosen in itertools.combinations(edges, order - 1)
        if len(_components(order, list(chosen))) == 1
    )


@functools.cache
def _deletion_contraction(order: int, edges: frozenset[Edge]) -> tuple[int, ...]:
    if not edges:
        return (0,) * order + (1,)
    u, v = min(edges)
    rest = edges - {(u, v)}
    merged = frozenset(
        (min(a, b) - (min(a, b) > v), max(a, b) - (max(a, b) > v))
        for a, b in ((u if a == v else a, u if b == v else b) for a, b in rest)
        if a != b
    )
    deleted = _deletion_contraction(order, rest)
    contracted = (*_deletion_contraction(order - 1, merged), 0)
    return tuple(d - c for d, c in zip(deleted, contracted, strict=True))


def _chromatic(order: int, edges: list[Edge]) -> sympy.Expr:
    coefficients = _deletion_contraction(order, frozenset(edges))
    return sympy.Add(*(c * X**power for power, c in enumerate(coefficients)))


def _read(path: pathlib.Path) -> list[str]:
    return [line for line in path.read_text().splitlines() if line.strip()]


def _graphs(cache: pathlib.Path) -> Iterator[tuple[str, int, str]]:
    for name in ALL_GRAPHS:
        yield from ((name, i, line) for i, line in enumerate(_read(cache / name), 1))
    for name in TREES:
        yield from ((name, i, line) for i, line in enumerate(_read(cache / "trees" / name), 1))
    planar_six = {_canonical(6, decode(line)[1]) for line in _read(cache / PLANAR_CONNECTED[6])}
    for i, line in enumerate(_read(cache / CONNECTED_6), 1):
        if _canonical(6, decode(line)[1]) not in planar_six:
            yield CONNECTED_6, i, line


def _planarity(cache: pathlib.Path, order: int, edges: list[Edge]) -> tuple[bool, str]:
    components = _components(order, edges)
    if order <= 4 or (len(components) == 1 and len(edges) == order - 1):
        return True, ""
    if len(components) > 1:
        return all(len(c) <= 4 for c in components), ""
    listed = PLANAR_CONNECTED[order]
    planar = {_canonical(order, decode(line)[1]) for line in _read(cache / listed)}
    return _canonical(order, edges) in planar, listed


def _types(order: int, edges: list[Edge], planar: bool) -> list[str]:
    degrees = {sum(v in e for e in edges) for v in range(order)}
    found = set()
    if len(_components(order, edges)) == 1 and len(edges) == order - 1:
        found.add("Trees")
    if _is_bipartite(order, edges):
        found.add("BipartiteGraphs")
    if planar:
        found.add("PlanarGraphs")
    if len(degrees) == 1:
        found.add("RegularGraphs")
        if degrees == {order - 1}:
            found.add("CompleteGraphs")
    return most_specific(found) or ["Graphs"]


def _row(cache: pathlib.Path, file: str, index: int, line: str) -> dict[str, str]:
    order, edges = decode(line)
    planar, planarity_file = _planarity(cache, order, edges)
    types = _types(order, edges, planar)
    chromatic = _chromatic(order, edges)
    if "Trees" in types and chromatic != sympy.expand(X * (X - 1) ** (order - 1)):
        raise ValueError(f"{line}: deletion-contraction disagrees with x(x - 1)^(n - 1)")
    adjacency = [[int((min(i, j), max(i, j)) in edges) for j in range(order)] for i in range(order)]
    return {
        "file": file,
        "index": str(index),
        "line": line,
        "order": str(order),
        "edges": json.dumps(edges),
        "types": ",".join(types),
        "spanning_trees": str(_spanning_trees(order, edges)),
        "chromatic_data": json.dumps(PRELUDE["to_data"](chromatic)),
        "chromatic_latex": sympy.latex(chromatic),
        "chromatic_types": ",".join(polynomial_types(chromatic, X)),
        "planar": "Y" if planar else "N",
        "planarity_file": planarity_file,
        "adjacency_types": ",".join(matrix_types(adjacency))
        if order <= MAX_ADJACENCY_ORDER
        else "",
    }


def main(cache_dir: str) -> None:
    cache = pathlib.Path(cache_dir)
    rows = [_row(cache, *graph) for graph in _graphs(cache)]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, COLUMNS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} graphs to {OUT}")


if __name__ == "__main__":
    main(sys.argv[1])
