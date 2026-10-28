from itertools import combinations


def _points(shape):
    if isinstance(shape, Polygon):
        return [tuple(point) for point in sorted(shape.vertices, key=tuple)]
    return [tuple(point) for point in shape.points]


def _solid(shape):
    return isinstance(shape, Polytope) and all(len(point) == 3 for point in shape.points)


def _minus(u, v):
    return [a - b for a, b in zip(u, v, strict=True)]


def _cross(u, v):
    return [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]


def accepts(shape):
    return _solid(shape)


def compute(shape):
    points = _points(shape)
    facets = set()
    for i, j, k in combinations(range(len(points)), 3):
        normal = _cross(_minus(points[j], points[i]), _minus(points[k], points[i]))
        if all(c == 0 for c in normal):
            continue
        heights = [
            sum(n * c for n, c in zip(normal, _minus(p, points[i]), strict=True)) for p in points
        ]
        if all(h >= 0 for h in heights) or all(h <= 0 for h in heights):
            facets.add(frozenset(m for m, h in enumerate(heights) if h == 0))
    edges = [
        (u, v)
        for u, v in combinations(range(len(points)), 2)
        if sum(1 for facet in facets if u in facet and v in facet) >= 2
    ]
    return Graph(len(points), edges)
