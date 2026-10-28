from seed_data.build import Instance, abelian, permgroup, presentation, small_group

INSTANCES: dict[str, Instance] = {
    "quaternion": ("Q_{8}", "The quaternion group.", [("FiniteGroups", small_group(8, 4))]),
    "a4": (
        "A_{4}",
        "The alternating group on four letters.",
        [("FiniteGroups", small_group(12, 3))],
    ),
    "s4": (
        "S_{4}",
        "The symmetric group on four letters: the rotations of a cube.",
        [
            ("FiniteGroups", small_group(24, 12)),
            ("PermutationGroups", permgroup(4, [[1, 2, 3, 0], [1, 0, 2, 3]])),
        ],
    ),
    "a5": (
        "A_{5}",
        "The smallest nonabelian simple group: the rotations of an icosahedron.",
        [
            ("SimpleGroups", small_group(60, 5)),
            ("PermutationGroups", permgroup(5, [[1, 2, 3, 4, 0], [1, 2, 0, 3, 4]])),
        ],
    ),
    "psl27": (
        r"\mathrm{PSL}(2, 7)",
        "The simple group of order 168, the symmetries of the Fano plane.",
        [("SimpleGroups", small_group(168, 42))],
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
            ("DihedralGroups", small_group(6, 1)),
            (
                "GroupPresentations",
                presentation(
                    ["a", "b"],
                    [[("a", 2)], [("b", 2)], [("a", 1), ("b", 1)] * 3],
                ),
            ),
        ],
    ),
    "d4": (
        "D_{4}",
        "The symmetries of a square, of order 8.",
        [("DihedralGroups", small_group(8, 3))],
    ),
    "d5": (
        "D_{5}",
        "The symmetries of a pentagon, of order 10.",
        [("DihedralGroups", small_group(10, 1))],
    ),
    "klein_four": (
        "V_{4}",
        "The Klein four-group.",
        [
            ("FiniteGroups", small_group(4, 2)),
            ("FinitelyGeneratedAbelianGroups", abelian(0, [2, 2])),
            ("PermutationGroups", permgroup(4, [[1, 0, 3, 2], [2, 3, 0, 1]])),
        ],
    ),
    "trefoil_group": (
        r"\left\langle x, y \mid x^{2} y^{-3} \right\rangle",
        "The fundamental group of the trefoil's complement, also the braid group on three strands.",
        [("GroupPresentations", presentation(["x", "y"], [[("x", 2), ("y", -3)]]))],
    ),
    "z2": (
        r"\mathbb{Z}^{2}",
        "The free abelian group of rank two.",
        [
            ("FinitelyGeneratedAbelianGroups", abelian(2, [])),
            (
                "GroupPresentations",
                presentation(["a", "b"], [[("a", 1), ("b", 1), ("a", -1), ("b", -1)]]),
            ),
        ],
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
}
