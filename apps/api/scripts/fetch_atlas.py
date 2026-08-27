"""Harvest KnotInfo and the graph census into scripts/data/, for import_atlas.py to read."""

import argparse
import csv
import datetime
import gzip
import importlib.util
import itertools
import json
import pathlib
import re

import database_knotinfo
import httpx
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

HOG_ENQUIRY = "https://houseofgraphs.org/api/enquiry"
HOG_VERTEX_INVARIANT = 15
HOG_RANGES = ((1, MAX_CENSUS_VERTICES), (MIN_OVERLAY_VERTICES, 10), (11, MAX_OVERLAY_VERTICES))
HOG_PROSE_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9 \-']*$")
HOG_INVARIANTS = "https://houseofgraphs.org/api/invariants"
HOG_WANTED = {
    "Number of Vertices": "number_of_vertices",
    "Number of Edges": "number_of_edges",
    "Chromatic Number": "chromatic_number",
    "Girth": "girth",
    "Diameter": "diameter",
    "Independence Number": "independence_number",
    "Clique Number": "clique_number",
    "Number of Triangles": "number_of_triangles",
    "Number of Spanning Trees": "number_of_spanning_trees",
    "Planar": "is_planar",
    "Hamiltonian": "is_hamiltonian",
    "Bipartite": "is_bipartite",
}


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


def _characteristic_polynomial(rows):
    return render(sympy.Matrix(rows).charpoly(_X).as_expr())


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


