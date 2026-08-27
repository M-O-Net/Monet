import pytest

from monet_api.objects.service import normalize_latex


@pytest.mark.parametrize(
    ("source", "canonical"),
    [
        ("x^{2} - 4 x + 3", "x^{2}-4x+3"),
        ("x^{2}-4x+3", "x^{2}-4x+3"),
        (r"\text{Is Singular}", r"\text{Is Singular}"),
        (r"\text{Is   Singular}", r"\text{Is Singular}"),
        (r"\text{IsSingular}", r"\text{IsSingular}"),
        (r"K_{1} \sqcup K_{1}", r"K_{1}\sqcup K_{1}"),
        (r"K_{1}\sqcup K_{1}", r"K_{1}\sqcup K_{1}"),
        (r"2 \cdot 3", r"2\cdot 3"),
        (r"2\cdot3", r"2\cdot 3"),
        (r"\begin{pmatrix}0 & 1\\1 & 0\end{pmatrix}", r"\begin{pmatrix}0&1\\1&0\end{pmatrix}"),
        ("t^{-2} - t^{-1} + 1", "t^{-2}-t^{-1}+1"),
    ],
)
def test_canonical_spelling(source: str, canonical: str) -> None:
    assert normalize_latex(source) == canonical
    assert normalize_latex(canonical) == canonical


def test_a_control_word_keeps_the_space_that_terminates_it() -> None:
    """Dropping it would leave \\sqcupK, an undefined control word KaTeX refuses to render."""
    assert "sqcup " in normalize_latex(r"C_{4} \sqcup K_{1}")


def test_distinct_names_stay_distinct() -> None:
    assert normalize_latex(r"\text{Is Singular}") != normalize_latex(r"\text{IsSingular}")
