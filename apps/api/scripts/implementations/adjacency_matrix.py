def accepts(g):
    return isinstance(g, Graph)


def compute(g):
    adjacent = set(g.edges)
    return Matrix(g.order, g.order, lambda i, j: 1 if (min(i, j), max(i, j)) in adjacent else 0)
