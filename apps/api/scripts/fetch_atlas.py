"""Harvest KnotInfo and the graph census into scripts/data/, for import_atlas.py to read."""

import argparse
import csv
import datetime
import gzip
import importlib.util
import itertools
import json
import pathlib

import database_knotinfo
import networkx as nx
import sympy
from networkx.generators.atlas import graph_atlas_g
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

SCRIPTS = pathlib.Path(__file__).resolve().parent
REPO = SCRIPTS.parents[2]
DATA = SCRIPTS / "data"

MAX_CROSSING_NUMBER = 11
MAX_CENSUS_VERTICES = 7
MIN_OVERLAY_VERTICES = 8
MAX_OVERLAY_VERTICES = 16


_TRANSFORMATIONS = (*standard_transformations, convert_xor, implicit_multiplication_application)
_T = sympy.Symbol("t")
_X = sympy.Symbol("x")


def _load_render():
    path = REPO / "apps" / "web" / "src" / "sandbox" / "prelude.py"
    spec = importlib.util.spec_from_file_location("monet_prelude", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    prelude = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prelude)
    return prelude.render


render = _load_render()


def _knotinfo_expression(text):
    return parse_expr(text.replace(" ", ""), transformations=_TRANSFORMATIONS)


def _integer(text):
    stripped = text.strip()
    return int(stripped) if stripped.lstrip("-").isdigit() else None


def _boolean(text):
    return {"Y": True, "N": False}.get(text.strip())


def harvest_knots():
    csv.field_size_limit(10**9)
    source = pathlib.Path(database_knotinfo.__file__).parent / "csv_data"
    path = source / "knotinfo_data_complete.csv"
    with path.open(newline="", encoding="utf-8", errors="replace") as handle:
        reader = csv.reader(handle, delimiter="|")
        columns = {name: index for index, name in enumerate(next(reader))}
        next(reader)
        rows = list(reader)

    knots = []
    for row in rows:
        field = {name: row[index].strip() for name, index in columns.items()}
        crossings = _integer(field["crossing_number"])
        if crossings is None or crossings > MAX_CROSSING_NUMBER or crossings == 0:
            continue
        alexander = _knotinfo_expression(field["alexander_polynomial"]).subs(_T, _X)
        jones = _knotinfo_expression(field["jones_polynomial"])
        name = field["name"]
        crossing_text, index = name.split("_", 1)
        knots.append(
            {
                "name": name,
                "latex": rf"\mathrm{{{crossing_text}}}_{{{index}}}",
                "alexander_polynomial": render(sympy.expand(alexander)),
                "jones_polynomial": render(sympy.expand(jones)),
                "crossing_number": crossings,
                "determinant": _integer(field["determinant"]),
                "signature": _integer(field["signature"]),
                "three_genus": _integer(field["three_genus"]),
                "braid_index": _integer(field["braid_index"]),
                "bridge_index": _integer(field["bridge_index"]),
                "arc_index": _integer(field["arc_index"]),
                "unknotting_number": _integer(field["unknotting_number"]),
                "symmetry_type": field["symmetry_type"] or None,
                "alternating": _boolean(field["alternating"]),
                "fibered": _boolean(field["fibered"]),
                "positive": _boolean(field["positive"]),
            }
        )
    return {"release": database_knotinfo.version(), "knots": knots}


def _canonical_permutation(graph):
    order = graph.number_of_nodes()
    classes = {}
    for vertex in graph.nodes():
        classes.setdefault(graph.degree(vertex), []).append(vertex)
    best_bits = None
    best_permutation = None
    groups = [itertools.permutations(classes[degree]) for degree in sorted(classes)]
    for combination in itertools.product(*groups):
        permutation = [vertex for group in combination for vertex in group]
        bits = tuple(
            1 if graph.has_edge(permutation[i], permutation[j]) else 0
            for i in range(order)
            for j in range(i + 1, order)
        )
        if best_bits is None or bits > best_bits:
            best_bits, best_permutation = bits, permutation
    return best_bits, best_permutation


