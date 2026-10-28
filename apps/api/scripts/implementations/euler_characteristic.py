from itertools import combinations


def _faces(complex_):
    found = {}
    for facet in complex_.facets:
        for size in range(1, len(facet) + 1):
            found.setdefault(size - 1, set()).update(combinations(facet, size))
    return {dimension: sorted(faces) for dimension, faces in found.items()}


def accepts(x):
    return isinstance(x, (Surface, SimplicialComplex))


def compute(x):
    if isinstance(x, Surface):
        return Integer(2 - 2 * x.genus if x.orientable else 2 - x.genus)
    return Integer(sum((-1) ** dimension * len(faces) for dimension, faces in _faces(x).items()))
