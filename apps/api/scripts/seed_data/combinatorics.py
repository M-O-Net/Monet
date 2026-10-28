from seed_data.build import (
    Instance,
    Reference,
    RelationSpec,
    Specimen,
    instance,
    integer,
    matrix_instance,
)


def _permutation(latex: str, images: list[int], even: bool) -> Instance:
    return instance(latex, {"perm": images}, ["EvenPermutations" if even else "Permutations"])


def _partition(parts: list[int], distinct: bool = False) -> Instance:
    latex = rf"\left({', '.join(map(str, parts))}\right) \vdash {sum(parts)}"
    return instance(
        latex, {"partition": parts}, ["DistinctPartitions" if distinct else "IntegerPartitions"]
    )


def _tableau(rows: list[list[int]]) -> Instance:
    body = r" \\ ".join(" & ".join(map(str, row)) for row in rows)
    latex = rf"\begin{{array}}{{{'l' * len(rows[0])}}}{body}\end{{array}}"
    return instance(latex, {"tableau": rows}, ["StandardYoungTableaux"])


def _images(values: list[int]) -> Instance:
    latex = r"\left( " + r", \  ".join(map(str, values)) + r"\right)"
    return instance(latex, {"tuple": [integer(v) for v in values]}, ["FiniteSequences"])


