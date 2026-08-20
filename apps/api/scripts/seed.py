"""Seeds the v0 demo dataset defined below: matrices, polynomials, and the operators between them.

Wipes and reinserts, so it's safe to re-run — `uv run python scripts/seed.py` from apps/api/,
or `just seed`, always resets to exactly this dataset. Pass --if-empty to skip entirely when
the objects table already has rows (used by docker-compose.dev.yml's startup command, so a
fresh `just up` always has demo data without clobbering anything you've since added by hand
through the GUI on every later restart).

Sectioning is data, not schema: an object belongs to a section because an `Element Of` relation
says so, and `Element Of` is the membership operator because its `operator_displays` row says
so — never because of its name. Sections nest the same way, so "Matrices is in Linear Algebra"
is the same kind of fact as "this matrix is in Matrices". `top_level_objects` then holds only
the three roots, which is where reading starts.
"""

import asyncio
import sys
import uuid

from sqlmodel import delete, func, select

from monet_api.core.db import async_session
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

        await session.exec(delete(OperatorDisplay))
        await session.exec(delete(TopLevelObject))
        await session.exec(delete(RelationOutput))
        await session.exec(delete(RelationInput))
        await session.exec(delete(Relation))
        await session.exec(delete(Object))
        await session.commit()

        # key -> (latex, description | None). Description is optional — most specimens don't
        # need one, but the sections and the operators benefit from one.
        objects: dict[str, tuple[str, str | None]] = {
            # roots of the contents page
            "LinearAlgebra": (r"\text{Linear Algebra}", "Matrices and the operations that act "
                              "on them."),
            "PolynomialAlgebra": (r"\text{Polynomial Algebra}", "Single-variable polynomials "
                                  "and the operations that act on them."),
            "Values": (r"\text{Values}", "The plain numbers and truth values that relations "
                       "produce as answers."),
            # sections nested under those roots
            "Matrices": (r"\text{Matrices}", "Square arrays of numbers."),
            "MatrixOperations": (r"\text{Matrix Operations}", "Operations taking matrices as "
                                 "their input: characteristic polynomials, inverses, "
                                 "determinants, sums."),
            "Polynomials": (r"\text{Polynomials}", "Single-variable polynomials."),
            "PolynomialOperations": (r"\text{Polynomial Operations}", "Operations taking "
                                     "polynomials as their input: companion matrices, degree."),
            "Integers": (r"\text{Integers}", "Whole numbers, positive and negative — the "
                         "values relations like Determinant and Degree produce."),
            "Booleans": (r"\text{Booleans}", "The two truth values a predicate-style relation, "
                         "like Is Singular, produces."),
            # matrix specimens
            "A": (r"\begin{pmatrix}2&1\\1&2\end{pmatrix}", None),
            "B": (r"\begin{pmatrix}1&0\\0&1\end{pmatrix}", None),
            "D": (r"\begin{pmatrix}0&1\\1&0\end{pmatrix}", None),
            "E": (r"\begin{pmatrix}3&1\\1&3\end{pmatrix}", None),
            "C": (r"\begin{pmatrix}0&-3\\1&4\end{pmatrix}", "The companion matrix of "
                  r"$x^2 - 4x + 3$ — its own characteristic polynomial closes the loop."),
            # polynomial specimens
            "P": (r"x^2 - 4x + 3", None),
            "Q": (r"x^2 - 2x + 1", None),
            "R": (r"x^2 - 1", None),
            # number/boolean specimens
            "one": ("1", None),
            "neg_one": ("-1", None),
            "three": ("3", None),
            "two": ("2", None),
            "true": (r"\text{True}", None),
            "false": (r"\text{False}", None),
            # operators — matrix operations. "Matrix Addition", not "Add": an operator is a
            # specific mathematical object, and there are many additions in mathematics.
            "CharacteristicPolynomial": (r"\text{Characteristic Polynomial}",
                "For a matrix A, the polynomial det(xI - A)."),
            "Inverse": (r"\text{Inverse}",
                        "The multiplicative inverse of a matrix, when one exists."),
            "Determinant": (r"\text{Determinant}", "The scalar determinant of a matrix."),
            "MatrixAddition": (r"\text{Matrix Addition}",
                               "The entrywise sum of two matrices of the same shape."),
            "IsSingular": (r"\text{Is Singular}", "Whether a matrix's determinant is zero."),
            # operators — polynomial operations
            "CompanionMatrix": (r"\text{Companion Matrix}", "For a monic polynomial, the "
                                 "matrix whose characteristic polynomial is that polynomial."),
            "Degree": (r"\text{Degree}", "The highest power of the variable in a polynomial."),
            # operator — sectioning
            "ElementOf": (r"\text{Element Of}",
                           "Marks an object as belonging to a section. Flagged as the "
                           "membership operator, so the GUI renders its relations as tags and "
                           "member lists rather than as ordinary rows."),
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
        await add_relation("MatrixAddition", ["A", "B"], ["E"])
        await add_relation("Determinant", ["A"], ["three"])
        await add_relation("IsSingular", ["A"], ["false"])
        await add_relation("Degree", ["P"], ["two"])

        relation_count = 11

        # How each operator wants its relations rendered. Purely presentation — see
        # OperatorDisplay. A template must mention every operand, or the front end falls back
        # to the plain operands-operator-outputs row rather than show a partial equation.
        # \op{...} marks the part of a template that IS the operator — the "+" in A + B = E is
        # Matrix Addition — so it renders as a link to it, exactly as the operands do.
        displays: dict[str, tuple[str | None, bool, bool]] = {
            # operator -> (template, hidden_by_default, is_membership)
            "ElementOf": (None, False, True),
            # Every matrix in the network will eventually have sums with every other, so these
            # rows are collapsed until asked for.
            "MatrixAddition": (r"{in0} \op{+} {in1} = {out0}", True, False),
            "Determinant": (r"\op{\det}({in0}) = {out0}", False, False),
            "Inverse": (r"{in0}^{\op{-1}} = {out0}", False, False),
            "Degree": (r"\op{\deg}({in0}) = {out0}", False, False),
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

        # Sections. Nesting a section inside another is the same kind of fact as filing a
        # specimen, so both are Element Of relations; only the three roots are top-level.
        sections = {
            "LinearAlgebra": ["Matrices", "MatrixOperations"],
            "PolynomialAlgebra": ["Polynomials", "PolynomialOperations"],
            "Values": ["Integers", "Booleans"],
            "Matrices": ["A", "B", "D", "E", "C"],
            "MatrixOperations": ["CharacteristicPolynomial", "Inverse", "Determinant",
                                 "MatrixAddition", "IsSingular"],
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

        await session.commit()
        print(f"seeded {len(objects)} objects and {relation_count} relations")


if __name__ == "__main__":
    asyncio.run(seed())
