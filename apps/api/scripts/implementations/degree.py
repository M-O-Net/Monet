def accepts(p):
    return isinstance(p, Expr) and Symbol("x") in p.free_symbols and p.is_polynomial(Symbol("x"))


def compute(p):
    return degree(p, Symbol("x"))