INSTANCES: dict[str, Instance] = {
    "transposition": instance(r"\left( 0\; 1\right)", {"perm": [1, 0]}, ["Permutations"]),
    "swap_last": instance(r"\left( 1\; 2\right)", {"perm": [0, 2, 1]}, ["Permutations"]),
    "four_cycle": instance(
        r"\left( 0\; 1\; 2\; 3\right)", {"perm": [1, 2, 3, 0]}, ["Permutations"]
    ),
    "three_cycle": instance(r"\left( 0\; 1\; 2\right)", {"perm": [1, 2, 0]}, ["EvenPermutations"]),
    "three_cycle_inverse": instance(
        r"\left( 0\; 2\; 1\right)", {"perm": [2, 0, 1]}, ["EvenPermutations"]
    ),
    "double_transposition": instance(
        r"\left( 0\; 1\right)\left( 2\; 3\right)",
        {"perm": [1, 0, 3, 2]},
        ["EvenPermutations"],
    ),
    "identity2": _permutation(r"\left( 0\right)\left( 1\right)", [0, 1], True),
    "identity3": _permutation(r"\left( 0\right)\left( 1\right)\left( 2\right)", [0, 1, 2], True),
    "transposition_in_s3": _permutation(r"\left( 0\; 1\right)\left( 2\right)", [1, 0, 2], False),
    "reversal3": _permutation(r"\left( 0\; 2\right)\left( 1\right)", [2, 1, 0], False),
    "transposition_in_s4": _permutation(
        r"\left( 0\; 1\right)\left( 2\right)\left( 3\right)", [1, 0, 2, 3], False
    ),
    "three_cycle_in_s4": _permutation(
        r"\left( 0\; 1\; 2\right)\left( 3\right)", [1, 2, 0, 3], True
    ),
    "three_cycle_023": _permutation(r"\left( 0\; 2\; 3\right)\left( 1\right)", [2, 1, 3, 0], True),
    "double_transposition_0213": _permutation(
        r"\left( 0\; 2\right)\left( 1\; 3\right)", [2, 3, 0, 1], True
    ),
    "five_cycle": _permutation(r"\left( 0\; 1\; 2\; 3\; 4\right)", [1, 2, 3, 4, 0], True),
    "three_cycle_in_s5": _permutation(
        r"\left( 0\; 1\; 2\right)\left( 3\right)\left( 4\right)", [1, 2, 0, 3, 4], True
    ),
    "three_two_cycle": _permutation(
        r"\left( 0\; 1\; 2\right)\left( 3\; 4\right)", [1, 2, 0, 4, 3], False
    ),
    "partition_22": instance(
        r"\left(2, 2\right) \vdash 4", {"partition": [2, 2]}, ["IntegerPartitions"]
    ),
    "partition_311": instance(
        r"\left(3, 1, 1\right) \vdash 5", {"partition": [3, 1, 1]}, ["IntegerPartitions"]
    ),
    "partition_2211": instance(
        r"\left(2, 2, 1, 1\right) \vdash 6", {"partition": [2, 2, 1, 1]}, ["IntegerPartitions"]
    ),
    "partition_321": instance(
        r"\left(3, 2, 1\right) \vdash 6",
        {"partition": [3, 2, 1]},
        ["DistinctPartitions"],
        "The staircase partition.",
    ),
    "partition_41": instance(
        r"\left(4, 1\right) \vdash 5", {"partition": [4, 1]}, ["DistinctPartitions"]
    ),
    "partition_5": instance(r"\left(5\right) \vdash 5", {"partition": [5]}, ["DistinctPartitions"]),
    "partition_2": _partition([2], distinct=True),
    "partition_21": _partition([2, 1], distinct=True),
    "partition_3": _partition([3], distinct=True),
    "partition_111": _partition([1, 1, 1]),
    "partition_211": _partition([2, 1, 1]),
    "partition_4": _partition([4], distinct=True),
    "partition_32": _partition([3, 2], distinct=True),
    "partition_221": _partition([2, 2, 1]),
    "partition_2111": _partition([2, 1, 1, 1]),
    "partition_11111": _partition([1, 1, 1, 1, 1]),
    "partition_42": _partition([4, 2], distinct=True),
    "tableau_32": instance(
        r"\begin{array}{lll}1 & 2 & 3 \\ 4 & 5\end{array}",
        {"tableau": [[1, 2, 3], [4, 5]]},
        ["StandardYoungTableaux"],
    ),
    "tableau_32_columns": instance(
        r"\begin{array}{lll}1 & 3 & 5 \\ 2 & 4\end{array}",
        {"tableau": [[1, 3, 5], [2, 4]]},
        ["StandardYoungTableaux"],
    ),
    "tableau_211": instance(
        r"\begin{array}{ll}1 & 2 \\ 3 \\ 4\end{array}",
        {"tableau": [[1, 2], [3], [4]]},
        ["StandardYoungTableaux"],
    ),
    "tableau_row3": _tableau([[1, 2, 3]]),
    "tableau_column3": _tableau([[1], [2], [3]]),
    "tableau_13_2": _tableau([[1, 3], [2]]),
    "tableau_12_3": _tableau([[1, 2], [3]]),
    "tableau_13_24": _tableau([[1, 3], [2, 4]]),
    "tableau_134_2": _tableau([[1, 3, 4], [2]]),
    "tableau_123_4": _tableau([[1, 2, 3], [4]]),
    "tableau_134_25": _tableau([[1, 3, 4], [2, 5]]),
    "tableau_124_35": _tableau([[1, 2, 4], [3, 5]]),
    "images_120": _images([1, 2, 0]),
    "images_201": _images([2, 0, 1]),
    "images_10": _images([1, 0]),
    "images_012": _images([0, 1, 2]),
    "images_1032": _images([1, 0, 3, 2]),
    "double_swap4": matrix_instance(
        [[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]],
        ["PermutationMatrices", "SymmetricMatrices", "SpecialLinearIntegerMatrices"],
    ),
}

SECTIONS: dict[str, Specimen] = {
    "CombinatoricsOperations": (
        r"\text{Combinatorics Operations}",
        "Operations taking permutations, partitions or tableaux as input.",
    ),
}

