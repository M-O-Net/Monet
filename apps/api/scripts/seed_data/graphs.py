from seed_data.build import (
    Instance,
    Reference,
    RelationSpec,
    Specimen,
    complete_graph,
    cycle_graph,
    graph,
    instance,
    matrix_instance,
    path_graph,
    permgroup,
    polynomial,
)

PETERSEN_EDGES = [
    *((i, (i + 1) % 5) for i in range(5)),
    *((i, i + 5) for i in range(5)),
    *((i + 5, (i + 2) % 5 + 5) for i in range(5)),
]
CUBE_EDGES = [(v, v ^ bit) for v in range(8) for bit in (1, 2, 4) if v < v ^ bit]


def _chromatic(*coeffs_from_constant: int) -> Instance:
    data = polynomial(*coeffs_from_constant)
    terms = [
        (power, c) for power, c in reversed(list(enumerate(coeffs_from_constant))) if c != 0
    ]
    pieces = []
    for power, c in terms:
        size = abs(c)
        monomial = "x" if power == 1 else f"x^{{{power}}}"
        body = monomial if size == 1 else f"{size} {monomial}"
        sign = "- " if c < 0 else ("+ " if pieces else "")
        pieces.append(sign + body)
    return instance(" ".join(pieces), data, ["MonicIntegerPolynomials"])


