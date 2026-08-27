"""Import the harvested knot and graph data on top of whatever seed.py left behind.

Reads scripts/data/*.json.gz -- no network access -- and reuses any object whose LaTeX is
already present, so the trefoil's Alexander polynomial lands on the seeded cyclotomic rather
than a duplicate. Re-running is a no-op.
"""

import asyncio
import gzip
import json
import pathlib
import uuid

import sqlalchemy as sa
from sqlmodel import select

from monet_api.core.db import async_session
from monet_api.objects.models import (
    Object,
    ObjectReference,
    OperatorDisplay,
    Relation,
    RelationInput,
    RelationOutput,
    TopLevelObject,
)
from monet_api.objects.service import normalize_latex

DATA = pathlib.Path(__file__).resolve().parent / "data"
MAX_OBJECTS = 10_000
CHUNK = 4_000

KNOT_OPERATORS = {
    "AlexanderPolynomial": ("alexander_polynomial", r"\op{\Delta(}{in0}\op{)} = {out0}", False),
    "JonesPolynomial": ("jones_polynomial", r"\op{V(}{in0}\op{)} = {out0}", False),
    "KnotDeterminant": ("determinant", r"\op{\det{}_{K}(}{in0}\op{)} = {out0}", False),
    "Signature": ("signature", r"\op{\sigma(}{in0}\op{)} = {out0}", False),
    "CrossingNumber": ("crossing_number", r"\op{c(}{in0}\op{)} = {out0}", False),
    "BraidIndex": ("braid_index", None, True),
    "BridgeIndex": ("bridge_index", None, True),
    "ArcIndex": ("arc_index", None, True),
    "SeifertGenus": ("three_genus", r"\op{g(}{in0}\op{)} = {out0}", False),
    "UnknottingNumber": ("unknotting_number", r"\op{u(}{in0}\op{)} = {out0}", False),
    "SymmetryType": ("symmetry_type", None, True),
    "IsAlternating": ("alternating", None, True),
    "IsFibered": ("fibered", None, True),
    "IsPositive": ("positive", None, True),
}

GRAPH_OPERATORS = {
    "NumberOfVertices": ("number_of_vertices", None, True),
    "NumberOfEdges": ("number_of_edges", None, True),
    "ChromaticNumber": ("chromatic_number", r"\op{\chi(}{in0}\op{)} = {out0}", False),
    "Girth": ("girth", None, True),
    "Diameter": ("diameter", None, True),
    "IndependenceNumber": ("independence_number", r"\op{\alpha(}{in0}\op{)} = {out0}", False),
    "CliqueNumber": ("clique_number", r"\op{\omega(}{in0}\op{)} = {out0}", False),
    "NumberOfTriangles": ("number_of_triangles", None, True),
    "NumberOfSpanningTrees": (
        "number_of_spanning_trees",
        r"\op{\tau(}{in0}\op{)} = {out0}",
        False,
    ),
    "IsPlanar": ("is_planar", None, True),
    "IsHamiltonian": ("is_hamiltonian", None, True),
    "IsBipartite": ("is_bipartite", None, True),
}

