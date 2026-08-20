import uuid

from sqlmodel import Field, SQLModel


class Implementation(SQLModel, table=True):
    """The sympy behind an operator, authored through the GUI rather than in this repo.

    Not keyed by the operator: one operator may be implemented more than once — most usefully at
    different arities, e.g. an Add that takes two matrices and an Add that takes several. There is
    No name (the operator names it) and no arity. Arity isn't recorded anywhere, and isn't read
    off `compute`'s signature either: one implementation may genuinely accept two, three or more
    inputs, so there is no single number to record. The GUI lets you hand it as many inputs as
    you like and the code raises if they don't suit it.

    `code` is plain Python text, executed only in the visitor's browser (Pyodide inside a
    sandboxed, opaque-origin iframe) — never by this process. See root AGENTS.md > Implementations.
    """

    __tablename__ = "implementations"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    operator_id: uuid.UUID = Field(foreign_key="objects.id")
    code: str
