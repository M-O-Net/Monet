def _rational_denominator(f):
    x = Symbol("x")
    if not f.is_rational_function(x):
        return None
    denominator = Poly(denom(cancel(f)), x)
    return denominator if denominator.degree() >= 1 else None


def _holonomic(f):
    if isinstance(f, HolonomicFunction):
        return f
    try:
        function = sympy.holonomic.expr_to_holonomic(f, Symbol("x"))
    except (NotImplementedError, TypeError, ValueError):
        return None
    return function if function.x0 == 0 else None


def accepts(f):
    if isinstance(f, HolonomicFunction):
        return f.x0 == 0
    if not (isinstance(f, Expr) and f.free_symbols == {Symbol("x")}):
        return False
    if f.is_rational_function(Symbol("x")):
        return _rational_denominator(f) is not None
    return _holonomic(f) is not None


def _weights(terms):
    for order in range(1, len(terms) // 2 + 1):
        system = Matrix([terms[i : i + order] for i in range(order)])
        if system.det() == 0:
            continue
        c = system.solve(Matrix(terms[order : 2 * order]))
        fits = all(
            terms[i + order] == sum(c[j] * terms[i + j] for j in range(order))
            for i in range(len(terms) - order)
        )
        if fits:
            return [c[order - k] for k in range(1, order + 1)]
    return None


def _from_rational(f):
    x, n, term = Symbol("x"), Symbol("n"), Function("a")
    count = 2 * _rational_denominator(f).degree() + 4
    expansion = Poly(series(f, x, 0, count).removeO(), x)
    terms = [expansion.coeff_monomial(x**i) for i in range(count)]
    weights = _weights(terms)
    if weights is None:
        raise ValueError("no constant-coefficient recurrence holds from the first term")
    rule = sum(w * term(n - k) for k, w in enumerate(weights, start=1))
    return RecursiveSeq(rule, term(n), n, terms[: len(weights)])


def _from_holonomic(function):
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


def compute(f):
    if isinstance(f, Expr) and _rational_denominator(f) is not None:
        return _from_rational(f)
    function = _holonomic(f)
    if function is None:
        raise ValueError("sympy finds no D-finite description about 0")
    return _from_holonomic(function)
