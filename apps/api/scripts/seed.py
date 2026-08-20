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

from sqlmodel import delete, func, select

from monet_api.core.db import async_session
from monet_api.implementations.models import Implementation
from monet_api.objects.models import (
    Object,
    OperatorDisplay,
    Relation,
    RelationInput,
    RelationOutput,
    TopLevelObject,
)


async def seed() -> None:
    async with async_session() as session:
        if "--if-empty" in sys.argv:
            count = (await session.exec(select(func.count()).select_from(Object))).one()
            if count > 0:
                print(f"objects table already has {count} rows, skipping (--if-empty)")
                return

        await session.exec(delete(Implementation))
        await session.exec(delete(OperatorDisplay))
        await session.exec(delete(TopLevelObject))
        await session.exec(delete(RelationOutput))
        await session.exec(delete(RelationInput))
        await session.exec(delete(Relation))
        await session.exec(delete(Object))
        await session.commit()

        Specimen = tuple[str, str | None]

        section_objects: dict[str, Specimen] = {
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
            "MatrixOperations": (
                r"\text{Matrix Operations}",
                "Operations taking matrices as "
                "their input: characteristic polynomials, inverses, "
                "determinants, sums.",
            ),
            "Polynomials": (r"\text{Polynomials}", "Single-variable polynomials."),
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
            "KnotOperations": (
                r"\text{Knot Operations}",
                "Operations taking a knot or its Seifert matrix as input: Seifert matrices, "
                "Alexander polynomials.",
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
            "one": ("1", None),
            "neg_one": ("-1", None),
            "three": ("3", None),
            "two": ("2", None),
            "six": ("6", None),
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
            "IsSingular": (r"\text{Is Singular}", "Whether a matrix's determinant is zero."),
        }

        polynomial_operators: dict[str, Specimen] = {
            "CompanionMatrix": (
                r"\text{Companion Matrix}",
                "For a monic polynomial, the "
                "matrix whose characteristic polynomial is that polynomial.",
            ),
            "Degree": (r"\text{Degree}", "The highest power of the variable in a polynomial."),
            "CyclotomicPolynomial": (
                r"\text{Cyclotomic Polynomial}",
                r"For $n$, the monic factor of $x^{n} - 1$ whose roots are exactly the "
                r"primitive $n$th roots of unity.",
            ),
        }

        sectioning_operators: dict[str, Specimen] = {
            "ElementOf": (
                r"\text{Element Of}",
                "Marks an object as belonging to a section. Flagged as the "
                "membership operator, so the GUI renders its relations as tags and "
                "member lists rather than as ordinary rows.",
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
            **sectioning_operators,
        }

        ids: dict[str, uuid.UUID] = {}
        for key, (latex, description) in objects.items():
            obj = Object(latex=latex, description=description)
            session.add(obj)
            await session.flush()
            ids[key] = obj.id

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

        relation_count = 22

        displays: dict[str, tuple[str | None, bool, bool]] = {
            "ElementOf": (None, False, True),
            "Add": (r"{in0} \op{+} {in1} = {out0}", True, False),
            "Determinant": (r"\op{\det(}{in0}\op{)} = {out0}", False, False),
            "Inverse": (r"{in0}^{\op{-1}} = {out0}", False, False),
            "Degree": (r"\op{\deg(}{in0}\op{)} = {out0}", False, False),
            "SeifertMatrix": (r"\op{V(}{in0}\op{)} = {out0}", False, False),
            "AlexanderPolynomial": (r"\op{\Delta(}{in0}\op{)} = {out0}", False, False),
            "CyclotomicPolynomial": (r"\op{\Phi}_{{in0}}(x) = {out0}", False, False),
        }
        for operator, (template, hidden, membership) in displays.items():
            session.add(
                OperatorDisplay(
                    operator_id=ids[operator],
                    template=template,
                    hidden_by_default=hidden,
                    is_membership=membership,
                )
            )

        sections = {
            "LinearAlgebra": ["Matrices", "MatrixOperations"],
            "PolynomialAlgebra": ["Polynomials", "PolynomialOperations"],
            "Values": ["Integers", "Booleans"],
            "Matrices": ["A", "B", "D", "E", "C", "V3", "V5", "V7", "CompPhi6"],
            "MatrixOperations": [
                "CharacteristicPolynomial",
                "Inverse",
                "Determinant",
                "Add",
                "IsSingular",
            ],
            "Polynomials": ["P", "Q", "R", "Phi6", "Phi10", "Phi14"],
            "PolynomialOperations": ["CompanionMatrix", "Degree", "CyclotomicPolynomial"],
            "Integers": ["one", "neg_one", "three", "two", "six", "ten", "fourteen"],
            "Booleans": ["true", "false"],
            "KnotTheory": ["Knots", "KnotOperations"],
            "Knots": ["K3", "K5", "K7"],
            "KnotOperations": ["SeifertMatrix", "AlexanderPolynomial"],
        }
        for section, members in sections.items():
            for member in members:
                await add_relation("ElementOf", [member], [section])
                relation_count += 1

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
            "CyclotomicPolynomial": "cyclotomic_polynomial",
        }
        for operator, filename in implementations.items():
            session.add(
                Implementation(
                    operator_id=ids[operator],
                    code=(implementation_dir / f"{filename}.py").read_text(),
                )
            )

        await session.commit()
        print(
            f"seeded {len(objects)} objects, {relation_count} relations, "
            f"and {len(implementations)} implementations"
        )


if __name__ == "__main__":
    asyncio.run(seed())
