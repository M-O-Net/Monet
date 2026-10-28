import itertools

from seed_data.build import (
    HALF_SQRT2_CELL,
    HALF_SQRT3_CELL,
    MINUS_HALF_SQRT2_CELL,
    MINUS_HALF_SQRT3_CELL,
    SQRT3_CELL,
    Instance,
    Reference,
    RelationSpec,
    Specimen,
    algebraic,
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
    "curve_11a": instance(
        r"y^{2} + y = x^{3} - x^{2} - 10 x - 20",
        {
            "curve": "Add(Pow(Symbol('x'), Integer(3)), Mul(Integer(-1), Pow(Symbol('x'), "
            "Integer(2))), Mul(Integer(-1), Integer(10), Symbol('x')), Mul(Integer(-1), "
            "Pow(Symbol('y'), Integer(2))), Mul(Integer(-1), Symbol('y')), Integer(-20))"
        },
        ["EllipticCurves"],
        "The elliptic curve of smallest conductor, 11, with five rational points.",
    ),
    "fermat_quartic": instance(
        r"x^{4} + y^{4} = 1",
        {"curve": "Add(Pow(Symbol('x'), Integer(4)), Pow(Symbol('y'), Integer(4)), Integer(-1))"},
        ["PlaneCurves"],
        "The Fermat quartic: smooth, so of genus three.",
    ),
    "regular_triangle": polygon_instance(
        [
            (fraction(-1, 2), MINUS_HALF_SQRT3_CELL),
            (fraction(-1, 2), HALF_SQRT3_CELL),
            (1, 0),
        ],
        ["Triangles"],
        "The equilateral triangle inscribed in the unit circle.",
    ),
    "unit_diamond": polygon_instance(
        [(-1, 0), (0, -1), (0, 1), (1, 0)],
        ["ConvexPolygons"],
        "The square inscribed in the unit circle.",
    ),
    "octagon": polygon_instance(
        [
            (-1, 0),
            (MINUS_HALF_SQRT2_CELL, MINUS_HALF_SQRT2_CELL),
            (MINUS_HALF_SQRT2_CELL, HALF_SQRT2_CELL),
            (0, -1),
            (0, 1),
            (HALF_SQRT2_CELL, MINUS_HALF_SQRT2_CELL),
            (HALF_SQRT2_CELL, HALF_SQRT2_CELL),
            (1, 0),
        ],
        ["ConvexPolygons"],
        "The regular octagon inscribed in the unit circle.",
    ),
    "right_triangle_medial": polygon_instance(
        [(0, fraction(1, 2)), (fraction(1, 2), 0), (fraction(1, 2), fraction(1, 2))],
        ["Triangles"],
    ),
    "triangle_345_medial": polygon_instance(
        [(0, fraction(3, 2)), (2, 0), (2, fraction(3, 2))], ["Triangles"]
    ),
    "equilateral_medial": polygon_instance(
        [(fraction(1, 2), HALF_SQRT3_CELL), (1, 0), (fraction(3, 2), HALF_SQRT3_CELL)],
        ["Triangles"],
    ),
    "sqrt3": instance(SQRT3_CELL[0], SQRT3_CELL[1], ["AlgebraicIntegers"]),
    "three_halves_sqrt3": instance(
        r"\frac{3 \sqrt{3}}{2}", algebraic([-27, 0, 4], 1), ["AlgebraicNumbers"]
    ),
}

SECTIONS: dict[str, Specimen] = {
    "GeometryOperations": (
        r"\text{Geometry Operations}",
        "Operations taking a polytope or a plane curve as input, and the constructions that "
        "produce one.",
    ),
}

