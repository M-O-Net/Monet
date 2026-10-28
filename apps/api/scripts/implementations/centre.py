from sympy.combinatorics.named_groups import AlternatingGroup, SymmetricGroup


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


MAX_DEGREE = 10


def accepts(g):
    return isinstance(g, PermutationGroup) and g.degree <= MAX_DEGREE


def compute(g):
    return _canonical(g.center())
