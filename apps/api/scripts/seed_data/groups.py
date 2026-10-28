from seed_data.build import (
    Data,
    Instance,
    Reference,
    RelationSpec,
    Specimen,
    abelian,
    permgroup,
    presentation,
    small_group,
)


def _cyclic_presentation(order: int) -> Data:
    return presentation(["x"], [[("x", order)]])


def _surface_relator(genus: int) -> list[tuple[str, int]]:
    return [
        letter
        for i in range(1, genus + 1)
        for letter in ((f"a_{i}", 1), (f"b_{i}", 1), (f"a_{i}", -1), (f"b_{i}", -1))
    ]


INSTANCES: dict[str, Instance] = {
    "quaternion": (
        "Q_{8}",
        "The quaternion group.",
        [
            (
                "GroupPresentations",
                presentation(
                    ["a", "b"],
                    [[("a", 4)], [("a", 2), ("b", -2)], [("b", -1), ("a", 1), ("b", 1), ("a", 1)]],
                ),
            ),
            ("FiniteGroups", small_group(8, 4)),
        ],
    ),
    "a4": (
        "A_{4}",
        "The alternating group on four letters: the rotations of a tetrahedron.",
        [
            ("PermutationGroups", permgroup(4, [[1, 2, 0, 3], [0, 2, 3, 1]])),
            ("FiniteGroups", small_group(12, 3)),
        ],
    ),
    "s4": (
        "S_{4}",
        "The symmetric group on four letters: the rotations of a cube.",
        [
            ("PermutationGroups", permgroup(4, [[1, 2, 3, 0], [1, 0, 2, 3]])),
            ("FiniteGroups", small_group(24, 12)),
        ],
    ),
    "a5": (
        "A_{5}",
        "The smallest nonabelian simple group: the rotations of an icosahedron.",
        [
            ("PermutationGroups", permgroup(5, [[1, 2, 0, 3, 4], [1, 2, 3, 4, 0]])),
            ("SimpleGroups", small_group(60, 5)),
        ],
    ),
    "s5": (
        "S_{5}",
        "The symmetric group on five letters: the automorphisms of the Petersen graph.",
        [
            ("PermutationGroups", permgroup(5, [[1, 2, 3, 4, 0], [1, 0, 2, 3, 4]])),
            ("FiniteGroups", small_group(120, 34)),
        ],
    ),
    "psl27": (
        r"\mathrm{PSL}(2, 7)",
        "The simple group of order 168, the symmetries of the Fano plane, here permuting its "
        r"seven points, whose lines are $\{i, i + 1, i + 3\}$ modulo $7$.",
        [
            (
                "PermutationGroups",
                permgroup(
                    7,
                    [
                        [0, 1, 4, 3, 2, 6, 5],
                        [0, 1, 5, 3, 6, 2, 4],
                        [0, 2, 1, 6, 4, 5, 3],
                        [1, 0, 2, 3, 6, 5, 4],
                    ],
                ),
            ),
            ("SimpleGroups", small_group(168, 42)),
        ],
    ),
    "c7": (
        r"\mathbb{Z}/7\mathbb{Z}",
        "Cyclic of prime order, hence simple.",
        [("SimpleGroups", small_group(7, 1)), ("CyclicGroups", abelian(0, [7]))],
    ),
    "s3": (
        "S_{3}",
        r"The symmetric group on three letters, which is also $D_{3}$, the symmetries of a "
        "triangle.",
        [
            ("PermutationGroups", permgroup(3, [[1, 2, 0], [1, 0, 2]])),
            (
                "GroupPresentations",
                presentation(
                    ["x_0", "x_1"],
                    [
                        [("x_1", 2)],
                        [("x_0", 3)],
                        [("x_1", 1), ("x_0", 1), ("x_1", -1), ("x_0", 1)],
                    ],
                ),
            ),
            ("DihedralGroups", small_group(6, 1)),
        ],
    ),
    "d4": (
        "D_{4}",
        "The symmetries of a square, of order 8.",
        [
            ("PermutationGroups", permgroup(4, [[0, 3, 2, 1], [1, 0, 3, 2]])),
            ("DihedralGroups", small_group(8, 3)),
        ],
    ),
    "d5": (
        "D_{5}",
        "The symmetries of a pentagon, of order 10.",
        [
            ("PermutationGroups", permgroup(5, [[0, 4, 3, 2, 1], [1, 0, 4, 3, 2]])),
            ("DihedralGroups", small_group(10, 1)),
        ],
    ),
    "d6": (
        "D_{6}",
        "The symmetries of a hexagon, of order 12.",
        [("DihedralGroups", small_group(12, 4))],
    ),
    "klein_four": (
        "V_{4}",
        r"The Klein four-group, which is also $D_{2}$, the symmetries of a rectangle.",
        [
            ("PermutationGroups", permgroup(4, [[1, 0, 3, 2], [2, 3, 0, 1]])),
            (
                "GroupPresentations",
                presentation(
                    ["x_0", "x_1"],
                    [
                        [("x_0", 2)],
                        [("x_1", 2)],
                        [("x_1", 1), ("x_0", 1), ("x_1", -1), ("x_0", -1)],
                    ],
                ),
            ),
            ("FinitelyGeneratedAbelianGroups", abelian(0, [2, 2])),
            ("DihedralGroups", small_group(4, 2)),
        ],
    ),
    "trefoil_group": (
        r"\left\langle x, y \mid x^{2} y^{-3} \right\rangle",
        "The fundamental group of the trefoil's complement, also the braid group on three strands.",
        [("GroupPresentations", presentation(["x", "y"], [[("x", 2), ("y", -3)]]))],
    ),
    "z2": (
        r"\mathbb{Z}^{2}",
        "The free abelian group of rank two: the fundamental group of the torus.",
        [
            ("GroupPresentations", presentation(["a_1", "b_1"], [_surface_relator(1)])),
            ("FinitelyGeneratedAbelianGroups", abelian(2, [])),
        ],
    ),
    "z4_free": (
        r"\mathbb{Z}^{4}",
        "The free abelian group of rank four.",
        [("FinitelyGeneratedAbelianGroups", abelian(4, []))],
    ),
    "genus2_group": (
        r"\left\langle a_{1}, b_{1}, a_{2}, b_{2} \mid [a_{1}, b_{1}] [a_{2}, b_{2}] \right\rangle",
        "The fundamental group of the closed orientable surface of genus two.",
        [
            (
                "GroupPresentations",
                presentation(["a_1", "b_1", "a_2", "b_2"], [_surface_relator(2)]),
            )
        ],
    ),
    "klein_bottle_group": (
        r"\left\langle a_{1}, a_{2} \mid a_{1}^{2} a_{2}^{2} \right\rangle",
        "The fundamental group of the Klein bottle.",
        [("GroupPresentations", presentation(["a_1", "a_2"], [[("a_1", 2), ("a_2", 2)]]))],
    ),
    "projective_plane_group": (
        r"\left\langle a_{1} \mid a_{1}^{2} \right\rangle",
        "The fundamental group of the real projective plane.",
        [("GroupPresentations", presentation(["a_1"], [[("a_1", 2)]]))],
    ),
    "z_plus_z2": (
        r"\mathbb{Z} \oplus \mathbb{Z}/2\mathbb{Z}",
        None,
        [("FinitelyGeneratedAbelianGroups", abelian(1, [2]))],
    ),
    "z2_plus_z4": (
        r"\mathbb{Z}/2\mathbb{Z} \oplus \mathbb{Z}/4\mathbb{Z}",
        None,
        [
            ("FiniteGroups", small_group(8, 2)),
            ("FinitelyGeneratedAbelianGroups", abelian(0, [2, 4])),
        ],
    ),
    "integers_group": (
        r"\mathbb{Z}",
        "The integers under addition: the infinite cyclic group.",
        [("CyclicGroups", abelian(1, []))],
    ),
    "c6": (
        r"\mathbb{Z}/6\mathbb{Z}",
        None,
        [("FiniteGroups", small_group(6, 2)), ("CyclicGroups", abelian(0, [6]))],
    ),
    "trivial_group": (
        r"\left\{ e \right\}",
        "The trivial group: the fundamental group of the sphere.",
        [
            ("PermutationGroups", permgroup(1, [[0]])),
            ("GroupPresentations", presentation([], [])),
            ("CyclicGroups", abelian(0, [])),
            ("FiniteGroups", small_group(1, 1)),
        ],
    ),
    "c2": (
        r"\mathbb{Z}/2\mathbb{Z}",
        "The cyclic group of order two, which is also the symmetric group on two letters.",
        [
            ("PermutationGroups", permgroup(2, [[1, 0]])),
            ("GroupPresentations", _cyclic_presentation(2)),
            ("CyclicGroups", abelian(0, [2])),
            ("SimpleGroups", small_group(2, 1)),
        ],
    ),
    "c3": (
        r"\mathbb{Z}/3\mathbb{Z}",
        "The cyclic group of order three, which is also the alternating group on three letters.",
        [
            ("PermutationGroups", permgroup(3, [[1, 2, 0]])),
            ("GroupPresentations", _cyclic_presentation(3)),
            ("CyclicGroups", abelian(0, [3])),
            ("SimpleGroups", small_group(3, 1)),
        ],
    ),
    "c4": (
        r"\mathbb{Z}/4\mathbb{Z}",
        None,
        [
            ("PermutationGroups", permgroup(4, [[1, 2, 3, 0]])),
            ("GroupPresentations", _cyclic_presentation(4)),
            ("CyclicGroups", abelian(0, [4])),
            ("FiniteGroups", small_group(4, 1)),
        ],
    ),
    "trivial3": (
        r"\left\{ e \right\} \leq S_{3}",
        "The trivial group, acting on three points.",
        [("PermutationGroups", permgroup(3, [[0, 1, 2]]))],
    ),
    "trivial4": (
        r"\left\{ e \right\} \leq S_{4}",
        "The trivial group, acting on four points.",
        [("PermutationGroups", permgroup(4, [[0, 1, 2, 3]]))],
    ),
    "centre_d4": (
        r"\left\langle \left( 0\; 2\right)\left( 1\; 3\right) \right\rangle",
        "The half turn of a square, labelled around: the centre of the dihedral group of order 8.",
        [("PermutationGroups", permgroup(4, [[2, 3, 0, 1]]))],
    ),
}

