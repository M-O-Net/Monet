import cmath
import functools
import math
import re

import sympy
from sympy import Matrix, Symbol
from sympy.combinatorics import Permutation, PermutationGroup
from sympy.combinatorics.fp_groups import FpGroup
from sympy.combinatorics.free_groups import free_group
from sympy.combinatorics.partitions import IntegerPartition
from sympy.holonomic import DifferentialOperators, HolonomicFunction
from sympy.liealgebras.cartan_type import CartanType, Standard_Cartan
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)
from sympy.polys.domains.modularinteger import ModularInteger
from sympy.polys.polyerrors import NotAlgebraic
from sympy.series.sequences import RecursiveSeq, SeqFormula

_TRANSFORMATIONS = (
    *standard_transformations,
    convert_xor,
    implicit_multiplication_application,
)

_MATRIX_ENV = re.compile(r"\\begin\{([pbv]?matrix)\}(.*?)\\end\{\1\}", re.DOTALL)
_BOOLEANS = {r"\text{True}": True, r"\text{False}": False}
_CYCLES = re.compile(r"(?:\\left\(\s*\d+(?:\\;\s*\d+)*\\right\))+")
_RESIDUE = re.compile(r"(\d+) \\bmod (\d+)")

_STRIP = (
    "\\left",
    "\\right",
    "\\,",
    "\\;",
    "\\:",
    "\\!",
    "\\quad",
    "\\qquad",
    "{",
    "}",
)

_X = Symbol("x")
_Y = Symbol("y")
_N = Symbol("n")
_TERM = sympy.Function("a")
_CONSTANTS = {"i": sympy.I, "e": sympy.E}
_REAL_TOLERANCE = 1e-12


def _scalar(latex):
    text = latex.strip()
    for macro in ("\\cdot", "\\times"):
        text = text.replace(macro, "*")
    for macro in _STRIP:
        text = text.replace(macro, "")
    if not text.strip():
        raise ValueError("empty expression")
    return parse_expr(text, local_dict=_CONSTANTS, transformations=_TRANSFORMATIONS)


def parse(latex):
    text = latex.strip()

    if text in _BOOLEANS:
        return _BOOLEANS[text]

    if _CYCLES.fullmatch(text):
        cycles = [[int(point) for point in re.findall(r"\d+", cycle)] for cycle in text.split(r"\right)")[:-1]]
        return Permutation(cycles, size=max(max(cycle) for cycle in cycles) + 1)

    match = _RESIDUE.fullmatch(text)
    if match:
        return residue(int(match.group(1)), int(match.group(2)))

    match = _MATRIX_ENV.search(text)
    if match:
        rows = []
        for row in re.split(r"\\\\", match.group(2)):
            if not row.strip():
                continue
            rows.append([_scalar(cell) for cell in row.split("&")])
        if not rows:
            raise ValueError("empty matrix")
        return Matrix(rows)

    if text.count("=") == 1:
        lhs, rhs = text.split("=")
        return sympy.Eq(_scalar(lhs), _scalar(rhs))

    return _scalar(text)


class Tableau:
    def __init__(self, rows):
        self.rows = tuple(tuple(int(cell) for cell in row) for row in rows)

    def __eq__(self, other):
        return isinstance(other, Tableau) and self.rows == other.rows

    def __hash__(self):
        return hash(self.rows)

    def __repr__(self):
        return f"Tableau({[list(row) for row in self.rows]})"

    @property
    def shape(self):
        return IntegerPartition([len(row) for row in self.rows])


def residue(a, n):
    return sympy.FF(n, symmetric=False)(a)


_JS_SAFE_INTEGER = 2**53


def _json_int(n):
    return n if abs(n) < _JS_SAFE_INTEGER else str(n)


def _polynomial_data(value):
    symbols = value.free_symbols
    if len(symbols) != 1:
        return None
    (var,) = symbols
    if not value.is_polynomial(var):
        return None
    poly = sympy.Poly(value, var)
    coeffs = poly.all_coeffs()[::-1]
    if poly.degree() < 1 or not all(c.is_Rational for c in coeffs):
        return None
    return {
        "poly": {
            "var": str(var),
            "degree": poly.degree(),
            "coeffs": {str(power): to_data(c) for power, c in enumerate(coeffs)},
        }
    }


