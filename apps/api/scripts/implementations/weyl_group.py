from sympy.combinatorics.named_groups import AlternatingGroup, SymmetricGroup
from sympy.liealgebras.cartan_type import Standard_Cartan


def _canonical(group):
    degree, order = group.degree, group.order()
    if order == factorial(degree):
        return SymmetricGroup(degree)
    if degree > 2 and 2 * order == factorial(degree):
        return AlternatingGroup(degree)
    chosen = []
    for element in sorted(group.generate(), key=lambda g: g.array_form):
        if chosen and PermutationGroup(chosen).order() == order:
            break
        if not element.is_Identity and not (chosen and PermutationGroup(chosen).contains(element)):
            chosen.append(element)
    return PermutationGroup(chosen or [Permutation(degree - 1)])


MAX_RANK = 4


def _reflect(vector, root):
    scale = 2 * sum(v * r for v, r in zip(vector, root, strict=True)) / sum(r * r for r in root)
    return tuple(v - scale * r for v, r in zip(vector, root, strict=True))


def accepts(g):
    return isinstance(g, Standard_Cartan) and g.series in "ABCDG" and g.rank() <= MAX_RANK


def compute(g):
    roots = [tuple(Rational(c) for c in g.simple_root(i)) for i in range(1, g.rank() + 1)]
    if g.series == "G":
        start = roots[0]
    else:
        start = tuple(Integer(int(i == 0)) for i in range(len(roots[0])))
    orbit, frontier = {start}, [start]
    while frontier:
        found = [_reflect(v, root) for v in frontier for root in roots]
        frontier = [v for v in found if v not in orbit]
        orbit.update(frontier)
    points = sorted(orbit, reverse=True)
    label = {v: i for i, v in enumerate(points)}
    generators = [Permutation([label[_reflect(v, root)] for v in points]) for root in roots]
    return _canonical(PermutationGroup(generators))
