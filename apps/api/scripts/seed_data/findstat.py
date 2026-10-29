import json
import pathlib
from typing import Any

from seed_data import combinatorics, graphs
from seed_data.build import (
    Data,
    Endpoint,
    Instance,
    Reference,
    RelationSpec,
    Specimen,
    held_by,
    instance,
)
from seed_data.sources import FINDSTAT

SNAPSHOT: dict[str, Any] = json.loads(
    (pathlib.Path(__file__).parent / "sources" / "findstat.json").read_text()
)

Value = int | list[int] | list[list[int]] | dict[str, Any]

COLLECTIONS = {
    "Permutations": "Permutations",
    "Integer partitions": "IntegerPartitions",
    "Standard tableaux": "StandardTableaux",
    "Graphs": "Graphs",
}

OPERATORS: dict[str, Specimen] = {
    "InversePermutation": (
        r"\text{Inverse Permutation}",
        r"The permutation $p^{-1}$ that undoes $p$: it sends $p(i)$ back to $i$.",
    ),
    "ReversePermutation": (
        r"\text{Reverse}",
        r"Read the images of a permutation backwards: $i \mapsto p(n - 1 - i)$.",
    ),
    "ComplementPermutation": (
        r"\text{Complement}",
        r"Turn the images of a permutation upside down: $i \mapsto n - 1 - p(i)$.",
    ),
    "FoataBijection": (
        r"\text{Foata Bijection}",
        "Foata's fundamental bijection, building the image one letter at a time by cutting "
        "the word so far into blocks and rotating each. It carries the major index of a "
        "permutation to the number of inversions of its image.",
    ),
    "ReadingWord": (
        r"\text{Reading Word}",
        "The permutation read off a standard Young tableau row by row, from the bottom row "
        "up. Its RSK insertion tableau is the tableau it was read from.",
    ),
    "ConjugateTableau": (
        r"\text{Conjugate Tableau}",
        "Reflect a standard Young tableau in its main diagonal, so rows become columns. Its "
        "shape is the conjugate of the original shape.",
    ),
    "Evacuation": (
        r"\text{Evacuation}",
        "Schützenberger's involution on standard Young tableaux: repeatedly remove the "
        "smallest entry, slide the hole out by jeu de taquin, and record where it leaves. "
        "RSK turns reversing and complementing a permutation into evacuating both tableaux.",
    ),
    "ComponentSizes": (
        r"\text{Component Sizes}",
        "The numbers of vertices in the connected components of a graph, as a partition of "
        "its order.",
    ),
    "InversionCount": (
        r"\text{Number of Inversions}",
        r"The number of pairs $i < j$ with $p(i) > p(j)$: the length of $p$ as a word in "
        "adjacent transpositions.",
    ),
    "DescentCount": (
        r"\text{Number of Descents}",
        r"The number of positions $i$ with $p(i) > p(i + 1)$.",
    ),
    "MajorIndex": (
        r"\text{Major Index}",
        r"The sum of the descent positions $i$, counted from $1$, where $p(i) > p(i + 1)$. "
        "MacMahon showed it is distributed like the number of inversions.",
    ),
    "FixedPointCount": (
        r"\text{Number of Fixed Points}",
        r"The number of points $i$ with $p(i) = i$.",
    ),
    "CycleCount": (
        r"\text{Number of Cycles}",
        "The number of cycles of a permutation, fixed points included.",
    ),
    "PermutationOrder": (
        r"\text{Order}",
        "The least number of times a permutation must be applied to give the identity: the "
        "least common multiple of its cycle lengths.",
    ),
    "LongestIncreasingSubsequence": (
        r"\text{Longest Increasing Subsequence}",
        "The length of the longest increasing subsequence of a permutation's images. By "
        "Schensted's theorem it is the length of the first row of its RSK tableaux.",
    ),
    "PartitionLength": (
        r"\text{Number of Parts}",
        "The number of parts of an integer partition.",
    ),
    "LargestPart": (
        r"\text{Largest Part}",
        "The largest part of an integer partition: the number of parts of its conjugate.",
    ),
    "DurfeeSquare": (
        r"\text{Durfee Square}",
        r"The side of the largest square that fits in the top left corner of a partition's "
        r"Young diagram: the largest $k$ with at least $k$ parts of size at least $k$.",
    ),
}