def _isolates(root, point):
    if not isinstance(root, sympy.CRootOf):
        return abs(complex(root) - point) <= _REAL_TOLERANCE * max(1.0, abs(point))
    box = root._get_interval()
    if root.is_real:
        return abs(point.imag) < _REAL_TOLERANCE and float(box.a) <= point.real <= float(box.b)
    return float(box.ax) <= point.real <= float(box.bx) and float(box.ay) <= point.imag <= float(box.by)


def _nearest(points, root):
    inside = [key for key, point in points.items() if _isolates(root, point)]
    if len(inside) == 1:
        return inside[0]
    approximate = complex(root.evalf(15))
    return min(points, key=lambda key: abs(points[key] - approximate))


def _algebraic_data(value):
    try:
        minpoly = sympy.Poly(sympy.minimal_polynomial(value, _X), _X)
    except (NotAlgebraic, NotImplementedError):
        return None
    point = complex(sympy.N(value, 20))
    roots = minpoly.all_roots(radicals=False)
    inside = [k for k, root in enumerate(roots) if _isolates(root, point)]
    if len(inside) != 1:
        inside = [min(range(len(roots)), key=lambda k: abs(complex(roots[k].evalf(15)) - point))]
    return {"algebraic": {"minpoly": to_data(minpoly.as_expr()), "root": inside[0]}}


def _algebraic_value(payload):
    minpoly = sympy.Poly(from_data(payload["minpoly"]), _X)
    root = sympy.rootof(minpoly, int(payload["root"]), radicals=True)
    if not isinstance(root, sympy.CRootOf) or not minpoly.is_cyclotomic:
        return root
    order = next(
        k for k in range(1, 2 * minpoly.degree() ** 2 + 3) if sympy.Poly(sympy.cyclotomic_poly(k, _X), _X) == minpoly
    )
    powers = {j: cmath.exp(2j * cmath.pi * j / order) for j in range(1, order) if math.gcd(j, order) == 1}
    return sympy.exp(2 * sympy.pi * sympy.I * sympy.Rational(_nearest(powers, root), order))


def _primitive(coefficients, var):
    exprs = [sympy.cancel(sympy.sympify(c)) for c in coefficients]
    denominator = sympy.lcm([sympy.fraction(e)[1] for e in exprs])
    polys = [sympy.Poly(sympy.cancel(e * denominator), var, domain="QQ") for e in exprs]
    common = functools.reduce(sympy.gcd, [p for p in polys if not p.is_zero])
    polys = [p.exquo(common) for p in polys]
    numbers = [c for p in polys for c in p.coeffs()]
    scale = sympy.lcm([sympy.Rational(c).q for c in numbers]) / sympy.gcd([sympy.Rational(c).p for c in numbers])
    if polys[-1].LC() < 0:
        scale = -scale
    return [(p * scale).as_expr() for p in polys]


def _linear_recurrence_data(seq):
    if seq.start != 0:
        return None
    order = len(seq.initial)
    n = seq.n
    rhs = seq.recurrence.rhs
    earlier = [seq.y(n - i) for i in range(1, order + 1)]
    weights = [sympy.cancel(rhs.diff(term)) for term in earlier]
    if any(w.has(*earlier) for w in weights):
        return None
    if sympy.cancel(rhs - sum(w * t for w, t in zip(weights, earlier, strict=True))) != 0:
        return None
    ahead = [-w.subs(n, _N + order) for w in reversed(weights)]
    coeffs = _primitive([*ahead, sympy.Integer(1)], _N)
    if all(not c.free_symbols for c in coeffs):
        found = seq.find_linear_recurrence(2 * order)
        weights = found or [-c / coeffs[-1] for c in reversed(coeffs[:-1])]
        return {
            "recurrence": {
                "coeffs": [to_data(w) for w in weights],
                "initial": [to_data(t) for t in seq[: len(weights)]],
            }
        }
    return {
        "holonomic": {
            "coeffs": [to_data(c) for c in coeffs],
            "initial": [to_data(v) for v in seq.initial],
        }
    }


def _recursive_value(weights, initial):
    shifted = sum(w * _TERM(_N - i) for i, w in enumerate(weights, start=1))
    return RecursiveSeq(shifted, _TERM(_N), _N, initial)


def _recurrence_value(payload):
    return _recursive_value([from_data(c) for c in payload["coeffs"]], [from_data(v) for v in payload["initial"]])


def _holonomic_value(payload):
    coeffs = [from_data(c) for c in payload["coeffs"]]
    order = len(coeffs) - 1
    back = [sympy.sympify(c).subs(_N, _N - order) for c in coeffs]
    weights = [sympy.cancel(-back[order - i] / back[order]) for i in range(1, order + 1)]
    return _recursive_value(weights, [from_data(v) for v in payload["initial"]])


