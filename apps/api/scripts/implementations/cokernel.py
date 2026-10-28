def accepts(m):
    return isinstance(m, MatrixBase) and all(entry.is_Integer for entry in m)


def compute(m):
    factors = [abs(int(f)) for f in sympy.matrices.normalforms.invariant_factors(m, domain=ZZ)]
    rank = m.rows - sum(1 for f in factors if f != 0)
    return AbelianGroup(rank, [f for f in factors if f > 1])
