import csv
import itertools
import json
import pathlib
import re
from fractions import Fraction

from seed_data import (
    analysis,
    combinatorics,
    fields,
    geometry,
    graphs,
    groups,
    linear_algebra,
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
    fingerprint,
    holdings,
    instance,
    knot,
    matrix_instance,
)
from seed_data.sources import KNOTINFO

SNAPSHOT = pathlib.Path(__file__).resolve().parent / "sources" / "knotinfo" / "knots.tsv"
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
)
JONES_MAX_CROSSINGS = 12
TORUS = re.compile(r"torus knot T\((\d+),(\d+)\)")

INSTANCES: dict[str, Instance] = {}
REFERENCES: dict[str, list[Reference]] = {}
RELATIONS: list[RelationSpec] = []
ASSERTED: list[RelationSpec] = []


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


def _knot_latex(name: str) -> str:
    crossings, index = name.split("_")
    return rf"\mathrm{{{crossings}}}_{{{index}}}"


def _braid_latex(word: list[int]) -> str:
    pieces = []
    for letter, run in itertools.groupby(word):
        power = len(list(run)) * (1 if letter > 0 else -1)
        pieces.append(rf"\sigma_{{{abs(letter)}}}" + ("" if power == 1 else f"^{{{power}}}"))
    return " ".join(pieces)


def _types(row: dict[str, str], column: str) -> list[str]:
    return row[column].split(",")


def _braid_words(notation: str) -> list[list[int]]:
    words = json.loads(notation)
    return words if isinstance(words[0], list) else [words]


def _relate_braid(
    key: str, word: list[int], latex: str, closure: tuple[str, str], credit: Reference
) -> None:
    knot_key, jones_key = closure
    braid: Data = {"braid": {"strands": max(map(abs, word)) + 1, "word": word}}
    braid_key = _hold(
        key, instance(_braid_latex(word), braid, ["BraidWords"], f"Its closure is ${latex}$.")
    )
    _credit(braid_key, credit)
    jones: RelationSpec = ("JonesPolynomial", [braid_key], [jones_key], [credit])
    (RELATIONS if len(word) <= JONES_MAX_CROSSINGS else ASSERTED).append(jones)
    ASSERTED.append(("BraidClosure", [braid_key], [knot_key], [credit]))


def _import(row: dict[str, str]) -> None:
    name = row["name"]
    credit = KNOTINFO.cite(name)
    latex = _knot_latex(name)
    seifert = json.loads(row["seifert_matrix"])

    knot_key = _hold(f"K{name}", instance(latex, knot(name), _types(row, "knot_types")))
    seifert_key = _hold(
        f"seifert_{name}",
        matrix_instance(seifert, _types(row, "seifert_types"), f"A Seifert matrix of ${latex}$."),
    )
    alexander_key = _hold(
        f"alexander_{name}",
        instance(
            row["alexander_latex"],
            json.loads(row["alexander_data"]),
            _types(row, "alexander_types"),
        ),
    )
    jones_key = _hold(
        f"jones_{name}",
        instance(row["jones_latex"], json.loads(row["jones_data"]), _types(row, "jones_types")),
    )
    for key in (knot_key, seifert_key):
        _credit(key, credit)
    for index, word in enumerate(_braid_words(row["braid_notation"])):
        key = f"braid_{name}" if index == 0 else f"braid_{name}_{index + 1}"
        _relate_braid(key, word, latex, (knot_key, jones_key), credit)

    RELATIONS.extend(
        [
            ("CrossingNumber", [knot_key], [int(row["crossing_number"])], [credit]),
            ("AlexanderPolynomial", [seifert_key], [alexander_key], [credit]),
            ("KnotDeterminant", [seifert_key], [int(row["determinant"])], [credit]),
            ("KnotSignature", [seifert_key], [int(row["signature"])], [credit]),
        ]
    )
    ASSERTED.append(("SeifertMatrix", [knot_key], [seifert_key], [credit]))
    if row["two_bridge_notation"]:
        p, q = json.loads(row["two_bridge_notation"])
        ASSERTED.append(("TwoBridgeKnot", [Fraction(p, q)], [knot_key], [credit]))
    torus = TORUS.fullmatch(row["geometric_type"])
    if torus:
        ASSERTED.append(("TorusKnot", [int(torus[1]), int(torus[2])], [knot_key], [credit]))


with SNAPSHOT.open(encoding="utf-8") as _snapshot:
    for _row in csv.DictReader(_snapshot, delimiter="\t"):
        _import(_row)
