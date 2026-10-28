from seed_data.build import Instance, complete_graph, cycle_graph, graph, instance, path_graph

PETERSEN_EDGES = [
    *((i, (i + 1) % 5) for i in range(5)),
    *((i, i + 5) for i in range(5)),
    *((i + 5, (i + 2) % 5 + 5) for i in range(5)),
]
CUBE_EDGES = [(v, v ^ bit) for v in range(8) for bit in (1, 2, 4) if v < v ^ bit]

INSTANCES: dict[str, Instance] = {
    "path4": instance("P_{4}", path_graph(4), ["Trees"], "The path on four vertices."),
    "claw": instance(
        "K_{1,3}",
        graph(4, [(0, 1), (0, 2), (0, 3)]),
        ["Trees"],
        "The claw: one vertex joined to three others.",
    ),
    "path5": instance("P_{5}", path_graph(5), ["Trees"]),
    "cycle4": instance(
        "C_{4}", cycle_graph(4), ["BipartiteGraphs", "PlanarGraphs", "RegularGraphs"]
    ),
    "k33": instance(
        "K_{3,3}",
        graph(6, [(i, j) for i in range(3) for j in range(3, 6)]),
        ["BipartiteGraphs", "RegularGraphs"],
        "Not planar: the utilities graph.",
    ),
    "cube_graph": instance(
        "Q_{3}",
        graph(8, CUBE_EDGES),
        ["BipartiteGraphs", "PlanarGraphs", "RegularGraphs"],
        "The vertices and edges of a cube.",
    ),
    "wheel5": instance(
        "W_{5}",
        graph(5, [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (2, 3), (3, 4), (1, 4)]),
        ["PlanarGraphs"],
        "The wheel: a hub joined to every vertex of a 4-cycle.",
    ),
    "cycle5": instance("C_{5}", cycle_graph(5), ["PlanarGraphs", "RegularGraphs"]),
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
}
