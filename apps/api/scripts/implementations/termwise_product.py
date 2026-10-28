def _constant_coefficients(a):
    return isinstance(a, RecursiveSeq) and "recurrence" in to_data(a)


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
    return _constant_coefficients(a)


def compute(a, b):
    if not _constant_coefficients(b):
        raise ValueError("both sequences need constant-coefficient recurrences")
    bound = len(a.initial) * len(b.initial)
    terms = [a[i] * b[i] for i in range(2 * bound + 2)]
    weights = _weights(terms)
    n, term = Symbol("n"), Function("a")
    rule = sum(w * term(n - k) for k, w in enumerate(weights, start=1))
    return RecursiveSeq(rule, term(n), n, terms[: len(weights)])
