import re

import sympy
from sympy import Matrix, Symbol
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

_TRANSFORMATIONS = (
    *standard_transformations,
    convert_xor,
    implicit_multiplication_application,
)

_MATRIX_ENV = re.compile(r"\\begin\{([pbv]?matrix)\}(.*?)\\end\{\1\}", re.DOTALL)
_BOOLEANS = {r"\text{True}": True, r"\text{False}": False}

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


def _scalar(latex):
    text = latex.strip()
    for macro in ("\\cdot", "\\times"):
        text = text.replace(macro, "*")
    for macro in _STRIP:
        text = text.replace(macro, "")
    if not text.strip():
        raise ValueError("empty expression")
    return parse_expr(text, transformations=_TRANSFORMATIONS)


def parse(latex):
    text = latex.strip()

    if text in _BOOLEANS:
        return _BOOLEANS[text]

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

    return _scalar(text)


def render(value):
    if isinstance(value, bool) or isinstance(value, sympy.logic.boolalg.BooleanAtom):
        return r"\text{True}" if bool(value) else r"\text{False}"
    if isinstance(value, sympy.MatrixBase):
        return sympy.latex(value, mat_str="pmatrix", mat_delim="")
    return sympy.latex(sympy.sympify(value))


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


def to_data(value):
    if isinstance(value, bool) or isinstance(value, sympy.logic.boolalg.BooleanAtom):
        return {"bool": bool(value)}
    if isinstance(value, sympy.MatrixBase):
        return {"matrix": [[to_data(value[i, j]) for j in range(value.cols)] for i in range(value.rows)]}
    value = sympy.sympify(value)
    if value.is_Integer:
        return {"int": _json_int(int(value))}
    if value.is_Rational:
        return {"rational": [_json_int(int(value.p)), _json_int(int(value.q))]}
    return _polynomial_data(value) or {"expr": sympy.srepr(value)}


def from_data(data):
    ((kind, payload),) = data.items()
    if kind == "bool":
        return payload
    if kind == "int":
        return sympy.Integer(int(payload))
    if kind == "rational":
        return sympy.Rational(int(payload[0]), int(payload[1]))
    if kind == "matrix":
        return Matrix([[from_data(cell) for cell in row] for row in payload])
    if kind == "poly":
        var = Symbol(payload["var"])
        return sympy.Add(*(from_data(c) * var ** int(power) for power, c in payload["coeffs"].items()))
    if kind == "expr":
        return sympy.sympify(payload)
    raise LookupError(f"no sympy value for {kind}")


def namespace():
    ns = {name: getattr(sympy, name) for name in sympy.__all__}
    ns["MatrixBase"] = sympy.MatrixBase
    ns["sympy"] = sympy
    ns["parse"] = parse
    ns["render"] = render
    ns["to_data"] = to_data
    ns["from_data"] = from_data
    return ns

