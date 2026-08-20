import re

import sympy
from sympy import Matrix
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


def namespace():
    ns = {name: getattr(sympy, name) for name in sympy.__all__}
    ns["MatrixBase"] = sympy.MatrixBase
    ns["sympy"] = sympy
    ns["parse"] = parse
    ns["render"] = render
    return ns

