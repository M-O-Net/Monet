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


def _laurent_terms(expression):
    symbols = expression.free_symbols
    if len(symbols) != 1:
        return None
    symbol = next(iter(symbols))
    terms = []
    for term in expression.as_ordered_terms():
        coefficient, exponent = term.as_coeff_exponent(symbol)
        if not (exponent.is_Integer and coefficient.is_Number):
            return None
        terms.append((int(exponent), coefficient))
    if not any(exponent < 0 for exponent, _ in terms):
        return None
    return symbol, sorted(terms, reverse=True)


def _render_laurent(symbol, terms):
    base = sympy.latex(symbol)
    pieces = []
    for position, (exponent, coefficient) in enumerate(terms):
        negative = coefficient.is_negative
        magnitude = -coefficient if negative else coefficient
        if exponent == 0:
            body = sympy.latex(magnitude)
        else:
            power = base if exponent == 1 else f"{base}^{{{exponent}}}"
            body = power if magnitude == 1 else f"{sympy.latex(magnitude)} {power}"
        sign = "-" if negative else "+"
        pieces.append(body if position == 0 and not negative else f"{sign} {body}")
    return " ".join(pieces)


def render(value):
    if isinstance(value, bool) or isinstance(value, sympy.logic.boolalg.BooleanAtom):
        return r"\text{True}" if bool(value) else r"\text{False}"
    if isinstance(value, sympy.MatrixBase):
        return sympy.latex(value, mat_str="pmatrix", mat_delim="")
    expression = sympy.sympify(value)
    laurent = _laurent_terms(sympy.expand(expression))
    if laurent is not None:
        return _render_laurent(*laurent)
    return sympy.latex(expression)


def namespace():
    ns = {name: getattr(sympy, name) for name in sympy.__all__}
    ns["MatrixBase"] = sympy.MatrixBase
    ns["sympy"] = sympy
    ns["parse"] = parse
    ns["render"] = render
    return ns

