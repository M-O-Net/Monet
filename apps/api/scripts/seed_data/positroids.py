import csv
import itertools
import json
import pathlib

from seed_data import (
    analysis,
    atlas,
    combinatorics,
    cremona,
    fields,
    findstat,
    geometry,
    graph_atlas,
    graphs,
    groups,
    knotinfo,
    linear_algebra,
    lmfdb,
    mckay,
    numbers,
    polynomials,
    sequences,
    topology,
)
from seed_data.build import (
    Data,
    Instance,
    Reference,
    RelationSpec,
    Specimen,
    fingerprint,
    holdings,
    instance,
    knot,
    pmatrix,
)

SNAPSHOT = pathlib.Path(__file__).resolve().parent / "sources" / "positroids" / "positroids.tsv"
ELSEWHERE = (
    numbers,
    sequences,
    linear_algebra,
    polynomials,
    analysis,
    combinatorics,
    graphs,
    groups,
    fields,
    topology,
    geometry,
    findstat,
    lmfdb,
    cremona,
    atlas,
    knotinfo,
    mckay,
    graph_atlas,
)
GALASHIN_LAM: Reference = (
    "Galashin-Lam, Positroids, knots, and q,t-Catalan numbers",
    "https://arxiv.org/abs/2012.09745",
)
CLUSTER: Reference = (
    "Galashin-Lam, Positroid varieties and cluster algebras",
    "https://arxiv.org/abs/1906.03501",
)
POSTNIKOV: Reference = (
    "Postnikov, Total positivity, Grassmannians, and networks",
    "https://arxiv.org/abs/math/0609764",
)
COMPUTED: Reference = (
    "Monet positroid census (SnapPy, Regina, mutation search)",
    "https://github.com/M-O-Net/Monet/tree/main/apps/api/scripts/snapshot_positroids.py",
)
_WIKI = "https://en.wikipedia.org/wiki/"

INSTANCES: dict[str, Instance] = {}
REFERENCES: dict[str, list[Reference]] = {}
RELATIONS: list[RelationSpec] = []
ASSERTED: list[RelationSpec] = []

SECTIONS: dict[str, Specimen] = {
    "PositroidOperations": (
        r"\text{Positroid Operations}",
        "Operations on positroids, their links and their cluster quivers.",
    ),
}

OPERATORS: dict[str, Specimen] = {
    "RotatePositroid": (
        r"\text{Rotate}",
        r"Relabel the ground set cyclically, $i \mapsto i + 1 \bmod n$. The positroid variety is "
        "carried isomorphically onto the rotated one.",
    ),
    "ReflectPositroid": (
        r"\text{Reflect}",
        r"Relabel the ground set by $i \mapsto n + 1 - i$, reversing the cyclic order.",
    ),
    "DualPositroid": (
        r"\text{Dual}",
        r"The dual matroid, whose bases are the complements of the bases: a positroid of "
        r"$\mathrm{Gr}(n - k, n)$.",
    ),
    "PositroidBraid": (
        r"\text{Positroid Braid}",
        r"Galashin and Lam's braid $\beta(w)\beta(v)^{-1}$ on $n$ strands, where $(v, w)$ is the "
        r"Knutson-Lam-Speyer pair of the positroid and $\beta(u)$ is the positive lift of a "
        "reduced word for $u$. Its closure is the positroid link.",
    ),
    "ClusterQuiver": (
        r"\text{Cluster Quiver}",
        "The mutable part of the quiver dual to Postnikov's Le-graph of the positroid, as an "
        "exchange matrix: a seed of the cluster structure on the open positroid variety. Defined "
        "here for positroids whose link is a knot.",
    ),
    "AcyclicSeed": (
        r"\text{Acyclic Seed}",
        "An exchange matrix without oriented cycles in the same mutation class, found by search.",
    ),
    "CoxeterPolynomial": (
        r"\text{Coxeter Polynomial}",
        r"The characteristic polynomial of the Coxeter transformation $-E^{-1}E^{T}$ of an "
        r"acyclic quiver, where $E$ is its Euler form in a topological order. Mutation-equivalent "
        "acyclic quivers share it.",
    ),
    "ClosureAlexanderPolynomial": (
        r"\text{Alexander Polynomial of the Closure}",
        r"The Alexander polynomial of a braid's closure, when the closure is a knot: "
        r"$\det(I - \psi(\beta))\,(1 - t)/(1 - t^{n})$ with $\psi$ the reduced Burau "
        "representation, normalised to a polynomial with positive leading coefficient.",
    ),
    "NegateVariable": (
        r"\text{Negate the Variable}",
        r"Substitute $-x$ for $x$, normalised to a positive leading coefficient.",
    ),
}

SIGNATURES: list[tuple[str, str, str]] = [
    ("RotatePositroid", "Positroids", "Positroids"),
    ("ReflectPositroid", "Positroids", "Positroids"),
    ("DualPositroid", "Positroids", "Positroids"),
    ("PositroidBraid", "Positroids", "BraidWords"),
    ("ClusterQuiver", "Positroids", "ExchangeMatrices"),
    ("AcyclicSeed", "ExchangeMatrices", "AcyclicExchangeMatrices"),
    ("CoxeterPolynomial", "AcyclicExchangeMatrices", "MonicIntegerPolynomials"),
    ("ClosureAlexanderPolynomial", "BraidWords", "IntegerPolynomials"),
    ("NegateVariable", "Polynomials", "Polynomials"),
]

