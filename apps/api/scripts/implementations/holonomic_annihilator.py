def accepts(f):
    return isinstance(f, Expr) and f.free_symbols == {Symbol("x")}


def compute(f):
    function = sympy.holonomic.expr_to_holonomic(f, Symbol("x"))
    if function.x0 != 0:
        raise ValueError(f"sympy can only give initial values at {function.x0}, not at 0")
    return function