SECTIONS: dict[str, Specimen] = {
    "GroupOperations": (
        r"\text{Group Operations}",
        "Operations taking a group as input, and the constructions that produce one.",
    ),
}

OPERATORS: dict[str, Specimen] = {
    "GroupOrder": (r"\text{Group Order}", "The number of elements of a finite group."),
    "Centre": (
        r"\text{Centre}",
        "The elements commuting with every element, as a permutation group with canonical "
        "generators.",
    ),
    "CompositionFactors": (
        r"\text{Composition Factors}",
        "The simple quotients along a composition series, from the top down, one output "
        "each. By Jordan–Hölder they do not depend on the series.",
    ),
    "Abelianisation": (
        r"\text{Abelianisation}",
        r"The largest abelian quotient $G / [G, G]$: the Smith normal form of the relators' "
        "exponent sums.",
    ),
    "Presentation": (
        r"\text{Presentation}",
        "Generators and relators for a permutation group, as sympy derives them.",
    ),
    "SmallGroupID": (
        r"\text{SmallGroup ID}",
        "The group's identifier in GAP's library of small groups: its order and an index. "
        "Asserted from GAP's IdGroup, which the sandbox does not have.",
    ),
    "CyclicGroup": (r"\text{Cyclic Group}", r"$\mathbb{Z}/n\mathbb{Z}$."),
    "DihedralGroup": (
        r"\text{Dihedral Group}",
        r"$D_{n}$, the symmetries of a regular $n$-gon, of order $2n$. Asserted: its "
        "SmallGroup index comes from a table.",
    ),
    "SymmetricGroup": (
        r"\text{Symmetric Group}",
        r"$S_{n}$, all permutations of $n$ points, generated by an $n$-cycle and a "
        "transposition.",
    ),
}

