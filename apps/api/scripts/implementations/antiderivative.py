def _canonical(e):
    return factor(cancel(e)) if e.is_rational_function(Symbol("x")) else expand(e)


def accepts(f):
    return isinstance(f, Expr) and f.free_symbols == {Symbol("x")}


def compute(f):
    found = integrate(f, Symbol("x"))
    if found.has(Integral):
        raise ValueError("sympy finds no antiderivative in closed form")
    return _canonical(found)
