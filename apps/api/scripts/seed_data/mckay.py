import csv
import json
import pathlib
from collections import Counter

from seed_data import (
    analysis,
    combinatorics,
    fields,
    geometry,
    graphs,
    groups,
    knotinfo,
    linear_algebra,
    numbers,
    polynomials,
    sequences,
    topology,
)
from seed_data.build import (
    Data,
    Instance,
    Reference,
    RelationSpec,
    graph,
    graph_complement,
    held_by,
    instance,
    isomorphic,
    matrix_instance,
    symmetric_permgroup,
)
from seed_data.sources import MCKAY

Edge = tuple[int, int]
SNAPSHOT = pathlib.Path(__file__).resolve().parent / "sources" / "mckay" / "graphs.tsv"
ELSEWHERE = (
    numbers,
    sequences,
    linear_algebra,
    polynomials,
    analysis,
    combinatorics,
    graphs,
    groups,
    fields,
    topology,
    geometry,
    knotinfo,
)
NUMBER_WORDS = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight"}

INSTANCES: dict[str, Instance] = {}
REFERENCES: dict[str, list[Reference]] = {}
RELATIONS: list[RelationSpec] = []
ASSERTED: list[RelationSpec] = []


def _decoded(row: dict[str, str]) -> tuple[int, list[Edge]]:
    return int(row["order"]), [(u, v) for u, v in json.loads(row["edges"])]


SEEDED_GRAPHS = [
    (str(key), facets[0][1])
    for area in ELSEWHERE
    for key, (_, _, facets) in area.INSTANCES.items()
    if "graph" in facets[0][1]
]


def _held(data: Data) -> str | None:
    return held_by(data, *ELSEWHERE) or next(
        (key for key, (_, _, facets) in INSTANCES.items() if facets[0][1] == data), None
    )


def _hold(key: str, specimen: Instance) -> str:
    holder = _held(specimen[2][0][1])
    if holder is None:
        INSTANCES[key] = specimen
        return key
    return holder


def _seeded_isomorph(data: Data) -> tuple[str, Data] | None:
    return next(((key, seeded) for key, seeded in SEEDED_GRAPHS if isomorphic(seeded, data)), None)


def _graph_latex(order: int, edges: list[Edge]) -> str:
    listed = ", ".join(rf"\{{{u}, {v}\}}" for u, v in edges)
    return rf"\left(\left\{{0, \dots, {order - 1}\right\}}, \left\{{{listed}\right\}}\right)"


def _description(file: str, index: str, order: int, counts: Counter[str]) -> str:
    stem = file.rsplit(".", 1)[0]
    vertices = NUMBER_WORDS[order]
    if stem.startswith("tree"):
        diameter = stem.split(".")[1]
        return (
            f"Tree {index} of the {counts[file]} on {vertices} vertices with diameter {diameter} "
            "in McKay's catalogue."
        )
    if stem == "graph6c":
        return (
            f"Connected graph {index} on six vertices in McKay's catalogue, one of the "
            f"{counts[file]} of them that are not planar."
        )
    return f"Graph {index} of the {counts[file]} on {vertices} vertices in McKay's catalogue."


def _new_graph(row: dict[str, str], counts: Counter[str]) -> tuple[str, Data]:
    order, edges = _decoded(row)
    key = f"{row['file'].rsplit('.', 1)[0].replace('.', '_')}_{row['index']}"
    data = graph(order, edges)
    description = _description(row["file"], row["index"], order, counts)
    INSTANCES[key] = instance(
        _graph_latex(order, edges), data, row["types"].split(","), description
    )
    if row["adjacency_types"]:
        adjacency = [
            [int((i, j) in edges or (j, i) in edges) for j in range(order)] for i in range(order)
        ]
        matrix = matrix_instance(adjacency, row["adjacency_types"].split(","))
        RELATIONS.append(("AdjacencyMatrix", [key], [_hold(f"adjacency_{key}", matrix)]))
    return key, data


def _import(row: dict[str, str], counts: Counter[str]) -> tuple[str, Data]:
    data = graph(*_decoded(row))
    exact = _held(data)
    holder, held = (exact, data) if exact else _seeded_isomorph(data) or _new_graph(row, counts)
    REFERENCES.setdefault(holder, []).append(MCKAY.cite(row["file"]))
    chromatic = instance(
        row["chromatic_latex"], json.loads(row["chromatic_data"]), row["chromatic_types"].split(",")
    )
    RELATIONS.extend(
        [
            ("SpanningTreeCount", [holder], [int(row["spanning_trees"])]),
            ("ChromaticPolynomial", [holder], [_hold(f"chromatic_{holder}", chromatic)]),
        ]
    )
    planar = "true" if row["planar"] == "Y" else "false"
    if row["planarity_file"]:
        ASSERTED.append(("IsPlanar", [holder], [planar], [MCKAY.cite(row["planarity_file"])]))
    else:
        ASSERTED.append(("IsPlanar", [holder], [planar]))
    return holder, held


with SNAPSHOT.open(encoding="utf-8") as _snapshot:
    _rows = list(csv.DictReader(_snapshot, delimiter="\t"))
_counts = Counter(row["file"] for row in _rows)
for _holder, _data in dict(_import(row, _counts) for row in _rows).items():
    _complement_holder = _held(graph_complement(_data))
    if _complement_holder is not None:
        RELATIONS.append(("Complement", [_holder], [_complement_holder]))
    _order, _edges = _data["graph"]["order"], _data["graph"]["edges"]
    _automorphisms = held_by(symmetric_permgroup(_order), groups)
    if _automorphisms is not None and len(_edges) in (0, _order * (_order - 1) // 2):
        RELATIONS.append(("AutomorphismGroup", [_holder], [_automorphisms]))