OPERATOR_LATEX = {
    "AdjacencyMatrix": (r"\text{Adjacency Matrix}", "The adjacency matrix of a graph."),
    "Complement": (r"\text{Complement}", "The graph on the same vertices with every edge flipped."),
    "LineGraph": (r"\text{Line Graph}", "The graph whose vertices are this graph's edges."),
    "JonesPolynomial": (r"\text{Jones Polynomial}", "A Laurent polynomial invariant of a knot."),
    "Signature": (r"\text{Signature}", "The signature of a knot's symmetrised Seifert form."),
    "CrossingNumber": (r"\text{Crossing Number}", "The fewest crossings in any diagram."),
    "BraidIndex": (r"\text{Braid Index}", "The fewest strands in any braid closing to this knot."),
    "BridgeIndex": (r"\text{Bridge Index}", "The fewest bridges in any diagram."),
    "ArcIndex": (r"\text{Arc Index}", "The fewest arcs in any arc presentation."),
    "SeifertGenus": (r"\text{Seifert Genus}", "The least genus of a Seifert surface."),
    "UnknottingNumber": (r"\text{Unknotting Number}", "The fewest crossing changes that untie it."),
    "SymmetryType": (r"\text{Symmetry Type}", "How a knot relates to its mirror and reverse."),
    "IsAlternating": (r"\text{Is Alternating}", None),
    "IsFibered": (r"\text{Is Fibered}", None),
    "IsPositive": (r"\text{Is Positive}", None),
    "NumberOfVertices": (r"\text{Number of Vertices}", None),
    "NumberOfEdges": (r"\text{Number of Edges}", None),
    "ChromaticNumber": (r"\text{Chromatic Number}", "The fewest colours that properly colour it."),
    "Girth": (r"\text{Girth}", "The length of a shortest cycle."),
    "Diameter": (r"\text{Diameter}", "The longest shortest path."),
    "IndependenceNumber": (
        r"\text{Independence Number}",
        "The largest set of pairwise non-adjacent vertices.",
    ),
    "CliqueNumber": (
        r"\text{Clique Number}",
        "The largest set of pairwise adjacent vertices.",
    ),
    "NumberOfTriangles": (r"\text{Number of Triangles}", None),
    "NumberOfSpanningTrees": (r"\text{Number of Spanning Trees}", None),
    "IsPlanar": (r"\text{Is Planar}", None),
    "IsHamiltonian": (r"\text{Is Hamiltonian}", "Whether some cycle visits every vertex once."),
    "IsBipartite": (r"\text{Is Bipartite}", None),
}

SECTIONS = {
    "GraphTheory": (
        r"\text{Graph Theory}",
        "Graphs, and the matrices and polynomials that identify them.",
    ),
    "Graphs": (
        r"\text{Graphs}",
        "Every graph on seven or fewer vertices, plus some larger named ones.",
    ),
    "GraphOperations": (r"\text{Graph Operations}", "Operations taking a graph as input."),
    "SymmetryTypes": (
        r"\text{Symmetry Types}",
        "How a knot relates to its mirror image and its reverse.",
    ),
    "LaurentPolynomials": (
        r"\text{Laurent Polynomials}",
        "Polynomials in $t$ with negative powers allowed.",
    ),
}

ATLAS_REFERENCE = (
    "An Atlas of Graphs (Read & Wilson)",
    "https://global.oup.com/academic/product/an-atlas-of-graphs-9780198526506",
)


Signature = tuple[uuid.UUID, tuple[uuid.UUID, ...], tuple[uuid.UUID, ...]]


class Catalogue:
    def __init__(self, existing: dict[str, uuid.UUID], related: set[Signature]) -> None:
        self._by_latex = dict(existing)
        self._related = set(related)
        self.new_objects: list[dict[str, object]] = []
        self.relations: list[dict[str, object]] = []
        self.inputs: list[dict[str, object]] = []
        self.outputs: list[dict[str, object]] = []
        self.references: list[dict[str, object]] = []
        self.displays: list[dict[str, object]] = []

    def object_id(self, latex: str, description: str | None = None) -> uuid.UUID:
        key = normalize_latex(latex)
        found = self._by_latex.get(key)
        if found is not None:
            return found
        minted = uuid.uuid4()
        self._by_latex[key] = minted
        self.new_objects.append({"id": minted, "latex": key, "description": description})
        return minted

    def is_new(self, latex: str) -> bool:
        return normalize_latex(latex) not in self._by_latex

    @staticmethod
    def _slot(relation: uuid.UUID, object_id: uuid.UUID, position: int) -> dict[str, object]:
        return {
            "id": uuid.uuid4(),
            "relation_id": relation,
            "object_id": object_id,
            "position": position,
        }

    def relate(
        self, operator: uuid.UUID, inputs: list[uuid.UUID], outputs: list[uuid.UUID]
    ) -> None:
        signature = (operator, tuple(inputs), tuple(outputs))
        if signature in self._related:
            return
        self._related.add(signature)
        relation = uuid.uuid4()
        self.relations.append({"id": relation, "operator_id": operator})
        for position, object_id in enumerate(inputs):
            self.inputs.append(self._slot(relation, object_id, position))
        for position, object_id in enumerate(outputs):
            self.outputs.append(self._slot(relation, object_id, position))

    def reference(self, object_id: uuid.UUID, label: str, url: str, position: int = 0) -> None:
        self.references.append(
            {
                "id": uuid.uuid4(),
                "object_id": object_id,
                "label": label,
                "url": url,
                "position": position,
            }
        )

    def display(self, operator: uuid.UUID, template: str | None, hidden: bool) -> None:
        self.displays.append(
            {
                "operator_id": operator,
                "template": template,
                "hidden_by_default": hidden,
                "is_membership": False,
            }
        )


