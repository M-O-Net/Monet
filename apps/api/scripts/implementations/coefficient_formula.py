def accepts(f):
    return isinstance(f, Expr) and f.free_symbols == {Symbol("x")}


def compute(f):
    x, n = Symbol("x"), Symbol("n")
    expansion = fps(f, x, 0)
    k, m = expansion.ak.variables[0], Dummy("m", integer=True, nonnegative=True)
    if expansion.xk.formula.subs(k, m) != x**m:
        raise ValueError("fps gives no power series in x")
    formula = simplify(expansion.ak.formula.subs(k, m))
    start = int(expansion.ak.start)
    independent = Poly(expand(expansion.ind), x)
    for j in range(max(start, independent.degree() + 1)):
        expected = independent.coeff_monomial(x**j) if j <= independent.degree() else 0
        if (j < start and formula.subs(m, j) != expected) or (j >= start and expected != 0):
            raise ValueError("no single formula gives every coefficient from n = 0")
    return SeqFormula(formula.subs(m, n), (n, 0, oo))
