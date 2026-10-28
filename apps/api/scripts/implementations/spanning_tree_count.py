def accepts(g):
    return isinstance(g, Graph) and g.order > 0


def compute(g):
    laplacian = zeros(g.order, g.order)
    for u, v in g.edges:
        laplacian[u, v] = laplacian[v, u] = -1
        laplacian[u, u] += 1
        laplacian[v, v] += 1
    return laplacian[1:, 1:].det() if g.order > 1 else Integer(1)