OPERATORS: dict[str, Specimen] = {
    "Sign": (
        r"\text{Sign}",
        r"For a permutation, $+1$ if it is a product of an even number of transpositions and "
        r"$-1$ otherwise. It is also the determinant of its permutation matrix.",
    ),
    "CycleType": (
        r"\text{Cycle Type}",
        "The lengths of a permutation's cycles, fixed points included, as a partition of its "
        "size. Two permutations are conjugate exactly when their cycle types agree.",
    ),
    "ComposePermutations": (
        r"\text{Compose}",
        r"The permutation that applies $p$ first and then $q$: $i \mapsto q(p(i))$.",
    ),
    "RSKCorrespondence": (
        r"\text{RSK Correspondence}",
        r"Robinson-Schensted: a permutation of $n$ becomes a pair of standard Young tableaux "
        r"of the same shape, by row-inserting $p(0) + 1, \dots, p(n - 1) + 1$. The first row "
        "is as long as the longest increasing subsequence.",
    ),
    "TableauShape": (
        r"\text{Shape}",
        "The row lengths of a standard Young tableau, as an integer partition.",
    ),
    "ConjugatePartition": (
        r"\text{Conjugate Partition}",
        "The partition whose Young diagram is the transpose of the given one.",
    ),
    "StandardTableauxCount": (
        r"\text{Number of Standard Young Tableaux}",
        r"By the hook length formula, $n!$ over the product of the hook lengths. It is the "
        r"dimension of the irreducible representation of $S_{n}$ for that shape.",
    ),
    "GlaisherBijection": (
        r"\text{Glaisher Bijection}",
        "Merge equal parts in pairs until all parts differ. On partitions into odd parts it "
        "is Glaisher's bijection onto partitions into distinct parts, proving Euler's theorem "
        "that the two are equinumerous.",
    ),
    "PermutationMatrix": (
        r"\text{Permutation Matrix}",
        r"The matrix sending the basis vector $e_{j}$ to $e_{p(j)}$.",
    ),
    "GeneratedGroup": (
        r"\text{Generated Group}",
        "The permutation group the inputs generate, given by canonical generators: sympy's "
        "for a full symmetric or alternating group, and otherwise each element, in "
        "lexicographic order of its images, that the earlier ones do not yet generate.",
    ),
    "ApplyPermutation": (
        r"\text{Apply Permutation}",
        r"Evaluate a permutation $p$ of $\{0, \dots, n - 1\}$ at a point $i$: $p(i)$.",
    ),
    "AsPermutation": (
        r"\text{As Permutation}",
        r"Read a list $(p(0), \dots, p(n - 1))$ of images as the permutation it lists — the "
        "inverse of evaluating a permutation at every point.",
    ),
}

SIGNATURES: list[tuple[str, str, str]] = [
    ("Sign", "Permutations", "Integers"),
    ("Sign", "EvenPermutations", "PositiveIntegers"),
    ("CycleType", "Permutations", "IntegerPartitions"),
    ("ComposePermutations", "Permutations", "Permutations"),
    ("ComposePermutations", "EvenPermutations", "EvenPermutations"),
    ("RSKCorrespondence", "Permutations", "StandardYoungTableaux"),
    ("TableauShape", "StandardYoungTableaux", "IntegerPartitions"),
    ("ConjugatePartition", "IntegerPartitions", "IntegerPartitions"),
    ("StandardTableauxCount", "IntegerPartitions", "PositiveIntegers"),
    ("GlaisherBijection", "IntegerPartitions", "DistinctPartitions"),
    ("PermutationMatrix", "Permutations", "PermutationMatrices"),
    ("GeneratedGroup", "Permutations", "PermutationGroups"),
    ("ApplyPermutation", "Permutations", "Integers"),
    ("AsPermutation", "FiniteSequences", "Permutations"),
]

IMPLEMENTATIONS: dict[str, str] = {
    "Sign": "sign",
    "CycleType": "cycle_type",
    "ComposePermutations": "compose_permutations",
    "RSKCorrespondence": "rsk",
    "TableauShape": "tableau_shape",
    "ConjugatePartition": "conjugate_partition",
    "StandardTableauxCount": "standard_tableaux_count",
    "GlaisherBijection": "glaisher_bijection",
    "PermutationMatrix": "permutation_matrix",
    "GeneratedGroup": "generated_group",
    "ApplyPermutation": "apply_permutation",
    "AsPermutation": "as_permutation",
}