INSTANCES: dict[str, Instance] = {
    "k1": instance("K_{1}", graph(1, []), ["Trees", "CompleteGraphs"], "A single vertex."),
    "k2": instance("K_{2}", graph(2, [(0, 1)]), ["Trees", "CompleteGraphs"], "A single edge."),
    "empty2": instance(
        r"\overline{K_{2}}",
        graph(2, []),
        ["BipartiteGraphs", "PlanarGraphs", "RegularGraphs"],
        "Two vertices and no edge.",
    ),
    "empty4": instance(
        r"\overline{K_{4}}",
        graph(4, []),
        ["BipartiteGraphs", "PlanarGraphs", "RegularGraphs"],
        "Four vertices and no edges.",
    ),
    "path4": instance("P_{4}", path_graph(4), ["Trees"], "The path on four vertices."),
    "path4_complement": instance(
        r"\overline{P_{4}}",
        graph(4, [(0, 2), (0, 3), (1, 3)]),
        ["Trees"],
        r"The path $2, 0, 3, 1$: $P_{4}$ is isomorphic to its own complement.",
    ),
    "claw": instance(
        "K_{1,3}",
        graph(4, [(0, 1), (0, 2), (0, 3)]),
        ["Trees"],
        "The claw: one vertex joined to three others.",
    ),
    "triangle_and_point": instance(
        r"K_{3} \sqcup K_{1}",
        graph(4, [(1, 2), (1, 3), (2, 3)]),
        ["PlanarGraphs"],
        "A triangle and an isolated vertex.",
    ),
    "path5": instance("P_{5}", path_graph(5), ["Trees"]),
    "two_edges": instance(
        r"2 K_{2}",
        graph(4, [(0, 1), (2, 3)]),
        ["BipartiteGraphs", "PlanarGraphs", "RegularGraphs"],
        "Two disjoint edges: disconnected, so it has no spanning tree.",
    ),
    "cycle4_complement": instance(
        r"\overline{C_{4}}",
        graph(4, [(0, 2), (1, 3)]),
        ["BipartiteGraphs", "PlanarGraphs", "RegularGraphs"],
        "The two diagonals of a square.",
    ),
    "cycle4": instance(
        "C_{4}", cycle_graph(4), ["BipartiteGraphs", "PlanarGraphs", "RegularGraphs"]
    ),
    "k22": instance(
        "K_{2,2}",
        graph(4, [(0, 2), (0, 3), (1, 2), (1, 3)]),
        ["BipartiteGraphs", "PlanarGraphs", "RegularGraphs"],
        r"A $4$-cycle, labelled by its two sides.",
    ),
    "k23": instance(
        "K_{2,3}", graph(5, [(i, j) for i in range(2) for j in range(2, 5)]), ["BipartiteGraphs"]
    ),
    "k33": instance(
        "K_{3,3}",
        graph(6, [(i, j) for i in range(3) for j in range(3, 6)]),
        ["BipartiteGraphs", "RegularGraphs"],
        "Not planar: the utilities graph.",
    ),
    "two_triangles": instance(
        r"2 K_{3}",
        graph(6, [(0, 1), (0, 2), (1, 2), (3, 4), (3, 5), (4, 5)]),
        ["PlanarGraphs", "RegularGraphs"],
        r"Two disjoint triangles: the complement of $K_{3,3}$.",
    ),
    "cube_graph": instance(
        "Q_{3}",
        graph(8, CUBE_EDGES),
        ["BipartiteGraphs", "PlanarGraphs", "RegularGraphs"],
        "The vertices and edges of a cube.",
    ),
    "wheel5": instance(
        "W_{5}",
        graph(5, [(0, 1), (1, 4), (3, 4), (0, 3), (0, 2), (1, 2), (2, 3), (2, 4)]),
        ["PlanarGraphs"],
        "The wheel: a hub joined to every vertex of a 4-cycle — the edges of a square pyramid.",
    ),
    "cycle5": instance("C_{5}", cycle_graph(5), ["PlanarGraphs", "RegularGraphs"]),
    "pentagram": instance(
        r"\overline{C_{5}}",
        graph(5, [(0, 2), (0, 3), (1, 3), (1, 4), (2, 4)]),
        ["PlanarGraphs", "RegularGraphs"],
        r"The pentagram $0, 2, 4, 1, 3$: $C_{5}$ is isomorphic to its own complement.",
    ),
    "petersen": instance(
        r"\text{Petersen graph}",
        graph(10, PETERSEN_EDGES),
        ["RegularGraphs"],
        "Three-regular on ten vertices, neither planar nor bipartite.",
    ),
    "k3": instance("K_{3}", complete_graph(3), ["CompleteGraphs", "PlanarGraphs"]),
    "k4": instance("K_{4}", complete_graph(4), ["CompleteGraphs", "PlanarGraphs"]),
    "k5": instance(
        "K_{5}",
        complete_graph(5),
        ["CompleteGraphs"],
        "The smallest complete graph that is not planar.",
    ),
    "adjacency_k3": matrix_instance(
        [[0, 1, 1], [1, 0, 1], [1, 1, 0]], ["SymmetricMatrices", "InvertibleRationalMatrices"]
    ),
    "adjacency_path4": matrix_instance(
        [[0, 1, 0, 0], [1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0]], ["SymmetricMatrices"]
    ),
    "adjacency_cycle4": matrix_instance(
        [[0, 1, 0, 1], [1, 0, 1, 0], [0, 1, 0, 1], [1, 0, 1, 0]],
        ["SymmetricMatrices", "SingularMatrices"],
    ),
    "adjacency_claw": matrix_instance(
        [[0, 1, 1, 1], [1, 0, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0]],
        ["SymmetricMatrices", "SingularMatrices"],
    ),
    "chromatic_tree4": _chromatic(0, -1, 3, -3, 1),
    "chromatic_k3": _chromatic(0, 2, -3, 1),
    "chromatic_k4": _chromatic(0, -6, 11, -6, 1),
    "chromatic_cycle4": _chromatic(0, -3, 6, -4, 1),
    "chromatic_cycle5": _chromatic(0, 4, -10, 10, -5, 1),
    "chromatic_two_edges": _chromatic(0, 0, 1, -2, 1),
    "chromatic_petersen": _chromatic(0, -704, 2606, -4305, 4275, -2861, 1353, -455, 105, -15, 1),
    "path_reversal_group": instance(
        r"\left\langle \left( 0\; 3\right)\left( 1\; 2\right) \right\rangle",
        permgroup(4, [[3, 2, 1, 0]]),
        ["PermutationGroups"],
        "Order two: reversing a path on four vertices.",
    ),
    "claw_automorphisms": instance(
        r"\left\langle \left( 2\; 3\right), \left( 1\; 2\right) \right\rangle",
        permgroup(4, [[0, 1, 3, 2], [0, 2, 1, 3]]),
        ["PermutationGroups"],
        r"$S_{3}$ permuting three of four points and fixing the fourth.",
    ),
    "k33_automorphisms": instance(
        r"S_{3} \wr S_{2}",
        permgroup(
            6,
            [
                [0, 1, 2, 3, 5, 4],
                [0, 1, 2, 4, 3, 5],
                [0, 2, 1, 3, 4, 5],
                [1, 0, 2, 3, 4, 5],
                [3, 4, 5, 0, 1, 2],
            ],
        ),
        ["PermutationGroups"],
        r"Of order $72$: permute each side of $K_{3,3}$, and swap the sides.",
    ),
}