RENDERED_FIELDS = frozenset({"alexander_polynomial", "jones_polynomial"})


def _value_latex(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return r"\text{True}" if value else r"\text{False}"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        return rf"\text{{{value}}}"
    return None


async def _existing(session) -> dict[str, uuid.UUID]:
    rows = (await session.exec(select(Object.id, Object.latex))).all()
    return {normalize_latex(latex): identifier for identifier, latex in rows}


async def _existing_relations(session) -> set[Signature]:
    operators = dict((await session.exec(select(Relation.id, Relation.operator_id))).all())
    slots: dict[uuid.UUID, dict[uuid.UUID, list[tuple[int, uuid.UUID]]]] = {}
    for table in (RelationInput, RelationOutput):
        rows = (await session.exec(
            select(table.relation_id, table.object_id, table.position)
        )).all()
        side = slots.setdefault(table, {})
        for relation_id, object_id, position in rows:
            side.setdefault(relation_id, []).append((position, object_id))

    def ordered(table, relation_id):
        return tuple(o for _, o in sorted(slots.get(table, {}).get(relation_id, [])))

    return {
        (operator_id, ordered(RelationInput, relation_id), ordered(RelationOutput, relation_id))
        for relation_id, operator_id in operators.items()
    }


async def _existing_displays(session) -> set[uuid.UUID]:
    rows = (await session.exec(select(OperatorDisplay.operator_id))).all()
    return set(rows)


EXISTING_SECTIONS = {
    "KnotTheory": r"\text{Knot Theory}",
    "Knots": r"\text{Knots}",
    "KnotOperations": r"\text{Knot Operations}",
    "PolynomialAlgebra": r"\text{Polynomial Algebra}",
    "Polynomials": r"\text{Polynomials}",
    "LinearAlgebra": r"\text{Linear Algebra}",
    "Matrices": r"\text{Matrices}",
    "Values": r"\text{Values}",
    "Integers": r"\text{Integers}",
    "Booleans": r"\text{Booleans}",
}

SECTION_PARENTS = {
    "GraphTheory": ["Graphs", "GraphOperations"],
    "KnotTheory": ["SymmetryTypes"],
    "PolynomialAlgebra": ["LaurentPolynomials"],
}


async def import_atlas() -> None:
    with gzip.open(DATA / "knots.json.gz", "rt", encoding="utf-8") as handle:
        knots = json.load(handle)["knots"]
    with gzip.open(DATA / "graphs.json.gz", "rt", encoding="utf-8") as handle:
        graphs_payload = json.load(handle)
    graphs = graphs_payload["census"] + graphs_payload["overlay"]

    async with async_session() as session:
        catalogue = Catalogue(await _existing(session), await _existing_relations(session))
        described = await _existing_displays(session)
        top_level = set((await session.exec(select(TopLevelObject.object_id))).all())

        section = {key: catalogue.object_id(latex) for key, latex in EXISTING_SECTIONS.items()}
        for key, (latex, description) in SECTIONS.items():
            section[key] = catalogue.object_id(latex, description)

        element_of = catalogue.object_id(r"\text{Element Of}")
        members: list[tuple[uuid.UUID, str]] = []

        def file_under(object_id: uuid.UUID, name: str) -> None:
            members.append((object_id, name))

        operator = {}
        for key, (latex, description) in OPERATOR_LATEX.items():
            operator[key] = catalogue.object_id(latex, description)
        operator["AlexanderPolynomial"] = catalogue.object_id(r"\text{Alexander Polynomial}")
        operator["KnotDeterminant"] = catalogue.object_id(r"\text{Knot Determinant}")
        operator["CharacteristicPolynomial"] = catalogue.object_id(
            r"\text{Characteristic Polynomial}"
        )

        for key, (_, template, hidden) in {**KNOT_OPERATORS, **GRAPH_OPERATORS}.items():
            if operator[key] not in described:
                catalogue.display(operator[key], template, hidden)
                described.add(operator[key])
        for key in ("AdjacencyMatrix", "Complement", "LineGraph"):
            if operator[key] not in described:
                catalogue.display(operator[key], None, False)
                described.add(operator[key])

        for key in KNOT_OPERATORS:
            file_under(operator[key], "KnotOperations")
        for key in (*GRAPH_OPERATORS, "AdjacencyMatrix", "Complement", "LineGraph"):
            file_under(operator[key], "GraphOperations")
        for parent, children in SECTION_PARENTS.items():
            for child in children:
                file_under(section[child], parent)

        for knot in knots:
            knot_id = catalogue.object_id(knot["latex"])
            file_under(knot_id, "Knots")
            catalogue.reference(knot_id, "KnotInfo", "https://knotinfo.org/")
            for key, (field, _, _) in KNOT_OPERATORS.items():
                raw = knot.get(field)
                latex = raw if field in RENDERED_FIELDS else _value_latex(raw)
                if latex is None:
                    continue
                value_id = catalogue.object_id(latex)
                if field == "alexander_polynomial":
                    file_under(value_id, "Polynomials")
                elif field == "jones_polynomial":
                    file_under(value_id, "LaurentPolynomials")
                elif field == "symmetry_type":
                    file_under(value_id, "SymmetryTypes")
                elif isinstance(knot[field], bool):
                    file_under(value_id, "Booleans")
                else:
                    file_under(value_id, "Integers")
                catalogue.relate(operator[key], [knot_id], [value_id])

        keys: dict[str, uuid.UUID] = {}
        for entry in graphs:
            graph_id = catalogue.object_id(entry["latex"])
            keys[entry["key"]] = graph_id
            file_under(graph_id, "Graphs")
            for position, (label, url) in enumerate(entry["references"]):
                catalogue.reference(graph_id, label, url, position)
            matrix_id = catalogue.object_id(entry["matrix_latex"])
            file_under(matrix_id, "Matrices")
            catalogue.relate(operator["AdjacencyMatrix"], [graph_id], [matrix_id])
            polynomial_id = catalogue.object_id(entry["characteristic_polynomial"])
            file_under(polynomial_id, "Polynomials")
            catalogue.relate(
                operator["CharacteristicPolynomial"], [matrix_id], [polynomial_id]
            )
            for key, (field, _, _) in GRAPH_OPERATORS.items():
                latex = _value_latex(entry["invariants"].get(field))
                if latex is None:
                    continue
                value_id = catalogue.object_id(latex)
                boolean = isinstance(entry["invariants"][field], bool)
                file_under(value_id, "Booleans" if boolean else "Integers")
                catalogue.relate(operator[key], [graph_id], [value_id])

        for entry in graphs:
            for field, key in (("complement_key", "Complement"), ("line_graph_key", "LineGraph")):
                target = entry.get(field)
                if target and target in keys:
                    catalogue.relate(operator[key], [keys[entry["key"]]], [keys[target]])

        for object_id, name in members:
            catalogue.relate(element_of, [object_id], [section[name]])

        if section["GraphTheory"] not in top_level:
            catalogue.new_top_level = section["GraphTheory"]

        await _write(session, catalogue, section)


async def _insert(session, table, rows: list[dict[str, object]]) -> None:
    for start in range(0, len(rows), CHUNK):
        await session.execute(sa.insert(table), rows[start : start + CHUNK])


async def _write(session, catalogue: Catalogue, section: dict[str, uuid.UUID]) -> None:
    total = len(catalogue._by_latex)
    if total > MAX_OBJECTS:
        raise SystemExit(f"refusing to import {total} objects, over the {MAX_OBJECTS} budget")

    await _insert(session, Object.__table__, catalogue.new_objects)
    await _insert(session, Relation.__table__, catalogue.relations)
    await _insert(session, RelationInput.__table__, catalogue.inputs)
    await _insert(session, RelationOutput.__table__, catalogue.outputs)
    await _insert(session, ObjectReference.__table__, catalogue.references)
    await _insert(session, OperatorDisplay.__table__, catalogue.displays)
    new_root = getattr(catalogue, "new_top_level", None)
    if new_root is not None:
        session.add(TopLevelObject(object_id=new_root))
    await session.commit()
    print(
        f"imported {len(catalogue.new_objects)} new objects "
        f"({total} in the network), {len(catalogue.relations)} relations, "
        f"{len(catalogue.references)} references"
    )


if __name__ == "__main__":
    asyncio.run(import_atlas())
