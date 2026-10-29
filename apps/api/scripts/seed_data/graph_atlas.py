import csv
import json
import pathlib

from seed_data import (
    analysis,
    atlas,
    combinatorics,
    cremona,
    fields,
    findstat,
    geometry,
    graphs,
    groups,
    knotinfo,
    linear_algebra,
    lmfdb,
    mckay,
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
    fingerprint,
    graph,
    graph_complement,
    held_by,
    holdings,
    instance,
    isomorphic,
    matrix_instance,
    symmetric_permgroup,
)
from seed_data.sources import GRAPH_ATLAS, NETWORKX

SNAPSHOT = pathlib.Path(__file__).resolve().parent / "sources" / "graph_atlas" / "graphs.tsv"
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
    findstat,
    lmfdb,
    cremona,
    atlas,
    knotinfo,
    mckay,
)
NAMED: dict[str, tuple[str, str, str | None]] = {
    "cubical_graph": ("Cubical graph", "small", "Hypercube_graph"),
    "sedgewick_maze_graph": ("Sedgewick maze graph", "small", None),
    "krackhardt_kite_graph": ("Krackhardt kite graph", "small", "Krackhardt_kite_graph"),
    "petersen_graph": ("Petersen graph", "small", "Petersen_graph"),
    "chvatal_graph": (r"Chv\'atal graph", "small", "Chv%C3%A1tal_graph"),
    "frucht_graph": ("Frucht graph", "small", "Frucht_graph"),
    "icosahedral_graph": ("Icosahedral graph", "small", "Regular_icosahedron"),
    "truncated_tetrahedron_graph": (
        "Truncated tetrahedron graph",
        "small",
        "Truncated_tetrahedron",
    ),
    "heawood_graph": ("Heawood graph", "small", "Heawood_graph"),
    "florentine_families_graph": ("Florentine families graph", "social", None),
    "moebius_kantor_graph": (
        r"M\"obius--Kantor graph",
        "small",
        "M%C3%B6bius%E2%80%93Kantor_graph",
    ),
}
PLANARITY = NETWORKX.cite(
    "algorithms/generated/networkx.algorithms.planarity.check_planarity.html",
    label="check_planarity",
)
WIKI = "https://en.wikipedia.org/wiki/"

INSTANCES: dict[str, Instance] = {}
REFERENCES: dict[str, list[Reference]] = {}
RELATIONS: list[RelationSpec] = []
ASSERTED: list[RelationSpec] = []

HELD = holdings(*ELSEWHERE)
Invariant = tuple[int, int, tuple[int, ...]]


def _invariant(data: Data) -> Invariant:
    order, edges = data["graph"]["order"], data["graph"]["edges"]
    degrees = [0] * order
    for u, v in edges:
        degrees[u] += 1
        degrees[v] += 1
    return order, len(edges), tuple(sorted(degrees))


SEEDED: dict[Invariant, list[tuple[str, Data]]] = {}
for _area in ELSEWHERE:
    for _key, (_, _, _facets) in getattr(_area, "INSTANCES", {}).items():
        for _data in {fingerprint(d): d for _, d in _facets if "graph" in d}.values():
            SEEDED.setdefault(_invariant(_data), []).append((str(_key), _data))


def _seeded_isomorphs(data: Data) -> list[tuple[str, Data]]:
    candidates = SEEDED.get(_invariant(data), [])
    return [(key, seeded) for key, seeded in candidates if isomorphic(seeded, data)]


def _hold(key: str, specimen: Instance) -> str:
    held = fingerprint(specimen[2][0][1])
    if held not in HELD:
        HELD[held] = key
        INSTANCES[key] = specimen
    return HELD[held]


def _credit(key: str, references: list[Reference]) -> None:
    held = REFERENCES.setdefault(key, [])
    held.extend(reference for reference in references if reference not in held)


def _citations(entry: str) -> list[Reference]:
    if entry not in NAMED:
        return [GRAPH_ATLAS.cite(entry)]
    _, module, article = NAMED[entry]
    generator = NETWORKX.cite(
        f"generated/networkx.generators.{module}.{entry}.html", label=f"{entry}()"
    )
    return [generator] if article is None else [("Wikipedia", WIKI + article), generator]


def _specimen(row: dict[str, str], data: Data) -> Instance:
    entry, order = row["entry"], data["graph"]["order"]
    size = len(data["graph"]["edges"])
    if entry in NAMED:
        return instance(rf"\text{{{NAMED[entry][0]}}}", data, row["types"].split(","))
    description = (
        f"Graph {entry} of Read and Wilson's An Atlas of Graphs: {order} vertices, {size} edges."
    )
    return instance(row["name"], data, row["types"].split(","), description)


def _place(row: dict[str, str]) -> list[tuple[str, Data]]:
    data = graph(int(row["order"]), [(u, v) for u, v in json.loads(row["edges"])])
    exact = HELD.get(fingerprint(data))
    if exact is not None:
        return [(exact, data)]
    isomorphs = _seeded_isomorphs(data)
    if isomorphs:
        return isomorphs
    complements = _seeded_isomorphs(graph_complement(data))
    if complements:
        data = graph_complement(complements[0][1])
    key = row["entry"] if row["entry"] in NAMED else f"atlas_{row['entry']}"
    return [(_hold(key, _specimen(row, data)), data)]


def _relate(row: dict[str, str], key: str, data: Data) -> None:
    entry, order = row["entry"], data["graph"]["order"]
    present = {tuple(e) for e in data["graph"]["edges"]}
    adjacency = [
        [int((min(i, j), max(i, j)) in present) for j in range(order)] for i in range(order)
    ]
    matrix_key = _hold(
        f"adjacency_{key}", matrix_instance(adjacency, row["adjacency_types"].split(","))
    )
    characteristic = instance(
        row["characteristic_latex"],
        json.loads(row["characteristic_data"]),
        row["characteristic_types"].split(","),
    )
    RELATIONS.extend(
        [
            ("AdjacencyMatrix", [key], [matrix_key]),
            (
                "CharacteristicPolynomial",
                [matrix_key],
                [_hold(f"characteristic_{entry}", characteristic)],
            ),
            ("SpanningTreeCount", [key], [int(row["spanning_trees"])]),
        ]
    )
    if row["chromatic_data"]:
        chromatic = instance(
            row["chromatic_latex"],
            json.loads(row["chromatic_data"]),
            row["chromatic_types"].split(","),
        )
        RELATIONS.append(("ChromaticPolynomial", [key], [_hold(f"chromatic_{entry}", chromatic)]))
    planar = "true" if row["planar"] == "Y" else "false"
    ASSERTED.append(("IsPlanar", [key], [planar], [PLANARITY]))


def _import(row: dict[str, str]) -> list[tuple[str, Data]]:
    placed = _place(row)
    for key, data in placed:
        _credit(key, _citations(row["entry"]))
        _relate(row, key, data)
    return placed


with SNAPSHOT.open(encoding="utf-8") as _snapshot:
    _placed = [
        placed for row in csv.DictReader(_snapshot, delimiter="\t") for placed in _import(row)
    ]
for _holder, _data in _placed:
    _complement_holder = HELD.get(fingerprint(graph_complement(_data)))
    if _complement_holder is not None:
        RELATIONS.append(("Complement", [_holder], [_complement_holder]))
    _order, _edges = _data["graph"]["order"], _data["graph"]["edges"]
    _automorphisms = held_by(symmetric_permgroup(_order), groups)
    if _automorphisms is not None and len(_edges) in (0, _order * (_order - 1) // 2):
        RELATIONS.append(("AutomorphismGroup", [_holder], [_automorphisms]))
