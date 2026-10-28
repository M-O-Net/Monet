"""Seed the demo dataset: objects, relations, and an implementation per operator.

Wipes and reinserts, so it's safe to re-run — `uv run python scripts/seed.py` from apps/api/,
or `just seed`, always resets to exactly this dataset. Pass --if-empty to skip entirely when
the objects table already has rows (used by docker-compose.dev.yml's startup command, so a
fresh `just up` always has demo data without clobbering anything you've since added by hand
through the GUI on every restart).
"""

import asyncio
import itertools
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
Specimen = tuple[str, str | None]
Facet = tuple[str, Data]
Instance = tuple[str, str | None, list[Facet]]
TypeSpec = tuple[str, str, str | None, list[str]]
Cell = int | tuple[str, Data]


def integer(n: int) -> Data:
    return {"int": n}


def rational(p: int, q: int) -> Data:
    return {"rational": [p, q]}


def cell(value: int | Data) -> Data:
    return integer(value) if isinstance(value, int) else value


def polynomial(*coeffs_from_constant: int | Data, var: str = "x") -> Data:
    return {
        "poly": {
            "var": var,
            "degree": len(coeffs_from_constant) - 1,
            "coeffs": {str(power): cell(c) for power, c in enumerate(coeffs_from_constant)},
        }
    }


def coefficient(*coeffs_from_constant: int, var: str) -> Data:
    if len(coeffs_from_constant) == 1:
        return integer(coeffs_from_constant[0])
    return polynomial(*coeffs_from_constant, var=var)


def algebraic(minpoly_from_constant: list[int], root: int) -> Data:
    return {"algebraic": {"minpoly": polynomial(*minpoly_from_constant), "root": root}}


def fraction(p: int, q: int) -> tuple[str, Data]:
    sign = "- " if p < 0 else ""
    return (rf"{sign}\frac{{{abs(p)}}}{{{q}}}", rational(p, q))


I_CELL = ("i", algebraic([1, 0, 1], 1))
SQRT2_CELL = (r"\sqrt{2}", algebraic([-2, 0, 1], 1))
SQRT3_CELL = (r"\sqrt{3}", algebraic([-3, 0, 1], 1))
HALF_SQRT2_CELL = (r"\frac{\sqrt{2}}{2}", algebraic([-1, 0, 2], 1))
MINUS_HALF_SQRT2_CELL = (r"- \frac{\sqrt{2}}{2}", algebraic([-1, 0, 2], 0))
HALF_SQRT3_CELL = (r"\frac{\sqrt{3}}{2}", algebraic([-3, 0, 4], 1))
MINUS_HALF_SQRT3_CELL = (r"- \frac{\sqrt{3}}{2}", algebraic([-3, 0, 4], 0))


def cell_latex(value: Cell) -> str:
    return str(value) if isinstance(value, int) else value[0]


def cell_data(value: Cell) -> Data:
    return integer(value) if isinstance(value, int) else value[1]


def matrix(rows: list[list[Cell]]) -> Data:
    return {"matrix": [[cell_data(c) for c in row] for row in rows]}


def pmatrix(rows: list[list[Cell]]) -> str:
    body = r"\\".join(" & ".join(cell_latex(c) for c in row) for row in rows)
    return rf"\begin{{pmatrix}}{body}\end{{pmatrix}}"


def seifert(size: int) -> list[list[Cell]]:
    return [[-1 if i == j else 1 if j == i + 1 else 0 for j in range(size)] for i in range(size)]


def residue(a: int, n: int) -> Data:
    return {"residue": [a, n]}


def seq(formula: str, start: int) -> Data:
    return {"seq": {"var": "n", "start": start, "formula": formula}}


def recurrence(coeffs: list[int], initial: list[int]) -> Data:
    return {
        "recurrence": {
            "coeffs": [integer(c) for c in coeffs],
            "initial": [integer(v) for v in initial],
        }
    }


def holonomic(coeffs: list[list[int]], initial: list[int]) -> Data:
    return {
        "holonomic": {
            "coeffs": [coefficient(*c, var="n") for c in coeffs],
            "initial": [integer(v) for v in initial],
        }
    }


def dfinite(coeffs: list[list[int]], initial: list[int | Data]) -> Data:
    return {
        "dfinite": {
            "coeffs": [coefficient(*c, var="x") for c in coeffs],
            "point": integer(0),
            "initial": [cell(v) for v in initial],
        }
    }


def graph(order: int, edges: list[tuple[int, int]]) -> Data:
    return {"graph": {"order": order, "edges": sorted([min(e), max(e)] for e in edges)}}


def complete_graph(order: int) -> Data:
    return graph(order, list(itertools.combinations(range(order), 2)))


def cycle_graph(order: int) -> Data:
    return graph(order, [(i, (i + 1) % order) for i in range(order)])


def path_graph(order: int) -> Data:
    return graph(order, [(i, i + 1) for i in range(order - 1)])


def small_group(order: int, index: int) -> Data:
    return {"smallgroup": [order, index]}


def abelian(rank: int, torsion: list[int]) -> Data:
    return {"abelian": {"rank": rank, "torsion": torsion}}


def permgroup(degree: int, generators: list[list[int]]) -> Data:
    return {"permgroup": {"degree": degree, "generators": generators}}


def presentation(generators: list[str], relators: list[list[tuple[str, int]]]) -> Data:
    return {
        "fpgroup": {
            "generators": generators,
            "relators": [[[letter, power] for letter, power in r] for r in relators],
        }
    }


def number_field(*coeffs_from_constant: int) -> Data:
    return {"numberfield": polynomial(*coeffs_from_constant)}


def surface(orientable: bool, genus: int) -> Data:
    return {"surface": {"orientable": orientable, "genus": genus}}


def simplicial(facets: list[tuple[int, ...]]) -> Data:
    return {"simplicial": sorted(sorted(f) for f in facets)}


def lattice_polytope(points: list[tuple[int, ...]]) -> Data:
    return {"polytope": [[integer(c) for c in p] for p in sorted(points)]}


def polygon_instance(
    points: list[tuple[Cell, Cell]], type_keys: list[str], description: str | None = None
) -> Instance:
    coordinates = ", ".join(rf"\left({cell_latex(x)}, {cell_latex(y)}\right)" for x, y in points)
    data = {"polytope": [[cell_data(x), cell_data(y)] for x, y in points]}
    return (
        rf"\operatorname{{conv}}\left\{{{coordinates}\right\}}",
        description,
        [(type_key, data) for type_key in type_keys],
    )


def knot(name: str) -> Data:
    return {"knot": name}


def expr(srepr: str) -> Data:
    return {"expr": srepr}