def _dfinite_data(function):
    if not isinstance(function.y0, list):
        return None
    base = function.annihilator.parent.base
    coeffs = [base.to_sympy(p).subs(function.x, _X) for p in function.annihilator.listofpoly]
    return {
        "dfinite": {
            "coeffs": [to_data(c) for c in _primitive(coeffs, _X)],
            "point": to_data(function.x0),
            "initial": [to_data(v) for v in function.y0],
        }
    }


def _dfinite_value(payload):
    _, dx = DifferentialOperators(sympy.QQ.old_poly_ring(_X), "Dx")
    operator = sum(from_data(c) * dx**i for i, c in enumerate(payload["coeffs"]))
    return HolonomicFunction(operator, _X, from_data(payload["point"]), [from_data(v) for v in payload["initial"]])


def _seq_data(seq):
    if seq.stop != sympy.oo:
        return None
    (var,) = seq.variables
    return {"seq": {"var": str(var), "start": _json_int(int(seq.start)), "formula": sympy.srepr(seq.formula)}}


def _seq_value(payload):
    return SeqFormula(sympy.sympify(payload["formula"]), (Symbol(payload["var"]), int(payload["start"]), sympy.oo))


def _curve_data(equation):
    difference = sympy.expand(equation.lhs - equation.rhs)
    if difference.free_symbols != {_X, _Y} or not difference.is_polynomial(_X, _Y):
        return None
    _, poly = sympy.Poly(difference, _X, _Y).clear_denoms()
    _, poly = poly.primitive()
    if poly.LC() < 0:
        poly = -poly
    return {"curve": sympy.srepr(poly.as_expr())}


def _curve_value(payload):
    poly = sympy.Poly(sympy.sympify(payload), _X, _Y)
    in_y = sympy.Poly(poly.as_expr(), _Y)
    weierstrass = (
        in_y.degree() == 2
        and not in_y.coeff_monomial(_Y**2).free_symbols
        and sympy.degree(in_y.coeff_monomial(_Y), _X) <= 1
        and sympy.degree(in_y.coeff_monomial(1), _X) == 3
    )
    if weierstrass:
        sign = sympy.sign(in_y.coeff_monomial(_Y**2))
        free = in_y.coeff_monomial(1)
        return sympy.Eq(sympy.expand(sign * (poly.as_expr() - free)), sympy.expand(-sign * free))
    constant = poly.coeff_monomial(1)
    return sympy.Eq(poly.as_expr() - constant, -constant)


def _polytope_data(polygon):
    return {"polytope": [[to_data(c) for c in point] for point in sorted(polygon.vertices, key=tuple)]}


def _polytope_value(payload):
    if any(len(point) != 2 for point in payload):
        raise LookupError("no sympy value for a polytope beyond the plane")
    return sympy.convex_hull(*(sympy.Point(*(from_data(c) for c in point)) for point in payload))


def _permgroup_data(group):
    return {
        "permgroup": {
            "degree": group.degree,
            "generators": [list(g.array_form) for g in group.generators],
        }
    }


def _permgroup_value(payload):
    return PermutationGroup([Permutation(g, size=payload["degree"]) for g in payload["generators"]])


def _fpgroup_data(group):
    return {
        "fpgroup": {
            "generators": [str(s) for s in group.free_group.symbols],
            "relators": [[[str(s), e] for s, e in r.array_form] for r in group.relators],
        }
    }


def _fpgroup_value(payload):
    free, *generators = free_group(", ".join(payload["generators"]))
    named = dict(zip(payload["generators"], generators, strict=True))
    relators = [
        functools.reduce(lambda word, letter: word * named[letter[0]] ** letter[1], r, free.identity)
        for r in payload["relators"]
    ]
    return FpGroup(free, relators)


_AS_DATA = (
    (ModularInteger, lambda r: {"residue": [_json_int(int(r.val) % r.mod), _json_int(r.mod)]}),
    (Tableau, lambda t: {"tableau": [list(row) for row in t.rows]}),
    (Permutation, lambda p: {"perm": list(p.array_form)}),
    (IntegerPartition, lambda p: {"partition": [int(part) for part in p.partition]}),
    (PermutationGroup, _permgroup_data),
    (FpGroup, _fpgroup_data),
    (HolonomicFunction, _dfinite_data),
    (Standard_Cartan, lambda c: {"cartan": [c.series, int(c.n)]}),
    (sympy.Tuple, lambda t: {"tuple": [to_data(e) for e in t]}),
    (SeqFormula, _seq_data),
    (RecursiveSeq, _linear_recurrence_data),
    (sympy.Polygon, _polytope_data),
    (sympy.Equality, _curve_data),
)


