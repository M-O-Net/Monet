def accepts(g):
    return isinstance(g, Graph)


def compute(g):
    parent = list(range(g.order))

    def root(v):
        while parent[v] != v:
            v = parent[v]
        return v

    for u, v in g.edges:
        parent[root(u)] = root(v)
    roots = [root(v) for v in range(g.order)]
    return IntegerPartition([roots.count(r) for r in set(roots)])