SIGNATURES: list[tuple[str, str, str]] = [
    ("GroupOrder", "PermutationGroups", "PositiveIntegers"),
    ("GroupOrder", "GroupPresentations", "PositiveIntegers"),
    ("GroupOrder", "FiniteGroups", "PositiveIntegers"),
    ("Centre", "PermutationGroups", "PermutationGroups"),
    ("CompositionFactors", "PermutationGroups", "SimpleGroups"),
    ("Abelianisation", "GroupPresentations", "FinitelyGeneratedAbelianGroups"),
    ("Abelianisation", "PermutationGroups", "FinitelyGeneratedAbelianGroups"),
    ("Presentation", "PermutationGroups", "GroupPresentations"),
    ("SmallGroupID", "PermutationGroups", "FiniteGroups"),
    ("SmallGroupID", "GroupPresentations", "FiniteGroups"),
    ("CyclicGroup", "PositiveIntegers", "CyclicGroups"),
    ("DihedralGroup", "PositiveIntegers", "DihedralGroups"),
    ("SymmetricGroup", "PositiveIntegers", "PermutationGroups"),
]

IMPLEMENTATIONS: dict[str, str] = {
    "GroupOrder": "group_order",
    "Centre": "centre",
    "CompositionFactors": "composition_factors",
    "Abelianisation": "abelianisation",
    "Presentation": "presentation",
    "CyclicGroup": "cyclic_group",
    "SymmetricGroup": "symmetric_group",
}

