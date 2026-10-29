import csv
import json
import multiprocessing
import pathlib
import re
import sys

import sympy
from snapshot_typing import load_prelude, matrix_types, most_specific, polynomial_types

MAX_CROSSINGS = 11
KEPT = [
    "name",
    "crossing_number",
    "alternating",
    "symmetry_type",
    "two_bridge_notation",
    "geometric_type",
    "braid_index",
    "braid_notation",
    "seifert_matrix",
    "determinant",
    "signature",
    "alexander_polynomial",
    "jones_polynomial",
]
DERIVED = [
    "knot_types",
    "seifert_types",
    "alexander_data",
    "alexander_latex",
    "alexander_types",
    "jones_data",
    "jones_latex",
    "jones_types",
]
OUT = pathlib.Path(__file__).resolve().parent / "seed_data" / "sources" / "knotinfo" / "knots.tsv"

X, T = sympy.Symbol("x"), sympy.Symbol("t")
PRELUDE = load_prelude()


def _knotinfo_polynomial(text: str, var: sympy.Symbol) -> sympy.Expr:
    return sympy.expand(sympy.sympify(text.replace("^", "**"), locals={"t": var}))


def _knot_types(row: dict[str, str]) -> list[str]:
    found = set()
    if row["alternating"] == "Y":
        found.add("AlternatingKnots")
    if "amphicheiral" in row["symmetry_type"]:
        found.add("AmphichiralKnots")
    if row["two_bridge_notation"]:
        found.add("TwoBridgeKnots")
    if row["geometric_type"].startswith("torus knot"):
        found.add("TorusKnots")
    return most_specific(found) or ["Knots"]


def _alexander(seifert: sympy.Matrix, knotinfo: str) -> sympy.Expr:
    computed = sympy.expand((seifert - X * seifert.T).det())
    normalised = _knotinfo_polynomial(knotinfo, X)
    ratio = sympy.cancel(computed / normalised)
    coefficient, power = ratio.as_coeff_exponent(X)
    if abs(coefficient) != 1 or ratio != coefficient * X**power:
        raise ValueError(f"det(V - xV^T) = {computed} is not a unit times {normalised}")
    return computed


def _signature(seifert: sympy.Matrix) -> int:
    roots = sympy.real_roots((seifert + seifert.T).charpoly(X).as_expr())
    return sum(1 if root > 0 else -1 for root in roots if root != 0)


def _derive(row: dict[str, str]) -> dict[str, str]:
    seifert_rows = json.loads(row["seifert_matrix"])
    seifert = sympy.Matrix(seifert_rows)
    if abs((seifert + seifert.T).det()) != int(row["determinant"]):
        raise ValueError(f"{row['name']}: |det(V + V^T)| disagrees with the determinant")
    if _signature(seifert) != int(row["signature"]):
        raise ValueError(f"{row['name']}: the signature of V + V^T disagrees")
    alexander = _alexander(seifert, row["alexander_polynomial"])
    jones = _knotinfo_polynomial(row["jones_polynomial"], T)
    jones_data = PRELUDE["to_data"](jones)
    jones_types = (
        polynomial_types(jones, T) if next(iter(jones_data)) == "poly" else ["Expressions"]
    )
    return {
        "knot_types": ",".join(_knot_types(row)),
        "seifert_types": ",".join(matrix_types(seifert_rows)),
        "alexander_data": json.dumps(PRELUDE["to_data"](alexander)),
        "alexander_latex": sympy.latex(alexander),
        "alexander_types": ",".join(polynomial_types(alexander, X)),
        "jones_data": json.dumps(jones_data),
        "jones_latex": sympy.latex(jones),
        "jones_types": ",".join(jones_types),
    }


def main(knotinfo_csv: str) -> None:
    csv.field_size_limit(10**9)
    with pathlib.Path(knotinfo_csv).open(encoding="utf-8") as source:
        header, _, *rows = csv.reader(source, delimiter="|")
    kept = []
    for values in rows:
        row = {column: values[header.index(column)].strip() for column in KEPT}
        crossings = row["crossing_number"]
        if crossings.isdigit() and 0 < int(crossings) <= MAX_CROSSINGS:
            row["seifert_matrix"] = re.sub(r"\s+", "", row["seifert_matrix"])
            kept.append(row)
    with multiprocessing.Pool() as pool:
        knots = [
            {**row, **derived} for row, derived in zip(kept, pool.map(_derive, kept), strict=True)
        ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, [*KEPT, *DERIVED], delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(knots)
    print(f"wrote {len(knots)} knots to {OUT}")


if __name__ == "__main__":
    main(sys.argv[1])
