def _recurrence(a):
    if not isinstance(a, RecursiveSeq):
        return None
    data = to_data(a)
    return data.get("recurrence")


def accepts(a):
    return _recurrence(a) is not None


def compute(a):
    x, recurrence = Symbol("x"), _recurrence(a)
    weights = [from_data(c) for c in recurrence["coeffs"]]
    initial = [from_data(v) for v in recurrence["initial"]]
    order = len(weights)
    denominator = 1 - sum(c * x**i for i, c in enumerate(weights, start=1))
    product = Poly(sum(v * x**i for i, v in enumerate(initial)) * denominator, x)
    numerator = sum(product.coeff_monomial(x**i) * x**i for i in range(order))
    return numerator / denominator
