def accepts(f):
    return isinstance(f, Expr) and f.free_symbols == {Symbol("x")}


def compute(f, a):
    if not (isinstance(a, Expr) and a.is_number):
        raise ValueError("the point must be a number")
    return simplify(f.subs(Symbol("x"), a))