RELATIONS: list[RelationSpec] = [
    ("GroupOrder", ["s4"], [24]),
    ("GroupOrder", ["a5"], [60]),
    ("GroupOrder", ["psl27"], [168]),
    ("GroupOrder", ["k33_automorphisms"], [72]),
    ("GroupOrder", ["claw_automorphisms"], [6]),
    ("GroupOrder", ["quaternion"], [8]),
    ("GroupOrder", ["c7"], [7]),
    ("GroupOrder", ["c6"], [6]),
    ("GroupOrder", ["z2_plus_z4"], [8]),
    ("Centre", ["s4"], ["trivial4"]),
    ("Centre", ["a4"], ["trivial4"]),
    ("Centre", ["s3"], ["trivial3"]),
    ("Centre", ["d4"], ["centre_d4"]),
    ("Centre", ["klein_four"], ["klein_four"]),
    ("Centre", ["c3"], ["c3"]),
    ("CompositionFactors", ["s4"], ["c2", "c3", "c2", "c2"]),
    ("CompositionFactors", ["a4"], ["c3", "c2", "c2"]),
    ("CompositionFactors", ["s3"], ["c2", "c3"]),
    ("CompositionFactors", ["d4"], ["c2", "c2", "c2"]),
    ("CompositionFactors", ["c4"], ["c2", "c2"]),
    ("CompositionFactors", ["a5"], ["a5"]),
    ("CompositionFactors", ["psl27"], ["psl27"]),
    ("Abelianisation", ["s3"], ["c2"]),
    ("Abelianisation", ["s4"], ["c2"]),
    ("Abelianisation", ["a4"], ["c3"]),
    ("Abelianisation", ["a5"], ["trivial_group"]),
    ("Abelianisation", ["d4"], ["klein_four"]),
    ("Abelianisation", ["trefoil_group"], ["integers_group"]),
    ("Abelianisation", ["z2"], ["z2"]),
    ("Abelianisation", ["quaternion"], ["klein_four"]),
    ("Abelianisation", ["klein_bottle_group"], ["z_plus_z2"]),
    ("Abelianisation", ["genus2_group"], ["z4_free"]),
    ("Abelianisation", ["projective_plane_group"], ["c2"]),
    ("Presentation", ["c2"], ["c2"]),
    ("Presentation", ["c3"], ["c3"]),
    ("Presentation", ["c4"], ["c4"]),
    ("Presentation", ["centre_d4"], ["c2"]),
    ("Presentation", ["klein_four"], ["klein_four"]),
    ("Presentation", ["s3"], ["s3"]),
    ("SmallGroupID", ["centre_d4"], ["c2"]),
    ("SmallGroupID", ["trivial3"], ["trivial_group"]),
    ("SmallGroupID", ["trivial4"], ["trivial_group"]),
    ("SmallGroupID", ["claw_automorphisms"], ["s3"]),
    ("SmallGroupID", ["path_reversal_group"], ["c2"]),
    ("SmallGroupID", ["projective_plane_group"], ["c2"]),
    ("CyclicGroup", [1], ["trivial_group"]),
    ("CyclicGroup", [2], ["c2"]),
    ("CyclicGroup", [3], ["c3"]),
    ("CyclicGroup", [4], ["c4"]),
    ("CyclicGroup", [6], ["c6"]),
    ("CyclicGroup", [7], ["c7"]),
    ("DihedralGroup", [2], ["klein_four"]),
    ("DihedralGroup", [3], ["s3"]),
    ("DihedralGroup", [4], ["d4"]),
    ("DihedralGroup", [5], ["d5"]),
    ("DihedralGroup", [6], ["d6"]),
    ("SymmetricGroup", [1], ["trivial_group"]),
    ("SymmetricGroup", [2], ["c2"]),
    ("SymmetricGroup", [3], ["s3"]),
    ("SymmetricGroup", [4], ["s4"]),
    ("SymmetricGroup", [5], ["s5"]),
]