SECTIONS: dict[str, Specimen] = {
    "GraphOperations": (
        r"\text{Graph Operations}",
        "Operations taking a graph as input, and the constructions that produce one.",
    ),
}

OPERATORS: dict[str, Specimen] = {
    "AdjacencyMatrix": (
        r"\text{Adjacency Matrix}",
        r"The matrix with a $1$ in row $i$, column $j$ exactly when vertices $i$ and $j$ are "
        "joined.",
    ),
    "SpanningTreeCount": (
        r"\text{Spanning Tree Count}",
        "The number of spanning trees: by the matrix-tree theorem, any cofactor of the "
        r"Laplacian $D - A$. Cayley's formula gives $n^{n - 2}$ for $K_{n}$.",
    ),
    "ChromaticPolynomial": (
        r"\text{Chromatic Polynomial}",
        r"The polynomial whose value at $k$ counts the proper colourings with $k$ colours, "
        r"summed here as $\sum_{j} a_{j}\, x (x - 1) \cdots (x - j + 1)$ over the $a_{j}$ ways "
        r"to split the vertices into $j$ independent sets.",
    ),
    "Complement": (
        r"\text{Complement}",
        "The graph on the same vertices joining exactly the pairs the input does not.",
    ),
    "IsPlanar": (
        r"\text{Is Planar}",
        r"Whether the graph can be drawn in the plane without crossings. By Kuratowski, "
        r"exactly when it contains no subdivision of $K_{5}$ or $K_{3,3}$.",
    ),
    "CompleteGraph": (
        r"\text{Complete Graph}",
        r"$K_{n}$: $n$ vertices, every pair joined.",
    ),
    "CompleteBipartiteGraph": (
        r"\text{Complete Bipartite Graph}",
        r"$K_{m,n}$: every vertex of $\{0, \dots, m - 1\}$ joined to every vertex of "
        r"$\{m, \dots, m + n - 1\}$.",
    ),
    "AutomorphismGroup": (
        r"\text{Automorphism Group}",
        "The permutations of the vertices that preserve adjacency, as a permutation group "
        "with canonical generators.",
    ),
}

SIGNATURES: list[tuple[str, str, str]] = [
    ("AdjacencyMatrix", "Graphs", "SymmetricMatrices"),
    ("SpanningTreeCount", "Graphs", "Integers"),
    ("ChromaticPolynomial", "Graphs", "IntegerPolynomials"),
    ("Complement", "Graphs", "Graphs"),
    ("Complement", "RegularGraphs", "RegularGraphs"),
    ("IsPlanar", "Graphs", "Booleans"),
    ("CompleteGraph", "PositiveIntegers", "CompleteGraphs"),
    ("CompleteBipartiteGraph", "PositiveIntegers", "BipartiteGraphs"),
    ("AutomorphismGroup", "Graphs", "PermutationGroups"),
]

IMPLEMENTATIONS: dict[str, str] = {
    "AdjacencyMatrix": "adjacency_matrix",
    "SpanningTreeCount": "spanning_tree_count",
    "ChromaticPolynomial": "chromatic_polynomial",
    "Complement": "complement",
    "CompleteGraph": "complete_graph",
    "CompleteBipartiteGraph": "complete_bipartite_graph",
    "AutomorphismGroup": "automorphism_group",
}

