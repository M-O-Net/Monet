"""Seed the v0 demo dataset: objects, relations, and an implementation behind each operator.

Matrices, polynomials, the operators between them, and the sympy implementation of each
(source in scripts/implementations/).

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
        await session.exec(delete(TopLevelObject))
        await session.exec(delete(RelationOutput))
        await session.exec(delete(RelationInput))
        await session.exec(delete(Relation))
        await session.exec(delete(Object))
        await session.commit()

        # key -> (latex, description | None). Description is optional — most specimens don't
        # need one, but the four sections and the operators benefit from one.
        objects: dict[str, tuple[str, str | None]] = {
            # sections (see TopLevelObject below)
            "Matrices": (
                r"\text{Matrices}",
                "Square arrays of numbers, and the operations "
                "that act on them: characteristic polynomials, inverses, "
                "determinants, sums.",
            ),
            "Polynomials": (
                r"\text{Polynomials}",
                "Single-variable polynomials, and the "
                "operations that act on them: companion matrices, degree.",
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
            # matrix specimens
            "A": (r"\begin{pmatrix}2&1\\1&2\end{pmatrix}", None),
            "B": (r"\begin{pmatrix}1&0\\0&1\end{pmatrix}", None),
            "D": (r"\begin{pmatrix}0&1\\1&0\end{pmatrix}", None),
            "E": (r"\begin{pmatrix}3&1\\1&3\end{pmatrix}", None),
            "C": (
                r"\begin{pmatrix}0&-3\\1&4\end{pmatrix}",
                "The companion matrix of "
                r"$x^{2} - 4 x + 3$ — its own characteristic polynomial closes the loop.",
            ),
            # polynomial specimens
            "P": (r"x^{2} - 4 x + 3", None),
            "Q": (r"x^{2} - 2 x + 1", None),
            "R": (r"x^{2} - 1", None),
            # number/boolean specimens
            "one": ("1", None),
            "neg_one": ("-1", None),
            "three": ("3", None),
            "two": ("2", None),
            "true": (r"\text{True}", None),
            "false": (r"\text{False}", None),
            # operators — matrix operations
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
            # operators — polynomial operations
            "CompanionMatrix": (
                r"\text{Companion Matrix}",
                "For a monic polynomial, the "
                "matrix whose characteristic polynomial is that polynomial.",
            ),
            "Degree": (r"\text{Degree}", "The highest power of the variable in a polynomial."),
            # operator — sectioning
            "ElementOf": (
                r"\text{Element Of}",
                "Marks an object as belonging to one of the top-level sections.",
            ),
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

        # Sections: every specimen and operator gets an Element Of relation to its section, and
        # the four section objects themselves are flagged as top-level (see TopLevelObject).
        sections = {
            "Matrices": [
                "A",
                "B",
                "D",
                "E",
                "C",
                "CharacteristicPolynomial",
                "Inverse",
                "Determinant",
                "Add",
                "IsSingular",
            ],
            "Polynomials": ["P", "Q", "R", "CompanionMatrix", "Degree"],
            "Integers": ["one", "neg_one", "three", "two"],
            "Booleans": ["true", "false"],
        }
        for section, members in sections.items():
            for member in members:
                await add_relation("ElementOf", [member], [section])
                relation_count += 1
            session.add(TopLevelObject(object_id=ids[section]))

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
