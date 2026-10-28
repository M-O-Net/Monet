from sympy.combinatorics.named_groups import AlternatingGroup, SymmetricGroup

MAX_DEGREE = 7


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


def accepts(p):
    return isinstance(p, Permutation) and p.size <= MAX_DEGREE


def compute(*permutations):
    degree = max(p.size for p in permutations)
    return _canonical(
        PermutationGroup([Permutation(p.array_form, size=degree) for p in permutations])
    )
