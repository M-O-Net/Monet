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


def _points(shape):
    if isinstance(shape, Polygon):
        return [tuple(point) for point in sorted(shape.vertices, key=tuple)]
    return [tuple(point) for point in shape.points]


def _solid(shape):
    return isinstance(shape, Polytope) and all(len(point) == 3 for point in shape.points)


TOLERANCE = 1e-9


def _negligible(value):
    return abs(value) < TOLERANCE


def _close(u, v):
    return all(_negligible(a - b) for a, b in zip(u, v, strict=True))


def _dot(u, v):
    return sum(a * b for a, b in zip(u, v, strict=True))


def _isometries(points):
    dimension = len(points[0])
    centre = [sum(p[k] for p in points) / len(points) for k in range(dimension)]
    vectors = [tuple(float(p[k] - centre[k]) for k in range(dimension)) for p in points]
    basis = []
    for i in range(len(vectors)):
        if Matrix([vectors[j] for j in [*basis, i]]).rank(iszerofunc=_negligible) > len(basis):
            basis.append(i)
    source = Matrix([vectors[i] for i in basis]).T.inv()
    found = []

    def fits(images, image):
        pairs = [*zip(basis, images, strict=False), (basis[len(images)], image)]
        target = basis[len(images)]
        return all(
            _negligible(_dot(vectors[target], vectors[b]) - _dot(vectors[image], vectors[i]))
            for b, i in pairs
        )

    def extend(images):
        if len(images) < len(basis):
            for image in range(len(vectors)):
                if image not in images and fits(images, image):
                    extend([*images, image])
            return
        linear = Matrix([vectors[i] for i in images]).T * source
        mapped = [tuple(linear * Matrix(v)) for v in vectors]
        permutation = [
            next((j for j, w in enumerate(vectors) if _close(m, w)), None) for m in mapped
        ]
        if None not in permutation and len(set(permutation)) == len(vectors):
            found.append(Permutation(permutation))

    extend([])
    return found


def accepts(shape):
    return isinstance(shape, Polygon) or _solid(shape)


def compute(shape):
    return _canonical(PermutationGroup(_isometries(_points(shape))))
