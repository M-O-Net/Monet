def _canonical(e):
    return factor(cancel(e)) if e.is_rational_function(Symbol("x")) else expand(e)


def accepts(f):
    return isinstance(f, Expr) and f.free_symbols == {Symbol("x")}


def compute(f):
    return _canonical(diff(f, Symbol("x")))
