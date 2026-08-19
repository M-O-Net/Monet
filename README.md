# Monet

**Mathematical Object Network** — a live, connected database of mathematical objects.

Monet stores mathematical **objects** (a specific matrix, a specific polynomial, a specific
group, a specific knot) and the **relations** that connect them, across all of mathematics rather
than a single domain. Objects come to point at one another through those relations: a matrix
yields its characteristic polynomial, a polynomial induces a Galois group, a finite graph is
equivalent to an adjacency matrix. The end goal is not the database itself — it's what becomes
visible once the network is dense enough: patterns, coincidences, and eventually conjectures worth
checking.

Where most math databases (LMFDB, OEIS, the Knot Atlas) are hand-curated within a single domain,
Monet's aim is to grow **across** domains, with the objects, the relations between them, and the
machinery to compute them all able to grow over time — including, eventually, machinery added
autonomously rather than hand-written in advance. That's a long-term goal; see "Where this is
going," below, for how it's staged.

## The data model

Everything in Monet is one of two things: an **object**, or a **relation** between objects.

**Objects** are specific mathematical things — not families or types. The matrix
`[[2,1],[1,2]]`, not "2×2 matrices." The polynomial `x²−4x+3`, not "quadratics." A specific finite
group, not "the class of finite simple groups." A specific knot, not "trefoil knots." Every object
is identified and displayed by its own rendered mathematical notation.

A deliberate design choice: **operators are objects too.** `CharacteristicPolynomial`,
`Inverse`, `Determinant` — the operations themselves are nodes in the network, on equal footing
with the matrices and polynomials they act on. A matrix is data; a transformation of a matrix is
also, in a real sense, a mathematical object worth naming and pointing at. This is what lets the
network eventually hold not just objects and their values but the operations connecting them, and
later, theorems _about_ those operations, as first-class citizens rather than a separate kind of
record bolted on.

**Relations** connect objects. A relation names an operator and a set of input objects and output
objects — not just "A relates to B," but "applying `CharacteristicPolynomial` to matrix `A`
produces polynomial `P`." Relations are deliberately **not** limited to one input and one output:
some operations take two inputs (`Add(A, B) → C`), some produce several outputs at once (a
polynomial's roots, all at once), and this shape needs to hold from the start rather than being
retrofitted later.

One consequence worth calling out, because it's the most interesting thing a small network can
already show: relations can **close a loop**. A polynomial's companion matrix has that polynomial
as _its own_ characteristic polynomial — start at a polynomial, follow two relations, and arrive
back where you started. That's not a coincidence the database records passively; it's a fact the
network makes visible simply by existing.

**Properties as relations.** Rather than treating "is this polynomial square-free" or "what is
this matrix's determinant" as a separate kind of record, both are just relations too — an operator
applied to one object, producing a value (a boolean, a number) as its output. This means a
property and a full-blown relation between two matrices are the same _kind_ of fact, differing
only in what the output happens to be. It also means that when many different objects' relations
converge on the same output — many matrices with determinant `3`, say — that convergence is
visible in the network itself, rather than hidden inside separate property tables. That
convergence is exactly where interesting numerical coincidences eventually get found.

**Identity.** The goal is one record per mathematical object — not, for instance, a record for
every equivalent way of writing down the same matrix. Getting this exactly right (canonical forms,
equivalence checks) is real work and is expected to deepen over time as more object types are
added; see below for how it's staged.

## Where this is going

**v0** (this release) is intentionally small: a database and a browsing/editing interface,
covering only matrices and polynomials, with every object and relation entered and edited by
hand. No computation happens automatically — the point of v0 is to prove the data model and the
experience of exploring the network, including the closed-loop example above, without needing any
of the machinery that makes the network _grow itself_.

**v1** adds that machinery: real implementations behind each operator (so applying
`CharacteristicPolynomial` to a matrix actually computes one), starting in one language and
designed to eventually support several, plus a canonical representation for each object type so
those implementations have something concrete to compute over.

**Beyond v1**, staged in roughly this order:

- **Verification badges** — recording _how_ a relation was established (an exact computation, a
  citation, a bare assertion) and _by whom_, human or machine. Not meaningful until v1 gives
  computation something to vary between.
- **Corroboration** — recording when a fact has been established more than one independent way,
  strengthening confidence in it.
- **A metered growth mechanism**, so that automatic computation can run across the network without
  looping forever or generating unbounded clutter.
- **Autonomous growth** — the project's real long-term thesis: new kinds of object, and the
  machinery to compute with them, added by AI agents rather than hand-curated in advance.
- **A conjecture layer** — searching the network itself for implications, closed loops, and
  numerical coincidences worth checking, once it's dense enough for that to mean something.
- **Wiki-style edit history** — once people are relying on Monet's data, edits should supersede
  rather than destroy, with a visible history, the way a wiki earns trust.

## Non-goals

Monet does not prove theorems — it records the epistemic status of claims, and is not in the
business of presenting a numerical or finite check as a proof. It does not aim for completeness
within any single domain — it is not a replacement for LMFDB, OEIS, or a domain-specific atlas.
And it is not a general-purpose computer algebra system: v1's operator implementations call into
existing math libraries (a matrix's characteristic polynomial via a linear-algebra library, say)
rather than reimplementing the algorithms themselves — Monet's own code is the network and the
orchestration around it, never a second copy of the computation.
