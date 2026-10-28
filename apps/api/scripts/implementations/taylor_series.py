def _recurrence(function, point):
    if point != function.x0:
        raise ValueError(f"this D-finite function is held about {function.x0}, not {point}")
    sequence = function.to_sequence()[0][0]
    base = sequence.recurrence.parent.base
    n, term = Symbol("n"), Function("a")
    polys = [base.to_sympy(p).subs(sequence.n, n) for p in sequence.recurrence.listofpoly]
    order = len(polys) - 1
    rule = sum(
        -polys[i].subs(n, n - order) / polys[order].subs(n, n - order) * term(n - order + i)
        for i in range(order)
    )
    initial = list(sequence.u0)
    found = RecursiveSeq(cancel(rule), term(n), n, initial[:order])
    if list(found[: len(initial)]) != initial:
        raise ValueError("the recurrence does not reproduce the initial values")
    return found


def _formula(f, point):
    x, n = Symbol("x"), Symbol("n")
    expansion = fps(f, x, point)
    k, m = expansion.ak.variables[0], Dummy("m", integer=True, nonnegative=True)
    if expansion.xk.formula.subs(k, m) != (x - point) ** m:
        raise ValueError("fps gives no series in powers of x - a")
    formula = simplify(expansion.ak.formula.subs(k, m))
    start = int(expansion.ak.start)
    independent = Poly(expand(expansion.ind.subs(x, x + point)), x)
    for j in range(max(start, independent.degree() + 1)):
        expected = independent.coeff_monomial(x**j) if j <= independent.degree() else 0
        if j < start and formula.subs(m, j) != expected:
            raise ValueError("no single formula gives every coefficient from n = 0")
        if j >= start and expected != 0:
            raise ValueError("no single formula gives every coefficient from n = 0")
    return SeqFormula(formula.subs(m, n), (n, 0, oo))


def accepts(f):
    if isinstance(f, HolonomicFunction):
        return True
    return isinstance(f, Expr) and f.free_symbols == {Symbol("x")}


def compute(f, point):
    if not (isinstance(point, Expr) and point.is_number):
        raise ValueError("the point must be a number")
    if isinstance(f, HolonomicFunction):
        return _recurrence(f, point)
    return _formula(f, point)
