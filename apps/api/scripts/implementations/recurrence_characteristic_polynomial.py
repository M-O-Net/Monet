def _weights(a):
    if not isinstance(a, RecursiveSeq):
        return None
    data = to_data(a)
    return [from_data(c) for c in data["recurrence"]["coeffs"]] if "recurrence" in data else None


def accepts(a):
    return _weights(a) is not None


def compute(a):
    x, weights = Symbol("x"), _weights(a)
    order = len(weights)
    return x**order - sum(c * x ** (order - i) for i, c in enumerate(weights, start=1))
