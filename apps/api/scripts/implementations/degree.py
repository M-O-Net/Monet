def accepts(p):
    return not isinstance(p, (bool, MatrixBase)) and Symbol("x") in getattr(p, "free_symbols", ())


def compute(p):
    return degree(p, Symbol("x"))