TYPES: dict[str, TypeSpec] = {
    "MathematicalObjects": (
        r"\text{Mathematical Objects}",
        "Every kind of object Monet catalogues. Each type sits somewhere beneath it.",
        None,
        [],
    ),
    "RationalNumbers": (
        r"\text{Rational Numbers}",
        "Fractions of integers.",
        "rational",
        ["MathematicalObjects"],
    ),
    "Integers": (
        r"\text{Integers}",
        "Whole numbers, positive and negative — the "
        "values relations like Determinant and Degree produce.",
        "int",
        ["RationalNumbers"],
    ),
    "PositiveIntegers": (
        r"\text{Positive Integers}",
        r"The counting numbers $1, 2, 3, \dots$",
        "int",
        ["Integers"],
    ),
    "PrimeNumbers": (
        r"\text{Prime Numbers}",
        "Positive integers with exactly two divisors.",
        "int",
        ["PositiveIntegers"],
    ),
    "ResidueClasses": (
        r"\text{Residue Classes}",
        r"Integers modulo $n$, held as $a \bmod n$ with $0 \le a < n$.",
        "residue",
        ["MathematicalObjects"],
    ),
    "UnitsModN": (
        r"\text{Units Modulo } n",
        r"Residues $a \bmod n$ with $\gcd(a, n) = 1$ — the invertible ones.",
        "residue",
        ["ResidueClasses"],
    ),
    "PrimitiveRoots": (
        r"\text{Primitive Roots}",
        r"Units whose powers reach every unit modulo $n$: their order is $\varphi(n)$.",
        "residue",
        ["UnitsModN"],
    ),
    "AlgebraicNumbers": (
        r"\text{Algebraic Numbers}",
        "Complex roots of nonzero rational polynomials, held as their minimal polynomial and "
        "which of its roots they are.",
        "algebraic",
        ["MathematicalObjects"],
    ),
    "AlgebraicIntegers": (
        r"\text{Algebraic Integers}",
        "Algebraic numbers whose minimal polynomial is monic with integer coefficients.",
        "algebraic",
        ["AlgebraicNumbers"],
    ),
    "RootsOfUnity": (
        r"\text{Roots of Unity}",
        r"Complex numbers $z$ with $z^{n} = 1$ for some $n$. Their minimal polynomials are "
        "cyclotomic.",
        "algebraic",
        ["AlgebraicIntegers"],
    ),
    "GaussianIntegers": (
        r"\text{Gaussian Integers}",
        r"Complex numbers $a + bi$ with $a$ and $b$ integers.",
        "algebraic",
        ["AlgebraicIntegers"],
    ),
    "GaussianPrimes": (
        r"\text{Gaussian Primes}",
        r"Gaussian integers that factor only trivially in $\mathbb{Z}[i]$.",
        "algebraic",
        ["GaussianIntegers"],
    ),
    "Booleans": (
        r"\text{Booleans}",
        "The two truth values a predicate-style relation, like Is Singular, produces.",
        "bool",
        ["MathematicalObjects"],
    ),
    "Expressions": (
        r"\text{Symbolic Expressions}",
        r"Exact values and equations no narrower type holds yet, such as $\pi$.",
        "expr",
        ["MathematicalObjects"],
    ),
    "Sequences": (
        r"\text{Sequences}",
        "Numbers listed in order, finitely or infinitely many.",
        None,
        ["MathematicalObjects"],
    ),
    "FiniteSequences": (
        r"\text{Finite Sequences}",
        "Ordered lists of finitely many values.",
        "tuple",
        ["Sequences"],
    ),
    "SequencesByFormula": (
        r"\text{Sequences by Formula}",
        r"Sequences given by a closed-form term in $n$ from a starting index.",
        "seq",
        ["Sequences"],
    ),
    "ArithmeticFunctions": (
        r"\text{Arithmetic Functions}",
        "Integer-valued functions on the positive integers.",
        "seq",
        ["SequencesByFormula"],
    ),
    "MultiplicativeFunctions": (
        r"\text{Multiplicative Functions}",
        r"Arithmetic functions with $f(mn) = f(m) f(n)$ whenever $m$ and $n$ are coprime.",
        "seq",
        ["ArithmeticFunctions"],
    ),
    "HolonomicSequences": (
        r"\text{P-recursive Sequences}",
        "Sequences satisfying a linear recurrence with polynomial coefficients — also called "
        "holonomic or D-finite. Held as that recurrence and its initial values.",
        "holonomic",
        ["Sequences"],
    ),
    "LinearRecurrences": (
        r"\text{Linear Recurrence Sequences}",
        "Sequences satisfying a linear recurrence with constant coefficients, held as the "
        "shortest such recurrence and its initial values.",
        "recurrence",
        ["HolonomicSequences"],
    ),
    "Matrices": (
        r"\text{Matrices}",
        "Rectangular arrays of numbers.",
        "matrix",
        ["MathematicalObjects"],
    ),
    "ColumnVectors": (
        r"\text{Column Vectors}",
        "Matrices with a single column.",
        "matrix",
        ["Matrices"],
    ),
    "SquareMatrices": (
        r"\text{Square Matrices}",
        "Matrices with as many rows as columns.",
        "matrix",
        ["Matrices"],
    ),
    "SymmetricMatrices": (
        r"\text{Symmetric Matrices}",
        "Square matrices equal to their own transpose.",
        "matrix",
        ["SquareMatrices"],
    ),
    "PositiveDefiniteMatrices": (
        r"\text{Positive Definite Matrices}",
        r"Real symmetric matrices $A$ with $v^{T} A v > 0$ for every nonzero $v$.",
        "matrix",
        ["SymmetricMatrices", "DiagonalizableMatrices", "InvertibleRealMatrices"],
    ),
    "DiagonalMatrices": (
        r"\text{Diagonal Matrices}",
        "Square matrices whose entries off the diagonal are all zero.",
        "matrix",
        ["SymmetricMatrices", "DiagonalizableMatrices", "JordanNormalForms"],
    ),
    "JordanNormalForms": (
        r"\text{Jordan Normal Forms}",
        "Square matrices already in Jordan normal form: Jordan blocks along the diagonal.",
        "matrix",
        ["SquareMatrices"],
    ),
    "NilpotentMatrices": (
        r"\text{Nilpotent Matrices}",
        r"Square matrices $N$ with $N^{k} = 0$ for some $k$.",
        "matrix",
        ["SquareMatrices", "SingularMatrices"],
    ),
    "DiagonalizableMatrices": (
        r"\text{Diagonalizable Matrices}",
        "Square matrices similar, over the complex numbers, to a diagonal matrix.",
        "matrix",
        ["SquareMatrices"],
    ),
    "SingularMatrices": (
        r"\text{Singular Matrices}",
        "Square matrices with determinant zero.",
        "matrix",
        ["SquareMatrices"],
    ),
    "InvertibleMatrices": (
        r"\text{Invertible Matrices}",
        "Square matrices with nonzero determinant. Entries may be any exact complex numbers.",
        "matrix",
        ["SquareMatrices"],
    ),
    "InvertibleRealMatrices": (
        r"\text{Invertible Real Matrices}",
        "Invertible matrices with real entries.",
        "matrix",
        ["InvertibleMatrices"],
    ),
    "InvertibleRationalMatrices": (
        r"\text{Invertible Rational Matrices}",
        "Invertible matrices with rational entries.",
        "matrix",
        ["InvertibleRealMatrices"],
    ),
    "InvertibleIntegerMatrices": (
        r"\text{Invertible Integer Matrices}",
        r"Integer matrices whose inverse is an integer matrix too: determinant $\pm 1$.",
        "matrix",
        ["InvertibleRationalMatrices"],
    ),
    "SpecialLinearIntegerMatrices": (
        r"\text{Special Linear Integer Matrices}",
        r"Integer matrices with determinant $1$.",
        "matrix",
        ["InvertibleIntegerMatrices"],
    ),
    "OrthogonalMatrices": (
        r"\text{Orthogonal Matrices}",
        r"Real matrices $Q$ with $Q Q^{T} = I$.",
        "matrix",
        ["InvertibleRealMatrices", "DiagonalizableMatrices"],
    ),
    "RotationMatrices": (
        r"\text{Rotation Matrices}",
        r"Orthogonal matrices with determinant $1$.",
        "matrix",
        ["OrthogonalMatrices"],
    ),
    "PermutationMatrices": (
        r"\text{Permutation Matrices}",
        "Matrices with exactly one 1 in each row and each column, and zeros elsewhere.",
        "matrix",
        ["OrthogonalMatrices", "InvertibleIntegerMatrices"],
    ),
    "CompanionMatrices": (
        r"\text{Companion Matrices}",
        "Matrices of the shape Companion Matrix produces: ones just below the diagonal, the "
        "negated coefficients of a monic polynomial in the last column.",
        "matrix",
        ["SquareMatrices"],
    ),
    "Polynomials": (
        r"\text{Polynomials}",
        "Single-variable polynomials with rational coefficients.",
        "poly",
        ["MathematicalObjects"],
    ),
    "IntegerPolynomials": (
        r"\text{Integer Polynomials}",
        "Polynomials with integer coefficients.",
        "poly",
        ["Polynomials"],
    ),
    "MonicIntegerPolynomials": (
        r"\text{Monic Integer Polynomials}",
        "Integer polynomials with leading coefficient 1.",
        "poly",
        ["IntegerPolynomials"],
    ),
    "IrreduciblePolynomials": (
        r"\text{Irreducible Polynomials}",
        "Polynomials that do not factor over the rationals.",
        "poly",
        ["Polynomials"],
    ),
    "CyclotomicPolynomials": (
        r"\text{Cyclotomic Polynomials}",
        "The minimal polynomials of the primitive roots of unity.",
        "poly",
        ["MonicIntegerPolynomials", "IrreduciblePolynomials"],
    ),
    "ChebyshevPolynomials": (
        r"\text{Chebyshev Polynomials}",
        r"The polynomials $T_{n}$ with $T_{n}(\cos\theta) = \cos n\theta$, and $U_{n}$ with "
        r"$U_{n}(\cos\theta) \sin\theta = \sin (n + 1)\theta$.",
        "poly",
        ["IntegerPolynomials"],
    ),
    "Permutations": (
        r"\text{Permutations}",
        r"Bijections of $\{0, \dots, n - 1\}$ to itself, held as the list of images.",
        "perm",
        ["MathematicalObjects"],
    ),
    "EvenPermutations": (
        r"\text{Even Permutations}",
        "Permutations that are a product of an even number of transpositions.",
        "perm",
        ["Permutations"],
    ),
    "IntegerPartitions": (
        r"\text{Integer Partitions}",
        "Ways to write a positive integer as a sum of positive integers, ignoring order.",
        "partition",
        ["MathematicalObjects"],
    ),
    "DistinctPartitions": (
        r"\text{Partitions into Distinct Parts}",
        "Integer partitions whose parts are all different.",
        "partition",
        ["IntegerPartitions"],
    ),
    "StandardYoungTableaux": (
        r"\text{Standard Young Tableaux}",
        r"Fillings of a Young diagram with $1, \dots, n$, increasing along every row and down "
        "every column.",
        "tableau",
        ["MathematicalObjects"],
    ),
    "Graphs": (
        r"\text{Graphs}",
        "Finite simple graphs, held as a vertex count and an edge list.",
        "graph",
        ["MathematicalObjects"],
    ),
    "Trees": (
        r"\text{Trees}",
        "Connected graphs without cycles.",
        "graph",
        [
            "BipartiteGraphs",
            "PlanarGraphs",
        ],
    ),
    "BipartiteGraphs": (
        r"\text{Bipartite Graphs}",
        "Graphs whose vertices split into two sets with every edge running between them.",
        "graph",
        ["Graphs"],
    ),
    "PlanarGraphs": (
        r"\text{Planar Graphs}",
        "Graphs that can be drawn in the plane without edges crossing.",
        "graph",
        ["Graphs"],
    ),
    "RegularGraphs": (
        r"\text{Regular Graphs}",
        "Graphs in which every vertex has the same degree.",
        "graph",
        ["Graphs"],
    ),
    "CompleteGraphs": (
        r"\text{Complete Graphs}",
        "Graphs with an edge between every pair of vertices.",
        "graph",
        ["RegularGraphs"],
    ),
    "Groups": (
        r"\text{Groups}",
        "Sets with an associative operation, an identity, and inverses.",
        None,
        ["MathematicalObjects"],
    ),
    "FiniteGroups": (
        r"\text{Finite Groups}",
        "Groups with finitely many elements, held by their GAP SmallGroup identifier: order "
        "and index.",
        "smallgroup",
        ["Groups"],
    ),
    "SimpleGroups": (
        r"\text{Simple Groups}",
        "Nontrivial finite groups whose only normal subgroups are the trivial group and "
        "themselves.",
        "smallgroup",
        ["FiniteGroups"],
    ),
    "DihedralGroups": (
        r"\text{Dihedral Groups}",
        r"Symmetry groups of regular polygons: $D_{n}$, of the $n$-gon, has order $2n$.",
        "smallgroup",
        ["FiniteGroups"],
    ),
    "PermutationGroups": (
        r"\text{Permutation Groups}",
        "Groups generated by explicit permutations of finitely many points.",
        "permgroup",
        ["Groups"],
    ),
    "GroupPresentations": (
        r"\text{Group Presentations}",
        "Groups given by generators and the relators they satisfy.",
        "fpgroup",
        ["Groups"],
    ),
    "FinitelyGeneratedAbelianGroups": (
        r"\text{Finitely Generated Abelian Groups}",
        "Abelian groups with finitely many generators, held as rank and torsion invariant factors.",
        "abelian",
        ["Groups"],
    ),
    "CyclicGroups": (
        r"\text{Cyclic Groups}",
        "Groups generated by a single element.",
        "abelian",
        ["FinitelyGeneratedAbelianGroups"],
    ),
    "Fields": (
        r"\text{Fields}",
        "Commutative rings in which every nonzero element has an inverse.",
        None,
        ["MathematicalObjects"],
    ),
    "FiniteFields": (
        r"\text{Finite Fields}",
        r"Fields with finitely many elements, $\mathbb{F}_{p^{k}}$, held as $p$ and $k$.",
        "finitefield",
        ["Fields"],
    ),
    "NumberFields": (
        r"\text{Number Fields}",
        "Finite extensions of the rationals, held by the reduced defining polynomial LMFDB uses.",
        "numberfield",
        ["Fields"],
    ),
    "QuadraticFields": (
        r"\text{Quadratic Fields}",
        "Number fields of degree 2.",
        "numberfield",
        ["NumberFields"],
    ),
    "CyclotomicFields": (
        r"\text{Cyclotomic Fields}",
        r"Number fields generated by a root of unity: $\mathbb{Q}(\zeta_{n})$.",
        "numberfield",
        ["NumberFields"],
    ),
    "SimpleLieAlgebras": (
        r"\text{Simple Lie Algebras}",
        "Complex simple Lie algebras, held by Cartan type: series and rank.",
        "cartan",
        ["MathematicalObjects"],
    ),
    "Knots": (
        r"\text{Knots}",
        "Specific knots, named the standard way.",
        "knot",
        ["MathematicalObjects"],
    ),
    "TorusKnots": (
        r"\text{Torus Knots}",
        "Knots that lie on the surface of an unknotted torus.",
        "knot",
        ["Knots"],
    ),
    "AlternatingKnots": (
        r"\text{Alternating Knots}",
        "Knots with a diagram whose crossings alternate over and under.",
        "knot",
        ["Knots"],
    ),
    "AmphichiralKnots": (
        r"\text{Amphichiral Knots}",
        "Knots equivalent to their own mirror image.",
        "knot",
        ["Knots"],
    ),
    "TwoBridgeKnots": (
        r"\text{Two-Bridge Knots}",
        "Knots with bridge number two.",
        "knot",
        ["Knots"],
    ),
    "BraidWords": (
        r"\text{Braid Words}",
        r"Words in the Artin generators $\sigma_{i}$ of a braid group, held as the number of "
        "strands and the signed generator indices.",
        "braid",
        ["MathematicalObjects"],
    ),
    "ClosedSurfaces": (
        r"\text{Closed Surfaces}",
        "Compact surfaces without boundary, held as orientability and genus.",
        "surface",
        ["MathematicalObjects"],
    ),
    "SimplicialComplexes": (
        r"\text{Simplicial Complexes}",
        "Finite abstract simplicial complexes, held as their maximal faces.",
        "simplicial",
        ["MathematicalObjects"],
    ),
    "ConvexPolytopes": (
        r"\text{Convex Polytopes}",
        "Convex hulls of finitely many points, held as their vertices.",
        "polytope",
        ["MathematicalObjects"],
    ),
    "ConvexPolygons": (
        r"\text{Convex Polygons}",
        "Convex polytopes in the plane.",
        "polytope",
        ["ConvexPolytopes"],
    ),
    "Triangles": (
        r"\text{Triangles}",
        "Convex polygons with three vertices.",
        "polytope",
        ["ConvexPolygons"],
    ),
    "ConvexPolyhedra": (
        r"\text{Convex Polyhedra}",
        "Convex polytopes in three dimensions.",
        "polytope",
        ["ConvexPolytopes"],
    ),
    "PlatonicSolids": (
        r"\text{Platonic Solids}",
        "Convex polyhedra whose faces are congruent regular polygons, with the same number "
        "meeting at every vertex.",
        "polytope",
        ["ConvexPolyhedra"],
    ),
    "PlaneCurves": (
        r"\text{Plane Algebraic Curves}",
        r"Zero sets of a polynomial $F(x, y)$, held as $F$ scaled to coprime integer "
        "coefficients.",
        "curve",
        ["MathematicalObjects"],
    ),
    "EllipticCurves": (
        r"\text{Elliptic Curves}",
        "Smooth plane cubics in Weierstrass form.",
        "curve",
        ["PlaneCurves"],
    ),
    "RealFunctions": (
        r"\text{Real Functions}",
        "Functions from the real numbers to the real numbers.",
        None,
        ["MathematicalObjects"],
    ),
    "ElementaryFunctions": (
        r"\text{Elementary Functions}",
        "Functions built from polynomials, exponentials, logarithms, roots and trigonometric "
        "functions.",
        None,
        ["RealFunctions"],
    ),
    "RationalFunctions": (
        r"\text{Rational Functions}",
        "Quotients of two polynomials.",
        None,
        ["ElementaryFunctions"],
    ),
    "EvenFunctions": (
        r"\text{Even Functions}",
        r"Functions with $f(-x) = f(x)$.",
        None,
        ["ElementaryFunctions"],
    ),
    "OddFunctions": (
        r"\text{Odd Functions}",
        r"Functions with $f(-x) = -f(x)$.",
        None,
        ["ElementaryFunctions"],
    ),
    "DFiniteFunctions": (
        r"\text{D-finite Functions}",
        "Functions satisfying a linear differential equation with polynomial coefficients — "
        "the generating functions of P-recursive sequences. Held as that equation and the "
        "initial values at 0.",
        "dfinite",
        ["RealFunctions"],
    ),
    "OrdinaryDifferentialEquations": (
        r"\text{Ordinary Differential Equations}",
        "Equations relating a function of one variable to its derivatives.",
        "expr",
        ["Expressions"],
    ),
    "LinearConstantCoefficientODEs": (
        r"\text{Linear ODEs with Constant Coefficients}",
        "Linear ordinary differential equations whose coefficients are constants.",
        "expr",
        ["OrdinaryDifferentialEquations"],
    ),
}

