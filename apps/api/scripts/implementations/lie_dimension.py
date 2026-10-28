from sympy.liealgebras.cartan_type import Standard_Cartan


def accepts(g):
    return isinstance(g, Standard_Cartan)


def compute(g):
    return g.rank() + 2 * len(g.positive_roots())
