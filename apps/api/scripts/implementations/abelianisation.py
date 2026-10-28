from sympy.matrices.normalforms import invariant_factors


def _abelian_quotient(generators, relators):
    if not generators:
        return AbelianGroup(0, [])
    rows = [[sum(e for s, e in r.array_form if s == g) for g in generators] for r in relators]
    factors = [abs(d) for d in invariant_factors(Matrix(rows), domain=ZZ)] if rows else []
    return AbelianGroup(
        len(generators) - sum(1 for d in factors if d != 0), [int(d) for d in factors if d > 1]
    )


MAX_DEGREE = 10


def accepts(g):
    return isinstance(g, FpGroup) or (isinstance(g, PermutationGroup) and g.degree <= MAX_DEGREE)


def compute(g):
    presentation = g if isinstance(g, FpGroup) else g.presentation()
    return _abelian_quotient(presentation.free_group.symbols, presentation.relators)
