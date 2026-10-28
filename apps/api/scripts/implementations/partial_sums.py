def accepts(a):
    if isinstance(a, Tuple):
        return all(isinstance(term, Expr) and term.is_number for term in a)
    return isinstance(a, SeqFormula)


def compute(a):
    if isinstance(a, Tuple):
        totals = [a[0]]
        for term in a[1:]:
            totals.append(totals[-1] + term)
        return Tuple(*totals)
    n, k = a.variables[0], Dummy("k")
    summed = powsimp(factor(summation(a.formula.subs(n, k), (k, a.start, n))))
    if summed.has(Sum):
        raise ValueError("sympy finds no closed form for these partial sums")
    return SeqFormula(summed, (n, a.start, oo))
