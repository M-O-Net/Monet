TERMS = 20


def _terms(a):
    if isinstance(a, Tuple):
        return list(a)
    return [simplify(a.formula.subs(a.variables[0], i)) for i in range(TERMS)]


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


def accepts(a):
    if isinstance(a, Tuple):
        return len(a) >= 2 and all(isinstance(term, Expr) and term.is_Rational for term in a)
    return isinstance(a, SeqFormula) and a.start == 0


def compute(a):
    terms = _terms(a)
    weights = _weights(terms)
    if weights is None:
        raise ValueError(f"no linear recurrence fits the first {len(terms)} terms")
    n, term = Symbol("n"), Function("a")
    rule = sum(w * term(n - k) for k, w in enumerate(weights, start=1))
    return RecursiveSeq(rule, term(n), n, terms[: len(weights)])