RELATIONS: list[RelationSpec] = [
    ("Sign", ["transposition"], [-1]),
    ("Sign", ["swap_last"], [-1]),
    ("Sign", ["four_cycle"], [-1]),
    ("Sign", ["three_two_cycle"], [-1]),
    ("Sign", ["three_cycle"], [1]),
    ("Sign", ["double_transposition"], [1]),
    ("Sign", ["identity3"], [1]),
    ("CycleType", ["transposition"], ["partition_2"]),
    ("CycleType", ["swap_last"], ["partition_21"]),
    ("CycleType", ["four_cycle"], ["partition_4"]),
    ("CycleType", ["three_cycle"], ["partition_3"]),
    ("CycleType", ["double_transposition"], ["partition_22"]),
    ("CycleType", ["three_two_cycle"], ["partition_32"]),
    ("CycleType", ["identity3"], ["partition_111"]),
    ("ComposePermutations", ["three_cycle", "three_cycle"], ["three_cycle_inverse"]),
    ("ComposePermutations", ["three_cycle", "three_cycle_inverse"], ["identity3"]),
    ("ComposePermutations", ["transposition_in_s3", "swap_last"], ["three_cycle_inverse"]),
    ("ComposePermutations", ["swap_last", "transposition_in_s3"], ["three_cycle"]),
    ("ComposePermutations", ["double_transposition", "three_cycle_in_s4"], ["three_cycle_023"]),
    ("ComposePermutations", ["four_cycle", "four_cycle"], ["double_transposition_0213"]),
    ("RSKCorrespondence", ["identity3"], ["tableau_row3", "tableau_row3"]),
    ("RSKCorrespondence", ["reversal3"], ["tableau_column3", "tableau_column3"]),
    ("RSKCorrespondence", ["three_cycle"], ["tableau_13_2", "tableau_12_3"]),
    ("RSKCorrespondence", ["three_cycle_inverse"], ["tableau_12_3", "tableau_13_2"]),
    ("RSKCorrespondence", ["double_transposition"], ["tableau_13_24", "tableau_13_24"]),
    ("RSKCorrespondence", ["four_cycle"], ["tableau_134_2", "tableau_123_4"]),
    ("RSKCorrespondence", ["three_two_cycle"], ["tableau_134_25", "tableau_124_35"]),
    ("TableauShape", ["tableau_32"], ["partition_32"]),
    ("TableauShape", ["tableau_32_columns"], ["partition_32"]),
    ("TableauShape", ["tableau_211"], ["partition_211"]),
    ("TableauShape", ["tableau_13_24"], ["partition_22"]),
    ("TableauShape", ["tableau_column3"], ["partition_111"]),
    ("TableauShape", ["tableau_row3"], ["partition_3"]),
    ("ConjugatePartition", ["partition_321"], ["partition_321"]),
    ("ConjugatePartition", ["partition_22"], ["partition_22"]),
    ("ConjugatePartition", ["partition_311"], ["partition_311"]),
    ("ConjugatePartition", ["partition_2211"], ["partition_42"]),
    ("ConjugatePartition", ["partition_42"], ["partition_2211"]),
    ("ConjugatePartition", ["partition_41"], ["partition_2111"]),
    ("ConjugatePartition", ["partition_5"], ["partition_11111"]),
    ("ConjugatePartition", ["partition_32"], ["partition_221"]),
    ("StandardTableauxCount", ["partition_5"], [1]),
    ("StandardTableauxCount", ["partition_41"], [4]),
    ("StandardTableauxCount", ["partition_32"], [5]),
    ("StandardTableauxCount", ["partition_311"], [6]),
    ("StandardTableauxCount", ["partition_221"], [5]),
    ("StandardTableauxCount", ["partition_2111"], [4]),
    ("StandardTableauxCount", ["partition_11111"], [1]),
    ("StandardTableauxCount", ["partition_22"], [2]),
    ("StandardTableauxCount", ["partition_2211"], [9]),
    ("StandardTableauxCount", ["partition_321"], [16]),
    ("GlaisherBijection", ["partition_11111"], ["partition_41"]),
    ("GlaisherBijection", ["partition_311"], ["partition_32"]),
    ("GlaisherBijection", ["partition_5"], ["partition_5"]),
    ("GlaisherBijection", ["partition_111"], ["partition_21"]),
    ("GlaisherBijection", ["partition_22"], ["partition_4"]),
    ("GlaisherBijection", ["partition_2111"], ["partition_41"]),
    ("GlaisherBijection", ["partition_321"], ["partition_321"]),
    ("PermutationMatrix", ["transposition"], ["D"]),
    ("PermutationMatrix", ["three_cycle"], ["cycle3"]),
    ("PermutationMatrix", ["three_cycle_inverse"], ["cycle3_inverse"]),
    ("PermutationMatrix", ["transposition_in_s3"], ["swap3"]),
    ("PermutationMatrix", ["double_transposition"], ["double_swap4"]),
    ("GeneratedGroup", ["four_cycle", "transposition_in_s4"], ["s4"]),
    ("GeneratedGroup", ["transposition_in_s4", "three_cycle_023"], ["s4"]),
    ("GeneratedGroup", ["transposition", "three_cycle"], ["s3"]),
    ("GeneratedGroup", ["double_transposition", "double_transposition_0213"], ["klein_four"]),
    ("GeneratedGroup", ["three_cycle_in_s5", "five_cycle"], ["a5"]),
    ("GeneratedGroup", ["three_cycle"], ["c3"]),
    ("GeneratedGroup", ["four_cycle"], ["c4"]),
    ("ApplyPermutation", ["three_cycle", 0], [1]),
    ("ApplyPermutation", ["three_cycle", 2], [0]),
    ("ApplyPermutation", ["four_cycle", 3], [0]),
    ("ApplyPermutation", ["double_transposition", 2], [3]),
    ("ApplyPermutation", ["three_two_cycle", 4], [3]),
    ("ApplyPermutation", ["transposition", 1], [0]),
    ("AsPermutation", ["images_120"], ["three_cycle"]),
    ("AsPermutation", ["images_201"], ["three_cycle_inverse"]),
    ("AsPermutation", ["images_10"], ["transposition"]),
    ("AsPermutation", ["images_012"], ["identity3"]),
    ("AsPermutation", ["images_1032"], ["double_transposition"]),
]

