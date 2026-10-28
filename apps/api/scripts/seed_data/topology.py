from seed_data.build import (
    Instance,
    Reference,
    RelationSpec,
    Specimen,
    instance,
    knot,
    knot_atlas,
    simplicial,
    surface,
)

TORUS_KNOT_TYPES = ["TorusKnots", "AlternatingKnots", "TwoBridgeKnots"]

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
}

SECTIONS: dict[str, Specimen] = {
    "KnotOperations": (
        r"\text{Knot Operations}",
        "Operations taking a knot or its Seifert matrix as input: Seifert matrices, "
        "Alexander polynomials.",
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
}

SIGNATURES: list[tuple[str, str, str]] = [
    ("SeifertMatrix", "Knots", "Matrices"),
    ("AlexanderPolynomial", "Matrices", "Polynomials"),
    ("KnotDeterminant", "Matrices", "Integers"),
]

IMPLEMENTATIONS: dict[str, str] = {
    "AlexanderPolynomial": "alexander_polynomial",
    "KnotDeterminant": "knot_determinant",
}

RELATIONS: list[RelationSpec] = [
    ("SeifertMatrix", ["K3"], ["V3"]),
    ("SeifertMatrix", ["K5"], ["V5"]),
    ("SeifertMatrix", ["K7"], ["V7"]),
    ("AlexanderPolynomial", ["V3"], ["Phi6"]),
    ("AlexanderPolynomial", ["V5"], ["Phi10"]),
    ("AlexanderPolynomial", ["V7"], ["Phi14"]),
    ("KnotDeterminant", ["V3"], ["three"]),
    ("KnotDeterminant", ["V5"], ["five"]),
    ("KnotDeterminant", ["V7"], ["seven"]),
]

DISPLAYS: dict[str, tuple[str | None, bool]] = {
    "SeifertMatrix": (r"\op{V(}{in0}\op{)} = {out0}", False),
    "AlexanderPolynomial": (r"\op{\Delta(}{in0}\op{)} = {out0}", False),
    "KnotDeterminant": (r"\op{\det{}_{K}(}{in0}\op{)} = {out0}", False),
}

REFERENCES: dict[str, list[Reference]] = {
    "K3": [
        *knot_atlas("3_1"),
        ("Wikipedia", "https://en.wikipedia.org/wiki/Trefoil_knot"),
    ],
    "K5": [
        *knot_atlas("5_1"),
        ("Wikipedia", "https://en.wikipedia.org/wiki/Cinquefoil_knot"),
    ],
    "K7": [
        *knot_atlas("7_1"),
        ("Wikipedia", "https://en.wikipedia.org/wiki/7_1_knot"),
    ],
    "K4_1": [
        *knot_atlas("4_1"),
        ("Wikipedia", "https://en.wikipedia.org/wiki/Figure-eight_knot_(mathematics)"),
    ],
    "K5_2": knot_atlas("5_2"),
    "K6_1": knot_atlas("6_1"),
    "K6_3": knot_atlas("6_3"),
    "K8_3": knot_atlas("8_3"),
    "K8_19": knot_atlas("8_19"),
    "SeifertMatrix": [("Wikipedia", "https://en.wikipedia.org/wiki/Seifert_surface")],
    "AlexanderPolynomial": [("Wikipedia", "https://en.wikipedia.org/wiki/Alexander_polynomial")],
}

FILINGS: dict[str, list[str]] = {
    "KnotTheory": ["KnotOperations"],
    "KnotOperations": ["SeifertMatrix", "AlexanderPolynomial", "KnotDeterminant"],
}

IMAGES: dict[str, str] = {
    "K3": "/knots/2-3.svg",
    "K5": "/knots/2-5.svg",
    "K7": "/knots/2-7.svg",
}