OPERATORS: dict[str, Specimen] = {
    "SymmetryGroup": (
        r"\text{Symmetry Group}",
        "The isometries of the plane or space mapping a polygon or polyhedron to itself, "
        "reflections included, as permutations of its vertices in their stored order.",
    ),
    "DualPolyhedron": (
        r"\text{Dual Polyhedron}",
        "The polyhedron with a vertex for each face and a face for each vertex, up to "
        "similarity. Asserted: building it needs a convex hull.",
    ),
    "EdgeGraph": (
        r"\text{Edge Graph}",
        "The vertices and edges of a polyhedron, numbered in the stored order of its "
        "vertices. Two vertices are joined when two faces contain both. By Steinitz's "
        "theorem these are exactly the 3-connected planar graphs.",
    ),
    "PolygonArea": (r"\text{Area}", "The area enclosed by a convex polygon."),
    "MedialTriangle": (
        r"\text{Medial Triangle}",
        r"The triangle on the midpoints of the sides: similar to the original, with ratio "
        r"$\frac{1}{2}$.",
    ),
    "RegularPolygon": (
        r"\text{Regular Polygon}",
        r"The regular $n$-gon inscribed in the unit circle with a vertex at $(1, 0)$.",
    ),
    "EllipticDiscriminant": (
        r"\text{Elliptic Discriminant}",
        r"$\Delta$ of a Weierstrass equation $y^{2} + a_{1} x y + a_{3} y = x^{3} + a_{2} "
        r"x^{2} + a_{4} x + a_{6}$. Its primes are where the curve has bad reduction.",
    ),
    "Conductor": (
        r"\text{Conductor}",
        "The arithmetic conductor of an elliptic curve, by which LMFDB labels it. Asserted "
        "from LMFDB: computing it needs Tate's algorithm.",
    ),
    "TorsionSubgroup": (
        r"\text{Torsion Subgroup}",
        "The rational points of finite order. By Mazur's theorem it is one of fifteen "
        "groups. Asserted from LMFDB.",
    ),
    "RiemannSurface": (
        r"\text{Riemann Surface}",
        r"The compact Riemann surface of a plane curve: orientable of genus "
        r"$(d - 1)(d - 2)/2$ for a smooth curve of degree $d$. Singular curves are asserted.",
    ),
}

SIGNATURES: list[tuple[str, str, str]] = [
    ("SymmetryGroup", "ConvexPolygons", "PermutationGroups"),
    ("SymmetryGroup", "ConvexPolyhedra", "PermutationGroups"),
    ("DualPolyhedron", "ConvexPolyhedra", "ConvexPolyhedra"),
    ("DualPolyhedron", "PlatonicSolids", "PlatonicSolids"),
    ("EdgeGraph", "ConvexPolyhedra", "PlanarGraphs"),
    ("EdgeGraph", "PlatonicSolids", "RegularGraphs"),
    ("PolygonArea", "ConvexPolygons", "RationalNumbers"),
    ("PolygonArea", "ConvexPolygons", "AlgebraicNumbers"),
    ("MedialTriangle", "Triangles", "Triangles"),
    ("RegularPolygon", "PositiveIntegers", "ConvexPolygons"),
    ("EllipticDiscriminant", "EllipticCurves", "RationalNumbers"),
    ("Conductor", "EllipticCurves", "PositiveIntegers"),
    ("TorsionSubgroup", "EllipticCurves", "FinitelyGeneratedAbelianGroups"),
    ("RiemannSurface", "PlaneCurves", "ClosedSurfaces"),
]

IMPLEMENTATIONS: dict[str, str] = {
    "SymmetryGroup": "symmetry_group",
    "EdgeGraph": "edge_graph",
    "PolygonArea": "polygon_area",
    "MedialTriangle": "medial_triangle",
    "RegularPolygon": "regular_polygon",
    "EllipticDiscriminant": "elliptic_discriminant",
    "RiemannSurface": "riemann_surface",
}

