from itertools import combinations

from sympy.matrices.normalforms import invariant_factors


def _faces(complex_):
    found = {}
    for facet in complex_.facets:
        for size in range(1, len(facet) + 1):
            found.setdefault(size - 1, set()).update(combinations(facet, size))
    return {dimension: sorted(faces) for dimension, faces in found.items()}


def _boundary(faces, dimension):
    rows = {face: i for i, face in enumerate(faces[dimension - 1])}
    columns = faces[dimension]
    m = zeros(len(rows), len(columns))
    for j, face in enumerate(columns):
        for k in range(len(face)):
            m[rows[face[:k] + face[k + 1 :]], j] = (-1) ** k
    return m


def accepts(x):
    return isinstance(x, (Surface, SimplicialComplex))


def compute(x):
    if isinstance(x, Surface):
        if x.orientable:
            return AbelianGroup(2 * x.genus, [])
        return AbelianGroup(x.genus - 1, [2])
    faces = _faces(x)
    top = max(faces)
    boundaries = {d: _boundary(faces, d) for d in range(1, top + 1)}
    groups = []
    for d in range(top + 1):
        cycles = len(faces[d]) - (boundaries[d].rank() if d > 0 else 0)
        incoming = boundaries.get(d + 1)
        factors = (
            [] if incoming is None else [abs(f) for f in invariant_factors(incoming, domain=ZZ)]
        )
        nonzero = [f for f in factors if f != 0]
        groups.append(AbelianGroup(cycles - len(nonzero), [int(f) for f in nonzero if f > 1]))
    return groups