OPERATOR_OF = {
    "Mp00044": "ConjugatePartition",
    "Mp00083": "TableauShape",
    "Mp00108": "CycleType",
    "Mp00312": "GlaisherBijection",
    "Mp00111": "Complement",
    "Mp00064": "ReversePermutation",
    "Mp00066": "InversePermutation",
    "Mp00067": "FoataBijection",
    "Mp00069": "ComplementPermutation",
    "Mp00081": "ReadingWord",
    "Mp00084": "ConjugateTableau",
    "Mp00085": "Evacuation",
    "Mp00037": "ComponentSizes",
    "St000003": "StandardTableauxCount",
    "St000037": "Sign",
    "St000018": "InversionCount",
    "St000021": "DescentCount",
    "St000004": "MajorIndex",
    "St000022": "FixedPointCount",
    "St000031": "CycleCount",
    "St000058": "PermutationOrder",
    "St000062": "LongestIncreasingSubsequence",
    "St000010": "PartitionLength",
    "St000147": "LargestPart",
    "St000183": "DurfeeSquare",
}
RSK_TABLEAUX = ("Mp00059", "Mp00070")

SIGNATURES: list[tuple[str, str, str]] = [
    ("InversePermutation", "Permutations", "Permutations"),
    ("InversePermutation", "EvenPermutations", "EvenPermutations"),
    ("ReversePermutation", "Permutations", "Permutations"),
    ("ComplementPermutation", "Permutations", "Permutations"),
    ("FoataBijection", "Permutations", "Permutations"),
    ("ReadingWord", "StandardYoungTableaux", "Permutations"),
    ("ConjugateTableau", "StandardYoungTableaux", "StandardYoungTableaux"),
    ("Evacuation", "StandardYoungTableaux", "StandardYoungTableaux"),
    ("ComponentSizes", "Graphs", "IntegerPartitions"),
    ("InversionCount", "Permutations", "Integers"),
    ("DescentCount", "Permutations", "Integers"),
    ("MajorIndex", "Permutations", "Integers"),
    ("FixedPointCount", "Permutations", "Integers"),
    ("CycleCount", "Permutations", "PositiveIntegers"),
    ("PermutationOrder", "Permutations", "PositiveIntegers"),
    ("LongestIncreasingSubsequence", "Permutations", "PositiveIntegers"),
    ("PartitionLength", "IntegerPartitions", "PositiveIntegers"),
    ("LargestPart", "IntegerPartitions", "PositiveIntegers"),
    ("DurfeeSquare", "IntegerPartitions", "PositiveIntegers"),
]

IMPLEMENTATIONS: dict[str, str] = {
    "InversePermutation": "inverse_permutation",
    "ReversePermutation": "reverse_permutation",
    "ComplementPermutation": "complement_permutation",
    "FoataBijection": "foata_bijection",
    "ReadingWord": "reading_word",
    "ConjugateTableau": "conjugate_tableau",
    "Evacuation": "evacuation",
    "ComponentSizes": "component_sizes",
    "InversionCount": "inversion_count",
    "DescentCount": "descent_count",
    "MajorIndex": "major_index",
    "FixedPointCount": "fixed_point_count",
    "CycleCount": "cycle_count",
    "PermutationOrder": "permutation_order",
    "LongestIncreasingSubsequence": "longest_increasing_subsequence",
    "PartitionLength": "partition_length",
    "LargestPart": "largest_part",
    "DurfeeSquare": "durfee_square",
}

DISPLAYS: dict[str, tuple[str | None, bool]] = {
    "InversePermutation": (r"{in0}\op{^{-1}} = {out0}", False),
}


def _entry(identifier: str) -> str:
    folder = "MapsDatabase" if identifier.startswith("Mp") else "StatisticsDatabase"
    return f"{folder}/{identifier}"


def _cycles(images: list[int]) -> str:
    seen: set[int] = set()
    cycles = []
    for start in range(len(images)):
        cycle = []
        point = start
        while point not in seen:
            seen.add(point)
            cycle.append(str(point))
            point = images[point]
        if cycle:
            cycles.append(r"\left( " + r"\; ".join(cycle) + r"\right)")
    return "".join(cycles)