DISPLAYS: dict[str, tuple[str | None, bool]] = {
    "GroupOrder": (r"\op{\lvert}{in0}\op{\rvert} = {out0}", False),
    "Centre": (r"\op{Z(}{in0}\op{)} = {out0}", False),
    "Abelianisation": (r"{in0}\op{^{\mathrm{ab}}} = {out0}", False),
    "CyclicGroup": (r"\op{C}_{{in0}} = {out0}", False),
    "DihedralGroup": (r"\op{D}_{{in0}} = {out0}", False),
    "SymmetricGroup": (r"\op{S}_{{in0}} = {out0}", False),
}

_WIKI = "https://en.wikipedia.org/wiki/"


def _groupnames(label: str, page: str) -> list[Reference]:
    return [(f"GroupNames {label}", f"https://people.maths.bris.ac.uk/~matyd/GroupNames/{page}")]


REFERENCES: dict[str, list[Reference]] = {
    "d6": _groupnames("D6", "1/D6.html"),
    "s5": _groupnames("S5", "61/S5.html"),
    "psl27": [("Wikipedia", _WIKI + "PSL(2,7)")],
    "CompositionFactors": [("Wikipedia", _WIKI + "Composition_series")],
    "Abelianisation": [("Wikipedia", _WIKI + "Commutator_subgroup#Abelianization")],
    "SmallGroupID": [("GAP SmallGrp", "https://docs.gap-system.org/pkg/smallgrp/doc/chap1.html")],
    "DihedralGroup": [("Wikipedia", _WIKI + "Dihedral_group")],
}

FILINGS: dict[str, list[str]] = {
    "GroupTheory": ["GroupOperations"],
    "GroupOperations": list(OPERATORS),
}
