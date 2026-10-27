"""Seed the demo dataset: objects, relations, and an implementation per operator.

Wipes and reinserts, so it's safe to re-run — `uv run python scripts/seed.py` from apps/api/,
or `just seed`, always resets to exactly this dataset. Pass --if-empty to skip entirely when
the objects table already has rows (used by docker-compose.dev.yml's startup command, so a
fresh `just up` always has demo data without clobbering anything you've since added by hand
through the GUI on every restart).
"""

import asyncio
import pathlib
import sys
import uuid
from typing import Any

from sqlmodel import delete, func, select

from monet_api.comments.models import Comment
from monet_api.core.db import async_session
from monet_api.events.models import Event
from monet_api.implementations.models import Implementation
from monet_api.objects.models import (
    Membership,
    Object,
    ObjectReference,
    OperatorDisplay,
    Relation,
    RelationInput,
    RelationOutput,
    SectionFiling,
    Signature,
    Subtype,
    TopLevelObject,
    Type,
)

Data = dict[str, Any]


def integer(n: int) -> Data:
    return {"int": n}


def matrix(rows: list[list[int]]) -> Data:
    return {"matrix": [[integer(cell) for cell in row] for row in rows]}


def polynomial(*coeffs_from_constant: int) -> Data:
    return {
        "poly": {
            "var": "x",
            "degree": len(coeffs_from_constant) - 1,
            "coeffs": {str(power): integer(c) for power, c in enumerate(coeffs_from_constant)},
        }
    }


def seifert(size: int) -> Data:
    return matrix(
        [[-1 if i == j else 1 if j == i + 1 else 0 for j in range(size)] for i in range(size)]
    )


