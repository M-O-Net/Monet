from sympy.matrices.normalforms import invariant_factors


def _abelian_quotient(generators, relators):
    if not generators:
        return AbelianGroup(0, [])
    rows = [[sum(e for s, e in r.array_form if s == g) for g in generators] for r in relators]
    factors = [abs(d) for d in invariant_factors(Matrix(rows), domain=ZZ)] if rows else []
    return AbelianGroup(
        len(generators) - sum(1 for d in factors if d != 0), [int(d) for d in factors if d > 1]
    )


def _from_prime_powers(prime_powers):
    by_prime = {}
    for power in prime_powers:
        by_prime.setdefault(min(factorint(power)), []).append(power)
    columns = [sorted(powers, reverse=True) for powers in by_prime.values()]
    depth = max((len(column) for column in columns), default=0)
    factors = [prod(column[k] for column in columns if k < len(column)) for k in range(depth)]
    return AbelianGroup(0, sorted(int(f) for f in factors))


def accepts(g):
    return isinstance(g, (FpGroup, PermutationGroup))


def compute(g):
    if isinstance(g, PermutationGroup):
        return _from_prime_powers(g.abelian_invariants())
    return _abelian_quotient(g.free_group.symbols, g.relators)