def harvest_census(house_of_graphs):
    atlas = graph_atlas_g()
    graphs = []
    keys = {}
    sources = {}
    for index, graph in enumerate(atlas):
        if not 1 <= graph.number_of_nodes() <= MAX_CENSUS_VERTICES:
            continue
        rows = canonical_rows(graph)
        name = graph_name(graph)
        signature = tuple(map(tuple, rows))
        keys[signature] = f"atlas:{index}"
        sources[f"atlas:{index}"] = graph
        known = house_of_graphs.get(signature)
        if name is None and known is not None:
            name = _hog_latex_name(known)
        graphs.append(
            {
                "key": f"atlas:{index}",
                "atlas_index": index,
                "latex": name if name else rf"\mathrm{{G}}_{{{index}}}",
                "matrix_latex": _matrix_latex(rows),
                "characteristic_polynomial": _characteristic_polynomial(rows),
                "rows": rows,
                "invariants": _census_invariants(graph, rows),
                "references": _hog_reference(known),
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


def _hog_rows(lower, upper, cache):
    stored = cache / f"hog-{lower}-{upper}.json" if cache else None
    if stored is not None and stored.exists():
        return json.loads(stored.read_text())
    body = {
        "invariantEnquiries": [],
        "interestingInvariantEnquiries": [],
        "graphClassEnquiries": [],
        "invariantParityEnquiries": [],
        "textEnquiries": [],
        "formulaEnquiries": [],
        "subgraphEnquiries": [],
        "mostRecent": -1,
        "mostPopular": -1,
        "invariantRangeEnquiries": [
            {"id": 0, "invariantId": HOG_VERTEX_INVARIANT, "from": lower, "to": upper}
        ],
    }
    response = httpx.post(
        HOG_ENQUIRY,
        params={
            "page": 0,
            "size": 8000,
            "sort": "graph_id",
            "sortDir": "asc",
            "offset": 0,
            "lastPageOffset": 0,
            "fullSearch": "true",
            "timeout": 180,
        },
        json=body,
        timeout=600.0,
    )
    response.raise_for_status()
    payload = response.json()
    rows = [
        {
            "graphId": row["graphId"],
            "graphName": row.get("graphName"),
            "canonicalForm": row.get("canonicalForm"),
            "adjacencyList": row["adjacencyList"],
            "invariantValues": row.get("invariantValues") or {},
        }
        for row in payload["_embedded"]["graphSearchModelList"]
    ]
    if len(rows) != payload["page"]["totalElements"]:
        total = payload["page"]["totalElements"]
        raise SystemExit(f"House of Graphs returned {len(rows)} of {total}")
    if stored is not None:
        stored.parent.mkdir(parents=True, exist_ok=True)
        stored.write_text(json.dumps(rows))
    return rows


def _hog_invariant_names(cache):
    stored = cache / "hog-invariants.json" if cache else None
    if stored is not None and stored.exists():
        payload = json.loads(stored.read_text())
    else:
        response = httpx.get(HOG_INVARIANTS, timeout=120.0)
        response.raise_for_status()
        payload = response.json()
        if stored is not None:
            stored.parent.mkdir(parents=True, exist_ok=True)
            stored.write_text(json.dumps(payload))
    return {
        str(entry["entity"]["invariantId"]): (
            entry["entity"]["invariantName"],
            entry["entity"]["typeName"],
        )
        for entry in payload["_embedded"]["invariantModelList"]
    }


def _hog_invariants(row, names):
    """Take House of Graphs' own values rather than recomputing.

    Hamiltonicity and chromatic number are backtracking searches; on sixteen vertices they can
    run for hours, and House of Graphs has already done the work.
    """
    invariants = {}
    for entry in row.get("invariantValues") or []:
        found = names.get(str(entry.get("invariantId")))
        raw = entry.get("invariantValue")
        if found is None or raw is None:
            continue
        label, kind = found
        key = HOG_WANTED.get(label)
        if key is None or not isinstance(raw, (int, float)) or raw != int(raw):
            continue
        invariants[key] = bool(int(raw)) if kind == "b" else int(raw)
    return invariants


def _graph_from_adjacency(adjacency):
    graph = nx.Graph()
    graph.add_nodes_from(range(len(adjacency)))
    for vertex, neighbours in enumerate(adjacency):
        for neighbour in neighbours:
            graph.add_edge(vertex, neighbour)
    return graph


def _hog_reference(row):
    if row is None:
        return []
    return [["House of Graphs", f"https://houseofgraphs.org/graphs/{row['graphId']}"]]


def _hog_latex_name(row):
    prose = _hog_prose_name(row)
    return rf"\text{{{prose}}}" if prose else None


def _hog_prose_name(row):
    name = " ".join((row.get("graphName") or "").split())
    return name if HOG_PROSE_NAME.match(name) else None


def fetch_house_of_graphs(cache):
    """Return {census signature: row} for small graphs, and the named larger rows.

    Our own canonical form permutes within degree classes, which is fine up to seven vertices
    and hopeless at sixteen. Beyond the census we take House of Graphs' canonicalForm, which is
    graph6 out of nauty; the two schemes never have to agree because the vertex counts are
    disjoint.
    """
    small, large = {}, []
    for lower, upper in HOG_RANGES:
        for row in _hog_rows(lower, upper, cache):
            order = len(row["adjacencyList"])
            if order <= MAX_CENSUS_VERTICES:
                graph = _graph_from_adjacency(row["adjacencyList"])
                small[tuple(map(tuple, canonical_rows(graph)))] = row
            elif order <= MAX_OVERLAY_VERTICES and row.get("canonicalForm"):
                large.append(row)
    return small, large


def harvest_named(candidates, names):
    graphs = []
    seen = set()
    for row in sorted(candidates, key=lambda item: item["graphId"]):
        canonical = row["canonicalForm"]
        if canonical in seen:
            continue
        graph = nx.from_graph6_bytes(canonical.encode())
        name = graph_name(graph) or _hog_latex_name(row)
        if name is None:
            continue
        seen.add(canonical)
        order = graph.number_of_nodes()
        rows = [[1 if graph.has_edge(i, j) else 0 for j in range(order)] for i in range(order)]
        graphs.append(
            {
                "key": f"hog:{row['graphId']}",
                "latex": name,
                "matrix_latex": _matrix_latex(rows),
                "characteristic_polynomial": _characteristic_polynomial(rows),
                "invariants": _hog_invariants(row, names),
                "complement_key": None,
                "line_graph_key": None,
                "references": _hog_reference(row),
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
    parser.add_argument("--hog-cache", type=pathlib.Path, default=None)
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
        small, large = fetch_house_of_graphs(arguments.hog_cache)
        census = harvest_census(small)
        overlay = harvest_named(large, _hog_invariant_names(arguments.hog_cache))
        if len(census) != 1252:
            raise SystemExit(f"expected 1252 census graphs, got {len(census)}")
        size = _write(
            DATA / "graphs.json.gz",
            {
                "source": (
                    "networkx graph_atlas_g (<= 7 vertices) and named graphs, "
                    "plus every named House of Graphs graph up to 16 vertices"
                ),
                "harvested": harvested,
                "networkx": nx.__version__,
                "census": census,
                "overlay": overlay,
            },
        )
        named = sum(1 for entry in census if not entry["latex"].startswith(r"\mathrm{G}"))
        cited = sum(1 for entry in census if entry["references"])
        print(
            f"graphs: {len(census)} census ({named} named, {cited} in House of Graphs) "
            f"+ {len(overlay)} named larger ones, written ({size / 1000:.0f} kB)"
        )


if __name__ == "__main__":
    main()
