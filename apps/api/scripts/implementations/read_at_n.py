def accepts(a):
    return isinstance(a, (SeqFormula, RecursiveSeq, Tuple))


def compute(a, n):
    if not (isinstance(n, Expr) and n.is_Integer):
        raise ValueError("the index must be an integer")
    if isinstance(a, Tuple):
        if not 1 <= n <= len(a):
            raise IndexError(f"a finite sequence of {len(a)} terms has no term {n}")
        return a[int(n) - 1]
    if n < a.start:
        raise IndexError(f"the sequence starts at {a.start}")
    if isinstance(a, RecursiveSeq):
        return a[int(n - a.start)]
    return simplify(a.formula.subs(a.variables[0], n))
