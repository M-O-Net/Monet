def _exponents(p):
    t = Symbol("t")
    if isinstance(p, (bool, MatrixBase)) or getattr(p, "free_symbols", set()) != {t}:
        return None
    powers = []
    for term in p.as_ordered_terms():
        coefficient, exponent = term.as_coeff_exponent(t)
        if not (exponent.is_Integer and coefficient.is_Number):
            return None
        powers.append(exponent)
    return powers


def accepts(p):
    powers = _exponents(p)
    return powers is not None and len(powers) > 1


def compute(p):
    powers = _exponents(p)
    return Max(*powers) - Min(*powers)
