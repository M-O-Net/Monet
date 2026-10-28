from sympy.matrices.normalforms import invariant_factors


def _abelian_quotient(generators, relators):
    if not generators:
        return AbelianGroup(0, [])
    rows = [[sum(e for s, e in r.array_form if s == g) for g in generators] for r in relators]
    factors = [abs(d) for d in invariant_factors(Matrix(rows), domain=ZZ)] if rows else []
    return AbelianGroup(
        len(generators) - sum(1 for d in factors if d != 0), [int(d) for d in factors if d > 1]
    )


def accepts(g):
    if isinstance(g, FpGroup):
        return _abelian_quotient(g.free_group.symbols, g.relators).rank == 0
    return isinstance(g, (PermutationGroup, SmallGroup))


def compute(g):
    return g.order if isinstance(g, SmallGroup) else g.order()