DISPLAYS: dict[str, tuple[str | None, bool]] = {
    "Sign": (r"\op{\operatorname{sgn}(}{in0}\op{)} = {out0}", False),
    "ComposePermutations": (r"{in0} \op{\cdot} {in1} = {out0}", False),
    "ConjugatePartition": (r"{in0}\op{'} = {out0}", False),
    "ApplyPermutation": (r"{in0}\op{(}{in1}\op{)} = {out0}", False),
}

_WIKI = "https://en.wikipedia.org/wiki/"

REFERENCES: dict[str, list[Reference]] = {
    "Sign": [("Wikipedia", _WIKI + "Parity_of_a_permutation")],
    "CycleType": [("Wikipedia", _WIKI + "Cycle_type")],
    "RSKCorrespondence": [("Wikipedia", _WIKI + "Robinson%E2%80%93Schensted_correspondence")],
    "ConjugatePartition": [("Wikipedia", _WIKI + "Integer_partition#Conjugate_partitions")],
    "StandardTableauxCount": [("Wikipedia", _WIKI + "Hook_length_formula")],
    "GlaisherBijection": [("Wikipedia", _WIKI + "Glaisher%27s_theorem")],
    "PermutationMatrix": [("Wikipedia", _WIKI + "Permutation_matrix")],
    "GeneratedGroup": [("Wikipedia", _WIKI + "Generating_set_of_a_group")],
}

FILINGS: dict[str, list[str]] = {
    "Combinatorics": ["CombinatoricsOperations"],
    "CombinatoricsOperations": list(OPERATORS),
}