async def seed() -> None:
    async with async_session() as session:
        if "--if-empty" in sys.argv:
            count = (await session.exec(select(func.count()).select_from(Object))).one()
            if count > 0:
                print(f"objects table already has {count} rows, skipping (--if-empty)")
                return

        await session.exec(delete(Event))
        await session.exec(delete(Comment))
        await session.exec(delete(Implementation))
        await session.exec(delete(ObjectReference))
        await session.exec(delete(OperatorDisplay))
        await session.exec(delete(TopLevelObject))
        await session.exec(delete(RelationOutput))
        await session.exec(delete(RelationInput))
        await session.exec(delete(Relation))
        await session.exec(delete(Object))
        await session.commit()

        Specimen = tuple[str, str | None]

        section_objects: dict[str, Specimen] = {
            "MathematicalObjects": (
                r"\text{Mathematical Objects}",
                "Every kind of object Monet catalogues. Each type sits somewhere beneath it.",
            ),
            "LinearAlgebra": (
                r"\text{Linear Algebra}",
                "Matrices and the operations that act on them.",
            ),
            "PolynomialAlgebra": (
                r"\text{Polynomial Algebra}",
                "Single-variable polynomials and the operations that act on them.",
            ),
            "Values": (
                r"\text{Values}",
                "The plain numbers and truth values that relations produce as answers.",
            ),
            "Matrices": (r"\text{Matrices}", "Square arrays of numbers."),
            "SymmetricMatrices": (
                r"\text{Symmetric Matrices}",
                "Matrices equal to their own transpose.",
            ),
            "MatrixOperations": (
                r"\text{Matrix Operations}",
                "Operations taking matrices as "
                "their input: characteristic polynomials, inverses, "
                "determinants, sums.",
            ),
            "Polynomials": (r"\text{Polynomials}", "Single-variable polynomials."),
            "CyclotomicPolynomials": (
                r"\text{Cyclotomic Polynomials}",
                "The minimal polynomials of the primitive roots of unity.",
            ),
            "PolynomialOperations": (
                r"\text{Polynomial Operations}",
                "Operations taking polynomials as their input: companion matrices, degree.",
            ),
            "Integers": (
                r"\text{Integers}",
                "Whole numbers, positive and negative — the "
                "values relations like Determinant and Degree produce.",
            ),
            "Booleans": (
                r"\text{Booleans}",
                "The two truth values a predicate-style relation, like Is Singular, produces.",
            ),
            "KnotTheory": (
                r"\text{Knot Theory}",
                "Knots, and the matrices and polynomials that identify them.",
            ),
            "Knots": (r"\text{Knots}", "Specific knots, named the standard way."),
            "RationalNumbers": (r"\text{Rational Numbers}", "Fractions of integers."),
            "Expressions": (
                r"\text{Symbolic Expressions}",
                "Exact values no narrower type holds yet, such as square roots.",
            ),
            "RealFunctions": (
                r"\text{Real Functions}",
                "Functions from the real numbers to the real numbers.",
            ),
            "TorusKnots": (
                r"\text{Torus Knots}",
                "Knots that lie on the surface of an unknotted torus.",
            ),
            "KnotOperations": (
                r"\text{Knot Operations}",
                "Operations taking a knot or its Seifert matrix as input: Seifert matrices, "
                "Alexander polynomials.",
            ),
            "NumberOperations": (
                r"\text{Number Operations}",
                "Operations taking a whole number as input.",
            ),
        }

        matrices: dict[str, Specimen] = {
            "A": (r"\begin{pmatrix}2&1\\1&2\end{pmatrix}", None),
            "B": (r"\begin{pmatrix}1&0\\0&1\end{pmatrix}", None),
            "D": (r"\begin{pmatrix}0&1\\1&0\end{pmatrix}", None),
            "E": (r"\begin{pmatrix}3&1\\1&3\end{pmatrix}", None),
            "C": (
                r"\begin{pmatrix}0&-3\\1&4\end{pmatrix}",
                "The companion matrix of "
                r"$x^{2} - 4 x + 3$ — its own characteristic polynomial closes the loop.",
            ),
            "V3": (
                r"\begin{pmatrix}-1&1\\0&-1\end{pmatrix}",
                "The Seifert matrix of the trefoil.",
            ),
            "V5": (
                r"\begin{pmatrix}-1&1&0&0\\0&-1&1&0\\0&0&-1&1\\0&0&0&-1\end{pmatrix}",
                r"The Seifert matrix of $5_1$.",
            ),
            "V7": (
                r"\begin{pmatrix}-1&1&0&0&0&0\\0&-1&1&0&0&0\\0&0&-1&1&0&0"
                r"\\0&0&0&-1&1&0\\0&0&0&0&-1&1\\0&0&0&0&0&-1\end{pmatrix}",
                r"The Seifert matrix of $7_1$.",
            ),
            "S": (
                r"\begin{pmatrix}1&2\\2&4\end{pmatrix}",
                "Singular: its rows are proportional, so it collapses the plane onto a line.",
            ),
            "CompPhi6": (
                r"\begin{pmatrix}0&-1\\1&1\end{pmatrix}",
                r"The companion matrix of $x^{2} - x + 1$ — the trefoil's polynomial, "
                "back in linear algebra.",
            ),
        }

        polynomials: dict[str, Specimen] = {
            # Spelled the way sandbox/prelude.py's render() emits it, so a computed
            # characteristic polynomial lands here instead of minting a near-identical twin.
            "P": (r"x^{2} - 4 x + 3", None),
            "Q": (r"x^{2} - 2 x + 1", None),
            "R": (r"x^{2} - 1", None),
            "Phi6": (
                r"x^{2} - x + 1",
                "The 6th cyclotomic polynomial — and the Alexander polynomial of the trefoil.",
            ),
            "Phi10": (
                r"x^{4} - x^{3} + x^{2} - x + 1",
                r"The 10th cyclotomic polynomial — and the Alexander polynomial of $5_1$.",
            ),
            "Phi14": (
                r"x^{6} - x^{5} + x^{4} - x^{3} + x^{2} - x + 1",
                r"The 14th cyclotomic polynomial — and the Alexander polynomial of $7_1$.",
            ),
        }

        integers: dict[str, Specimen] = {
            "zero": ("0", None),
            "one": ("1", None),
            "neg_one": ("-1", None),
            "two": ("2", None),
            "three": ("3", None),
            "four": ("4", None),
            "five": ("5", None),
            "six": ("6", None),
            "seven": ("7", None),
            "ten": ("10", None),
            "fourteen": ("14", None),
        }

        booleans: dict[str, Specimen] = {
            "true": (r"\text{True}", None),
            "false": (r"\text{False}", None),
        }

        # \mathrm{} stops sympy reading these as the integers 31, 51 and 71.
        knots: dict[str, Specimen] = {
            "K3": (r"\mathrm{3}_{1}", "The trefoil — the simplest knot that cannot be untied."),
            "K5": (r"\mathrm{5}_{1}", "The (2, 5) torus knot: two strands, five crossings."),
            "K7": (r"\mathrm{7}_{1}", "The (2, 7) torus knot: two strands, seven crossings."),
        }

        knot_operators: dict[str, Specimen] = {
            "SeifertMatrix": (
                r"\text{Seifert Matrix}",
                "For a knot, the integer matrix recording how a surface spanning it twists. "
                "Asserted rather than computed: it depends on a choice of surface.",
            ),
            "KnotDeterminant": (
                r"\text{Knot Determinant}",
                r"For a Seifert matrix $V$, the value $|\det(V + V^{T})|$. For the $(2, n)$ "
                r"torus knots seeded here it comes out as $n$ itself.",
            ),
            "AlexanderPolynomial": (
                r"\text{Alexander Polynomial}",
                r"For a Seifert matrix $V$, the polynomial $\det(V - xV^{T})$.",
            ),
        }

        matrix_operators: dict[str, Specimen] = {
            "CharacteristicPolynomial": (
                r"\text{Characteristic Polynomial}",
                "For a matrix A, the polynomial det(xI - A).",
            ),
            "Inverse": (
                r"\text{Inverse}",
                "The multiplicative inverse of a matrix, when one exists.",
            ),
            "Determinant": (r"\text{Determinant}", "The scalar determinant of a matrix."),
            "Add": (r"\text{Add}", "The entrywise sum of two matrices of the same shape."),
            "MatrixOrder": (
                r"\text{Matrix Order}",
                "How many times a matrix must be multiplied by itself to reach the identity. "
                "Only some matrices ever get there.",
            ),
            "Eigenvalues": (
                r"\text{Eigenvalues}",
                "The values a matrix merely scales its eigenvectors by, one output each.",
            ),
            "IsSingular": (r"\text{Is Singular}", "Whether a matrix's determinant is zero."),
        }

        polynomial_operators: dict[str, Specimen] = {
            "CompanionMatrix": (
                r"\text{Companion Matrix}",
                "For a monic polynomial, the "
                "matrix whose characteristic polynomial is that polynomial.",
            ),
            "Degree": (r"\text{Degree}", "The highest power of the variable in a polynomial."),
            "Roots": (
                r"\text{Roots}",
                "Every value at which a polynomial vanishes, one output each.",
            ),
            "CyclotomicPolynomial": (
                r"\text{Cyclotomic Polynomial}",
                r"For $n$, the monic factor of $x^{n} - 1$ whose roots are exactly the "
                r"primitive $n$th roots of unity.",
            ),
        }

        number_operators: dict[str, Specimen] = {
            "EulerTotient": (
                r"\text{Euler Totient}",
                r"How many of $1 \dots n$ share no factor with $n$. It is also the degree of "
                r"the $n$th cyclotomic polynomial.",
            ),
        }

        objects: dict[str, Specimen] = {
            **section_objects,
            **matrices,
            **polynomials,
            **integers,
            **booleans,
            **knots,
            **matrix_operators,
            **polynomial_operators,
            **knot_operators,
            **number_operators,
        }

        types: dict[str, str | None] = {
            "MathematicalObjects": None,
            "Matrices": "matrix",
            "SymmetricMatrices": "matrix",
            "Polynomials": "poly",
            "CyclotomicPolynomials": "poly",
            "RationalNumbers": "rational",
            "Integers": "int",
            "Booleans": "bool",
            "Knots": "knot",
            "TorusKnots": "knot",
            "Expressions": "expr",
            "RealFunctions": None,
        }

        most_specific_type = {
            **dict.fromkeys(["A", "B", "D", "E", "S"], "SymmetricMatrices"),
            **dict.fromkeys(["C", "V3", "V5", "V7", "CompPhi6"], "Matrices"),
            **dict.fromkeys(["P", "Q", "R"], "Polynomials"),
            **dict.fromkeys(["Phi6", "Phi10", "Phi14"], "CyclotomicPolynomials"),
            **dict.fromkeys(integers, "Integers"),
            **dict.fromkeys(booleans, "Booleans"),
            **dict.fromkeys(knots, "TorusKnots"),
        }
        also_functions = ["P", "Phi6"]

        data: dict[str, Data] = {
            "A": matrix([[2, 1], [1, 2]]),
            "B": matrix([[1, 0], [0, 1]]),
            "D": matrix([[0, 1], [1, 0]]),
            "E": matrix([[3, 1], [1, 3]]),
            "C": matrix([[0, -3], [1, 4]]),
            "V3": seifert(2),
            "V5": seifert(4),
            "V7": seifert(6),
            "S": matrix([[1, 2], [2, 4]]),
            "CompPhi6": matrix([[0, -1], [1, 1]]),
            "P": polynomial(3, -4, 1),
            "Q": polynomial(1, -2, 1),
            "R": polynomial(-1, 0, 1),
            "Phi6": polynomial(1, -1, 1),
            "Phi10": polynomial(1, -1, 1, -1, 1),
            "Phi14": polynomial(1, -1, 1, -1, 1, -1, 1),
            "zero": integer(0),
            "one": integer(1),
            "neg_one": integer(-1),
            "two": integer(2),
            "three": integer(3),
            "four": integer(4),
            "five": integer(5),
            "six": integer(6),
            "seven": integer(7),
            "ten": integer(10),
            "fourteen": integer(14),
            "true": {"bool": True},
            "false": {"bool": False},
            "K3": {"knot": "3_1"},
            "K5": {"knot": "5_1"},
            "K7": {"knot": "7_1"},
        }

        images: dict[str, str] = {
            "K3": "/knots/2-3.svg",
            "K5": "/knots/2-5.svg",
            "K7": "/knots/2-7.svg",
        }

        oeis = ("OEIS A013595", "https://oeis.org/A013595")
        cyclotomic_wiki = ("Wikipedia", "https://en.wikipedia.org/wiki/Cyclotomic_polynomial")

        references: dict[str, list[tuple[str, str]]] = {
            "K3": [
                ("Knot Atlas", "https://katlas.org/wiki/3_1"),
                ("Wikipedia", "https://en.wikipedia.org/wiki/Trefoil_knot"),
            ],
            "K5": [
                ("Knot Atlas", "https://katlas.org/wiki/5_1"),
                ("Wikipedia", "https://en.wikipedia.org/wiki/Cinquefoil_knot"),
            ],
            "K7": [
                ("Knot Atlas", "https://katlas.org/wiki/7_1"),
                ("Wikipedia", "https://en.wikipedia.org/wiki/7_1_knot"),
            ],
            # LMFDB names the last two by Q(zeta_5) and Q(zeta_7): Q(zeta_2m) = Q(zeta_m) for odd
            # m, so they are the same fields under a different name. Each page's defining
            # polynomial is exactly the object it is filed under here.
            "Phi6": [
                ("LMFDB 2.0.3.1", "https://www.lmfdb.org/NumberField/2.0.3.1"),
                oeis,
                cyclotomic_wiki,
            ],
            "Phi10": [
                ("LMFDB 4.0.125.1", "https://www.lmfdb.org/NumberField/4.0.125.1"),
                oeis,
                cyclotomic_wiki,
            ],
            "Phi14": [
                ("LMFDB 6.0.16807.1", "https://www.lmfdb.org/NumberField/6.0.16807.1"),
                oeis,
                cyclotomic_wiki,
            ],
            "SeifertMatrix": [("Wikipedia", "https://en.wikipedia.org/wiki/Seifert_surface")],
            "AlexanderPolynomial": [
                ("Wikipedia", "https://en.wikipedia.org/wiki/Alexander_polynomial")
            ],
            "CyclotomicPolynomial": [cyclotomic_wiki],
        }

        ids: dict[str, uuid.UUID] = {}
        for key, (latex, description) in objects.items():
            obj = Object(latex=latex, description=description, image_url=images.get(key))
            session.add(obj)
            await session.flush()
            ids[key] = obj.id

        for key, entries in references.items():
            for position, (label, url) in enumerate(entries):
                session.add(
                    ObjectReference(object_id=ids[key], label=label, url=url, position=position)
                )

        async def add_relation(operator: str, inputs: list[str], outputs: list[str]) -> None:
            rel = Relation(operator_id=ids[operator])
            session.add(rel)
            await session.flush()
            for position, key in enumerate(inputs):
                session.add(
                    RelationInput(relation_id=rel.id, object_id=ids[key], position=position)
                )
            for position, key in enumerate(outputs):
                session.add(
                    RelationOutput(relation_id=rel.id, object_id=ids[key], position=position)
                )

        await add_relation("CharacteristicPolynomial", ["A"], ["P"])
        await add_relation("CompanionMatrix", ["P"], ["C"])
        await add_relation("CharacteristicPolynomial", ["C"], ["P"])  # closes the loop
        await add_relation("Inverse", ["B"], ["B"])
        await add_relation("Inverse", ["D"], ["D"])
        await add_relation("CharacteristicPolynomial", ["B"], ["Q"])
        await add_relation("CharacteristicPolynomial", ["D"], ["R"])
        await add_relation("Add", ["A", "B"], ["E"])
        await add_relation("Determinant", ["A"], ["three"])
        await add_relation("IsSingular", ["A"], ["false"])
        await add_relation("Degree", ["P"], ["two"])
        await add_relation("SeifertMatrix", ["K3"], ["V3"])
        await add_relation("SeifertMatrix", ["K5"], ["V5"])
        await add_relation("SeifertMatrix", ["K7"], ["V7"])
        await add_relation("AlexanderPolynomial", ["V3"], ["Phi6"])
        await add_relation("AlexanderPolynomial", ["V5"], ["Phi10"])
        await add_relation("AlexanderPolynomial", ["V7"], ["Phi14"])
        await add_relation("CyclotomicPolynomial", ["six"], ["Phi6"])
        await add_relation("CyclotomicPolynomial", ["ten"], ["Phi10"])
        await add_relation("CyclotomicPolynomial", ["fourteen"], ["Phi14"])
        await add_relation("CompanionMatrix", ["Phi6"], ["CompPhi6"])
        await add_relation("CharacteristicPolynomial", ["CompPhi6"], ["Phi6"])
        await add_relation("CompanionMatrix", ["R"], ["D"])
        await add_relation("MatrixOrder", ["CompPhi6"], ["six"])
        await add_relation("MatrixOrder", ["B"], ["one"])
        await add_relation("MatrixOrder", ["D"], ["two"])
        await add_relation("KnotDeterminant", ["V3"], ["three"])
        await add_relation("KnotDeterminant", ["V5"], ["five"])
        await add_relation("KnotDeterminant", ["V7"], ["seven"])
        await add_relation("Roots", ["P"], ["one", "three"])
        await add_relation("Eigenvalues", ["A"], ["one", "three"])
        await add_relation("Determinant", ["B"], ["one"])
        await add_relation("Determinant", ["D"], ["neg_one"])
        await add_relation("Determinant", ["C"], ["three"])
        await add_relation("Determinant", ["S"], ["zero"])
        await add_relation("IsSingular", ["S"], ["true"])
        await add_relation("EulerTotient", ["six"], ["two"])
        await add_relation("EulerTotient", ["ten"], ["four"])
        await add_relation("EulerTotient", ["fourteen"], ["six"])

        relation_count = 39

        for key, data_kind in types.items():
            session.add(Type(object_id=ids[key], data_kind=data_kind))
        await session.flush()

        subtypes = {
            "Matrices": "MathematicalObjects",
            "Polynomials": "MathematicalObjects",
            "RationalNumbers": "MathematicalObjects",
            "Booleans": "MathematicalObjects",
            "Knots": "MathematicalObjects",
            "Expressions": "MathematicalObjects",
            "RealFunctions": "MathematicalObjects",
            "Integers": "RationalNumbers",
            "SymmetricMatrices": "Matrices",
            "CyclotomicPolynomials": "Polynomials",
            "TorusKnots": "Knots",
        }
        for subtype, supertype in subtypes.items():
            session.add(Subtype(type_id=ids[subtype], supertype_id=ids[supertype]))

        for key, type_key in most_specific_type.items():
            session.add(Membership(object_id=ids[key], type_id=ids[type_key], data=data[key]))
        for key in also_functions:
            session.add(
                Membership(object_id=ids[key], type_id=ids["RealFunctions"], data=data[key])
            )

        signatures = [
            ("CharacteristicPolynomial", "Matrices", "Polynomials"),
            ("Inverse", "Matrices", "Matrices"),
            ("Inverse", "SymmetricMatrices", "SymmetricMatrices"),
            ("Determinant", "Matrices", "Integers"),
            ("Add", "Matrices", "Matrices"),
            ("IsSingular", "Matrices", "Booleans"),
            ("MatrixOrder", "Matrices", "Integers"),
            ("CompanionMatrix", "Polynomials", "Matrices"),
            ("Degree", "Polynomials", "Integers"),
            ("CyclotomicPolynomial", "Integers", "CyclotomicPolynomials"),
            ("EulerTotient", "Integers", "Integers"),
            ("SeifertMatrix", "Knots", "Matrices"),
            ("AlexanderPolynomial", "Matrices", "Polynomials"),
            ("KnotDeterminant", "Matrices", "Integers"),
        ]
        for operator, domain, codomain in signatures:
            session.add(
                Signature(map_id=ids[operator], domain_id=ids[domain], codomain_id=ids[codomain])
            )

        displays: dict[str, tuple[str | None, bool]] = {
            "Add": (r"{in0} \op{+} {in1} = {out0}", True),
            "Determinant": (r"\op{\det(}{in0}\op{)} = {out0}", False),
            "Inverse": (r"{in0}^{\op{-1}} = {out0}", False),
            "Degree": (r"\op{\deg(}{in0}\op{)} = {out0}", False),
            "SeifertMatrix": (r"\op{V(}{in0}\op{)} = {out0}", False),
            "AlexanderPolynomial": (r"\op{\Delta(}{in0}\op{)} = {out0}", False),
            "CyclotomicPolynomial": (r"\op{\Phi}_{{in0}}(x) = {out0}", False),
            "KnotDeterminant": (r"\op{\det{}_{K}(}{in0}\op{)} = {out0}", False),
            "MatrixOrder": (r"\op{\mathrm{ord}(}{in0}\op{)} = {out0}", False),
            "EulerTotient": (r"\op{\varphi(}{in0}\op{)} = {out0}", False),
        }
        for operator, (template, hidden) in displays.items():
            session.add(
                OperatorDisplay(
                    operator_id=ids[operator], template=template, hidden_by_default=hidden
                )
            )

        filings = {
            "LinearAlgebra": ["Matrices", "SymmetricMatrices", "MatrixOperations"],
            "MatrixOperations": [
                "CharacteristicPolynomial",
                "Inverse",
                "Determinant",
                "Add",
                "IsSingular",
                "MatrixOrder",
                "Eigenvalues",
            ],
            "PolynomialAlgebra": ["Polynomials", "CyclotomicPolynomials", "PolynomialOperations"],
            "PolynomialOperations": ["CompanionMatrix", "Degree", "Roots", "CyclotomicPolynomial"],
            "Values": [
                "Integers",
                "RationalNumbers",
                "Booleans",
                "Expressions",
                "RealFunctions",
                "NumberOperations",
            ],
            "NumberOperations": ["EulerTotient"],
            "KnotTheory": ["Knots", "TorusKnots", "KnotOperations"],
            "KnotOperations": ["SeifertMatrix", "AlexanderPolynomial", "KnotDeterminant"],
        }
        for section, filed in filings.items():
            for key in filed:
                session.add(SectionFiling(object_id=ids[key], section_id=ids[section]))

        for root in ("LinearAlgebra", "PolynomialAlgebra", "KnotTheory", "Values"):
            session.add(TopLevelObject(object_id=ids[root]))

        implementation_dir = pathlib.Path(__file__).parent / "implementations"
        implementations = {
            "CharacteristicPolynomial": "characteristic_polynomial",
            "Inverse": "inverse",
            "Determinant": "determinant",
            "Add": "add",
            "IsSingular": "is_singular",
            "CompanionMatrix": "companion_matrix",
            "Degree": "degree",
            "AlexanderPolynomial": "alexander_polynomial",
            "KnotDeterminant": "knot_determinant",
            "CyclotomicPolynomial": "cyclotomic_polynomial",
            "MatrixOrder": "matrix_order",
            "Eigenvalues": "eigenvalues",
            "Roots": "roots",
            "EulerTotient": "euler_totient",
        }
        for operator, filename in implementations.items():
            session.add(
                Implementation(
                    operator_id=ids[operator],
                    code=(implementation_dir / f"{filename}.py").read_text(),
                )
            )

        await session.commit()
        reference_count = sum(len(entries) for entries in references.values())
        print(
            f"seeded {len(objects)} objects ({len(types)} types), {relation_count} relations, "
            f"{len(implementations)} implementations, {len(images)} images "
            f"and {reference_count} references"
        )


if __name__ == "__main__":
    asyncio.run(seed())
