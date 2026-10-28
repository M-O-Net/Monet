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


MAX_ORDER = 10


def _automorphisms(g):
    adjacent = set(g.edges) | {(v, u) for u, v in g.edges}
    found = []

    def extend(images):
        vertex = len(images)
        if vertex == g.order:
            found.append(Permutation(images))
            return
        for image in range(g.order):
            if image not in images and all(
                ((earlier, vertex) in adjacent) == ((images[earlier], image) in adjacent)
                for earlier in range(vertex)
            ):
                extend([*images, image])

    extend([])
    return found


def accepts(g):
    return isinstance(g, Graph) and 0 < g.order <= MAX_ORDER


def compute(g):
    return _canonical(PermutationGroup(_automorphisms(g)))