IMPLEMENTATIONS: dict[str, str] = {
    "RotatePositroid": "rotate_positroid",
    "ReflectPositroid": "reflect_positroid",
    "DualPositroid": "dual_positroid",
    "PositroidBraid": "positroid_braid",
    "ClusterQuiver": "cluster_quiver",
    "CoxeterPolynomial": "coxeter_polynomial",
    "ClosureAlexanderPolynomial": "closure_alexander_polynomial",
    "NegateVariable": "negate_variable",
}

DISPLAYS: dict[str, tuple[str | None, bool]] = {
    "RotatePositroid": (r"\op{\rho(}{in0}\op{)} = {out0}", False),
    "DualPositroid": (r"{in0}\op{^{*}} = {out0}", False),
}

FILINGS: dict[str, list[str]] = {
    "Combinatorics": ["PositroidOperations"],
    "PositroidOperations": list(OPERATORS),
}

HELD = holdings(*ELSEWHERE)


def _hold(key: str, specimen: Instance) -> str:
    held = fingerprint(specimen[2][0][1])
    if held not in HELD:
        HELD[held] = key
        INSTANCES[key] = specimen
    return HELD[held]


def _credit(key: str, reference: Reference) -> None:
    if reference not in REFERENCES.setdefault(key, []):
        REFERENCES[key].append(reference)


def _window_key(window: list[int]) -> str:
    return "positroid_" + "_".join(map(str, window))


def _positroid_data(window: list[int]) -> Data:
    return {"positroid": {"n": len(window), "window": window}}


def _knot_latex(name: str) -> str:
    crossings, _, index = name.partition("_")
    return rf"\mathrm{{{crossings}}}_{{{index}}}"


def _braid_latex(word: list[int], strands: int) -> str:
    if not word:
        return rf"1_{{B_{{{strands}}}}}"
    pieces = []
    for letter, run in itertools.groupby(word):
        power = len(list(run)) * (1 if letter > 0 else -1)
        pieces.append(rf"\sigma_{{{abs(letter)}}}" + ("" if power == 1 else f"^{{{power}}}"))
    return " ".join(pieces)


def _types(text: str) -> list[str]:
    return text.split(",")


def _polynomial(key: str, row: dict[str, str], column: str) -> str:
    return _hold(
        key,
        instance(row[f"{column}_latex"], json.loads(row[column]), _types(row[f"{column}_types"])),
    )


def _matrix(key: str, rows_text: str, types_text: str) -> str:
    rows = json.loads(rows_text)
    data: Data = {"matrix": [[{"int": int(x)} for x in r] for r in rows]}
    return _hold(key, instance(pmatrix(rows), data, _types(types_text)))


def _import(row: dict[str, str]) -> None:
    window = json.loads(row["window"])
    n, k = len(window), int(row["k"])
    name = row["knot"]
    latex = _knot_latex(name)
    tag = "_".join(map(str, window))
    key = _window_key(window)
    INSTANCES[key] = instance(
        rf"\Pi^{{\circ}}_{{[{', '.join(map(str, window))}]}}",
        _positroid_data(window),
        ["Positroids"],
        rf"A positroid of $\mathrm{{Gr}}({k}, {n})$ whose link is ${latex}$.",
    )
    word = json.loads(row["braid"])
    braid_key = _hold(
        f"positroid_braid_{tag}",
        instance(_braid_latex(word, n), {"braid": {"strands": n, "word": word}}, ["BraidWords"]),
    )
    knot_key = _hold(
        f"K{name}",
        instance(latex, knot(name), ["Knots"], "The unknot." if name == "0_1" else None),
    )
    RELATIONS.extend(
        [
            ("RotatePositroid", [key], [_positroid_data(json.loads(row["rotated"]))]),
            ("ReflectPositroid", [key], [_positroid_data(json.loads(row["reflected"]))]),
            ("DualPositroid", [key], [_positroid_data(json.loads(row["dual"]))]),
            ("PositroidBraid", [key], [braid_key], [GALASHIN_LAM]),
        ]
    )
    ASSERTED.append(("BraidClosure", [braid_key], [knot_key], [COMPUTED]))
    if row["negated"]:
        alexander_key = _polynomial(f"positroid_alexander_{tag}", row, "alexander")
        negated_key = _polynomial(f"positroid_negated_{tag}", row, "negated")
        RELATIONS.extend(
            [
                ("ClosureAlexanderPolynomial", [braid_key], [alexander_key]),
                ("NegateVariable", [alexander_key], [negated_key]),
            ]
        )
    if row["quiver"]:
        quiver_key = _matrix(f"positroid_quiver_{tag}", row["quiver"], row["quiver_types"])
        RELATIONS.append(("ClusterQuiver", [key], [quiver_key], [CLUSTER, POSTNIKOV]))
        if row["seed"]:
            seed_key = _matrix(f"positroid_seed_{tag}", row["seed"], row["seed_types"])
            coxeter_key = _polynomial(f"positroid_coxeter_{tag}", row, "coxeter")
            ASSERTED.append(("AcyclicSeed", [quiver_key], [seed_key], [COMPUTED]))
            RELATIONS.append(("CoxeterPolynomial", [seed_key], [coxeter_key]))


with SNAPSHOT.open(encoding="utf-8") as _snapshot:
    for _row in csv.DictReader(_snapshot, delimiter="\t"):
        _import(_row)

REFERENCES.update(
    {
        "PositroidBraid": [GALASHIN_LAM],
        "ClusterQuiver": [CLUSTER, POSTNIKOV],
        "CoxeterPolynomial": [("Wikipedia", _WIKI + "Coxeter_element")],
        "ClosureAlexanderPolynomial": [("Wikipedia", _WIKI + "Burau_representation")],
    }
)
