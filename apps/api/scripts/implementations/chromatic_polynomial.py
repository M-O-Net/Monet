MAX_ORDER = 12


def accepts(g):
    return isinstance(g, Graph) and 0 < g.order <= MAX_ORDER


def compute(g):
    neighbours = [0] * g.order
    for u, v in g.edges:
        neighbours[u] |= 1 << v
        neighbours[v] |= 1 << u
    full = (1 << g.order) - 1
    independent = [True] * (full + 1)
    for subset in range(1, full + 1):
        lowest = (subset & -subset).bit_length() - 1
        rest = subset & ~(1 << lowest)
        independent[subset] = independent[rest] and not neighbours[lowest] & rest
    partitions = [{} for _ in range(full + 1)]
    partitions[0] = {0: 1}
    for subset in range(1, full + 1):
        lowest = subset & -subset
        rest = subset & ~lowest
        block_rest = rest
        while True:
            block = block_rest | lowest
            if independent[block]:
                for blocks, count in partitions[subset & ~block].items():
                    partitions[subset][blocks + 1] = partitions[subset].get(blocks + 1, 0) + count
            if block_rest == 0:
                break
            block_rest = (block_rest - 1) & rest
    x = Symbol("x")
    return expand(sum(count * ff(x, blocks) for blocks, count in partitions[full].items()))
