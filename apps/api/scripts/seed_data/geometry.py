import itertools

from seed_data.build import (
    HALF_SQRT3_CELL,
    MINUS_HALF_SQRT3_CELL,
    SQRT3_CELL,
    Instance,
    Reference,
    fraction,
    instance,
    lattice_polytope,
    polygon_instance,
)

INSTANCES: dict[str, Instance] = {
    "simplex4": instance(
        r"\operatorname{conv}\left\{0, e_{1}, e_{2}, e_{3}, e_{4}\right\}",
        lattice_polytope([(0, 0, 0, 0), *(tuple(int(i == j) for j in range(4)) for i in range(4))]),
        ["ConvexPolytopes"],
        "A four-dimensional simplex.",
    ),
    "tesseract": instance(
        r"[0, 1]^{4}",
        lattice_polytope(list(itertools.product((0, 1), repeat=4))),
        ["ConvexPolytopes"],
        "The four-dimensional cube.",
    ),
    "cross_polytope4": instance(
        r"\operatorname{conv}\left\{\pm e_{1}, \pm e_{2}, \pm e_{3}, \pm e_{4}\right\}",
        lattice_polytope(
            [tuple(sign if i == j else 0 for j in range(4)) for i in range(4) for sign in (1, -1)]
        ),
        ["ConvexPolytopes"],
        "The 16-cell.",
    ),
    "unit_square": polygon_instance([(0, 0), (0, 1), (1, 0), (1, 1)], ["ConvexPolygons"]),
    "trapezoid": polygon_instance([(0, 0), (1, 1), (2, 1), (3, 0)], ["ConvexPolygons"]),
    "hexagon": polygon_instance(
        [
            (-1, 0),
            (fraction(-1, 2), MINUS_HALF_SQRT3_CELL),
            (fraction(-1, 2), HALF_SQRT3_CELL),
            (fraction(1, 2), MINUS_HALF_SQRT3_CELL),
            (fraction(1, 2), HALF_SQRT3_CELL),
            (1, 0),
        ],
        ["ConvexPolygons"],
        "The regular hexagon inscribed in the unit circle.",
    ),
    "right_triangle": polygon_instance([(0, 0), (0, 1), (1, 0)], ["Triangles"]),
    "triangle_345": polygon_instance(
        [(0, 0), (0, 3), (4, 0)], ["Triangles"], "The 3-4-5 right triangle."
    ),
    "equilateral_triangle": polygon_instance(
        [(0, 0), (1, SQRT3_CELL), (2, 0)], ["Triangles"], "The equilateral triangle of side 2."
    ),
    "square_pyramid": instance(
        r"\operatorname{conv}\left\{\left(0, 0, 0\right), \left(0, 2, 0\right), "
        r"\left(1, 1, 1\right), \left(2, 0, 0\right), \left(2, 2, 0\right)\right\}",
        lattice_polytope([(0, 0, 0), (2, 0, 0), (0, 2, 0), (2, 2, 0), (1, 1, 1)]),
        ["ConvexPolyhedra"],
        "A square pyramid.",
    ),
    "triangular_prism": instance(
        r"\operatorname{conv}\left\{0, e_{1}, e_{2}\right\} \times [0, 1]",
        lattice_polytope([(x, y, z) for x, y in ((0, 0), (1, 0), (0, 1)) for z in (0, 1)]),
        ["ConvexPolyhedra"],
        "A triangular prism.",
    ),
    "cuboid": instance(
        r"[0, 1] \times [0, 1] \times [0, 2]",
        lattice_polytope(list(itertools.product((0, 1), (0, 1), (0, 2)))),
        ["ConvexPolyhedra"],
        "A box twice as tall as it is wide.",
    ),
    "tetrahedron": instance(
        r"\operatorname{conv}\left\{\left(0, 0, 0\right), \left(0, 1, 1\right), "
        r"\left(1, 0, 1\right), \left(1, 1, 0\right)\right\}",
        lattice_polytope([(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)]),
        ["PlatonicSolids"],
        "A regular tetrahedron: every other vertex of the unit cube.",
    ),
    "cube": instance(
        r"[0, 1]^{3}",
        lattice_polytope(list(itertools.product((0, 1), repeat=3))),
        ["PlatonicSolids"],
        "The unit cube.",
    ),
    "octahedron": instance(
        r"\operatorname{conv}\left\{\pm e_{1}, \pm e_{2}, \pm e_{3}\right\}",
        lattice_polytope(
            [tuple(sign if i == j else 0 for j in range(3)) for i in range(3) for sign in (1, -1)]
        ),
        ["PlatonicSolids"],
        "The regular octahedron.",
    ),
    "circle": instance(
        r"x^{2} + y^{2} = 1",
        {"curve": "Add(Pow(Symbol('x'), Integer(2)), Pow(Symbol('y'), Integer(2)), Integer(-1))"},
        ["PlaneCurves"],
        "The unit circle.",
    ),
    "cusp": instance(
        r"y^{2} = x^{3}",
        {
            "curve": "Add(Pow(Symbol('x'), Integer(3)), "
            "Mul(Integer(-1), Pow(Symbol('y'), Integer(2))))"
        },
        ["PlaneCurves"],
        "The cuspidal cubic: a Weierstrass equation that is singular at the origin, so not "
        "an elliptic curve.",
    ),
    "folium": instance(
        r"x^{3} - 3 x y + y^{3} = 0",
        {
            "curve": "Add(Pow(Symbol('x'), Integer(3)), Mul(Integer(-1), Integer(3), "
            "Symbol('x'), Symbol('y')), Pow(Symbol('y'), Integer(3)))"
        },
        ["PlaneCurves"],
        "The folium of Descartes.",
    ),
    "congruent_number_curve": instance(
        r"y^{2} = x^{3} - x",
        {
            "curve": "Add(Pow(Symbol('x'), Integer(3)), Mul(Integer(-1), Symbol('x')), "
            "Mul(Integer(-1), Pow(Symbol('y'), Integer(2))))"
        },
        ["EllipticCurves"],
        "Conductor 32; it has complex multiplication by the Gaussian integers.",
    ),
    "curve_36": instance(
        r"y^{2} = x^{3} + 1",
        {
            "curve": "Add(Pow(Symbol('x'), Integer(3)), Mul(Integer(-1), Pow(Symbol('y'), "
            "Integer(2))), Integer(1))"
        },
        ["EllipticCurves"],
        "Conductor 36; six rational points, including the point at infinity.",
    ),
    "curve_37a": instance(
        r"y^{2} + y = x^{3} - x",
        {
            "curve": "Add(Pow(Symbol('x'), Integer(3)), Mul(Integer(-1), Symbol('x')), "
            "Mul(Integer(-1), Pow(Symbol('y'), Integer(2))), Mul(Integer(-1), Symbol('y')))"
        },
        ["EllipticCurves"],
        "The elliptic curve of rank one with the smallest conductor, 37.",
    ),
}

REFERENCES: dict[str, list[Reference]] = {
    "curve_37a": [("LMFDB 37.a1", "https://www.lmfdb.org/EllipticCurve/Q/37/a/1")],
}
