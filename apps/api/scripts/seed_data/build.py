import itertools
from dataclasses import dataclass
from fractions import Fraction
from types import ModuleType
from typing import Any

Data = dict[str, Any]
Specimen = tuple[str, str | None]
Facet = tuple[str, Data]
Instance = tuple[str, str | None, list[Facet]]
TypeSpec = tuple[str, str, str | None, list[str]]
Cell = int | tuple[str, Data]
Endpoint = str | int | Fraction | Data
Reference = tuple[str, str]
RelationSpec = (
    tuple[str, list[Endpoint], list[Endpoint]]
    | tuple[str, list[Endpoint], list[Endpoint], list[Reference]]
)


@dataclass(frozen=True)
class Source:
    name: str
    homepage: str
    license: str
    obtained: str
    page: str | None = None

    def cite(self, entry: str | None = None) -> Reference:
        if entry is None:
            return self.name, self.homepage
        if self.page is None:
            raise ValueError(f"{self.name} has no page to link {entry} to")
        return self.name, self.page.format(entry)


def held_by(data: Data, *areas: ModuleType) -> str | None:
    for area in areas:
        for key, (_, _, facets) in getattr(area, "INSTANCES", {}).items():
            if any(held == data for _, held in facets):
                return str(key)
    return None


def integer(n: int) -> Data:
    return {"int": n}


def rational(p: int, q: int) -> Data:
    return {"rational": [p, q]}


def cell(value: int | Data) -> Data:
    return integer(value) if isinstance(value, int) else value


def polynomial(*coeffs_from_constant: int | Data, var: str = "x") -> Data:
    return {
        "poly": {
            "var": var,
            "degree": len(coeffs_from_constant) - 1,
            "coeffs": {str(power): cell(c) for power, c in enumerate(coeffs_from_constant)},
        }
    }


def coefficient(*coeffs_from_constant: int, var: str) -> Data:
    if len(coeffs_from_constant) == 1:
        return integer(coeffs_from_constant[0])
    return polynomial(*coeffs_from_constant, var=var)


def algebraic(minpoly_from_constant: list[int], root: int) -> Data:
    return {"algebraic": {"minpoly": polynomial(*minpoly_from_constant), "root": root}}


def fraction(p: int, q: int) -> tuple[str, Data]:
    sign = "- " if p < 0 else ""
    return (rf"{sign}\frac{{{abs(p)}}}{{{q}}}", rational(p, q))


I_CELL = ("i", algebraic([1, 0, 1], 1))
SQRT2_CELL = (r"\sqrt{2}", algebraic([-2, 0, 1], 1))
SQRT3_CELL = (r"\sqrt{3}", algebraic([-3, 0, 1], 1))
HALF_SQRT2_CELL = (r"\frac{\sqrt{2}}{2}", algebraic([-1, 0, 2], 1))
MINUS_HALF_SQRT2_CELL = (r"- \frac{\sqrt{2}}{2}", algebraic([-1, 0, 2], 0))
HALF_SQRT3_CELL = (r"\frac{\sqrt{3}}{2}", algebraic([-3, 0, 4], 1))
MINUS_HALF_SQRT3_CELL = (r"- \frac{\sqrt{3}}{2}", algebraic([-3, 0, 4], 0))


def cell_latex(value: Cell) -> str:
    return str(value) if isinstance(value, int) else value[0]


def cell_data(value: Cell) -> Data:
    return integer(value) if isinstance(value, int) else value[1]


def matrix(rows: list[list[Cell]]) -> Data:
    return {"matrix": [[cell_data(c) for c in row] for row in rows]}


def pmatrix(rows: list[list[Cell]]) -> str:
    body = r"\\".join(" & ".join(cell_latex(c) for c in row) for row in rows)
    return rf"\begin{{pmatrix}}{body}\end{{pmatrix}}"


def seifert(size: int) -> list[list[Cell]]:
    return [[-1 if i == j else 1 if j == i + 1 else 0 for j in range(size)] for i in range(size)]


def residue(a: int, n: int) -> Data:
    return {"residue": [a, n]}


