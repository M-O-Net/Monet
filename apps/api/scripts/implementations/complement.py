def accepts(g):
    return isinstance(g, Graph)


def compute(g):
    present = set(g.edges)
    missing = [(u, v) for u in range(g.order) for v in range(u + 1, g.order) if (u, v) not in present]
    return Graph(g.order, missing)