RELATIONS: list[RelationSpec] = [
    ("AdjacencyMatrix", ["k2"], ["D"]),
    ("AdjacencyMatrix", ["empty2"], ["zero2"]),
    ("AdjacencyMatrix", ["k3"], ["adjacency_k3"]),
    ("AdjacencyMatrix", ["path4"], ["adjacency_path4"]),
    ("AdjacencyMatrix", ["cycle4"], ["adjacency_cycle4"]),
    ("AdjacencyMatrix", ["claw"], ["adjacency_claw"]),
    ("AdjacencyMatrix", ["two_edges"], ["double_swap4"]),
    ("SpanningTreeCount", ["k3"], [3]),
    ("SpanningTreeCount", ["k4"], [16]),
    ("SpanningTreeCount", ["k5"], [125]),
    ("SpanningTreeCount", ["cycle5"], [5]),
    ("SpanningTreeCount", ["path4"], [1]),
    ("SpanningTreeCount", ["k33"], [81]),
    ("SpanningTreeCount", ["wheel5"], [45]),
    ("SpanningTreeCount", ["cube_graph"], [384]),
    ("SpanningTreeCount", ["petersen"], [2000]),
    ("SpanningTreeCount", ["two_edges"], [0]),
    ("ChromaticPolynomial", ["path4"], ["chromatic_tree4"]),
    ("ChromaticPolynomial", ["claw"], ["chromatic_tree4"]),
    ("ChromaticPolynomial", ["k3"], ["chromatic_k3"]),
    ("ChromaticPolynomial", ["k4"], ["chromatic_k4"]),
    ("ChromaticPolynomial", ["cycle4"], ["chromatic_cycle4"]),
    ("ChromaticPolynomial", ["cycle5"], ["chromatic_cycle5"]),
    ("ChromaticPolynomial", ["two_edges"], ["chromatic_two_edges"]),
    ("ChromaticPolynomial", ["petersen"], ["chromatic_petersen"]),
    ("Complement", ["k4"], ["empty4"]),
    ("Complement", ["empty4"], ["k4"]),
    ("Complement", ["k2"], ["empty2"]),
    ("Complement", ["path4"], ["path4_complement"]),
    ("Complement", ["claw"], ["triangle_and_point"]),
    ("Complement", ["cycle4"], ["cycle4_complement"]),
    ("Complement", ["k33"], ["two_triangles"]),
    ("Complement", ["cycle5"], ["pentagram"]),
    ("Complement", ["pentagram"], ["cycle5"]),
    ("CompleteGraph", [1], ["k1"]),
    ("CompleteGraph", [2], ["k2"]),
    ("CompleteGraph", [3], ["k3"]),
    ("CompleteGraph", [4], ["k4"]),
    ("CompleteGraph", [5], ["k5"]),
    ("CompleteBipartiteGraph", [1, 1], ["k2"]),
    ("CompleteBipartiteGraph", [1, 3], ["claw"]),
    ("CompleteBipartiteGraph", [2, 2], ["k22"]),
    ("CompleteBipartiteGraph", [2, 3], ["k23"]),
    ("CompleteBipartiteGraph", [3, 3], ["k33"]),
    ("AutomorphismGroup", ["k3"], ["s3"]),
    ("AutomorphismGroup", ["k4"], ["s4"]),
    ("AutomorphismGroup", ["empty4"], ["s4"]),
    ("AutomorphismGroup", ["cycle4"], ["d4"]),
    ("AutomorphismGroup", ["cycle5"], ["d5"]),
    ("AutomorphismGroup", ["path4"], ["path_reversal_group"]),
    ("AutomorphismGroup", ["claw"], ["claw_automorphisms"]),
    ("AutomorphismGroup", ["k33"], ["k33_automorphisms"]),
    ("IsPlanar", ["k5"], ["false"]),
    ("IsPlanar", ["k33"], ["false"]),
    ("IsPlanar", ["petersen"], ["false"]),
    ("IsPlanar", ["k4"], ["true"]),
    ("IsPlanar", ["cube_graph"], ["true"]),
    ("IsPlanar", ["wheel5"], ["true"]),
    ("IsPlanar", ["pentagram"], ["true"]),
]

DISPLAYS: dict[str, tuple[str | None, bool]] = {
    "CompleteGraph": (r"\op{K}_{{in0}} = {out0}", False),
    "CompleteBipartiteGraph": (r"\op{K}_{{in0}, {in1}} = {out0}", False),
}

_WIKI = "https://en.wikipedia.org/wiki/"

REFERENCES: dict[str, list[Reference]] = {
    "petersen": [("Wikipedia", _WIKI + "Petersen_graph")],
    "chromatic_petersen": [("Wikipedia", _WIKI + "Petersen_graph")],
    "SpanningTreeCount": [("Wikipedia", _WIKI + "Kirchhoff%27s_theorem")],
    "ChromaticPolynomial": [("Wikipedia", _WIKI + "Chromatic_polynomial")],
    "IsPlanar": [("Wikipedia", _WIKI + "Kuratowski%27s_theorem")],
    "AutomorphismGroup": [("Wikipedia", _WIKI + "Graph_automorphism")],
    "cube_graph": [("Wikipedia", _WIKI + "Hypercube_graph")],
    "wheel5": [("Wikipedia", _WIKI + "Wheel_graph")],
}

FILINGS: dict[str, list[str]] = {
    "GraphTheory": ["GraphOperations"],
    "GraphOperations": list(OPERATORS),
}