def to_data(value):
    if isinstance(value, bool) or isinstance(value, sympy.logic.boolalg.BooleanAtom):
        return {"bool": bool(value)}
    if isinstance(value, sympy.MatrixBase):
        return {"matrix": [[to_data(value[i, j]) for j in range(value.cols)] for i in range(value.rows)]}
    for structured, as_data in _AS_DATA:
        if isinstance(value, structured):
            data = as_data(value)
            if data is not None:
                return data
    value = sympy.sympify(value)
    if value.is_Integer:
        return {"int": _json_int(int(value))}
    if value.is_Rational:
        return {"rational": [_json_int(int(value.p)), _json_int(int(value.q))]}
    if value.is_number and value.is_algebraic:
        data = _algebraic_data(value)
        if data is not None:
            return data
    if isinstance(value, sympy.Expr):
        data = _polynomial_data(value)
        if data is not None:
            return data
    return {"expr": sympy.srepr(value)}


_FROM_DATA = {
    "bool": lambda payload: payload,
    "int": lambda payload: sympy.Integer(int(payload)),
    "rational": lambda payload: sympy.Rational(int(payload[0]), int(payload[1])),
    "matrix": lambda payload: Matrix([[from_data(cell) for cell in row] for row in payload]),
    "poly": lambda payload: sympy.Add(
        *(from_data(c) * Symbol(payload["var"]) ** int(power) for power, c in payload["coeffs"].items())
    ),
    "expr": sympy.sympify,
    "residue": lambda payload: residue(int(payload[0]), int(payload[1])),
    "algebraic": _algebraic_value,
    "tuple": lambda payload: sympy.Tuple(*(from_data(e) for e in payload)),
    "seq": _seq_value,
    "recurrence": _recurrence_value,
    "holonomic": _holonomic_value,
    "dfinite": _dfinite_value,
    "perm": Permutation,
    "partition": IntegerPartition,
    "tableau": Tableau,
    "permgroup": _permgroup_value,
    "fpgroup": _fpgroup_value,
    "cartan": lambda payload: CartanType([payload[0], int(payload[1])]),
    "curve": _curve_value,
    "polytope": _polytope_value,
}


def from_data(data):
    ((kind, payload),) = data.items()
    if kind not in _FROM_DATA:
        raise LookupError(f"no sympy value for {kind}")
    return _FROM_DATA[kind](payload)


def _latex_of(data):
    return sympy.latex(from_data(data))


def _combination(terms):
    pieces = []
    for coefficient, thing in terms:
        coefficient = sympy.sympify(coefficient)
        if coefficient == 0:
            continue
        negative = coefficient.could_extract_minus_sign()
        size = sympy.factor(-coefficient if negative else coefficient)
        if size == 1:
            piece = thing
        elif size.is_Add:
            piece = rf"\left({sympy.latex(size)}\right) {thing}"
        else:
            piece = f"{sympy.latex(size)} {thing}"
        if not pieces:
            pieces.append(f"- {piece}" if negative else piece)
        else:
            pieces.append(f"{'-' if negative else '+'} {piece}")
    return " ".join(pieces) if pieces else "0"


def _term(shift):
    return f"a_{{{sympy.latex(_N + shift)}}}"


def _initial_values(initial):
    return ", ".join(f"a_{{{k}}} = {_latex_of(v)}" for k, v in enumerate(initial))


def _recurrence_latex(payload):
    terms = [(from_data(c), _term(-i)) for i, c in enumerate(payload["coeffs"], start=1)]
    return rf"a_{{n}} = {_combination(terms)}, \quad {_initial_values(payload['initial'])}"


def _holonomic_latex(payload):
    terms = [(from_data(c), _term(i)) for i, c in reversed(list(enumerate(payload["coeffs"])))]
    return rf"{_combination(terms)} = 0, \quad {_initial_values(payload['initial'])}"


def _derivative(order):
    return "y" + ("'" * order if order < 4 else f"^{{({order})}}")


