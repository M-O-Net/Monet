from fractions import Fraction

from seed_data.build import (
    Cell,
    Instance,
    Reference,
    RelationSpec,
    Specimen,
    expr,
    instance,
    knot,
    knot_atlas,
    matrix_instance,
    polynomial,
    simplicial,
    surface,
)

TORUS_KNOT_TYPES = ["TorusKnots", "AlternatingKnots", "TwoBridgeKnots"]


def _twist_seifert(twists: int) -> list[list[Cell]]:
    return [[-1, 1], [0, twists]]


def _t_power(sign: int, power: int) -> Cell:
    latex = ("- " if sign < 0 else "") + f"t^{{{power}}}"
    return latex, polynomial(*([0] * power), sign, var="t")


def _laurent(latex: str, srepr: str) -> Cell:
    return latex, expr(srepr)


# \mathrm{} stops sympy reading these as the integers 31, 51 and 71.
INSTANCES: dict[str, Instance] = {
    "K3": instance(
        r"\mathrm{3}_{1}",
        knot("3_1"),
        TORUS_KNOT_TYPES,
        "The trefoil — the simplest knot that cannot be untied.",
    ),
    "K5": instance(
        r"\mathrm{5}_{1}",
        knot("5_1"),
        TORUS_KNOT_TYPES,
        "The (2, 5) torus knot: two strands, five crossings.",
    ),
    "K7": instance(
        r"\mathrm{7}_{1}",
        knot("7_1"),
        TORUS_KNOT_TYPES,
        "The (2, 7) torus knot: two strands, seven crossings.",
    ),
    "K4_1": instance(
        r"\mathrm{4}_{1}",
        knot("4_1"),
        ["AlternatingKnots", "AmphichiralKnots", "TwoBridgeKnots"],
        "The figure-eight knot.",
    ),
    "K5_2": instance(
        r"\mathrm{5}_{2}",
        knot("5_2"),
        ["AlternatingKnots", "TwoBridgeKnots"],
        "The three-twist knot.",
    ),
    "K6_1": instance(
        r"\mathrm{6}_{1}", knot("6_1"), ["AlternatingKnots", "TwoBridgeKnots"], "Stevedore's knot."
    ),
    "K6_3": instance(
        r"\mathrm{6}_{3}", knot("6_3"), ["AlternatingKnots", "AmphichiralKnots", "TwoBridgeKnots"]
    ),
    "K8_3": instance(
        r"\mathrm{8}_{3}", knot("8_3"), ["AlternatingKnots", "AmphichiralKnots", "TwoBridgeKnots"]
    ),
    "K8_19": instance(
        r"\mathrm{8}_{19}",
        knot("8_19"),
        ["TorusKnots"],
        "The (3, 4) torus knot, and the first knot in the table that is not alternating.",
    ),
    "trefoil_braid": instance(
        r"\sigma_{1}^{3}",
        {"braid": {"strands": 2, "word": [1, 1, 1]}},
        ["BraidWords"],
        "Two strands, three half-twists; its closure is the trefoil.",
    ),
    "figure_eight_braid": instance(
        r"\sigma_{1} \sigma_{2}^{-1} \sigma_{1} \sigma_{2}^{-1}",
        {"braid": {"strands": 3, "word": [1, -2, 1, -2]}},
        ["BraidWords"],
        "Its closure is the figure-eight knot.",
    ),
    "torus_braid_34": instance(
        r"\left(\sigma_{1} \sigma_{2}\right)^{4}",
        {"braid": {"strands": 3, "word": [1, 2, 1, 2, 1, 2, 1, 2]}},
        ["BraidWords"],
        r"Its closure is the $(3, 4)$ torus knot $8_{19}$.",
    ),
    "sphere": instance("S^{2}", surface(True, 0), ["ClosedSurfaces"], "The sphere."),
    "torus": instance("T^{2}", surface(True, 1), ["ClosedSurfaces"], "The torus."),
    "genus2": instance(
        r"T^{2} \# T^{2}", surface(True, 2), ["ClosedSurfaces"], "The surface of genus two."
    ),
    "genus3": instance(
        r"T^{2} \# T^{2} \# T^{2}",
        surface(True, 3),
        ["ClosedSurfaces"],
        "The surface of genus three: the Riemann surface of a smooth plane quartic.",
    ),
    "projective_plane": instance(
        r"\mathbb{RP}^{2}", surface(False, 1), ["ClosedSurfaces"], "The real projective plane."
    ),
    "klein_bottle": instance(
        r"\mathbb{RP}^{2} \# \mathbb{RP}^{2}",
        surface(False, 2),
        ["ClosedSurfaces"],
        "The Klein bottle.",
    ),
    "triangle_boundary": instance(
        r"\partial \Delta^{2}",
        simplicial([(0, 1), (0, 2), (1, 2)]),
        ["SimplicialComplexes"],
        "The boundary of a triangle: a circle.",
    ),
    "tetrahedron_boundary": instance(
        r"\partial \Delta^{3}",
        simplicial([(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]),
        ["SimplicialComplexes"],
        "The boundary of a tetrahedron: a sphere.",
    ),
    "moebius_torus": instance(
        r"T^{2}_{7}",
        simplicial(
            [
                *((i, (i + 1) % 7, (i + 3) % 7) for i in range(7)),
                *((i, (i + 2) % 7, (i + 3) % 7) for i in range(7)),
            ]
        ),
        ["SimplicialComplexes"],
        "Möbius's torus: the smallest triangulation of the torus, on seven vertices.",
    ),
    "cinquefoil_braid": instance(
        r"\sigma_{1}^{5}",
        {"braid": {"strands": 2, "word": [1, 1, 1, 1, 1]}},
        ["BraidWords"],
        r"Two strands, five half-twists; its closure is $5_{1}$.",
    ),
    "hopf_braid": instance(
        r"\sigma_{1}^{2}",
        {"braid": {"strands": 2, "word": [1, 1]}},
        ["BraidWords"],
        "Its closure is the Hopf link, two linked circles: a link rather than a knot.",
    ),
    "rp2_6": instance(
        r"\mathbb{RP}^{2}_{6}",
        simplicial(
            [
                (0, 1, 2),
                (0, 1, 3),
                (0, 2, 4),
                (0, 3, 5),
                (0, 4, 5),
                (1, 2, 5),
                (1, 3, 4),
                (1, 4, 5),
                (2, 3, 4),
                (2, 3, 5),
            ]
        ),
        ["SimplicialComplexes"],
        "The smallest triangulation of the real projective plane, on six vertices: half an "
        "icosahedron.",
    ),
    "solid_triangle": instance(
        r"\Delta^{2}",
        simplicial([(0, 1, 2)]),
        ["SimplicialComplexes"],
        "A filled triangle: contractible.",
    ),
    "two_circles": instance(
        r"\partial \Delta^{2} \sqcup \partial \Delta^{2}",
        simplicial([(0, 1), (0, 2), (1, 2), (3, 4), (3, 5), (4, 5)]),
        ["SimplicialComplexes"],
        "Two disjoint circles.",
    ),
    "V4_1": matrix_instance(
        _twist_seifert(1),
        ["InvertibleIntegerMatrices", "DiagonalizableMatrices"],
        r"A Seifert matrix of $4_{1}$.",
    ),
    "V5_2": matrix_instance(
        _twist_seifert(-2),
        ["InvertibleRationalMatrices", "DiagonalizableMatrices"],
        r"A Seifert matrix of $5_{2}$.",
    ),
    "V6_1": matrix_instance(
        _twist_seifert(2),
        ["InvertibleRationalMatrices", "DiagonalizableMatrices"],
        r"A Seifert matrix of $6_{1}$.",
    ),
    "alexander_4_1": instance(
        r"- x^{2} + 3 x - 1",
        polynomial(-1, 3, -1),
        ["IntegerPolynomials", "IrreduciblePolynomials"],
    ),
    "alexander_5_2": instance(
        r"2 x^{2} - 3 x + 2", polynomial(2, -3, 2), ["IntegerPolynomials", "IrreduciblePolynomials"]
    ),
    "alexander_6_1": instance(
        r"- 2 x^{2} + 5 x - 2", polynomial(-2, 5, -2), ["IntegerPolynomials"]
    ),
    "jones_3_1": instance(
        r"- t^{4} + t^{3} + t", polynomial(0, 1, 0, 1, -1, var="t"), ["IntegerPolynomials"]
    ),
    "jones_5_1": instance(
        r"- t^{7} + t^{6} - t^{5} + t^{4} + t^{2}",
        polynomial(0, 0, 1, 0, 1, -1, 1, -1, var="t"),
        ["IntegerPolynomials"],
    ),
    "jones_8_19": instance(
        r"- t^{8} + t^{5} + t^{3}",
        polynomial(0, 0, 0, 1, 0, 1, 0, 0, -1, var="t"),
        ["IntegerPolynomials"],
    ),
    "jones_4_1": instance(
        r"t^{2} - t + 1 - \frac{1}{t} + \frac{1}{t^{2}}",
        expr(
            "Add(Pow(Symbol('t'), Integer(2)), Mul(Integer(-1), Symbol('t')), Integer(1), "
            "Mul(Integer(-1), Pow(Symbol('t'), Integer(-1))), Pow(Symbol('t'), Integer(-2)))"
        ),
        ["Expressions"],
    ),
    "jones_hopf": instance(
        r"- t^{\frac{5}{2}} - \sqrt{t}",
        expr(
            "Add(Mul(Integer(-1), Pow(Symbol('t'), Rational(5, 2))), "
            "Mul(Integer(-1), Pow(Symbol('t'), Rational(1, 2))))"
        ),
        ["Expressions"],
        "The Jones polynomial of the Hopf link: half-integer powers, as for every link with "
        "an even number of components.",
    ),
    "burau_3_1": matrix_instance([[_t_power(-1, 3)]], ["InvertibleMatrices", "ColumnVectors"]),
    "burau_5_1": matrix_instance([[_t_power(-1, 5)]], ["InvertibleMatrices", "ColumnVectors"]),
    "burau_hopf": matrix_instance([[_t_power(1, 2)]], ["InvertibleMatrices", "ColumnVectors"]),
    "burau_8_19": matrix_instance(
        [[0, _t_power(-1, 4)], [_t_power(1, 4), _t_power(-1, 4)]], ["InvertibleMatrices"]
    ),
    "burau_4_1": matrix_instance(
        [
            [
                _laurent(
                    r"t^{2} - 2 t + 1 - \frac{1}{t}",
                    "Add(Pow(Symbol('t'), Integer(2)), Mul(Integer(-1), Integer(2), "
                    "Symbol('t')), Integer(1), Mul(Integer(-1), Pow(Symbol('t'), Integer(-1))))",
                ),
                _laurent(
                    r"1 - \frac{1}{t} + \frac{1}{t^{2}}",
                    "Add(Integer(1), Mul(Integer(-1), Pow(Symbol('t'), Integer(-1))), "
                    "Pow(Symbol('t'), Integer(-2)))",
                ),
            ],
            [
                _laurent(
                    r"- t + 1 - \frac{1}{t}",
                    "Add(Mul(Integer(-1), Symbol('t')), Integer(1), "
                    "Mul(Integer(-1), Pow(Symbol('t'), Integer(-1))))",
                ),
                _laurent(
                    r"- \frac{1}{t} + \frac{1}{t^{2}}",
                    "Add(Mul(Integer(-1), Pow(Symbol('t'), Integer(-1))), "
                    "Pow(Symbol('t'), Integer(-2)))",
                ),
            ],
        ],
        ["InvertibleMatrices"],
    ),
}

SECTIONS: dict[str, Specimen] = {
    "KnotOperations": (
        r"\text{Knot Operations}",
        "Operations taking a knot, a braid or a Seifert matrix as input: Seifert matrices, "
        "Alexander and Jones polynomials, braid closures.",
    ),
    "SurfaceOperations": (
        r"\text{Surface Operations}",
        "Operations taking a closed surface or a simplicial complex as input.",
    ),
}

OPERATORS: dict[str, Specimen] = {
    "SeifertMatrix": (
        r"\text{Seifert Matrix}",
        "For a knot, the integer matrix recording how a surface spanning it twists. "
        "Asserted rather than computed: it depends on a choice of surface.",
    ),
    "KnotDeterminant": (
        r"\text{Knot Determinant}",
        r"For a Seifert matrix $V$, the value $|\det(V + V^{T})|$. For the $(2, n)$ "
        r"torus knots seeded here it comes out as $n$ itself.",
    ),
    "AlexanderPolynomial": (
        r"\text{Alexander Polynomial}",
        r"For a Seifert matrix $V$, the polynomial $\det(V - xV^{T})$.",
    ),
    "KnotSignature": (
        r"\text{Knot Signature}",
        r"For a Seifert matrix $V$, the number of positive eigenvalues of $V + V^{T}$ minus "
        "the number of negative ones. It bounds the unknotting number from below.",
    ),
    "JonesPolynomial": (
        r"\text{Jones Polynomial}",
        "The Jones polynomial of a braid's closure, from the Kauffman bracket summed over "
        r"all $2^{c}$ smoothings of its $c$ crossings. It tells the trefoil from its mirror, "
        "which the Alexander polynomial cannot.",
    ),
    "CrossingNumber": (
        r"\text{Crossing Number}",
        "The fewest crossings of any diagram of the knot, read from its Rolfsen name.",
    ),
    "TorusKnot": (
        r"\text{Torus Knot}",
        r"$T(p, q)$, winding $p$ times around one axis of a torus and $q$ times around the "
        "other. Asserted from the knot table.",
    ),
    "TwoBridgeKnot": (
        r"\text{Two-Bridge Knot}",
        r"Schubert's $K(p/q)$, for $p/q$ the continued fraction of the knot's Conway "
        r"notation. Its determinant is $p$. Asserted from the knot table.",
    ),
    "BraidClosure": (
        r"\text{Braid Closure}",
        "The knot formed by joining the top of each strand to its bottom. Asserted: naming "
        "the closure needs a knot table.",
    ),
    "BurauMatrix": (
        r"\text{Burau Matrix}",
        "The reduced Burau representation of a braid on n strands: an (n - 1) square matrix "
        r"over $\mathbb{Z}[t, t^{-1}]$. Divided by $1 + t + \dots + t^{n - 1}$, "
        r"$\det(I - B)$ is the Alexander polynomial of the closure.",
    ),
    "BraidPermutation": (
        r"\text{Braid Permutation}",
        r"Where each strand ends: $p(i)$ is the bottom position of the strand starting at "
        "position i. Its cycles are the components of the closure.",
    ),
    "EulerCharacteristic": (
        r"\text{Euler Characteristic}",
        r"Vertices minus edges plus faces, and so on: $2 - 2g$ for an orientable surface of "
        r"genus $g$, $2 - k$ for a sum of $k$ projective planes.",
    ),
    "Homology": (
        r"\text{Homology}",
        r"For a closed surface its first homology group; for a simplicial complex every "
        "homology group, from dimension 0 up, from the Smith normal forms of its boundary "
        "matrices.",
    ),
    "FundamentalGroup": (
        r"\text{Fundamental Group}",
        r"$\langle a_{1}, b_{1}, \dots, a_{g}, b_{g} \mid [a_{1}, b_{1}] \cdots [a_{g}, "
        r"b_{g}] \rangle$ for an orientable surface, $\langle a_{1}, \dots, a_{k} \mid "
        r"a_{1}^{2} \cdots a_{k}^{2} \rangle$ for a sum of projective planes.",
    ),
}

SIGNATURES: list[tuple[str, str, str]] = [
    ("SeifertMatrix", "Knots", "Matrices"),
    ("AlexanderPolynomial", "Matrices", "Polynomials"),
    ("AlexanderPolynomial", "Matrices", "IntegerPolynomials"),
    ("KnotDeterminant", "Matrices", "Integers"),
    ("KnotSignature", "Matrices", "Integers"),
    ("JonesPolynomial", "BraidWords", "Expressions"),
    ("JonesPolynomial", "BraidWords", "IntegerPolynomials"),
    ("CrossingNumber", "Knots", "PositiveIntegers"),
    ("TorusKnot", "PositiveIntegers", "TorusKnots"),
    ("TwoBridgeKnot", "RationalNumbers", "TwoBridgeKnots"),
    ("BraidClosure", "BraidWords", "Knots"),
    ("BurauMatrix", "BraidWords", "InvertibleMatrices"),
    ("BraidPermutation", "BraidWords", "Permutations"),
    ("EulerCharacteristic", "ClosedSurfaces", "Integers"),
    ("EulerCharacteristic", "SimplicialComplexes", "Integers"),
    ("Homology", "ClosedSurfaces", "FinitelyGeneratedAbelianGroups"),
    ("Homology", "SimplicialComplexes", "FinitelyGeneratedAbelianGroups"),
    ("FundamentalGroup", "ClosedSurfaces", "GroupPresentations"),
]

IMPLEMENTATIONS: dict[str, str] = {
    "AlexanderPolynomial": "alexander_polynomial",
    "KnotDeterminant": "knot_determinant",
    "KnotSignature": "knot_signature",
    "JonesPolynomial": "jones_polynomial",
    "CrossingNumber": "crossing_number",
    "BurauMatrix": "burau_matrix",
    "BraidPermutation": "braid_permutation",
    "EulerCharacteristic": "euler_characteristic",
    "Homology": "homology",
    "FundamentalGroup": "fundamental_group",
}

RELATIONS: list[RelationSpec] = [
    ("SeifertMatrix", ["K3"], ["V3"]),
    ("SeifertMatrix", ["K5"], ["V5"]),
    ("SeifertMatrix", ["K7"], ["V7"]),
    ("SeifertMatrix", ["K4_1"], ["V4_1"]),
    ("SeifertMatrix", ["K5_2"], ["V5_2"]),
    ("SeifertMatrix", ["K6_1"], ["V6_1"]),
    ("AlexanderPolynomial", ["V3"], ["Phi6"]),
    ("AlexanderPolynomial", ["V5"], ["Phi10"]),
    ("AlexanderPolynomial", ["V7"], ["Phi14"]),
    ("AlexanderPolynomial", ["V4_1"], ["alexander_4_1"]),
    ("AlexanderPolynomial", ["V5_2"], ["alexander_5_2"]),
    ("AlexanderPolynomial", ["V6_1"], ["alexander_6_1"]),
    ("KnotDeterminant", ["V3"], ["three"]),
    ("KnotDeterminant", ["V5"], ["five"]),
    ("KnotDeterminant", ["V7"], ["seven"]),
    ("KnotDeterminant", ["V4_1"], [5]),
    ("KnotDeterminant", ["V5_2"], [7]),
    ("KnotDeterminant", ["V6_1"], [9]),
    ("KnotSignature", ["V3"], [-2]),
    ("KnotSignature", ["V5"], [-4]),
    ("KnotSignature", ["V7"], [-6]),
    ("KnotSignature", ["V4_1"], [0]),
    ("KnotSignature", ["V5_2"], [-2]),
    ("KnotSignature", ["V6_1"], [0]),
    ("JonesPolynomial", ["trefoil_braid"], ["jones_3_1"]),
    ("JonesPolynomial", ["cinquefoil_braid"], ["jones_5_1"]),
    ("JonesPolynomial", ["torus_braid_34"], ["jones_8_19"]),
    ("JonesPolynomial", ["figure_eight_braid"], ["jones_4_1"]),
    ("JonesPolynomial", ["hopf_braid"], ["jones_hopf"]),
    ("CrossingNumber", ["K3"], [3]),
    ("CrossingNumber", ["K4_1"], [4]),
    ("CrossingNumber", ["K5"], [5]),
    ("CrossingNumber", ["K5_2"], [5]),
    ("CrossingNumber", ["K6_3"], [6]),
    ("CrossingNumber", ["K7"], [7]),
    ("CrossingNumber", ["K8_19"], [8]),
    ("TorusKnot", [2, 3], ["K3"]),
    ("TorusKnot", [2, 5], ["K5"]),
    ("TorusKnot", [2, 7], ["K7"]),
    ("TorusKnot", [3, 4], ["K8_19"]),
    ("TwoBridgeKnot", [3], ["K3"]),
    ("TwoBridgeKnot", [5], ["K5"]),
    ("TwoBridgeKnot", [7], ["K7"]),
    ("TwoBridgeKnot", [Fraction(5, 2)], ["K4_1"]),
    ("TwoBridgeKnot", [Fraction(7, 2)], ["K5_2"]),
    ("TwoBridgeKnot", [Fraction(9, 2)], ["K6_1"]),
    ("TwoBridgeKnot", [Fraction(13, 5)], ["K6_3"]),
    ("TwoBridgeKnot", [Fraction(17, 4)], ["K8_3"]),
    ("BraidClosure", ["trefoil_braid"], ["K3"]),
    ("BraidClosure", ["cinquefoil_braid"], ["K5"]),
    ("BraidClosure", ["figure_eight_braid"], ["K4_1"]),
    ("BraidClosure", ["torus_braid_34"], ["K8_19"]),
    ("BurauMatrix", ["trefoil_braid"], ["burau_3_1"]),
    ("BurauMatrix", ["cinquefoil_braid"], ["burau_5_1"]),
    ("BurauMatrix", ["hopf_braid"], ["burau_hopf"]),
    ("BurauMatrix", ["torus_braid_34"], ["burau_8_19"]),
    ("BurauMatrix", ["figure_eight_braid"], ["burau_4_1"]),
    ("BraidPermutation", ["trefoil_braid"], ["transposition"]),
    ("BraidPermutation", ["cinquefoil_braid"], ["transposition"]),
    ("BraidPermutation", ["hopf_braid"], ["identity2"]),
    ("BraidPermutation", ["figure_eight_braid"], ["three_cycle"]),
    ("BraidPermutation", ["torus_braid_34"], ["three_cycle_inverse"]),
    ("EulerCharacteristic", ["sphere"], [2]),
    ("EulerCharacteristic", ["torus"], [0]),
    ("EulerCharacteristic", ["genus2"], [-2]),
    ("EulerCharacteristic", ["projective_plane"], [1]),
    ("EulerCharacteristic", ["klein_bottle"], [0]),
    ("EulerCharacteristic", ["triangle_boundary"], [0]),
    ("EulerCharacteristic", ["tetrahedron_boundary"], [2]),
    ("EulerCharacteristic", ["moebius_torus"], [0]),
    ("EulerCharacteristic", ["rp2_6"], [1]),
    ("EulerCharacteristic", ["solid_triangle"], [1]),
    ("EulerCharacteristic", ["two_circles"], [0]),
    ("Homology", ["sphere"], ["trivial_group"]),
    ("Homology", ["torus"], ["z2"]),
    ("Homology", ["genus2"], ["z4_free"]),
    ("Homology", ["projective_plane"], ["c2"]),
    ("Homology", ["klein_bottle"], ["z_plus_z2"]),
    ("Homology", ["triangle_boundary"], ["integers_group", "integers_group"]),
    ("Homology", ["tetrahedron_boundary"], ["integers_group", "trivial_group", "integers_group"]),
    ("Homology", ["moebius_torus"], ["integers_group", "z2", "integers_group"]),
    ("Homology", ["rp2_6"], ["integers_group", "c2", "trivial_group"]),
    ("Homology", ["solid_triangle"], ["integers_group", "trivial_group", "trivial_group"]),
    ("Homology", ["two_circles"], ["z2", "z2"]),
    ("FundamentalGroup", ["sphere"], ["trivial_group"]),
    ("FundamentalGroup", ["torus"], ["z2"]),
    ("FundamentalGroup", ["genus2"], ["genus2_group"]),
    ("FundamentalGroup", ["projective_plane"], ["projective_plane_group"]),
    ("FundamentalGroup", ["klein_bottle"], ["klein_bottle_group"]),
]

DISPLAYS: dict[str, tuple[str | None, bool]] = {
    "SeifertMatrix": (r"\op{V(}{in0}\op{)} = {out0}", False),
    "AlexanderPolynomial": (r"\op{\Delta(}{in0}\op{)} = {out0}", False),
    "KnotDeterminant": (r"\op{\det{}_{K}(}{in0}\op{)} = {out0}", False),
    "KnotSignature": (r"\op{\sigma(}{in0}\op{)} = {out0}", False),
    "JonesPolynomial": (r"\op{V_{}}{in0}\op{(t)} = {out0}", False),
    "TorusKnot": (r"\op{T(}{in0}, {in1}\op{)} = {out0}", False),
    "TwoBridgeKnot": (r"\op{K(}{in0}\op{)} = {out0}", False),
    "BraidClosure": (r"\op{\widehat{}}{in0} = {out0}", False),
    "EulerCharacteristic": (r"\op{\chi(}{in0}\op{)} = {out0}", False),
    "FundamentalGroup": (r"\op{\pi_{1}(}{in0}\op{)} = {out0}", False),
}

_WIKI = "https://en.wikipedia.org/wiki/"


def _knotinfo(name: str) -> list[Reference]:
    return [
        (
            "KnotInfo",
            f"https://knotinfo.math.indiana.edu/results.php?searchmode=singleknot&desktopmode=0&singleknot={name}",
        )
    ]


REFERENCES: dict[str, list[Reference]] = {
    "K3": [
        *knot_atlas("3_1"),
        ("Wikipedia", _WIKI + "Trefoil_knot"),
    ],
    "K5": [
        *knot_atlas("5_1"),
        ("Wikipedia", _WIKI + "Cinquefoil_knot"),
    ],
    "K7": [
        *knot_atlas("7_1"),
        ("Wikipedia", _WIKI + "7_1_knot"),
    ],
    "K4_1": [
        *knot_atlas("4_1"),
        ("Wikipedia", _WIKI + "Figure-eight_knot_(mathematics)"),
    ],
    "K5_2": knot_atlas("5_2"),
    "K6_1": knot_atlas("6_1"),
    "K6_3": knot_atlas("6_3"),
    "K8_3": knot_atlas("8_3"),
    "K8_19": knot_atlas("8_19"),
    "jones_3_1": _knotinfo("3_1"),
    "jones_5_1": _knotinfo("5_1"),
    "jones_4_1": _knotinfo("4_1"),
    "jones_8_19": _knotinfo("8_19"),
    "jones_hopf": [("Wikipedia", _WIKI + "Hopf_link")],
    "V4_1": _knotinfo("4_1"),
    "V5_2": _knotinfo("5_2"),
    "V6_1": _knotinfo("6_1"),
    "rp2_6": [("Wikipedia", _WIKI + "Hemi-icosahedron")],
    "SeifertMatrix": [("Wikipedia", _WIKI + "Seifert_surface")],
    "AlexanderPolynomial": [("Wikipedia", _WIKI + "Alexander_polynomial")],
    "KnotSignature": [("Wikipedia", _WIKI + "Signature_(topology)")],
    "JonesPolynomial": [("Wikipedia", _WIKI + "Jones_polynomial")],
    "TwoBridgeKnot": [("Wikipedia", _WIKI + "2-bridge_knot")],
    "TorusKnot": [("Wikipedia", _WIKI + "Torus_knot")],
    "BurauMatrix": [("Wikipedia", _WIKI + "Burau_representation")],
    "Homology": [("Wikipedia", _WIKI + "Simplicial_homology")],
    "FundamentalGroup": [("Wikipedia", _WIKI + "Fundamental_polygon")],
}

FILINGS: dict[str, list[str]] = {
    "KnotTheory": ["KnotOperations", "SurfaceOperations"],
    "KnotOperations": [
        "SeifertMatrix",
        "AlexanderPolynomial",
        "KnotDeterminant",
        "KnotSignature",
        "JonesPolynomial",
        "CrossingNumber",
        "TorusKnot",
        "TwoBridgeKnot",
        "BraidClosure",
        "BurauMatrix",
        "BraidPermutation",
    ],
    "SurfaceOperations": ["EulerCharacteristic", "Homology", "FundamentalGroup"],
}

IMAGES: dict[str, str] = {
    "K3": "/knots/2-3.svg",
    "K5": "/knots/2-5.svg",
    "K7": "/knots/2-7.svg",
}
