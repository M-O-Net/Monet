"""The trusted bridge between Monet's LaTeX and sympy.

Shipped with the frontend and run inside the sandbox before any implementation code — deliberately
NOT stored in the `implementations` table, so implementation authors get `parse`/`render` for free and
can't redefine what LaTeX Monet writes.

`render` is the single source of truth for Monet's LaTeX conventions; `scripts/seed.py` is
aligned to whatever it emits, so an implementation run over the seeded dataset lands on the objects
that are already there instead of minting near-duplicates.

sympy.parsing.latex is deliberately unused: it needs antlr or lark, neither of which is in the
Pyodide distribution, and it cannot parse matrix environments anyway.
"""

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
    """Parse a single non-matrix cell or expression."""
    text = latex.strip()
    for macro in ("\\cdot", "\\times"):
        text = text.replace(macro, "*")
    for macro in _STRIP:
        text = text.replace(macro, "")
    if not text.strip():
        raise ValueError("empty expression")
    return parse_expr(text, transformations=_TRANSFORMATIONS)


def parse(latex):
    """LaTeX in, sympy out. Raises if the string isn't something Monet knows how to read."""
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
    """sympy in, LaTeX out — in exactly the form Monet stores."""
    if isinstance(value, bool) or isinstance(value, sympy.logic.boolalg.BooleanAtom):
        return r"\text{True}" if bool(value) else r"\text{False}"
    if isinstance(value, sympy.MatrixBase):
        return sympy.latex(value, mat_str="pmatrix", mat_delim="")
    return sympy.latex(sympy.sympify(value))


def namespace():
    """The globals an implementation is exec'd against: all of sympy, plus parse/render."""
    ns = {name: getattr(sympy, name) for name in sympy.__all__}
    ns["MatrixBase"] = sympy.MatrixBase
    ns["sympy"] = sympy
    ns["parse"] = parse
    ns["render"] = render
    return ns