def _dfinite_latex(payload):
    terms = [(from_data(c), _derivative(i)) for i, c in reversed(list(enumerate(payload["coeffs"])))]
    point = _latex_of(payload["point"])
    initial = ", ".join(f"{_derivative(k)}({point}) = {_latex_of(v)}" for k, v in enumerate(payload["initial"]))
    return rf"{_combination(terms)} = 0, \quad {initial}"


def _seq_latex(payload):
    formula = sympy.latex(sympy.sympify(payload["formula"]))
    return rf"\left({formula}\right)_{{{payload['var']} \geq {payload['start']}}}"


def _word_latex(word):
    return " ".join(letter if exponent == 1 else f"{letter}^{{{exponent}}}" for letter, exponent in word)


def _fpgroup_latex(payload):
    relators = ", ".join(_word_latex(r) for r in payload["relators"])
    return rf"\left\langle {', '.join(payload['generators'])} \mid {relators} \right\rangle"


def _permgroup_latex(payload):
    generators = ", ".join(sympy.latex(Permutation(g, size=payload["degree"])) for g in payload["generators"])
    return rf"\left\langle {generators} \right\rangle"


_LIE_ALGEBRAS = {
    "A": lambda n: (r"\mathfrak{sl}", n + 1),
    "B": lambda n: (r"\mathfrak{so}", 2 * n + 1),
    "C": lambda n: (r"\mathfrak{sp}", 2 * n),
    "D": lambda n: (r"\mathfrak{so}", 2 * n),
    "E": lambda n: (r"\mathfrak{e}", n),
    "F": lambda n: (r"\mathfrak{f}", n),
    "G": lambda n: (r"\mathfrak{g}", n),
}


def _cartan_latex(payload):
    name, index = _LIE_ALGEBRAS[payload[0]](int(payload[1]))
    return f"{name}_{{{index}}}"


def _tableau_latex(payload):
    rows = r" \\ ".join(" & ".join(str(cell) for cell in row) for row in payload)
    return rf"\begin{{array}}{{{'l' * len(payload[0])}}}{rows}\end{{array}}"


def _polytope_latex(payload):
    points = ", ".join(r"\left(" + ", ".join(_latex_of(c) for c in point) + r"\right)" for point in payload)
    return rf"\operatorname{{conv}}\left\{{{points}\right\}}"


_LATEX_OF = {
    "residue": lambda payload: rf"{payload[0]} \bmod {payload[1]}",
    "partition": lambda payload: rf"\left({', '.join(map(str, payload))}\right) \vdash {sum(payload)}",
    "tableau": _tableau_latex,
    "recurrence": _recurrence_latex,
    "holonomic": _holonomic_latex,
    "dfinite": _dfinite_latex,
    "seq": _seq_latex,
    "permgroup": _permgroup_latex,
    "fpgroup": _fpgroup_latex,
    "cartan": _cartan_latex,
    "polytope": _polytope_latex,
}

_RENDERED_FROM_DATA = (
    ModularInteger,
    Tableau,
    IntegerPartition,
    PermutationGroup,
    FpGroup,
    HolonomicFunction,
    Standard_Cartan,
    SeqFormula,
    RecursiveSeq,
    sympy.Polygon,
)


def render(value):
    if isinstance(value, bool) or isinstance(value, sympy.logic.boolalg.BooleanAtom):
        return r"\text{True}" if bool(value) else r"\text{False}"
    if isinstance(value, sympy.MatrixBase):
        return sympy.latex(value, mat_str="pmatrix", mat_delim="")
    if isinstance(value, _RENDERED_FROM_DATA):
        ((kind, payload),) = to_data(value).items()
        if kind in _LATEX_OF:
            return _LATEX_OF[kind](payload)
    return sympy.latex(sympy.sympify(value))


def namespace():
    ns = {name: getattr(sympy, name) for name in sympy.__all__}
    ns["MatrixBase"] = sympy.MatrixBase
    ns["sympy"] = sympy
    ns["parse"] = parse
    ns["render"] = render
    ns["to_data"] = to_data
    ns["from_data"] = from_data
    ns["Permutation"] = Permutation
    ns["PermutationGroup"] = PermutationGroup
    ns["IntegerPartition"] = IntegerPartition
    ns["Tableau"] = Tableau
    ns["residue"] = residue
    ns["ModularInteger"] = ModularInteger
    ns["RecursiveSeq"] = RecursiveSeq
    ns["HolonomicFunction"] = HolonomicFunction
    ns["DifferentialOperators"] = DifferentialOperators
    ns["FpGroup"] = FpGroup
    ns["free_group"] = free_group
    ns["CartanType"] = CartanType
    return ns