SECTIONS: dict[str, Specimen] = {
    "NumberTheory": (r"\text{Number Theory}", "Integers, residues and algebraic numbers."),
    "SequencesAndRecurrences": (
        r"\text{Sequences and Recurrences}",
        "Sequences given by their terms, a formula, or a recurrence.",
    ),
    "LinearAlgebra": (
        r"\text{Linear Algebra}",
        "Matrices and the operations that act on them.",
    ),
    "PolynomialAlgebra": (
        r"\text{Polynomial Algebra}",
        "Single-variable polynomials and the operations that act on them.",
    ),
    "Combinatorics": (
        r"\text{Combinatorics}",
        "Permutations, partitions and tableaux.",
    ),
    "GraphTheory": (r"\text{Graph Theory}", "Finite simple graphs and their families."),
    "GroupTheory": (
        r"\text{Group Theory}",
        "Groups, given abstractly, by permutations, or by a presentation.",
    ),
    "FieldsAndLieAlgebras": (
        r"\text{Fields and Lie Algebras}",
        "Finite fields, number fields, and the simple Lie algebras.",
    ),
    "KnotTheory": (
        r"\text{Topology and Knots}",
        "Knots, braids, surfaces and simplicial complexes, and the matrices and polynomials "
        "that identify them.",
    ),
    "Geometry": (r"\text{Geometry}", "Convex polytopes and plane algebraic curves."),
    "Analysis": (
        r"\text{Analysis}",
        "Real functions and the differential equations they satisfy.",
    ),
    "Values": (
        r"\text{Values}",
        "Truth values, and exact values no narrower type holds.",
    ),
    "MatrixOperations": (
        r"\text{Matrix Operations}",
        "Operations taking matrices as "
        "their input: characteristic polynomials, inverses, "
        "determinants, sums.",
    ),
    "PolynomialOperations": (
        r"\text{Polynomial Operations}",
        "Operations taking polynomials as their input: companion matrices, degree.",
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


def matrix_instance(
    rows: list[list[Cell]], type_keys: list[str], description: str | None = None
) -> Instance:
    data = matrix(rows)
    return pmatrix(rows), description, [(type_key, data) for type_key in type_keys]


def instance(
    latex: str, data: Data, type_keys: list[str], description: str | None = None
) -> Instance:
    return latex, description, [(type_key, data) for type_key in type_keys]


NUMBERS: dict[str, Instance] = {
    "zero": instance("0", integer(0), ["Integers"]),
    "neg_one": instance("-1", integer(-1), ["Integers"]),
    "neg_seven": instance("-7", integer(-7), ["Integers"]),
    "one": instance("1", integer(1), ["PositiveIntegers"]),
    "four": instance("4", integer(4), ["PositiveIntegers"]),
    "six": instance("6", integer(6), ["PositiveIntegers"]),
    "ten": instance("10", integer(10), ["PositiveIntegers"]),
    "twelve": instance("12", integer(12), ["PositiveIntegers"]),
    "fourteen": instance("14", integer(14), ["PositiveIntegers"]),
    "two": instance("2", integer(2), ["PrimeNumbers"]),
    "three": instance("3", integer(3), ["PrimeNumbers"]),
    "five": instance("5", integer(5), ["PrimeNumbers"]),
    "seven": instance("7", integer(7), ["PrimeNumbers"]),
    "thirteen": instance("13", integer(13), ["PrimeNumbers"]),
    "half": instance(r"\frac{1}{2}", rational(1, 2), ["RationalNumbers"]),
    "minus_half": instance(r"- \frac{1}{2}", rational(-1, 2), ["RationalNumbers"]),
    "three_quarters": instance(r"\frac{3}{4}", rational(3, 4), ["RationalNumbers"]),
    "twenty_two_sevenths": instance(
        r"\frac{22}{7}",
        rational(22, 7),
        ["RationalNumbers"],
        r"A classical approximation to $\pi$.",
    ),
    "four_mod_12": instance(r"4 \bmod 12", residue(4, 12), ["ResidueClasses"]),
    "six_mod_9": instance(r"6 \bmod 9", residue(6, 9), ["ResidueClasses"]),
    "zero_mod_5": instance(r"0 \bmod 5", residue(0, 5), ["ResidueClasses"]),
    "five_mod_12": instance(
        r"5 \bmod 12",
        residue(5, 12),
        ["UnitsModN"],
        r"Its own inverse. No unit modulo 12 is a primitive root: every one squares to $1$.",
    ),
    "three_mod_8": instance(r"3 \bmod 8", residue(3, 8), ["UnitsModN"]),
    "four_mod_7": instance(
        r"4 \bmod 7", residue(4, 7), ["UnitsModN"], r"Order 3: its powers are $4, 2, 1$."
    ),
    "three_mod_7": instance(
        r"3 \bmod 7",
        residue(3, 7),
        ["PrimitiveRoots"],
        r"Its powers run through every unit: $3, 2, 6, 4, 5, 1$.",
    ),
    "two_mod_5": instance(r"2 \bmod 5", residue(2, 5), ["PrimitiveRoots"]),
    "three_mod_10": instance(r"3 \bmod 10", residue(3, 10), ["PrimitiveRoots"]),
    "half_sqrt2": instance(r"\frac{\sqrt{2}}{2}", algebraic([-1, 0, 2], 1), ["AlgebraicNumbers"]),
    "half_i": instance(r"\frac{i}{2}", algebraic([1, 0, 4], 1), ["AlgebraicNumbers"]),
    "cbrt_half": instance(
        r"\frac{2^{\frac{2}{3}}}{2}",
        algebraic([-1, 0, 0, 2], 0),
        ["AlgebraicNumbers"],
        r"The real cube root of $\frac{1}{2}$.",
    ),
    "sqrt2": instance(r"\sqrt{2}", algebraic([-2, 0, 1], 1), ["AlgebraicIntegers"]),
    "golden_ratio": instance(
        r"\frac{1}{2} + \frac{\sqrt{5}}{2}",
        algebraic([-1, -1, 1], 1),
        ["AlgebraicIntegers"],
        r"The golden ratio, the larger root of $x^{2} - x - 1$.",
    ),
    "cbrt2": instance(r"\sqrt[3]{2}", algebraic([-2, 0, 0, 1], 0), ["AlgebraicIntegers"]),
    "i": instance(
        "i",
        algebraic([1, 0, 1], 1),
        ["RootsOfUnity", "GaussianIntegers"],
        "A fourth root of unity, and a unit of the Gaussian integers.",
    ),
    "omega": instance(
        r"- \frac{1}{2} + \frac{\sqrt{3} i}{2}",
        algebraic([1, 1, 1], 1),
        ["RootsOfUnity"],
        r"$e^{2 \pi i / 3}$, a primitive cube root of unity.",
    ),
    "zeta5": instance(r"e^{\frac{2 i \pi}{5}}", algebraic([1, 1, 1, 1, 1], 3), ["RootsOfUnity"]),
    "three_plus_4i": instance(
        "3 + 4 i",
        algebraic([25, -6, 1], 1),
        ["GaussianIntegers"],
        r"Norm $25$: it factors as $(2 + i)^{2}$ times a unit.",
    ),
    "two_i": instance("2 i", algebraic([4, 0, 1], 1), ["GaussianIntegers"]),
    "one_plus_i": instance(
        "1 + i",
        algebraic([2, -2, 1], 1),
        ["GaussianPrimes"],
        r"Norm $2$. The only Gaussian prime dividing $2$, up to units.",
    ),
    "two_plus_i": instance(
        "2 + i",
        algebraic([5, -4, 1], 1),
        ["GaussianPrimes"],
        r"Norm $5$: the rational prime $5$ splits as $(2 + i)(2 - i)$.",
    ),
    "three_plus_2i": instance(
        "3 + 2 i", algebraic([13, -6, 1], 1), ["GaussianPrimes"], r"Norm $13$."
    ),
    "true": instance(r"\text{True}", {"bool": True}, ["Booleans"]),
    "false": instance(r"\text{False}", {"bool": False}, ["Booleans"]),
    "pi": instance(r"\pi", expr("pi"), ["Expressions"]),
    "e": instance("e", expr("E"), ["Expressions"], "Euler's number."),
    "zeta3": instance(
        r"\zeta\left(3\right)",
        expr("zeta(Integer(3))"),
        ["Expressions"],
        "Apéry's constant, proved irrational with the help of the Apéry numbers.",
    ),
}

SEQUENCES: dict[str, Instance] = {
    "first_fibonacci": instance(
        r"\left( 1, \  1, \  2, \  3, \  5\right)",
        {"tuple": [integer(v) for v in (1, 1, 2, 3, 5)]},
        ["FiniteSequences"],
    ),
    "first_primes": instance(
        r"\left( 2, \  3, \  5, \  7, \  11\right)",
        {"tuple": [integer(v) for v in (2, 3, 5, 7, 11)]},
        ["FiniteSequences"],
    ),
    "first_factorials": instance(
        r"\left( 1, \  2, \  6, \  24, \  120\right)",
        {"tuple": [integer(v) for v in (1, 2, 6, 24, 120)]},
        ["FiniteSequences"],
    ),
    "squares": instance(
        r"\left(n^{2}\right)_{n \geq 0}",
        seq("Pow(Symbol('n'), Integer(2))", 0),
        ["SequencesByFormula"],
    ),
    "powers_of_two": instance(
        r"\left(2^{n}\right)_{n \geq 0}",
        seq("Pow(Integer(2), Symbol('n'))", 0),
        ["SequencesByFormula"],
    ),
    "factorials": instance(
        r"\left(n!\right)_{n \geq 0}",
        seq("factorial(Symbol('n'))", 0),
        ["SequencesByFormula"],
    ),
    "prime_counting": instance(
        r"\left(\operatorname{primepi}{\left(n \right)}\right)_{n \geq 1}",
        seq("primepi(Symbol('n'))", 1),
        ["ArithmeticFunctions"],
        r"$\pi(n)$, the number of primes up to $n$.",
    ),
    "big_omega": instance(
        r"\left(\Omega\left(n\right)\right)_{n \geq 1}",
        seq("primeomega(Symbol('n'))", 1),
        ["ArithmeticFunctions"],
        "The number of prime factors of n, counted with multiplicity. Additive, not "
        "multiplicative.",
    ),
    "little_omega": instance(
        r"\left(\nu\left(n\right)\right)_{n \geq 1}",
        seq("primenu(Symbol('n'))", 1),
        ["ArithmeticFunctions"],
        r"The number of distinct primes dividing $n$, often written $\omega(n)$.",
    ),
    "totient": instance(
        r"\left(\phi\left(n\right)\right)_{n \geq 1}",
        seq("totient(Symbol('n'))", 1),
        ["MultiplicativeFunctions"],
        "Euler's totient, as a sequence.",
    ),
    "divisor_sum": instance(
        r"\left(\sigma\left(n\right)\right)_{n \geq 1}",
        seq("divisor_sigma(Symbol('n'))", 1),
        ["MultiplicativeFunctions"],
        r"The sum of the divisors of $n$.",
    ),
    "mobius": instance(
        r"\left(\mu\left(n\right)\right)_{n \geq 1}",
        seq("mobius(Symbol('n'))", 1),
        ["MultiplicativeFunctions"],
        "The Möbius function.",
    ),
    "catalan_numbers": instance(
        r"\left(n + 2\right) a_{n + 1} - 2 \left(2 n + 1\right) a_{n} = 0, \quad a_{0} = 1",
        holonomic([[-2, -4], [2, 1]], [1]),
        ["HolonomicSequences"],
        r"The Catalan numbers $1, 1, 2, 5, 14, 42, \dots$",
    ),
    "central_binomials": instance(
        r"\left(n + 1\right) a_{n + 1} - 2 \left(2 n + 1\right) a_{n} = 0, \quad a_{0} = 1",
        holonomic([[-2, -4], [1, 1]], [1]),
        ["HolonomicSequences"],
        r"The central binomial coefficients $\binom{2n}{n}$: $1, 2, 6, 20, 70, \dots$",
    ),
    "apery_numbers": instance(
        r"\left(n + 2\right)^{3} a_{n + 2} - \left(2 n + 3\right) \left(17 n^{2} + 51 n + 39\right)"
        r" a_{n + 1} + \left(n + 1\right)^{3} a_{n} = 0, \quad a_{0} = 1, a_{1} = 5",
        holonomic([[1, 3, 3, 1], [-117, -231, -153, -34], [8, 12, 6, 1]], [1, 5]),
        ["HolonomicSequences"],
        r"The Apéry numbers $1, 5, 73, 1445, \dots$, behind the irrationality of $\zeta(3)$.",
    ),
    "fibonacci": instance(
        r"a_{n} = a_{n - 1} + a_{n - 2}, \quad a_{0} = 0, a_{1} = 1",
        recurrence([1, 1], [0, 1]),
        ["LinearRecurrences"],
        "The Fibonacci numbers.",
    ),
    "lucas": instance(
        r"a_{n} = a_{n - 1} + a_{n - 2}, \quad a_{0} = 2, a_{1} = 1",
        recurrence([1, 1], [2, 1]),
        ["LinearRecurrences"],
        "The Lucas numbers: Fibonacci's recurrence from different initial values.",
    ),
    "pell": instance(
        r"a_{n} = 2 a_{n - 1} + a_{n - 2}, \quad a_{0} = 0, a_{1} = 1",
        recurrence([2, 1], [0, 1]),
        ["LinearRecurrences"],
        "The Pell numbers.",
    ),
}

MATRICES: dict[str, Instance] = {
    "A": matrix_instance(
        [[2, 1], [1, 2]], ["PositiveDefiniteMatrices", "InvertibleRationalMatrices"]
    ),
    "B": matrix_instance(
        [[1, 0], [0, 1]],
        [
            "DiagonalMatrices",
            "PositiveDefiniteMatrices",
            "PermutationMatrices",
            "RotationMatrices",
            "SpecialLinearIntegerMatrices",
        ],
        "The identity.",
    ),
    "D": matrix_instance(
        [[0, 1], [1, 0]],
        ["SymmetricMatrices", "PermutationMatrices", "CompanionMatrices"],
    ),
    "E": matrix_instance(
        [[3, 1], [1, 3]], ["PositiveDefiniteMatrices", "InvertibleRationalMatrices"]
    ),
    "C": matrix_instance(
        [[0, -3], [1, 4]],
        ["CompanionMatrices", "InvertibleRationalMatrices", "DiagonalizableMatrices"],
        "The companion matrix of "
        r"$x^{2} - 4 x + 3$ — its own characteristic polynomial closes the loop.",
    ),
    "V3": matrix_instance(
        seifert(2),
        ["JordanNormalForms", "SpecialLinearIntegerMatrices"],
        "The Seifert matrix of the trefoil.",
    ),
    "V5": matrix_instance(
        seifert(4),
        ["JordanNormalForms", "SpecialLinearIntegerMatrices"],
        r"The Seifert matrix of $5_1$.",
    ),
    "V7": matrix_instance(
        seifert(6),
        ["JordanNormalForms", "SpecialLinearIntegerMatrices"],
        r"The Seifert matrix of $7_1$.",
    ),
    "S": matrix_instance(
        [[1, 2], [2, 4]],
        ["SymmetricMatrices", "SingularMatrices", "DiagonalizableMatrices"],
        "Singular: its rows are proportional, so it collapses the plane onto a line.",
    ),
    "CompPhi6": matrix_instance(
        [[0, -1], [1, 1]],
        ["CompanionMatrices", "SpecialLinearIntegerMatrices", "DiagonalizableMatrices"],
        r"The companion matrix of $x^{2} - x + 1$ — the trefoil's polynomial, "
        "back in linear algebra.",
    ),
    "wide": matrix_instance([[1, 2, 3], [4, 5, 6]], ["Matrices"]),
    "tall": matrix_instance([[1, 0], [0, 1], [1, 1]], ["Matrices"]),
    "row": matrix_instance([[1, 2]], ["Matrices"], "A row vector."),
    "e1": matrix_instance([[1], [0]], ["ColumnVectors"]),
    "e2": matrix_instance([[0], [1]], ["ColumnVectors"]),
    "v123": matrix_instance([[1], [2], [3]], ["ColumnVectors"]),
    "cartan_a2": matrix_instance(
        [[2, -1], [-1, 2]],
        ["PositiveDefiniteMatrices", "InvertibleRationalMatrices"],
        r"The Cartan matrix of $\mathfrak{sl}_{3}$.",
    ),
    "cat_map": matrix_instance(
        [[2, 1], [1, 1]],
        ["PositiveDefiniteMatrices", "SpecialLinearIntegerMatrices"],
        "Arnold's cat map on the torus.",
    ),
    "cat_map_inverse": matrix_instance(
        [[1, -1], [-1, 2]], ["PositiveDefiniteMatrices", "SpecialLinearIntegerMatrices"]
    ),
    "diag12": matrix_instance(
        [[1, 0], [0, 2]],
        ["DiagonalMatrices", "PositiveDefiniteMatrices", "InvertibleRationalMatrices"],
    ),
    "zero2": matrix_instance(
        [[0, 0], [0, 0]], ["DiagonalMatrices", "NilpotentMatrices"], "The zero matrix."
    ),
    "reflection": matrix_instance(
        [[1, 0], [0, -1]],
        ["DiagonalMatrices", "OrthogonalMatrices", "InvertibleIntegerMatrices"],
        "Reflection in the horizontal axis.",
    ),
    "shear": matrix_instance(
        [[1, 1], [0, 1]], ["JordanNormalForms", "SpecialLinearIntegerMatrices"]
    ),
    "nilpotent_block": matrix_instance(
        [[0, 1], [0, 0]], ["JordanNormalForms", "NilpotentMatrices"]
    ),
    "jordan3": matrix_instance(
        [[2, 1, 0], [0, 2, 0], [0, 0, 3]], ["JordanNormalForms", "InvertibleRationalMatrices"]
    ),
    "nilpotent_block3": matrix_instance(
        [[0, 1, 0], [0, 0, 1], [0, 0, 0]], ["JordanNormalForms", "NilpotentMatrices"]
    ),
    "nilpotent_dense": matrix_instance(
        [[2, -4], [1, -2]], ["NilpotentMatrices"], "Squares to zero, with no zero entry."
    ),
    "nilpotent_symmetric": matrix_instance(
        [[1, I_CELL], [I_CELL, -1]],
        ["SymmetricMatrices", "NilpotentMatrices"],
        "Symmetric yet not diagonalizable — possible only with complex entries.",
    ),
    "upper_triangular": matrix_instance(
        [[1, 1], [0, 2]], ["DiagonalizableMatrices", "InvertibleRationalMatrices"]
    ),
    "real_upper_triangular": matrix_instance(
        [[2, SQRT3_CELL], [0, 1]], ["DiagonalizableMatrices", "InvertibleRealMatrices"]
    ),
    "singular3": matrix_instance(
        [[1, 2, 3], [4, 5, 6], [7, 8, 9]], ["SingularMatrices", "DiagonalizableMatrices"]
    ),
    "ones2": matrix_instance(
        [[1, 1], [1, 1]],
        ["SymmetricMatrices", "SingularMatrices", "DiagonalizableMatrices"],
    ),
    "complex_shear": matrix_instance([[1, I_CELL], [0, 1]], ["InvertibleMatrices"]),
    "complex_symmetric": matrix_instance(
        [[0, I_CELL], [I_CELL, 0]],
        ["SymmetricMatrices", "DiagonalizableMatrices", "InvertibleMatrices"],
    ),
    "complex_jordan": matrix_instance(
        [[I_CELL, 1], [0, I_CELL]], ["JordanNormalForms", "InvertibleMatrices"]
    ),
    "real_shear": matrix_instance([[1, SQRT2_CELL], [0, 1]], ["InvertibleRealMatrices"]),
    "real_positive_definite": matrix_instance(
        [[SQRT2_CELL, 1], [1, SQRT2_CELL]], ["PositiveDefiniteMatrices"]
    ),
    "fibonacci_matrix": matrix_instance(
        [[1, 1], [1, 0]],
        ["SymmetricMatrices", "InvertibleIntegerMatrices", "DiagonalizableMatrices"],
        r"Its $n$th power holds the Fibonacci numbers $F_{n+1}, F_{n}, F_{n-1}$.",
    ),
    "rational_reflection": matrix_instance(
        [[fraction(3, 5), fraction(4, 5)], [fraction(4, 5), fraction(-3, 5)]],
        ["SymmetricMatrices", "OrthogonalMatrices", "InvertibleRationalMatrices"],
    ),
    "rotation90": matrix_instance(
        [[0, -1], [1, 0]],
        ["RotationMatrices", "SpecialLinearIntegerMatrices", "CompanionMatrices"],
        "A quarter turn.",
    ),
    "rational_rotation": matrix_instance(
        [[fraction(3, 5), fraction(-4, 5)], [fraction(4, 5), fraction(3, 5)]],
        ["RotationMatrices", "InvertibleRationalMatrices"],
        "Rotation through the angle of a 3-4-5 triangle.",
    ),
    "rotation45": matrix_instance(
        [[HALF_SQRT2_CELL, MINUS_HALF_SQRT2_CELL], [HALF_SQRT2_CELL, HALF_SQRT2_CELL]],
        ["RotationMatrices"],
        "An eighth of a turn.",
    ),
    "cycle3": matrix_instance(
        [[0, 0, 1], [1, 0, 0], [0, 1, 0]],
        [
            "PermutationMatrices",
            "RotationMatrices",
            "SpecialLinearIntegerMatrices",
            "CompanionMatrices",
        ],
        r"Cycles the coordinate axes: a third of a turn about $(1, 1, 1)$.",
    ),
    "swap3": matrix_instance(
        [[0, 1, 0], [1, 0, 0], [0, 0, 1]], ["SymmetricMatrices", "PermutationMatrices"]
    ),
}

POLYNOMIALS: dict[str, Instance] = {
    "P": instance(
        r"x^{2} - 4 x + 3",
        polynomial(3, -4, 1),
        ["MonicIntegerPolynomials", "RationalFunctions"],
    ),
    "Q": instance(r"x^{2} - 2 x + 1", polynomial(1, -2, 1), ["MonicIntegerPolynomials"]),
    "R": instance(
        r"x^{2} - 1",
        polynomial(-1, 0, 1),
        ["MonicIntegerPolynomials", "RationalFunctions", "EvenFunctions"],
    ),
    "Phi4": instance(
        r"x^{2} + 1",
        polynomial(1, 0, 1),
        ["CyclotomicPolynomials"],
        r"The 4th cyclotomic polynomial, whose roots are $\pm i$.",
    ),
    "Phi6": instance(
        r"x^{2} - x + 1",
        polynomial(1, -1, 1),
        ["CyclotomicPolynomials", "RationalFunctions"],
        "The 6th cyclotomic polynomial — and the Alexander polynomial of the trefoil.",
    ),
    "Phi10": instance(
        r"x^{4} - x^{3} + x^{2} - x + 1",
        polynomial(1, -1, 1, -1, 1),
        ["CyclotomicPolynomials"],
        r"The 10th cyclotomic polynomial — and the Alexander polynomial of $5_1$.",
    ),
    "Phi14": instance(
        r"x^{6} - x^{5} + x^{4} - x^{3} + x^{2} - x + 1",
        polynomial(1, -1, 1, -1, 1, -1, 1),
        ["CyclotomicPolynomials"],
        r"The 14th cyclotomic polynomial — and the Alexander polynomial of $7_1$.",
    ),
    "cube_minus_one": instance(r"x^{3} - 1", polynomial(-1, 0, 0, 1), ["MonicIntegerPolynomials"]),
    "square_minus_two": instance(
        r"x^{2} - 2",
        polynomial(-2, 0, 1),
        ["MonicIntegerPolynomials", "IrreduciblePolynomials"],
    ),
    "golden_polynomial": instance(
        r"x^{2} - x - 1",
        polynomial(-1, -1, 1),
        ["MonicIntegerPolynomials", "IrreduciblePolynomials"],
        "The minimal polynomial of the golden ratio.",
    ),
    "cube_minus_two": instance(
        r"x^{3} - 2",
        polynomial(-2, 0, 0, 1),
        ["MonicIntegerPolynomials", "IrreduciblePolynomials"],
    ),
    "plastic_polynomial": instance(
        r"x^{3} - x - 1",
        polynomial(-1, -1, 0, 1),
        ["MonicIntegerPolynomials", "IrreduciblePolynomials"],
        "Its real root is the plastic number.",
    ),
    "two_square_plus_one": instance(
        r"2 x^{2} + 1",
        polynomial(1, 0, 2),
        ["IntegerPolynomials", "IrreduciblePolynomials"],
    ),
    "integer_quadratic": instance(
        r"2 x^{2} + 3 x + 1", polynomial(1, 3, 2), ["IntegerPolynomials"]
    ),
    "integer_cubic": instance(r"2 x^{3} - 2 x", polynomial(0, -2, 0, 2), ["IntegerPolynomials"]),
    "integer_quadratic2": instance(
        r"6 x^{2} - x - 1", polynomial(-1, -1, 6), ["IntegerPolynomials"]
    ),
    "rational_quadratic": instance(
        r"x^{2} - \frac{1}{4}", polynomial(rational(-1, 4), 0, 1), ["Polynomials"]
    ),
    "rational_quadratic2": instance(
        r"\frac{x^{2}}{2} - \frac{x}{2}",
        polynomial(0, rational(-1, 2), rational(1, 2)),
        ["Polynomials"],
    ),
    "rational_cubic": instance(
        r"\frac{x^{3}}{3} - x", polynomial(0, -1, 0, rational(1, 3)), ["Polynomials"]
    ),
    "irreducible_quadratic": instance(
        r"x^{2} - \frac{1}{2}", polynomial(rational(-1, 2), 0, 1), ["IrreduciblePolynomials"]
    ),
    "irreducible_quadratic2": instance(
        r"\frac{x^{2}}{2} + \frac{1}{3}",
        polynomial(rational(1, 3), 0, rational(1, 2)),
        ["IrreduciblePolynomials"],
    ),
    "irreducible_cubic": instance(
        r"x^{3} - \frac{1}{2}",
        polynomial(rational(-1, 2), 0, 0, 1),
        ["IrreduciblePolynomials"],
    ),
    "T2": instance(
        r"2 x^{2} - 1",
        polynomial(-1, 0, 2),
        ["ChebyshevPolynomials", "IrreduciblePolynomials"],
        r"$T_{2}$: $\cos 2\theta = 2\cos^{2}\theta - 1$.",
    ),
    "T3": instance(
        r"4 x^{3} - 3 x",
        polynomial(0, -3, 0, 4),
        ["ChebyshevPolynomials"],
        r"$T_{3}$: $\cos 3\theta = 4\cos^{3}\theta - 3\cos\theta$.",
    ),
    "T4": instance(
        r"8 x^{4} - 8 x^{2} + 1",
        polynomial(1, 0, -8, 0, 8),
        ["ChebyshevPolynomials", "IrreduciblePolynomials"],
        r"$T_{4}$.",
    ),
}

COMBINATORICS: dict[str, Instance] = {
    "transposition": instance(r"\left( 0\; 1\right)", {"perm": [1, 0]}, ["Permutations"]),
    "swap_last": instance(r"\left( 1\; 2\right)", {"perm": [0, 2, 1]}, ["Permutations"]),
    "four_cycle": instance(
        r"\left( 0\; 1\; 2\; 3\right)", {"perm": [1, 2, 3, 0]}, ["Permutations"]
    ),
    "three_cycle": instance(r"\left( 0\; 1\; 2\right)", {"perm": [1, 2, 0]}, ["EvenPermutations"]),
    "three_cycle_inverse": instance(
        r"\left( 0\; 2\; 1\right)", {"perm": [2, 0, 1]}, ["EvenPermutations"]
    ),
    "double_transposition": instance(
        r"\left( 0\; 1\right)\left( 2\; 3\right)",
        {"perm": [1, 0, 3, 2]},
        ["EvenPermutations"],
    ),
    "partition_22": instance(
        r"\left(2, 2\right) \vdash 4", {"partition": [2, 2]}, ["IntegerPartitions"]
    ),
    "partition_311": instance(
        r"\left(3, 1, 1\right) \vdash 5", {"partition": [3, 1, 1]}, ["IntegerPartitions"]
    ),
    "partition_2211": instance(
        r"\left(2, 2, 1, 1\right) \vdash 6", {"partition": [2, 2, 1, 1]}, ["IntegerPartitions"]
    ),
    "partition_321": instance(
        r"\left(3, 2, 1\right) \vdash 6",
        {"partition": [3, 2, 1]},
        ["DistinctPartitions"],
        "The staircase partition.",
    ),
    "partition_41": instance(
        r"\left(4, 1\right) \vdash 5", {"partition": [4, 1]}, ["DistinctPartitions"]
    ),
    "partition_5": instance(r"\left(5\right) \vdash 5", {"partition": [5]}, ["DistinctPartitions"]),
    "tableau_32": instance(
        r"\begin{array}{lll}1 & 2 & 3 \\ 4 & 5\end{array}",
        {"tableau": [[1, 2, 3], [4, 5]]},
        ["StandardYoungTableaux"],
    ),
    "tableau_32_columns": instance(
        r"\begin{array}{lll}1 & 3 & 5 \\ 2 & 4\end{array}",
        {"tableau": [[1, 3, 5], [2, 4]]},
        ["StandardYoungTableaux"],
    ),
    "tableau_211": instance(
        r"\begin{array}{ll}1 & 2 \\ 3 \\ 4\end{array}",
        {"tableau": [[1, 2], [3], [4]]},
        ["StandardYoungTableaux"],
    ),
}

PETERSEN_EDGES = [
    *((i, (i + 1) % 5) for i in range(5)),
    *((i, i + 5) for i in range(5)),
    *((i + 5, (i + 2) % 5 + 5) for i in range(5)),
]
CUBE_EDGES = [(v, v ^ bit) for v in range(8) for bit in (1, 2, 4) if v < v ^ bit]

GRAPHS: dict[str, Instance] = {
    "path4": instance("P_{4}", path_graph(4), ["Trees"], "The path on four vertices."),
    "claw": instance(
        "K_{1,3}",
        graph(4, [(0, 1), (0, 2), (0, 3)]),
        ["Trees"],
        "The claw: one vertex joined to three others.",
    ),
    "path5": instance("P_{5}", path_graph(5), ["Trees"]),
    "cycle4": instance(
        "C_{4}", cycle_graph(4), ["BipartiteGraphs", "PlanarGraphs", "RegularGraphs"]
    ),
    "k33": instance(
        "K_{3,3}",
        graph(6, [(i, j) for i in range(3) for j in range(3, 6)]),
        ["BipartiteGraphs", "RegularGraphs"],
        "Not planar: the utilities graph.",
    ),
    "cube_graph": instance(
        "Q_{3}",
        graph(8, CUBE_EDGES),
        ["BipartiteGraphs", "PlanarGraphs", "RegularGraphs"],
        "The vertices and edges of a cube.",
    ),
    "wheel5": instance(
        "W_{5}",
        graph(5, [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (2, 3), (3, 4), (1, 4)]),
        ["PlanarGraphs"],
        "The wheel: a hub joined to every vertex of a 4-cycle.",
    ),
    "cycle5": instance("C_{5}", cycle_graph(5), ["PlanarGraphs", "RegularGraphs"]),
    "petersen": instance(
        r"\text{Petersen graph}",
        graph(10, PETERSEN_EDGES),
        ["RegularGraphs"],
        "Three-regular on ten vertices, neither planar nor bipartite.",
    ),
    "k3": instance("K_{3}", complete_graph(3), ["CompleteGraphs", "PlanarGraphs"]),
    "k4": instance("K_{4}", complete_graph(4), ["CompleteGraphs", "PlanarGraphs"]),
    "k5": instance(
        "K_{5}",
        complete_graph(5),
        ["CompleteGraphs"],
        "The smallest complete graph that is not planar.",
    ),
}

GROUPS: dict[str, Instance] = {
    "quaternion": ("Q_{8}", "The quaternion group.", [("FiniteGroups", small_group(8, 4))]),
    "a4": (
        "A_{4}",
        "The alternating group on four letters.",
        [("FiniteGroups", small_group(12, 3))],
    ),
    "s4": (
        "S_{4}",
        "The symmetric group on four letters: the rotations of a cube.",
        [
            ("FiniteGroups", small_group(24, 12)),
            ("PermutationGroups", permgroup(4, [[1, 2, 3, 0], [1, 0, 2, 3]])),
        ],
    ),
    "a5": (
        "A_{5}",
        "The smallest nonabelian simple group: the rotations of an icosahedron.",
        [
            ("SimpleGroups", small_group(60, 5)),
            ("PermutationGroups", permgroup(5, [[1, 2, 3, 4, 0], [1, 2, 0, 3, 4]])),
        ],
    ),
    "psl27": (
        r"\mathrm{PSL}(2, 7)",
        "The simple group of order 168, the symmetries of the Fano plane.",
        [("SimpleGroups", small_group(168, 42))],
    ),
    "c7": (
        r"\mathbb{Z}/7\mathbb{Z}",
        "Cyclic of prime order, hence simple.",
        [("SimpleGroups", small_group(7, 1)), ("CyclicGroups", abelian(0, [7]))],
    ),
    "s3": (
        "S_{3}",
        r"The symmetric group on three letters, which is also $D_{3}$, the symmetries of a "
        "triangle.",
        [
            ("DihedralGroups", small_group(6, 1)),
            (
                "GroupPresentations",
                presentation(
                    ["a", "b"],
                    [[("a", 2)], [("b", 2)], [("a", 1), ("b", 1)] * 3],
                ),
            ),
        ],
    ),
    "d4": (
        "D_{4}",
        "The symmetries of a square, of order 8.",
        [("DihedralGroups", small_group(8, 3))],
    ),
    "d5": (
        "D_{5}",
        "The symmetries of a pentagon, of order 10.",
        [("DihedralGroups", small_group(10, 1))],
    ),
    "klein_four": (
        "V_{4}",
        "The Klein four-group.",
        [
            ("FiniteGroups", small_group(4, 2)),
            ("FinitelyGeneratedAbelianGroups", abelian(0, [2, 2])),
            ("PermutationGroups", permgroup(4, [[1, 0, 3, 2], [2, 3, 0, 1]])),
        ],
    ),
    "trefoil_group": (
        r"\left\langle x, y \mid x^{2} y^{-3} \right\rangle",
        "The fundamental group of the trefoil's complement, also the braid group on three strands.",
        [("GroupPresentations", presentation(["x", "y"], [[("x", 2), ("y", -3)]]))],
    ),
    "z2": (
        r"\mathbb{Z}^{2}",
        "The free abelian group of rank two.",
        [
            ("FinitelyGeneratedAbelianGroups", abelian(2, [])),
            (
                "GroupPresentations",
                presentation(["a", "b"], [[("a", 1), ("b", 1), ("a", -1), ("b", -1)]]),
            ),
        ],
    ),
    "z_plus_z2": (
        r"\mathbb{Z} \oplus \mathbb{Z}/2\mathbb{Z}",
        None,
        [("FinitelyGeneratedAbelianGroups", abelian(1, [2]))],
    ),
    "z2_plus_z4": (
        r"\mathbb{Z}/2\mathbb{Z} \oplus \mathbb{Z}/4\mathbb{Z}",
        None,
        [
            ("FiniteGroups", small_group(8, 2)),
            ("FinitelyGeneratedAbelianGroups", abelian(0, [2, 4])),
        ],
    ),
    "integers_group": (
        r"\mathbb{Z}",
        "The integers under addition: the infinite cyclic group.",
        [("CyclicGroups", abelian(1, []))],
    ),
    "c6": (
        r"\mathbb{Z}/6\mathbb{Z}",
        None,
        [("FiniteGroups", small_group(6, 2)), ("CyclicGroups", abelian(0, [6]))],
    ),
}

FIELDS: dict[str, Instance] = {
    "f2": instance(r"\mathbb{F}_{2}", {"finitefield": [2, 1]}, ["FiniteFields"]),
    "f4": instance(r"\mathbb{F}_{4}", {"finitefield": [2, 2]}, ["FiniteFields"]),
    "f9": instance(r"\mathbb{F}_{9}", {"finitefield": [3, 2]}, ["FiniteFields"]),
    "q_cbrt2": instance(r"\mathbb{Q}(\sqrt[3]{2})", number_field(-2, 0, 0, 1), ["NumberFields"]),
    "q_cbrt3": instance(r"\mathbb{Q}(\sqrt[3]{3})", number_field(-3, 0, 0, 1), ["NumberFields"]),
    "q_zeta7_plus": instance(
        r"\mathbb{Q}(\zeta_{7})^{+}",
        number_field(1, -2, -1, 1),
        ["NumberFields"],
        r"The real subfield of $\mathbb{Q}(\zeta_{7})$, generated by $2\cos(2\pi/7)$.",
    ),
    "q_sqrt2": instance(r"\mathbb{Q}(\sqrt{2})", number_field(-2, 0, 1), ["QuadraticFields"]),
    "q_sqrt5": instance(r"\mathbb{Q}(\sqrt{5})", number_field(-1, -1, 1), ["QuadraticFields"]),
    "q_sqrt_minus5": instance(
        r"\mathbb{Q}(\sqrt{-5})",
        number_field(5, 0, 1),
        ["QuadraticFields"],
        r"Here $6 = 2 \cdot 3 = (1 + \sqrt{-5})(1 - \sqrt{-5})$: factorization is not unique.",
    ),
    "q_i": instance(
        r"\mathbb{Q}(i)", number_field(1, 0, 1), ["QuadraticFields", "CyclotomicFields"]
    ),
    "q_zeta3": instance(
        r"\mathbb{Q}(\zeta_{3})",
        number_field(1, -1, 1),
        ["QuadraticFields", "CyclotomicFields"],
        r"Also $\mathbb{Q}(\sqrt{-3})$.",
    ),
    "q_zeta5": instance(
        r"\mathbb{Q}(\zeta_{5})", number_field(1, -1, 1, -1, 1), ["CyclotomicFields"]
    ),
    "q_zeta7": instance(
        r"\mathbb{Q}(\zeta_{7})", number_field(1, -1, 1, -1, 1, -1, 1), ["CyclotomicFields"]
    ),
    "q_zeta8": instance(
        r"\mathbb{Q}(\zeta_{8})", number_field(1, 0, 0, 0, 1), ["CyclotomicFields"]
    ),
    "sl2": instance(r"\mathfrak{sl}_{2}", {"cartan": ["A", 1]}, ["SimpleLieAlgebras"]),
    "sl3": instance(r"\mathfrak{sl}_{3}", {"cartan": ["A", 2]}, ["SimpleLieAlgebras"]),
    "g2": instance(
        r"\mathfrak{g}_{2}",
        {"cartan": ["G", 2]},
        ["SimpleLieAlgebras"],
        "The smallest exceptional simple Lie algebra, of dimension 14.",
    ),
    "e8": instance(
        r"\mathfrak{e}_{8}",
        {"cartan": ["E", 8]},
        ["SimpleLieAlgebras"],
        "The largest exceptional simple Lie algebra, of dimension 248.",
    ),
}

TORUS_KNOT_TYPES = ["TorusKnots", "AlternatingKnots", "TwoBridgeKnots"]

# \mathrm{} stops sympy reading these as the integers 31, 51 and 71.
TOPOLOGY: dict[str, Instance] = {
    "K3": instance(
        r"\mathrm{3}_{1}",
        knot("3_1"),
        TORUS_KNOT_TYPES,
        "The trefoil — the simplest knot that cannot be untied.",
    ),
    "K5": instance(
        r"\mathrm{5}_{1}",
        knot("5_1"),
        TORUS_KNOT_TYPES,
        "The (2, 5) torus knot: two strands, five crossings.",
    ),
    "K7": instance(
        r"\mathrm{7}_{1}",
        knot("7_1"),
        TORUS_KNOT_TYPES,
        "The (2, 7) torus knot: two strands, seven crossings.",
    ),
    "K4_1": instance(
        r"\mathrm{4}_{1}",
        knot("4_1"),
        ["AlternatingKnots", "AmphichiralKnots", "TwoBridgeKnots"],
        "The figure-eight knot.",
    ),
    "K5_2": instance(
        r"\mathrm{5}_{2}",
        knot("5_2"),
        ["AlternatingKnots", "TwoBridgeKnots"],
        "The three-twist knot.",
    ),
    "K6_1": instance(
        r"\mathrm{6}_{1}", knot("6_1"), ["AlternatingKnots", "TwoBridgeKnots"], "Stevedore's knot."
    ),
    "K6_3": instance(
        r"\mathrm{6}_{3}", knot("6_3"), ["AlternatingKnots", "AmphichiralKnots", "TwoBridgeKnots"]
    ),
    "K8_3": instance(
        r"\mathrm{8}_{3}", knot("8_3"), ["AlternatingKnots", "AmphichiralKnots", "TwoBridgeKnots"]
    ),
    "K8_19": instance(
        r"\mathrm{8}_{19}",
        knot("8_19"),
        ["TorusKnots"],
        "The (3, 4) torus knot, and the first knot in the table that is not alternating.",
    ),
    "trefoil_braid": instance(
        r"\sigma_{1}^{3}",
        {"braid": {"strands": 2, "word": [1, 1, 1]}},
        ["BraidWords"],
        "Two strands, three half-twists; its closure is the trefoil.",
    ),
    "figure_eight_braid": instance(
        r"\sigma_{1} \sigma_{2}^{-1} \sigma_{1} \sigma_{2}^{-1}",
        {"braid": {"strands": 3, "word": [1, -2, 1, -2]}},
        ["BraidWords"],
        "Its closure is the figure-eight knot.",
    ),
    "torus_braid_34": instance(
        r"\left(\sigma_{1} \sigma_{2}\right)^{4}",
        {"braid": {"strands": 3, "word": [1, 2, 1, 2, 1, 2, 1, 2]}},
        ["BraidWords"],
        r"Its closure is the $(3, 4)$ torus knot $8_{19}$.",
    ),
    "sphere": instance("S^{2}", surface(True, 0), ["ClosedSurfaces"], "The sphere."),
    "torus": instance("T^{2}", surface(True, 1), ["ClosedSurfaces"], "The torus."),
    "genus2": instance(
        r"T^{2} \# T^{2}", surface(True, 2), ["ClosedSurfaces"], "The surface of genus two."
    ),
    "projective_plane": instance(
        r"\mathbb{RP}^{2}", surface(False, 1), ["ClosedSurfaces"], "The real projective plane."
    ),
    "klein_bottle": instance(
        r"\mathbb{RP}^{2} \# \mathbb{RP}^{2}",
        surface(False, 2),
        ["ClosedSurfaces"],
        "The Klein bottle.",
    ),
    "triangle_boundary": instance(
        r"\partial \Delta^{2}",
        simplicial([(0, 1), (0, 2), (1, 2)]),
        ["SimplicialComplexes"],
        "The boundary of a triangle: a circle.",
    ),
    "tetrahedron_boundary": instance(
        r"\partial \Delta^{3}",
        simplicial([(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]),
        ["SimplicialComplexes"],
        "The boundary of a tetrahedron: a sphere.",
    ),
    "moebius_torus": instance(
        r"T^{2}_{7}",
        simplicial(
            [
                *((i, (i + 1) % 7, (i + 3) % 7) for i in range(7)),
                *((i, (i + 2) % 7, (i + 3) % 7) for i in range(7)),
            ]
        ),
        ["SimplicialComplexes"],
        "Möbius's torus: the smallest triangulation of the torus, on seven vertices.",
    ),
}

GEOMETRY: dict[str, Instance] = {
    "simplex4": instance(
        r"\operatorname{conv}\left\{0, e_{1}, e_{2}, e_{3}, e_{4}\right\}",
        lattice_polytope([(0, 0, 0, 0), *(tuple(int(i == j) for j in range(4)) for i in range(4))]),
        ["ConvexPolytopes"],
        "A four-dimensional simplex.",
    ),
    "tesseract": instance(
        r"[0, 1]^{4}",
        lattice_polytope(list(itertools.product((0, 1), repeat=4))),
        ["ConvexPolytopes"],
        "The four-dimensional cube.",
    ),
    "cross_polytope4": instance(
        r"\operatorname{conv}\left\{\pm e_{1}, \pm e_{2}, \pm e_{3}, \pm e_{4}\right\}",
        lattice_polytope(
            [tuple(sign if i == j else 0 for j in range(4)) for i in range(4) for sign in (1, -1)]
        ),
        ["ConvexPolytopes"],
        "The 16-cell.",
    ),
    "unit_square": polygon_instance([(0, 0), (0, 1), (1, 0), (1, 1)], ["ConvexPolygons"]),
    "trapezoid": polygon_instance([(0, 0), (1, 1), (2, 1), (3, 0)], ["ConvexPolygons"]),
    "hexagon": polygon_instance(
        [
            (-1, 0),
            (fraction(-1, 2), MINUS_HALF_SQRT3_CELL),
            (fraction(-1, 2), HALF_SQRT3_CELL),
            (fraction(1, 2), MINUS_HALF_SQRT3_CELL),
            (fraction(1, 2), HALF_SQRT3_CELL),
            (1, 0),
        ],
        ["ConvexPolygons"],
        "The regular hexagon inscribed in the unit circle.",
    ),
    "right_triangle": polygon_instance([(0, 0), (0, 1), (1, 0)], ["Triangles"]),
    "triangle_345": polygon_instance(
        [(0, 0), (0, 3), (4, 0)], ["Triangles"], "The 3-4-5 right triangle."
    ),
    "equilateral_triangle": polygon_instance(
        [(0, 0), (1, SQRT3_CELL), (2, 0)], ["Triangles"], "The equilateral triangle of side 2."
    ),
    "square_pyramid": instance(
        r"\operatorname{conv}\left\{\left(0, 0, 0\right), \left(0, 2, 0\right), "
        r"\left(1, 1, 1\right), \left(2, 0, 0\right), \left(2, 2, 0\right)\right\}",
        lattice_polytope([(0, 0, 0), (2, 0, 0), (0, 2, 0), (2, 2, 0), (1, 1, 1)]),
        ["ConvexPolyhedra"],
        "A square pyramid.",
    ),
    "triangular_prism": instance(
        r"\operatorname{conv}\left\{0, e_{1}, e_{2}\right\} \times [0, 1]",
        lattice_polytope([(x, y, z) for x, y in ((0, 0), (1, 0), (0, 1)) for z in (0, 1)]),
        ["ConvexPolyhedra"],
        "A triangular prism.",
    ),
    "cuboid": instance(
        r"[0, 1] \times [0, 1] \times [0, 2]",
        lattice_polytope(list(itertools.product((0, 1), (0, 1), (0, 2)))),
        ["ConvexPolyhedra"],
        "A box twice as tall as it is wide.",
    ),
    "tetrahedron": instance(
        r"\operatorname{conv}\left\{\left(0, 0, 0\right), \left(0, 1, 1\right), "
        r"\left(1, 0, 1\right), \left(1, 1, 0\right)\right\}",
        lattice_polytope([(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)]),
        ["PlatonicSolids"],
        "A regular tetrahedron: every other vertex of the unit cube.",
    ),
    "cube": instance(
        r"[0, 1]^{3}",
        lattice_polytope(list(itertools.product((0, 1), repeat=3))),
        ["PlatonicSolids"],
        "The unit cube.",
    ),
    "octahedron": instance(
        r"\operatorname{conv}\left\{\pm e_{1}, \pm e_{2}, \pm e_{3}\right\}",
        lattice_polytope(
            [tuple(sign if i == j else 0 for j in range(3)) for i in range(3) for sign in (1, -1)]
        ),
        ["PlatonicSolids"],
        "The regular octahedron.",
    ),
    "circle": instance(
        r"x^{2} + y^{2} = 1",
        {"curve": "Add(Pow(Symbol('x'), Integer(2)), Pow(Symbol('y'), Integer(2)), Integer(-1))"},
        ["PlaneCurves"],
        "The unit circle.",
    ),
    "cusp": instance(
        r"y^{2} = x^{3}",
        {
            "curve": "Add(Pow(Symbol('x'), Integer(3)), "
            "Mul(Integer(-1), Pow(Symbol('y'), Integer(2))))"
        },
        ["PlaneCurves"],
        "The cuspidal cubic: a Weierstrass equation that is singular at the origin, so not "
        "an elliptic curve.",
    ),
    "folium": instance(
        r"x^{3} - 3 x y + y^{3} = 0",
        {
            "curve": "Add(Pow(Symbol('x'), Integer(3)), Mul(Integer(-1), Integer(3), "
            "Symbol('x'), Symbol('y')), Pow(Symbol('y'), Integer(3)))"
        },
        ["PlaneCurves"],
        "The folium of Descartes.",
    ),
    "congruent_number_curve": instance(
        r"y^{2} = x^{3} - x",
        {
            "curve": "Add(Pow(Symbol('x'), Integer(3)), Mul(Integer(-1), Symbol('x')), "
            "Mul(Integer(-1), Pow(Symbol('y'), Integer(2))))"
        },
        ["EllipticCurves"],
        "Conductor 32; it has complex multiplication by the Gaussian integers.",
    ),
    "curve_36": instance(
        r"y^{2} = x^{3} + 1",
        {
            "curve": "Add(Pow(Symbol('x'), Integer(3)), Mul(Integer(-1), Pow(Symbol('y'), "
            "Integer(2))), Integer(1))"
        },
        ["EllipticCurves"],
        "Conductor 36; six rational points, including the point at infinity.",
    ),
    "curve_37a": instance(
        r"y^{2} + y = x^{3} - x",
        {
            "curve": "Add(Pow(Symbol('x'), Integer(3)), Mul(Integer(-1), Symbol('x')), "
            "Mul(Integer(-1), Pow(Symbol('y'), Integer(2))), Mul(Integer(-1), Symbol('y')))"
        },
        ["EllipticCurves"],
        "The elliptic curve of rank one with the smallest conductor, 37.",
    ),
}

ANALYSIS: dict[str, Instance] = {
    "exp": (
        "e^{x}",
        "The exponential function.",
        [
            ("ElementaryFunctions", expr("exp(Symbol('x'))")),
            ("DFiniteFunctions", dfinite([[-1], [1]], [1])),
        ],
    ),
    "log": instance(r"\log{\left(x \right)}", expr("log(Symbol('x'))"), ["ElementaryFunctions"]),
    "catalan_generating_function": (
        r"\frac{1 - \sqrt{1 - 4 x}}{2 x}",
        "The generating function of the Catalan numbers.",
        [
            (
                "ElementaryFunctions",
                expr(
                    "Mul(Rational(1, 2), Pow(Symbol('x'), Integer(-1)), Add(Integer(1), "
                    "Mul(Integer(-1), Pow(Add(Integer(1), Mul(Integer(-1), Integer(4), "
                    "Symbol('x'))), Rational(1, 2)))))"
                ),
            ),
            ("DFiniteFunctions", dfinite([[2], [-2, 10], [0, -1, 4]], [1, 1])),
        ],
    ),
    "reciprocal_shift": instance(
        r"\frac{1}{x - 1}",
        expr("Pow(Add(Symbol('x'), Integer(-1)), Integer(-1))"),
        ["RationalFunctions"],
    ),
    "mobius_transformation": instance(
        r"\frac{x + 1}{x - 1}",
        expr("Mul(Pow(Add(Symbol('x'), Integer(-1)), Integer(-1)), Add(Symbol('x'), Integer(1)))"),
        ["RationalFunctions"],
    ),
    "lorentzian": instance(
        r"\frac{1}{x^{2} + 1}",
        expr("Pow(Add(Pow(Symbol('x'), Integer(2)), Integer(1)), Integer(-1))"),
        ["RationalFunctions", "EvenFunctions"],
        r"The derivative of $\arctan x$.",
    ),
    "odd_rational": instance(
        r"\frac{x}{x^{2} + 1}",
        expr("Mul(Symbol('x'), Pow(Add(Pow(Symbol('x'), Integer(2)), Integer(1)), Integer(-1)))"),
        ["RationalFunctions", "OddFunctions"],
    ),
    "cos": instance(r"\cos{\left(x \right)}", expr("cos(Symbol('x'))"), ["EvenFunctions"]),
    "sin": instance(r"\sin{\left(x \right)}", expr("sin(Symbol('x'))"), ["OddFunctions"]),
    "arctan": (
        r"\operatorname{atan}{\left(x \right)}",
        "The inverse tangent.",
        [
            ("OddFunctions", expr("atan(Symbol('x'))")),
            ("DFiniteFunctions", dfinite([[0], [0, 2], [1, 0, 1]], [0, 1])),
        ],
    ),
    "airy_ai": instance(
        r"y'' - x y = 0, \quad y(0) = \frac{\sqrt[3]{3}}{3 \Gamma\left(\frac{2}{3}\right)}, "
        r"y'(0) = - \frac{3^{\frac{2}{3}}}{3 \Gamma\left(\frac{1}{3}\right)}",
        dfinite(
            [[0, -1], [0], [1]],
            [
                expr(
                    "Mul(Rational(1, 3), Pow(Integer(3), Rational(1, 3)), "
                    "Pow(gamma(Rational(2, 3)), Integer(-1)))"
                ),
                expr(
                    "Mul(Integer(-1), Rational(1, 3), Pow(Integer(3), Rational(2, 3)), "
                    "Pow(gamma(Rational(1, 3)), Integer(-1)))"
                ),
            ],
        ),
        ["DFiniteFunctions"],
        r"The Airy function $\operatorname{Ai}(x)$: D-finite, but not elementary.",
    ),
    "riccati": instance(
        r"\frac{d}{d x} y{\left(x \right)} = y^{2}{\left(x \right)}",
        expr(
            "Equality(Derivative(Function('y')(Symbol('x')), Tuple(Symbol('x'), Integer(1))), "
            "Pow(Function('y')(Symbol('x')), Integer(2)))"
        ),
        ["OrdinaryDifferentialEquations"],
        "Nonlinear: its solutions blow up in finite time.",
    ),
    "airy_equation": instance(
        r"\frac{d^{2}}{d x^{2}} y{\left(x \right)} = x y{\left(x \right)}",
        expr(
            "Equality(Derivative(Function('y')(Symbol('x')), Tuple(Symbol('x'), Integer(2))), "
            "Mul(Symbol('x'), Function('y')(Symbol('x'))))"
        ),
        ["OrdinaryDifferentialEquations"],
        "The Airy equation: linear, with a coefficient that is not constant.",
    ),
    "pendulum": instance(
        r"\sin{\left(y{\left(x \right)} \right)} + \frac{d^{2}}{d x^{2}} y{\left(x \right)} = 0",
        expr(
            "Equality(Add(sin(Function('y')(Symbol('x'))), Derivative(Function('y')(Symbol('x')),"
            " Tuple(Symbol('x'), Integer(2)))), Integer(0))"
        ),
        ["OrdinaryDifferentialEquations"],
        "The undamped pendulum.",
    ),
    "harmonic_oscillator": instance(
        r"y{\left(x \right)} + \frac{d^{2}}{d x^{2}} y{\left(x \right)} = 0",
        expr(
            "Equality(Add(Function('y')(Symbol('x')), Derivative(Function('y')(Symbol('x')), "
            "Tuple(Symbol('x'), Integer(2)))), Integer(0))"
        ),
        ["LinearConstantCoefficientODEs"],
        r"The harmonic oscillator, solved by $\sin x$ and $\cos x$.",
    ),
    "two_exponentials": instance(
        r"2 y{\left(x \right)} - 3 \frac{d}{d x} y{\left(x \right)} + \frac{d^{2}}{d x^{2}} "
        r"y{\left(x \right)} = 0",
        expr(
            "Equality(Add(Mul(Integer(2), Function('y')(Symbol('x'))), Mul(Integer(-1), "
            "Integer(3), Derivative(Function('y')(Symbol('x')), Tuple(Symbol('x'), Integer(1)))),"
            " Derivative(Function('y')(Symbol('x')), Tuple(Symbol('x'), Integer(2)))), "
            "Integer(0))"
        ),
        ["LinearConstantCoefficientODEs"],
        r"Solved by $e^{x}$ and $e^{2x}$.",
    ),
    "growth": instance(
        r"\frac{d}{d x} y{\left(x \right)} = y{\left(x \right)}",
        expr(
            "Equality(Derivative(Function('y')(Symbol('x')), Tuple(Symbol('x'), Integer(1))), "
            "Function('y')(Symbol('x')))"
        ),
        ["LinearConstantCoefficientODEs"],
        r"Exponential growth, solved by $e^{x}$.",
    ),
}

INSTANCES: dict[str, Instance] = {
    **NUMBERS,
    **SEQUENCES,
    **MATRICES,
    **POLYNOMIALS,
    **COMBINATORICS,
    **GRAPHS,
    **GROUPS,
    **FIELDS,
    **TOPOLOGY,
    **GEOMETRY,
    **ANALYSIS,
}

OPERATORS: dict[str, Specimen] = {
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
    "CompanionMatrix": (
        r"\text{Companion Matrix}",
        "For a monic polynomial, the matrix whose characteristic polynomial is that polynomial.",
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
    "EulerTotient": (
        r"\text{Euler Totient}",
        r"How many of $1 \dots n$ share no factor with $n$. It is also the degree of "
        r"the $n$th cyclotomic polynomial.",
    ),
}

RELATIONS: list[tuple[str, list[str], list[str]]] = [
    ("CharacteristicPolynomial", ["A"], ["P"]),
    ("CompanionMatrix", ["P"], ["C"]),
    ("CharacteristicPolynomial", ["C"], ["P"]),
    ("Inverse", ["B"], ["B"]),
    ("Inverse", ["D"], ["D"]),
    ("CharacteristicPolynomial", ["B"], ["Q"]),
    ("CharacteristicPolynomial", ["D"], ["R"]),
    ("Add", ["A", "B"], ["E"]),
    ("Determinant", ["A"], ["three"]),
    ("IsSingular", ["A"], ["false"]),
    ("Degree", ["P"], ["two"]),
    ("SeifertMatrix", ["K3"], ["V3"]),
    ("SeifertMatrix", ["K5"], ["V5"]),
    ("SeifertMatrix", ["K7"], ["V7"]),
    ("AlexanderPolynomial", ["V3"], ["Phi6"]),
    ("AlexanderPolynomial", ["V5"], ["Phi10"]),
    ("AlexanderPolynomial", ["V7"], ["Phi14"]),
    ("CyclotomicPolynomial", ["six"], ["Phi6"]),
    ("CyclotomicPolynomial", ["ten"], ["Phi10"]),
    ("CyclotomicPolynomial", ["fourteen"], ["Phi14"]),
    ("CompanionMatrix", ["Phi6"], ["CompPhi6"]),
    ("CharacteristicPolynomial", ["CompPhi6"], ["Phi6"]),
    ("CompanionMatrix", ["R"], ["D"]),
    ("MatrixOrder", ["CompPhi6"], ["six"]),
    ("MatrixOrder", ["B"], ["one"]),
    ("MatrixOrder", ["D"], ["two"]),
    ("KnotDeterminant", ["V3"], ["three"]),
    ("KnotDeterminant", ["V5"], ["five"]),
    ("KnotDeterminant", ["V7"], ["seven"]),
    ("Roots", ["P"], ["one", "three"]),
    ("Eigenvalues", ["A"], ["one", "three"]),
    ("Determinant", ["B"], ["one"]),
    ("Determinant", ["D"], ["neg_one"]),
    ("Determinant", ["C"], ["three"]),
    ("Determinant", ["S"], ["zero"]),
    ("IsSingular", ["S"], ["true"]),
    ("EulerTotient", ["six"], ["two"]),
    ("EulerTotient", ["ten"], ["four"]),
    ("EulerTotient", ["fourteen"], ["six"]),
    ("CyclotomicPolynomial", ["four"], ["Phi4"]),
    ("CompanionMatrix", ["Phi4"], ["rotation90"]),
    ("CharacteristicPolynomial", ["rotation90"], ["Phi4"]),
    ("MatrixOrder", ["rotation90"], ["four"]),
    ("Determinant", ["rotation90"], ["one"]),
    ("CharacteristicPolynomial", ["fibonacci_matrix"], ["golden_polynomial"]),
    ("Determinant", ["fibonacci_matrix"], ["neg_one"]),
    ("CharacteristicPolynomial", ["cycle3"], ["cube_minus_one"]),
    ("CompanionMatrix", ["cube_minus_one"], ["cycle3"]),
    ("MatrixOrder", ["cycle3"], ["three"]),
    ("CharacteristicPolynomial", ["cartan_a2"], ["P"]),
    ("Eigenvalues", ["cartan_a2"], ["one", "three"]),
    ("Determinant", ["cartan_a2"], ["three"]),
    ("Inverse", ["cat_map"], ["cat_map_inverse"]),
    ("Inverse", ["cat_map_inverse"], ["cat_map"]),
    ("Eigenvalues", ["diag12"], ["one", "two"]),
    ("Determinant", ["nilpotent_block"], ["zero"]),
    ("IsSingular", ["nilpotent_block"], ["true"]),
    ("Roots", ["rational_quadratic"], ["minus_half", "half"]),
    ("Degree", ["T4"], ["four"]),
    ("EulerTotient", ["thirteen"], ["twelve"]),
    ("EulerTotient", ["seven"], ["six"]),
    ("EulerTotient", ["five"], ["four"]),
]

IMAGES: dict[str, str] = {
    "K3": "/knots/2-3.svg",
    "K5": "/knots/2-5.svg",
    "K7": "/knots/2-7.svg",
}

CYCLOTOMIC_WIKI = ("Wikipedia", "https://en.wikipedia.org/wiki/Cyclotomic_polynomial")


def oeis(number: str) -> list[tuple[str, str]]:
    return [(f"OEIS {number}", f"https://oeis.org/{number}")]


def lmfdb_field(label: str) -> list[tuple[str, str]]:
    return [(f"LMFDB {label}", f"https://www.lmfdb.org/NumberField/{label}")]


def knot_atlas(name: str) -> list[tuple[str, str]]:
    return [("Knot Atlas", f"https://katlas.org/wiki/{name}")]


REFERENCES: dict[str, list[tuple[str, str]]] = {
    "K3": [
        *knot_atlas("3_1"),
        ("Wikipedia", "https://en.wikipedia.org/wiki/Trefoil_knot"),
    ],
    "K5": [
        *knot_atlas("5_1"),
        ("Wikipedia", "https://en.wikipedia.org/wiki/Cinquefoil_knot"),
    ],
    "K7": [
        *knot_atlas("7_1"),
        ("Wikipedia", "https://en.wikipedia.org/wiki/7_1_knot"),
    ],
    "K4_1": [
        *knot_atlas("4_1"),
        ("Wikipedia", "https://en.wikipedia.org/wiki/Figure-eight_knot_(mathematics)"),
    ],
    "K5_2": knot_atlas("5_2"),
    "K6_1": knot_atlas("6_1"),
    "K6_3": knot_atlas("6_3"),
    "K8_3": knot_atlas("8_3"),
    "K8_19": knot_atlas("8_19"),
    # LMFDB names the last two by Q(zeta_5) and Q(zeta_7): Q(zeta_2m) = Q(zeta_m) for odd
    # m, so they are the same fields under a different name. Each page's defining
    # polynomial is exactly the object it is filed under here.
    "Phi6": [*lmfdb_field("2.0.3.1"), *oeis("A013595"), CYCLOTOMIC_WIKI],
    "Phi10": [*lmfdb_field("4.0.125.1"), *oeis("A013595"), CYCLOTOMIC_WIKI],
    "Phi14": [*lmfdb_field("6.0.16807.1"), *oeis("A013595"), CYCLOTOMIC_WIKI],
    "SeifertMatrix": [("Wikipedia", "https://en.wikipedia.org/wiki/Seifert_surface")],
    "AlexanderPolynomial": [("Wikipedia", "https://en.wikipedia.org/wiki/Alexander_polynomial")],
    "CyclotomicPolynomial": [CYCLOTOMIC_WIKI],
    "q_cbrt2": lmfdb_field("3.1.108.1"),
    "q_zeta7_plus": lmfdb_field("3.3.49.1"),
    "q_sqrt2": lmfdb_field("2.2.8.1"),
    "q_sqrt5": lmfdb_field("2.2.5.1"),
    "q_sqrt_minus5": lmfdb_field("2.0.20.1"),
    "q_i": lmfdb_field("2.0.4.1"),
    "q_zeta3": lmfdb_field("2.0.3.1"),
    "q_zeta5": lmfdb_field("4.0.125.1"),
    "q_zeta7": lmfdb_field("6.0.16807.1"),
    "q_zeta8": lmfdb_field("4.0.256.1"),
    "curve_37a": [("LMFDB 37.a1", "https://www.lmfdb.org/EllipticCurve/Q/37/a/1")],
    "catalan_numbers": oeis("A000108"),
    "central_binomials": oeis("A000984"),
    "apery_numbers": oeis("A005259"),
    "fibonacci": oeis("A000045"),
    "lucas": oeis("A000032"),
    "pell": oeis("A000129"),
    "squares": oeis("A000290"),
    "powers_of_two": oeis("A000079"),
    "factorials": oeis("A000142"),
    "prime_counting": oeis("A000720"),
    "big_omega": oeis("A001222"),
    "little_omega": oeis("A001221"),
    "totient": oeis("A000010"),
    "divisor_sum": oeis("A000203"),
    "mobius": oeis("A008683"),
}

SIGNATURES = [
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

DISPLAYS: dict[str, tuple[str | None, bool]] = {
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

FILINGS: dict[str, list[str]] = {
    "NumberTheory": [
        "RationalNumbers",
        "Integers",
        "PositiveIntegers",
        "PrimeNumbers",
        "ResidueClasses",
        "UnitsModN",
        "PrimitiveRoots",
        "AlgebraicNumbers",
        "AlgebraicIntegers",
        "RootsOfUnity",
        "GaussianIntegers",
        "GaussianPrimes",
        "NumberOperations",
    ],
    "NumberOperations": ["EulerTotient"],
    "SequencesAndRecurrences": [
        "Sequences",
        "FiniteSequences",
        "SequencesByFormula",
        "ArithmeticFunctions",
        "MultiplicativeFunctions",
        "HolonomicSequences",
        "LinearRecurrences",
    ],
    "LinearAlgebra": [
        "Matrices",
        "ColumnVectors",
        "SquareMatrices",
        "SymmetricMatrices",
        "PositiveDefiniteMatrices",
        "DiagonalMatrices",
        "JordanNormalForms",
        "NilpotentMatrices",
        "DiagonalizableMatrices",
        "SingularMatrices",
        "InvertibleMatrices",
        "InvertibleRealMatrices",
        "InvertibleRationalMatrices",
        "InvertibleIntegerMatrices",
        "SpecialLinearIntegerMatrices",
        "OrthogonalMatrices",
        "RotationMatrices",
        "PermutationMatrices",
        "CompanionMatrices",
        "MatrixOperations",
    ],
    "MatrixOperations": [
        "CharacteristicPolynomial",
        "Inverse",
        "Determinant",
        "Add",
        "IsSingular",
        "MatrixOrder",
        "Eigenvalues",
    ],
    "PolynomialAlgebra": [
        "Polynomials",
        "IntegerPolynomials",
        "MonicIntegerPolynomials",
        "IrreduciblePolynomials",
        "CyclotomicPolynomials",
        "ChebyshevPolynomials",
        "PolynomialOperations",
    ],
    "PolynomialOperations": ["CompanionMatrix", "Degree", "Roots", "CyclotomicPolynomial"],
    "Combinatorics": [
        "Permutations",
        "EvenPermutations",
        "IntegerPartitions",
        "DistinctPartitions",
        "StandardYoungTableaux",
    ],
    "GraphTheory": [
        "Graphs",
        "Trees",
        "BipartiteGraphs",
        "PlanarGraphs",
        "RegularGraphs",
        "CompleteGraphs",
    ],
    "GroupTheory": [
        "Groups",
        "FiniteGroups",
        "SimpleGroups",
        "DihedralGroups",
        "PermutationGroups",
        "GroupPresentations",
        "FinitelyGeneratedAbelianGroups",
        "CyclicGroups",
    ],
    "FieldsAndLieAlgebras": [
        "Fields",
        "FiniteFields",
        "NumberFields",
        "QuadraticFields",
        "CyclotomicFields",
        "SimpleLieAlgebras",
    ],
    "KnotTheory": [
        "Knots",
        "TorusKnots",
        "AlternatingKnots",
        "AmphichiralKnots",
        "TwoBridgeKnots",
        "BraidWords",
        "ClosedSurfaces",
        "SimplicialComplexes",
        "KnotOperations",
    ],
    "KnotOperations": ["SeifertMatrix", "AlexanderPolynomial", "KnotDeterminant"],
    "Geometry": [
        "ConvexPolytopes",
        "ConvexPolygons",
        "Triangles",
        "ConvexPolyhedra",
        "PlatonicSolids",
        "PlaneCurves",
        "EllipticCurves",
    ],
    "Analysis": [
        "RealFunctions",
        "ElementaryFunctions",
        "RationalFunctions",
        "EvenFunctions",
        "OddFunctions",
        "DFiniteFunctions",
        "OrdinaryDifferentialEquations",
        "LinearConstantCoefficientODEs",
    ],
    "Values": ["Booleans", "Expressions"],
}

TOP_LEVEL = [
    "NumberTheory",
    "SequencesAndRecurrences",
    "LinearAlgebra",
    "PolynomialAlgebra",
    "Combinatorics",
    "GraphTheory",
    "GroupTheory",
    "FieldsAndLieAlgebras",
    "KnotTheory",
    "Geometry",
    "Analysis",
    "Values",
]

IMPLEMENTATIONS = {
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

        objects: dict[str, Specimen] = {
            **SECTIONS,
            **{key: (latex, description) for key, (latex, description, _, _) in TYPES.items()},
            **{key: (latex, description) for key, (latex, description, _) in INSTANCES.items()},
            **OPERATORS,
        }

        ids: dict[str, uuid.UUID] = {}
        for key, (latex, description) in objects.items():
            obj = Object(latex=latex, description=description, image_url=IMAGES.get(key))
            session.add(obj)
            await session.flush()
            ids[key] = obj.id

        for key, entries in REFERENCES.items():
            for position, (label, url) in enumerate(entries):
                session.add(
                    ObjectReference(object_id=ids[key], label=label, url=url, position=position)
                )

        for operator, inputs, outputs in RELATIONS:
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

        for key, (_, _, data_kind, _) in TYPES.items():
            session.add(Type(object_id=ids[key], data_kind=data_kind))
        await session.flush()

        for key, (_, _, _, supertypes) in TYPES.items():
            for supertype in supertypes:
                session.add(Subtype(type_id=ids[key], supertype_id=ids[supertype]))

        for key, (_, _, facets) in INSTANCES.items():
            for type_key, data in facets:
                session.add(Membership(object_id=ids[key], type_id=ids[type_key], data=data))

        for operator, domain, codomain in SIGNATURES:
            session.add(
                Signature(map_id=ids[operator], domain_id=ids[domain], codomain_id=ids[codomain])
            )

        for operator, (template, hidden) in DISPLAYS.items():
            session.add(
                OperatorDisplay(
                    operator_id=ids[operator], template=template, hidden_by_default=hidden
                )
            )

        for section, filed in FILINGS.items():
            for key in filed:
                session.add(SectionFiling(object_id=ids[key], section_id=ids[section]))

        for root in TOP_LEVEL:
            session.add(TopLevelObject(object_id=ids[root]))

        implementation_dir = pathlib.Path(__file__).parent / "implementations"
        for operator, filename in IMPLEMENTATIONS.items():
            session.add(
                Implementation(
                    operator_id=ids[operator],
                    code=(implementation_dir / f"{filename}.py").read_text(),
                )
            )

        await session.commit()
        reference_count = sum(len(entries) for entries in REFERENCES.values())
        print(
            f"seeded {len(objects)} objects ({len(TYPES)} types), {len(RELATIONS)} relations, "
            f"{len(IMPLEMENTATIONS)} implementations, {len(IMAGES)} images "
            f"and {reference_count} references"
        )


if __name__ == "__main__":
    asyncio.run(seed())
