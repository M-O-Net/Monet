def _rational_roots(p):
    roots = Poly(p, Symbol("x")).all_roots()
    return roots if roots and all(root.is_Rational for root in roots) else None


def accepts(p):
    if isinstance(p, (bool, MatrixBase)) or Symbol("x") not in getattr(p, "free_symbols", ()):
        return False
    return _rational_roots(p) is not None


def compute(p):
    return _rational_roots(p)