def _is_even(images: list[int]) -> bool:
    inversions = sum(1 for i, a in enumerate(images) for b in images[i + 1 :] if a > b)
    return inversions % 2 == 0


def _tableau_latex(rows: list[list[int]]) -> str:
    body = r" \\ ".join(" & ".join(map(str, row)) for row in rows)
    return rf"\begin{{array}}{{{'l' * len(rows[0])}}}{body}\end{{array}}"


def _monet(value: Value, collection: str) -> tuple[Data, str, Instance | None]:
    if collection == "Permutations":
        images = [i - 1 for i in value]
        kind = "EvenPermutations" if _is_even(images) else "Permutations"
        data = {"perm": images}
        return data, "perm_" + "".join(map(str, images)), instance(_cycles(images), data, [kind])
    if collection == "Integer partitions":
        kind = "DistinctPartitions" if len(set(value)) == len(value) else "IntegerPartitions"
        latex = rf"\left({', '.join(map(str, value))}\right) \vdash {sum(value)}"
        data = {"partition": value}
        return data, "partition_" + "".join(map(str, value)), instance(latex, data, [kind])
    if collection == "Standard tableaux":
        data = {"tableau": value}
        key = "tableau_" + "_".join("".join(map(str, row)) for row in value)
        return data, key, instance(_tableau_latex(value), data, ["StandardYoungTableaux"])
    if collection == "Graphs":
        return {"graph": value}, "", None
    raise ValueError(f"FindStat collection {collection} has no Monet type")


INSTANCES: dict[str, Instance] = {}
REFERENCES: dict[str, list[Reference]] = {}


def _endpoint(value: Value, collection: str) -> Endpoint:
    if collection == "Integer":
        return int(value)
    data, key, created = _monet(value, collection)
    held = held_by(data, combinatorics, graphs) or (key if key in INSTANCES else None)
    if held is None:
        if created is None:
            raise ValueError(f"FindStat names {value}, which Monet does not hold")
        INSTANCES[key] = created
        held = key
    REFERENCES[held] = [FINDSTAT.cite(f"CollectionsDatabase/{COLLECTIONS[collection]}/")]
    return data


def _credit(*identifiers: str) -> list[Reference]:
    return [FINDSTAT.cite(_entry(identifier)) for identifier in identifiers]


def _values(identifier: str) -> list[tuple[Value, Value]]:
    return [
        (json.loads(element), image if isinstance(image, int) else json.loads(image))
        for element, image in SNAPSHOT[identifier]["values"].items()
    ]


def _relations() -> list[RelationSpec]:
    specs: list[RelationSpec] = []
    for identifier, operator in OPERATOR_OF.items():
        entry = SNAPSHOT[identifier]
        specs.extend(
            (
                operator,
                [_endpoint(value, entry["domain"])],
                [_endpoint(image, entry["codomain"])],
                _credit(identifier),
            )
            for value, image in _values(identifier)
        )
    insertion, recording = (SNAPSHOT[identifier]["values"] for identifier in RSK_TABLEAUX)
    specs.extend(
        (
            "RSKCorrespondence",
            [_endpoint(json.loads(permutation), "Permutations")],
            [
                _endpoint(json.loads(insertion[permutation]), "Standard tableaux"),
                _endpoint(json.loads(recording[permutation]), "Standard tableaux"),
            ],
            _credit(*RSK_TABLEAUX),
        )
        for permutation in insertion
        if permutation in recording
    )
    return specs


RELATIONS: list[RelationSpec] = _relations()

for _operator, _identifiers in [
    *((operator, [identifier]) for identifier, operator in OPERATOR_OF.items()),
    ("RSKCorrespondence", list(RSK_TABLEAUX)),
]:
    if _operator != "GlaisherBijection":
        REFERENCES[_operator] = _credit(*_identifiers)

FILINGS: dict[str, list[str]] = {
    "CombinatoricsOperations": [key for key in OPERATORS if key != "ComponentSizes"],
    "GraphOperations": ["ComponentSizes"],
}
