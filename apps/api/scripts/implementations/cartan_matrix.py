from sympy.liealgebras.cartan_type import Standard_Cartan


def _simple_roots(g):
    return [Matrix([Rational(c) for c in g.simple_root(i)]) for i in range(1, g.rank() + 1)]


def _cartan(g):
    roots = _simple_roots(g)
    return Matrix(
        len(roots), len(roots), lambda i, j: 2 * roots[i].dot(roots[j]) / roots[j].dot(roots[j])
    )


def accepts(g):
    return isinstance(g, Standard_Cartan)


def compute(g):
    return _cartan(g)