def seq(formula: str, start: int) -> Data:
    return {"seq": {"var": "n", "start": start, "formula": formula}}


def recurrence(coeffs: list[int], initial: list[int]) -> Data:
    return {
        "recurrence": {
            "coeffs": [integer(c) for c in coeffs],
            "initial": [integer(v) for v in initial],
        }
    }


def holonomic(coeffs: list[list[int]], initial: list[int]) -> Data:
    return {
        "holonomic": {
            "coeffs": [coefficient(*c, var="n") for c in coeffs],
            "initial": [integer(v) for v in initial],
        }
    }


def dfinite(coeffs: list[list[int]], initial: list[int | Data]) -> Data:
    return {
        "dfinite": {
            "coeffs": [coefficient(*c, var="x") for c in coeffs],
            "point": integer(0),
            "initial": [cell(v) for v in initial],
        }
    }


def graph(order: int, edges: list[tuple[int, int]]) -> Data:
    return {"graph": {"order": order, "edges": sorted([min(e), max(e)] for e in edges)}}


def complete_graph(order: int) -> Data:
    return graph(order, list(itertools.combinations(range(order), 2)))


def cycle_graph(order: int) -> Data:
    return graph(order, [(i, (i + 1) % order) for i in range(order)])


def path_graph(order: int) -> Data:
    return graph(order, [(i, i + 1) for i in range(order - 1)])


def small_group(order: int, index: int) -> Data:
    return {"smallgroup": [order, index]}


def abelian(rank: int, torsion: list[int]) -> Data:
    return {"abelian": {"rank": rank, "torsion": torsion}}


def permgroup(degree: int, generators: list[list[int]]) -> Data:
    return {"permgroup": {"degree": degree, "generators": generators}}


def presentation(generators: list[str], relators: list[list[tuple[str, int]]]) -> Data:
    return {
        "fpgroup": {
            "generators": generators,
            "relators": [[[letter, power] for letter, power in r] for r in relators],
        }
    }


def number_field(*coeffs_from_constant: int) -> Data:
    return {"numberfield": polynomial(*coeffs_from_constant)}


def surface(orientable: bool, genus: int) -> Data:
    return {"surface": {"orientable": orientable, "genus": genus}}


def simplicial(facets: list[tuple[int, ...]]) -> Data:
    return {"simplicial": sorted(sorted(f) for f in facets)}


def lattice_polytope(points: list[tuple[int, ...]]) -> Data:
    return {"polytope": [[integer(c) for c in p] for p in sorted(points)]}


def polygon_instance(
    points: list[tuple[Cell, Cell]], type_keys: list[str], description: str | None = None
) -> Instance:
    coordinates = ", ".join(rf"\left({cell_latex(x)}, {cell_latex(y)}\right)" for x, y in points)
    data = {"polytope": [[cell_data(x), cell_data(y)] for x, y in points]}
    return (
        rf"\operatorname{{conv}}\left\{{{coordinates}\right\}}",
        description,
        [(type_key, data) for type_key in type_keys],
    )


def knot(name: str) -> Data:
    return {"knot": name}


def expr(srepr: str) -> Data:
    return {"expr": srepr}


def matrix_instance(
    rows: list[list[Cell]], type_keys: list[str], description: str | None = None
) -> Instance:
    data = matrix(rows)
    return pmatrix(rows), description, [(type_key, data) for type_key in type_keys]


def instance(
    latex: str, data: Data, type_keys: list[str], description: str | None = None
) -> Instance:
    return latex, description, [(type_key, data) for type_key in type_keys]


CYCLOTOMIC_WIKI = ("Wikipedia", "https://en.wikipedia.org/wiki/Cyclotomic_polynomial")


def oeis(number: str) -> list[tuple[str, str]]:
    return [(f"OEIS {number}", f"https://oeis.org/{number}")]


def lmfdb_field(label: str) -> list[tuple[str, str]]:
    return [(f"LMFDB {label}", f"https://www.lmfdb.org/NumberField/{label}")]


def knot_atlas(name: str) -> list[tuple[str, str]]:
    return [("Knot Atlas", f"https://katlas.org/wiki/{name}")]
