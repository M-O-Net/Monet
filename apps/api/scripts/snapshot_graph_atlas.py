import csv
import itertools
import json
import multiprocessing
import pathlib

import networkx as nx
import sympy
from networkx.generators.atlas import graph_atlas_g
from snapshot_mckay import chromatic_polynomial, graph_types, spanning_trees
from snapshot_typing import load_prelude, matrix_types, polynomial_types

Edge = tuple[int, int]
MAX_ATLAS_ORDER = 7
MAX_CHROMATIC_ORDER = 12
NAMED = [
    "cubical_graph",
    "sedgewick_maze_graph",
    "krackhardt_kite_graph",
    "petersen_graph",
    "chvatal_graph",
    "frucht_graph",
    "icosahedral_graph",
    "truncated_tetrahedron_graph",
    "heawood_graph",
    "florentine_families_graph",
    "moebius_kantor_graph",
]
COLUMNS = [
    "entry",
    "name",
    "order",
    "edges",
    "types",
    "planar",
    "spanning_trees",
    "chromatic_data",
    "chromatic_latex",
    "chromatic_types",
    "adjacency_types",
    "characteristic_data",
    "characteristic_latex",
    "characteristic_types",
]
OUT = (
    pathlib.Path(__file__).resolve().parent / "seed_data" / "sources" / "graph_atlas" / "graphs.tsv"
)

X = sympy.Symbol("x")
PRELUDE = load_prelude()
ATLAS = graph_atlas_g()


def _best_labelling(g: nx.Graph) -> tuple[tuple[int, ...], list[int]]:
    classes: dict[int, list[int]] = {}
    for vertex in g:
        classes.setdefault(g.degree(vertex), []).append(vertex)
    pairs = list(itertools.combinations(range(g.number_of_nodes()), 2))
    best: tuple[tuple[int, ...], list[int]] | None = None
    for combination in itertools.product(
        *(itertools.permutations(classes[d]) for d in sorted(classes))
    ):
        order = [vertex for group in combination for vertex in group]
        bits = tuple(int(g.has_edge(order[i], order[j])) for i, j in pairs)
        if best is None or bits > best[0]:
            best = (bits, order)
    if best is None:
        raise ValueError("a graph with no vertices has no labelling")
    return best


def canonical_edges(g: nx.Graph) -> list[Edge]:
    complement = nx.complement(g)
    sparser = min(
        (g, complement),
        key=lambda h: (h.number_of_edges(), [-bit for bit in _best_labelling(h)[0]]),
    )
    position = {vertex: i for i, vertex in enumerate(_best_labelling(sparser)[1])}
    return sorted(
        (min(position[u], position[v]), max(position[u], position[v])) for u, v in g.edges
    )


def _connected_name(g: nx.Graph) -> str | None:
    order, size = g.number_of_nodes(), g.number_of_edges()
    degrees = sorted(degree for _, degree in g.degree())
    if size == order * (order - 1) // 2:
        return f"K_{{{order}}}"
    if order >= 3 and degrees == [2] * order:
        return f"C_{{{order}}}"
    if size == order - 1 and degrees == [1, 1] + [2] * (order - 2):
        return f"P_{{{order}}}"
    if nx.is_bipartite(g):
        left, right = nx.bipartite.sets(g)
        if size == len(left) * len(right):
            smaller, larger = sorted((len(left), len(right)))
            return f"K_{{{smaller},{larger}}}"
    return None


def graph_name(g: nx.Graph) -> str | None:
    components = sorted(
        (g.subgraph(part) for part in nx.connected_components(g)),
        key=lambda c: (-c.number_of_nodes(), -c.number_of_edges()),
    )
    names = [_connected_name(component) for component in components]
    return None if None in names else r" \sqcup ".join(map(str, names))


def _row(entry: str, name: str, g: nx.Graph, edges: list[Edge]) -> dict[str, str]:
    order = g.number_of_nodes()
    planar = nx.check_planarity(g)[0]
    adjacency = [[int((min(i, j), max(i, j)) in edges) for j in range(order)] for i in range(order)]
    characteristic = sympy.Matrix(adjacency).charpoly(X).as_expr()
    row = {
        "entry": entry,
        "name": name,
        "order": str(order),
        "edges": json.dumps(edges),
        "types": ",".join(graph_types(order, edges, planar)),
        "planar": "Y" if planar else "N",
        "spanning_trees": str(
            spanning_trees(order, edges)
            if order <= MAX_ATLAS_ORDER
            else (sympy.diag(*map(sum, adjacency)) - sympy.Matrix(adjacency))[1:, 1:].det()
        ),
        "chromatic_data": "",
        "chromatic_latex": "",
        "chromatic_types": "",
        "adjacency_types": ",".join(matrix_types(adjacency)),
        "characteristic_data": json.dumps(PRELUDE["to_data"](characteristic)),
        "characteristic_latex": sympy.latex(characteristic),
        "characteristic_types": ",".join(polynomial_types(characteristic, X)),
    }
    if order <= MAX_CHROMATIC_ORDER:
        chromatic = chromatic_polynomial(order, edges)
        row["chromatic_data"] = json.dumps(PRELUDE["to_data"](chromatic))
        row["chromatic_latex"] = sympy.latex(chromatic)
        row["chromatic_types"] = ",".join(polynomial_types(chromatic, X))
    return row


def _atlas_row(index: int) -> dict[str, str]:
    g = ATLAS[index]
    name = graph_name(g) or rf"\mathrm{{G}}_{{{index}}}"
    return _row(f"G{index}", name, g, canonical_edges(g))


def _named_row(generator: str) -> dict[str, str]:
    g = nx.convert_node_labels_to_integers(getattr(nx, generator)())
    edges = sorted((min(u, v), max(u, v)) for u, v in g.edges)
    return _row(generator, "", g, edges)


def main() -> None:
    indices = [i for i, g in enumerate(ATLAS) if g.number_of_nodes() > 0]
    with multiprocessing.Pool() as pool:
        rows = [*pool.imap(_atlas_row, indices), *pool.imap(_named_row, NAMED)]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, COLUMNS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} graphs from networkx {nx.__version__} to {OUT}")


if __name__ == "__main__":
    main()
