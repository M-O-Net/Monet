import json
import pathlib
import re
from math import prod
from typing import Any

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
    abelian,
    held_by,
    instance,
    number_field,
    polynomial,
    small_group,
)
from seed_data.sources import LMFDB, SMALL_GROUPS

MONET = (
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
SNAPSHOTS = pathlib.Path(__file__).resolve().parent / "sources"
MAX_COMPUTED_DEGREE = 10
GALOIS_GROUPS = {
    "2T1": "c2",
    "3T1": "c3",
    "3T2": "s3",
    "4T1": "c4",
    "4T2": "klein_four",
    "6T1": "c6",
}
CYCLOTOMIC_FIELDS = {"4.0.144.1": 12, "6.0.19683.1": 9}
CYCLOTOMIC_POLYNOMIALS = {"6.0.19683.1": 18}
TEX_MACROS = {
    r"\OD": r"\mathrm{OD}",
    r"\SD": r"\mathrm{SD}",
    ":": r" \rtimes ",
    r"\times": r" \times ",
}


def snapshot(path: str) -> list[dict[str, Any]]:
    header, *rows = (line.split("\t") for line in (SNAPSHOTS / path).read_text().splitlines())
    return [dict(zip(header, map(json.loads, row), strict=True)) for row in rows]


INSTANCES: dict[str, Instance] = {}
REFERENCES: dict[str, list[Reference]] = {"SmallGroupID": [SMALL_GROUPS.cite()]}
RELATIONS: list[RelationSpec] = []
ASSERTED: list[RelationSpec] = []


def holder(data: Data) -> str | None:
    mine = (key for key, (_, _, facets) in INSTANCES.items() if any(d == data for _, d in facets))
    return next(mine, None) or held_by(data, *MONET)


def polynomial_latex(coefficients: list[int], var: str = "x") -> str:
    terms = []
    for power in reversed(range(len(coefficients))):
        coefficient = coefficients[power]
        if coefficient == 0:
            continue
        monomial = "" if power == 0 else var if power == 1 else f"{var}^{{{power}}}"
        magnitude = "" if abs(coefficient) == 1 and power else str(abs(coefficient))
        terms.append(("-" if coefficient < 0 else "+", f"{magnitude} {monomial}".strip()))
    (sign, first), *rest = terms
    return ("- " if sign == "-" else "") + first + "".join(f" {s} {t}" for s, t in rest)


def _field(row: dict[str, Any]) -> tuple[str, Instance]:
    label, coefficients = row["label"], row["coefficients"]
    data = number_field(*coefficients)
    if label in CYCLOTOMIC_FIELDS:
        n = CYCLOTOMIC_FIELDS[label]
        return f"q_zeta{n}", instance(rf"\mathbb{{Q}}(\zeta_{{{n}}})", data, ["CyclotomicFields"])
    if len(coefficients) == 3:
        discriminant = row["discriminant"]
        d = discriminant if discriminant % 4 == 1 else discriminant // 4
        key = f"q_sqrt{d}" if d > 0 else f"q_sqrt_minus{-d}"
        return key, instance(rf"\mathbb{{Q}}(\sqrt{{{d}}})", data, ["QuadraticFields"])
    latex = rf"\mathbb{{Q}}[x]/\left({polynomial_latex(coefficients)}\right)"
    return "nf_" + label.replace(".", "_"), instance(latex, data, ["NumberFields"])


def _defining_polynomial(field_key: str, label: str, coefficients: list[int]) -> str:
    data = polynomial(*coefficients)
    key = holder(data)
    if key is not None:
        return key
    if label in CYCLOTOMIC_POLYNOMIALS:
        key = f"Phi{CYCLOTOMIC_POLYNOMIALS[label]}"
        INSTANCES[key] = instance(polynomial_latex(coefficients), data, ["CyclotomicPolynomials"])
        RELATIONS.append(("CyclotomicPolynomial", [CYCLOTOMIC_POLYNOMIALS[label]], [key]))
        return key
    key = f"{field_key}_polynomial"
    INSTANCES[key] = instance(
        polynomial_latex(coefficients), data, ["MonicIntegerPolynomials", "IrreduciblePolynomials"]
    )
    return key


def _number_fields() -> None:
    for row in snapshot("lmfdb/number_fields.tsv"):
        cite = [LMFDB.cite(f"NumberField/{row['label']}", row["label"])]
        key, created = _field(row)
        existing = holder(created[2][0][1])
        if existing is None:
            INSTANCES[key] = created
        else:
            key = existing
        REFERENCES[key] = cite
        quadratic = len(row["coefficients"]) == 3
        defining = _defining_polynomial(key, row["label"], row["coefficients"])
        RELATIONS.append(("FieldDiscriminant", [key], [row["discriminant"]], cite))
        RELATIONS.append(("GaloisGroup", [key], [GALOIS_GROUPS[row["galois_group"]]], cite))
        RELATIONS.append(("DefiningPolynomial", [key], [defining], cite))
        (RELATIONS if quadratic else ASSERTED).extend(
            [
                ("ClassNumber", [key], [prod(row["class_group"])], cite),
                ("StemField", [defining], [key], cite),
            ]
        )


def weierstrass_latex(ainvs: list[int]) -> str:
    a1, a2, a3, a4, a6 = ainvs
    left = "y^{2}"
    for coefficient, monomial in ((a1, "x y"), (a3, "y")):
        if coefficient:
            magnitude = "" if abs(coefficient) == 1 else f"{abs(coefficient)} "
            left += f" {'-' if coefficient < 0 else '+'} {magnitude}{monomial}"
    return f"{left} = {polynomial_latex([a6, a4, a2, 1])}"


def curve_path(label: str) -> str:
    conductor, isogeny_class, number = re.findall(r"(\d+)\.([a-z]+)(\d+)", label)[0]
    return f"EllipticCurve/Q/{conductor}/{isogeny_class}/{number}"


def _elliptic_curves() -> None:
    for row in snapshot("lmfdb/elliptic_curves.tsv"):
        cite = [LMFDB.cite(curve_path(row["label"]), row["label"])]
        key = holder(row["curve"])
        if key is None:
            key = f"curve_{row['cremona_label']}"
            INSTANCES[key] = instance(
                weierstrass_latex(row["ainvs"]), row["curve"], ["EllipticCurves"]
            )
        REFERENCES[key] = cite
        RELATIONS.append(("EllipticDiscriminant", [key], [row["discriminant"]], cite))
        ASSERTED.append(("Conductor", [key], [row["conductor"]], cite))
        ASSERTED.append(("TorsionSubgroup", [key], [abelian(0, row["torsion"])], cite))


def cycles_latex(image: list[int]) -> str:
    seen, cycles = set(), []
    for start in range(len(image)):
        cycle, point = [], start
        while point not in seen:
            seen.add(point)
            cycle.append(point)
            point = image[point]
        if len(cycle) > 1:
            cycles.append(r"\left( " + r"\; ".join(map(str, cycle)) + r"\right)")
    return "".join(cycles) or "e"


def trivial_group_on(degree: int) -> Instance:
    return instance(
        rf"\left\{{ e \right\}} \leq S_{{{degree}}}",
        {"permgroup": {"degree": degree, "generators": [list(range(degree))]}},
        ["PermutationGroups"],
        f"The trivial group, acting on {degree} points.",
    )


def subgroup_key(data: Data, name: str) -> str:
    key = holder(data)
    if key is not None:
        return key
    degree, generators = data["permgroup"]["degree"], data["permgroup"]["generators"]
    if generators == [list(range(degree))]:
        key = f"trivial{degree}"
        INSTANCES[key] = trivial_group_on(degree)
        return key
    latex = r"\left\langle " + ", ".join(map(cycles_latex, generators)) + r" \right\rangle"
    INSTANCES[name] = instance(latex, data, ["PermutationGroups"])
    return name


def _abelian_latex(invariants: list[int]) -> str:
    return r" \oplus ".join(rf"\mathbb{{Z}}/{n}\mathbb{{Z}}" for n in invariants)


def _group_latex(name: str) -> str:
    latex = re.sub(r"([_^])(\d+)", r"\1{\2}", name)
    for macro, replacement in TEX_MACROS.items():
        latex = latex.replace(macro, replacement)
    return latex.replace("  ", " ")


def _group(row: dict[str, Any]) -> tuple[str, Instance]:
    order, index = map(int, row["label"].split("."))
    invariants = row["abelian_invariants"]
    facets = [("PermutationGroups", row["permutation"])]
    if invariants is not None:
        cyclic = len(invariants) == 1
        kind = "CyclicGroups" if cyclic else "FinitelyGeneratedAbelianGroups"
        facets.append((kind, abelian(0, invariants)))
        key, latex = (
            (f"c{order}" if cyclic else f"group_{order}_{index}"),
            _abelian_latex(invariants),
        )
    else:
        key, latex = f"group_{order}_{index}", _group_latex(row["name"])
    if re.fullmatch(r"D_\{?\d+\}?", row["name"]):
        key, kind = f"d{order // 2}", "DihedralGroups"
    else:
        prime = all(order % d for d in range(2, order))
        kind = "SimpleGroups" if prime else "FiniteGroups"
    facets.append((kind, small_group(order, index)))
    return key, (latex, None, facets)


def _first_facet(key: str) -> Data:
    area = next((area for area in MONET if key in getattr(area, "INSTANCES", {})), None)
    first: Data = (INSTANCES if area is None else area.INSTANCES)[key][2][0][1]
    return first


def _groups() -> None:
    rows = snapshot("lmfdb/abstract_groups.tsv")
    invariants = {row["label"]: row["abelian_invariants"] for row in rows}
    for row in rows:
        label = row["label"]
        order, index = map(int, label.split("."))
        key = holder(small_group(order, index))
        if key is None and row["permutation"] is None:
            continue
        cite = [LMFDB.cite(f"Groups/Abstract/{label}", label)]
        if key is None:
            key, created = _group(row)
            INSTANCES[key] = created
            if created[2][1][0] == "CyclicGroups":
                RELATIONS.append(("CyclicGroup", [order], [key]))
            if created[2][-1][0] == "DihedralGroups":
                ASSERTED.append(("DihedralGroup", [order // 2], [key], cite))
        REFERENCES[key] = [*cite, SMALL_GROUPS.cite()]
        first = _first_facet(key)
        computed = "permgroup" in first and first["permgroup"]["degree"] <= MAX_COMPUTED_DEGREE
        RELATIONS.append(("GroupOrder", [key], [order], cite))
        if "permgroup" in first or "fpgroup" in first:
            quotient = abelian(0, invariants[row["abelianization"]])
            RELATIONS.append(("Abelianisation", [key], [quotient], cite))
        if row["centre"] is not None:
            centre = subgroup_key(row["centre"], f"centre_{key}")
            (RELATIONS if computed else ASSERTED).append(("Centre", [key], [centre], cite))
            if centre != key:
                centre_id = small_group(*map(int, row["center"].split(".")))
                ASSERTED.append(
                    ("SmallGroupID", [centre], [centre_id], [*cite, SMALL_GROUPS.cite()])
                )
        if row["composition_factors"] is not None:
            factors = [small_group(*factor) for factor in row["composition_factors"]]
            (RELATIONS if computed else ASSERTED).append(
                ("CompositionFactors", [key], factors, cite)
            )


_number_fields()
_elliptic_curves()
_groups()
