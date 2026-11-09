def accepts(p):
    if isinstance(p, MatrixBase) or not isinstance(p, Expr) or p.is_number:
        return False
    variables = p.free_symbols
    return len(variables) == 1 and p.is_polynomial(*variables)


def compute(p):
    (x,) = p.free_symbols
    q = Poly(expand(p.subs(x, -x)), x)
    return q.as_expr() if q.LC() > 0 else -q.as_expr()