def canonical_rows(graph):
    order = graph.number_of_nodes()
    if order < 2:
        return [[0] * order for _ in range(order)]
    complement = nx.complement(graph)
    edges, complement_edges = graph.number_of_edges(), complement.number_of_edges()
    if edges < complement_edges:
        source, inverted = graph, False
    elif complement_edges < edges:
        source, inverted = complement, True
    else:
        source, inverted = (
            (graph, False)
            if _canonical_permutation(graph)[0] >= _canonical_permutation(complement)[0]
            else (complement, True)
        )
    _, permutation = _canonical_permutation(source)
    rows = [
        [1 if source.has_edge(permutation[i], permutation[j]) else 0 for j in range(order)]
        for i in range(order)
    ]
    if not inverted:
        return rows
    return [[0 if i == j else 1 - rows[i][j] for j in range(order)] for i in range(order)]


def _connected_name(graph):
    order, size = graph.number_of_nodes(), graph.number_of_edges()
    degrees = sorted(degree for _, degree in graph.degree())
    if size == order * (order - 1) // 2:
        return f"K_{{{order}}}"
    if order >= 3 and size == order and degrees == [2] * order:
        return f"C_{{{order}}}"
    if order >= 2 and size == order - 1 and degrees == [1, 1] + [2] * (order - 2):
        return f"P_{{{order}}}"
    if nx.is_bipartite(graph):
        left, right = nx.bipartite.sets(graph)
        if size == len(left) * len(right):
            smaller, larger = sorted((len(left), len(right)))
            return f"K_{{{smaller},{larger}}}"
    return None


def graph_name(graph):
    components = [graph.subgraph(part).copy() for part in nx.connected_components(graph)]
    if len(components) == 1:
        return _connected_name(graph)
    names = []
    for component in sorted(
        components, key=lambda c: (-c.number_of_nodes(), -c.number_of_edges())
    ):
        name = _connected_name(component)
        if name is None:
            return None
        names.append(name)
    return r" \sqcup ".join(names)


def _extend_colouring(graph, vertices, position, colours, assignment):
    if position == len(vertices):
        return True
    vertex = vertices[position]
    for colour in range(colours):
        if all(assignment.get(neighbour) != colour for neighbour in graph.neighbors(vertex)):
            assignment[vertex] = colour
            if _extend_colouring(graph, vertices, position + 1, colours, assignment):
                return True
            del assignment[vertex]
    return False


def _chromatic_number(graph):
    order = graph.number_of_nodes()
    if graph.number_of_edges() == 0:
        return 1 if order else 0
    vertices = list(graph.nodes())
    for colours in range(2, order + 1):
        if _extend_colouring(graph, vertices, 0, colours, {}):
            return colours
    return order


def _is_hamiltonian(graph):
    order = graph.number_of_nodes()
    if order < 3 or not nx.is_connected(graph):
        return False
    start = next(iter(graph.nodes()))
    path, visited = [start], {start}

    def extend():
        if len(path) == order:
            return graph.has_edge(path[-1], start)
        for neighbour in graph.neighbors(path[-1]):
            if neighbour in visited:
                continue
            visited.add(neighbour)
            path.append(neighbour)
            if extend():
                return True
            path.pop()
            visited.remove(neighbour)
        return False

    return extend()


def _spanning_trees(rows):
    order = len(rows)
    if order == 1:
        return 1
    laplacian = sympy.Matrix(
        order,
        order,
        lambda i, j: sum(rows[i]) if i == j else -rows[i][j],
    )
    return int(laplacian.minor_submatrix(0, 0).det())


def _matrix_latex(rows):
    return render(sympy.Matrix(rows))


def _census_invariants(graph, rows):
    order = graph.number_of_nodes()
    connected = nx.is_connected(graph)
    invariants = {
        "number_of_vertices": order,
        "number_of_edges": graph.number_of_edges(),
        "chromatic_number": _chromatic_number(graph),
        "clique_number": nx.max_weight_clique(graph, weight=None)[1],
        "independence_number": nx.max_weight_clique(nx.complement(graph), weight=None)[1],
        "number_of_triangles": sum(nx.triangles(graph).values()) // 3,
        "number_of_spanning_trees": _spanning_trees(rows),
        "is_planar": nx.check_planarity(graph)[0],
        "is_hamiltonian": _is_hamiltonian(graph),
        "is_bipartite": nx.is_bipartite(graph),
    }
    if connected and order > 1:
        invariants["diameter"] = nx.diameter(graph)
    if not nx.is_forest(graph):
        invariants["girth"] = nx.girth(graph)
    return invariants