RELATIONS: list[RelationSpec] = [
    ("SymmetryGroup", ["equilateral_triangle"], ["s3"]),
    ("SymmetryGroup", ["triangle_345"], ["trivial3"]),
    ("SymmetryGroup", ["trapezoid"], ["path_reversal_group"]),
    ("SymmetryGroup", ["unit_square"], ["square_symmetry"]),
    ("SymmetryGroup", ["hexagon"], ["d6"]),
    ("SymmetryGroup", ["tetrahedron"], ["s4"]),
    ("SymmetryGroup", ["octahedron"], ["signed_permutations3"]),
    ("SymmetryGroup", ["cube"], ["cube_symmetry"]),
    ("DualPolyhedron", ["cube"], ["octahedron"]),
    ("DualPolyhedron", ["octahedron"], ["cube"]),
    ("DualPolyhedron", ["tetrahedron"], ["tetrahedron"]),
    ("DualPolyhedron", ["square_pyramid"], ["square_pyramid"]),
    ("EdgeGraph", ["tetrahedron"], ["k4"]),
    ("EdgeGraph", ["cube"], ["cube_graph"]),
    ("EdgeGraph", ["cuboid"], ["cube_graph"]),
    ("EdgeGraph", ["octahedron"], ["octahedral_graph"]),
    ("EdgeGraph", ["square_pyramid"], ["wheel5"]),
    ("EdgeGraph", ["triangular_prism"], ["prism_graph"]),
    ("PolygonArea", ["unit_square"], [1]),
    ("PolygonArea", ["trapezoid"], [2]),
    ("PolygonArea", ["right_triangle"], ["half"]),
    ("PolygonArea", ["triangle_345"], [6]),
    ("PolygonArea", ["equilateral_triangle"], ["sqrt3"]),
    ("PolygonArea", ["hexagon"], ["three_halves_sqrt3"]),
    ("MedialTriangle", ["right_triangle"], ["right_triangle_medial"]),
    ("MedialTriangle", ["triangle_345"], ["triangle_345_medial"]),
    ("MedialTriangle", ["equilateral_triangle"], ["equilateral_medial"]),
    ("RegularPolygon", [3], ["regular_triangle"]),
    ("RegularPolygon", [4], ["unit_diamond"]),
    ("RegularPolygon", [6], ["hexagon"]),
    ("RegularPolygon", [8], ["octagon"]),
    ("EllipticDiscriminant", ["congruent_number_curve"], [64]),
    ("EllipticDiscriminant", ["curve_36"], [-432]),
    ("EllipticDiscriminant", ["curve_37a"], [37]),
    ("EllipticDiscriminant", ["curve_11a"], [-161051]),
    ("Conductor", ["congruent_number_curve"], [32]),
    ("Conductor", ["curve_36"], [36]),
    ("Conductor", ["curve_37a"], [37]),
    ("Conductor", ["curve_11a"], [11]),
    ("TorsionSubgroup", ["congruent_number_curve"], ["klein_four"]),
    ("TorsionSubgroup", ["curve_36"], ["c6"]),
    ("TorsionSubgroup", ["curve_37a"], ["trivial_group"]),
    ("TorsionSubgroup", ["curve_11a"], ["c5"]),
    ("RiemannSurface", ["circle"], ["sphere"]),
    ("RiemannSurface", ["congruent_number_curve"], ["torus"]),
    ("RiemannSurface", ["curve_36"], ["torus"]),
    ("RiemannSurface", ["curve_37a"], ["torus"]),
    ("RiemannSurface", ["curve_11a"], ["torus"]),
    ("RiemannSurface", ["fermat_quartic"], ["genus3"]),
]

ASSERTED: list[RelationSpec] = [
    ("RiemannSurface", ["folium"], ["sphere"]),
    ("RiemannSurface", ["cusp"], ["sphere"]),
]

DISPLAYS: dict[str, tuple[str | None, bool]] = {
    "PolygonArea": (r"\op{\operatorname{area}(}{in0}\op{)} = {out0}", False),
    "EllipticDiscriminant": (r"\op{\Delta(}{in0}\op{)} = {out0}", False),
    "Conductor": (r"\op{N(}{in0}\op{)} = {out0}", False),
}


def _lmfdb_curve(label: str, path: str) -> list[Reference]:
    return [(f"LMFDB {label}", f"https://www.lmfdb.org/EllipticCurve/Q/{path}")]


REFERENCES: dict[str, list[Reference]] = {
    "curve_37a": _lmfdb_curve("37.a1", "37/a/1"),
    "curve_11a": _lmfdb_curve("11.a2", "11/a/2"),
    "congruent_number_curve": _lmfdb_curve("32.a3", "32/a/3"),
    "curve_36": _lmfdb_curve("36.a4", "36/a/4"),
    "EllipticDiscriminant": [("Wikipedia", "https://en.wikipedia.org/wiki/Elliptic_curve")],
    "TorsionSubgroup": [("Wikipedia", "https://en.wikipedia.org/wiki/Mazur%27s_torsion_theorem")],
    "RiemannSurface": [("Wikipedia", "https://en.wikipedia.org/wiki/Genus%E2%80%93degree_formula")],
    "DualPolyhedron": [("Wikipedia", "https://en.wikipedia.org/wiki/Dual_polyhedron")],
    "EdgeGraph": [("Wikipedia", "https://en.wikipedia.org/wiki/Steinitz%27s_theorem")],
}

FILINGS: dict[str, list[str]] = {
    "Geometry": ["GeometryOperations"],
    "GeometryOperations": list(OPERATORS),
}
