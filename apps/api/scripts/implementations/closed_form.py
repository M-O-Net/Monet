def accepts(a):
    return isinstance(a, RecursiveSeq) and "recurrence" in to_data(a)


def compute(a):
    y, n = a.y, a.n
    initial = {y(a.start + i): value for i, value in enumerate(a.initial)}
    solution = rsolve(a.recurrence.lhs - a.recurrence.rhs, y(n), initial)
    if solution is None:
        raise ValueError("rsolve found no closed form")
    return SeqFormula(solution, (n, a.start, oo))