def harvest_census():
    atlas = graph_atlas_g()
    graphs = []
    keys = {}
    sources = {}
    for index, graph in enumerate(atlas):
        if not 1 <= graph.number_of_nodes() <= MAX_CENSUS_VERTICES:
            continue
        rows = canonical_rows(graph)
        name = graph_name(graph)
        keys[tuple(map(tuple, rows))] = f"atlas:{index}"
        sources[f"atlas:{index}"] = graph
        graphs.append(
            {
                "key": f"atlas:{index}",
                "atlas_index": index,
                "latex": name if name else rf"\mathrm{{G}}_{{{index}}}",
                "matrix_latex": _matrix_latex(rows),
                "rows": rows,
                "invariants": _census_invariants(graph, rows),
                "references": [],
            }
        )
    for entry in graphs:
        order = len(entry["rows"])
        complement = canonical_rows(nx.complement(sources[entry["key"]]))
        entry["complement_key"] = keys.get(tuple(map(tuple, complement)))
        source = nx.Graph(
            (i, j)
            for i in range(order)
            for j in range(i + 1, order)
            if entry["rows"][i][j]
        )
        source.add_nodes_from(range(order))
        line_graph = nx.line_graph(source)
        if 1 <= line_graph.number_of_nodes() <= MAX_CENSUS_VERTICES:
            relabelled = nx.convert_node_labels_to_integers(line_graph)
            entry["line_graph_key"] = keys.get(tuple(map(tuple, canonical_rows(relabelled))))
        else:
            entry["line_graph_key"] = None
        del entry["rows"]
    return graphs


FAMOUS_GRAPHS = {
    "cubical_graph": "Cubical graph",
    "sedgewick_maze_graph": "Sedgewick maze graph",
    "krackhardt_kite_graph": "Krackhardt kite graph",
    "petersen_graph": "Petersen graph",
    "chvatal_graph": "Chvatal graph",
    "frucht_graph": "Frucht graph",
    "icosahedral_graph": "Icosahedral graph",
    "truncated_tetrahedron_graph": "Truncated tetrahedron graph",
    "heawood_graph": "Heawood graph",
    "florentine_families_graph": "Florentine families graph",
    "moebius_kantor_graph": "Moebius-Kantor graph",
}


def harvest_famous():
    graphs = []
    for generator, title in FAMOUS_GRAPHS.items():
        graph = nx.convert_node_labels_to_integers(getattr(nx, generator)())
        order = graph.number_of_nodes()
        if not MIN_OVERLAY_VERTICES <= order <= MAX_OVERLAY_VERTICES:
            raise SystemExit(f"{generator} has {order} vertices, outside the overlay range")
        rows = [[1 if graph.has_edge(i, j) else 0 for j in range(order)] for i in range(order)]
        graphs.append(
            {
                "key": f"famous:{generator}",
                "latex": rf"\text{{{title}}}",
                "matrix_latex": _matrix_latex(rows),
                "invariants": _census_invariants(graph, rows),
                "complement_key": None,
                "line_graph_key": None,
                "references": [
                    ["Wikipedia", f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"]
                ],
            }
        )
    return graphs


def _write(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        json.dump(payload, handle, separators=(",", ":"), sort_keys=True)
    return path.stat().st_size


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-knots", action="store_true")
    parser.add_argument("--skip-graphs", action="store_true")
    arguments = parser.parse_args()
    harvested = datetime.datetime.now(tz=datetime.UTC).date().isoformat()

    if not arguments.skip_knots:
        knots = harvest_knots()
        if len(knots["knots"]) != 801:
            raise SystemExit(f"expected 801 knots, got {len(knots['knots'])}")
        size = _write(
            DATA / "knots.json.gz",
            {"source": "KnotInfo", "harvested": harvested, **knots},
        )
        print(f"knots: {len(knots['knots'])} written ({size / 1000:.0f} kB)")

    if not arguments.skip_graphs:
        census = harvest_census()
        overlay = harvest_famous()
        if len(census) != 1252:
            raise SystemExit(f"expected 1252 census graphs, got {len(census)}")
        size = _write(
            DATA / "graphs.json.gz",
            {
                "source": "networkx: graph_atlas_g (<= 7 vertices) and named graphs (8-16)",
                "harvested": harvested,
                "networkx": nx.__version__,
                "census": census,
                "overlay": overlay,
            },
        )
        named = sum(1 for entry in census if not entry["latex"].startswith(r"\mathrm{G}"))
        print(
            f"graphs: {len(census)} census ({named} named) + {len(overlay)} overlay "
            f"written ({size / 1000:.0f} kB)"
        )


if __name__ == "__main__":
    main()
