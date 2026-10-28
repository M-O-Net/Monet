NONABELIAN_SIMPLE = {60: 5, 168: 42}
MAX_DEGREE = 10


def accepts(g):
    if not isinstance(g, PermutationGroup) or g.degree > MAX_DEGREE:
        return False
    return g.is_solvable or (g.is_perfect and g.order() in NONABELIAN_SIMPLE)


def compute(g):
    if not g.is_solvable:
        return [SmallGroup(g.order(), NONABELIAN_SIMPLE[g.order()])]
    orders = [h.order() for h in g.composition_series()]
    return [SmallGroup(above // below, 1) for above, below in zip(orders, orders[1:])]
