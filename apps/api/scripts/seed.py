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
        }

        polynomials: dict[str, Specimen] = {
            # Spelled the way sandbox/prelude.py's render() emits it, so a computed
            # characteristic polynomial lands here instead of minting a near-identical twin.
            "P": (r"x^{2} - 4 x + 3", None),
            "Q": (r"x^{2} - 2 x + 1", None),
            "R": (r"x^{2} - 1", None),
        }

        integers: dict[str, Specimen] = {
            "one": ("1", None),
            "neg_one": ("-1", None),
            "three": ("3", None),
            "two": ("2", None),
        }

        booleans: dict[str, Specimen] = {
            "true": (r"\text{True}", None),
            "false": (r"\text{False}", None),
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
            **matrix_operators,
            **polynomial_operators,
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

        relation_count = 11

        displays: dict[str, tuple[str | None, bool, bool]] = {
            "ElementOf": (None, False, True),
            "Add": (r"{in0} \op{+} {in1} = {out0}", True, False),
            "Determinant": (r"\op{\det(}{in0}\op{)} = {out0}", False, False),
            "Inverse": (r"{in0}^{\op{-1}} = {out0}", False, False),
            "Degree": (r"\op{\deg(}{in0}\op{)} = {out0}", False, False),
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
            "Matrices": ["A", "B", "D", "E", "C"],
            "MatrixOperations": [
                "CharacteristicPolynomial",
                "Inverse",
                "Determinant",
                "Add",
                "IsSingular",
            ],
            "Polynomials": ["P", "Q", "R"],
            "PolynomialOperations": ["CompanionMatrix", "Degree"],
            "Integers": ["one", "neg_one", "three", "two"],
            "Booleans": ["true", "false"],
        }
        for section, members in sections.items():
            for member in members:
                await add_relation("ElementOf", [member], [section])
                relation_count += 1

        for root in ("LinearAlgebra", "PolynomialAlgebra", "Values"):
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
