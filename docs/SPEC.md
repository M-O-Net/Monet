# Monet — Product Specification (Draft 1)

## Context

Mathematical knowledge is fragmented across databases that are each curated by hand for a
single kind of object. LMFDB knows about L-functions and modular forms, the OEIS knows about
integer sequences, the Knot Atlas knows about knots. In every case a human decided in advance
which properties matter, wrote the code to compute them, and hand-wired the links between
objects. The schema is fixed by people, the code is written by people, and the connections
between different areas of mathematics — which is where most of the interesting content lives —
are largely absent.

Monet is a **live, connected, autonomous database of mathematical objects**. It stores objects,
the properties they satisfy, and the relations that connect them, across all of mathematics
rather than one domain. Its distinguishing claim is that the database grows not only in rows
but in **schema and in code**: new kinds of object, and the machinery to compute with them,
are added autonomously by AI agents rather than by hand.

The end goal is not the database. It is what becomes possible once the network is dense enough:
searching for conjectures, and then verifying them.

---

## 1. Data model

Three record types. Every record, of every type, carries **metadata** (citations, source,
justification) and a **verification badge** (§3).

### 1.1 Objects

Objects are **instances**, never families or types. A specific polynomial. A specific finite
group. A specific knot. Not "cyclotomic polynomials" and not "the class of finite simple groups."

An object belongs to a **type** (polynomial, group, matrix, knot, manifold, cohomology, elliptic
curve, …). Types are open-ended and grow over time.

### 1.2 Properties

Assertions about a single object. Two flavors, one record type:

- **Predicates** — boolean. Square-free, invertible, irreducible. Stored as explicit set
  membership: an object is in the `is_squarefree` set, or in the `is_not_squarefree` set, or in
  neither. **There is no third value.** Absence means unknown, unchecked, or not interesting
  enough to check.
- **Attributes** — valued. `degree = 5`, `det = −23`, `rank = 2`. Queryable and indexed, but
  not nodes in the network.

Predicates are the **precondition system for the compute layer**: they are what tells a relator
whether it is eligible to run. Attributes are what mathematicians search over, and where
numerical-coincidence conjectures come from.

Predicates may be *derived* from attributes — `is_singular` is `det = 0` — which keeps the
gating layer boolean without discarding the values.

**Promotion — used sparingly.** A value may be promoted to a full object when something needs to
point at it: the integer 691 is a column until the day a relation needs it as a target. But
promotion is not automatic and should be rare. Every promotion creates a node that attracts
relations, and promoting freely would densify the graph with edges that carry little information
— every object with `degree = 5` pointing at a shared node `5` is mostly noise. The promotion
policy (what threshold, decided by whom) is **deferred** (§10).

### 1.3 Relations

Edges between objects, carrying a **kind**:

- **Isomorphism / equivalence** — finite graph ↔ adjacency matrix
- **Derivation / projection** — matrix → characteristic polynomial
- and others as they arise

Relations vary in **cardinality**: one-to-one, many-to-one, one-to-many, many-to-many. Cardinality
is a property of the relation *type* and has direct consequences for budgeting (§5).

Relation *types* carry their own metadata: preconditions, cost, which relator implements them,
who wrote it. Relation *instances* carry metadata and a badge like any other record.

### 1.4 Derivation paths

A chain of relation instances is itself a recordable object with its own badge. This is required
for the conjecture layer (§7), and it is what makes a **closed loop** — the companion matrix of a
polynomial having that polynomial as its characteristic polynomial — expressible as an assertion
rather than an accident.

---

## 2. Identity and equivalence

**The goal is one record per mathematical object.** Deciding when two records denote the same
object is genuinely hard — graph isomorphism, knot equivalence, and group presentation equivalence
are all nontrivial or worse — but that difficulty is a problem to be solved, not a constraint to
be accepted. A database holding all n! vertex-orderings of a graph as separate records has failed.

Each object type must therefore provide, in order of preference:

1. **A canonical form.** Deterministic, computable, hashable. It may be **arbitrary** — there is
   no requirement that the chosen representative be mathematically natural, only that the choice
   is consistent, so that the same object always canonicalizes to the same record. This is the
   strongly preferred path and should be the default expectation for a new type.
2. **A fast equivalence algorithm.** Where no canonical form is practical, a decision procedure
   cheap enough to run on insertion. Invariants already stored in the network give the cheap
   negative direction: two knots with different Jones polynomials are provably inequivalent at
   almost no cost, so the expensive check runs only on survivors.
3. **Duplicate records — last resort only.** Where neither of the above exists for a type,
   Monet tolerates duplicates rather than blocking. This is a **fallback, not a feature.** It is
   an admission that canonicalization for that type is unsolved, and it should be recorded as an
   open problem against the type rather than treated as normal operation.

**Equivalence remains a relation** (§1.3) — computed by a relator, carrying a badge — because for
hard types the equivalence *claim* itself has an epistemic status: two knots whose every known
invariant agrees are conjecturally equivalent, badged as numeric evidence, not proven equal.

**On merging.** When two records are later established to denote the same object, they are merged
into one, with the distinct presentations retained as alternate representations on the surviving
record. The presentations are worth keeping; the second record is not.

**Relation to the bijection policy.** This is the storage-side counterpart of §5.3. That rule
says intra-type re-presentations are never *generated*; this one says they are never *stored*.
Cross-type equivalences — graph ↔ adjacency matrix — remain first-class relations between
genuinely distinct objects.

---

## 3. The verification badge

Three independent axes. They vary independently and must not be collapsed into a single value
at storage time (a derived scalar for display and ranking is fine).

### 3.1 Method

| Level | Meaning |
|---|---|
| `formal` | Machine-checked proof (Lean or equivalent) |
| `exact` | Exact symbolic computation over exact arithmetic — complete for this instance |
| `numeric` | Floating point, sampling, or finite checking of an unbounded claim — evidence only |
| `literature` | Asserted in a cited source |
| `asserted` | Stated without computation or citation |

**`exact` and `numeric` must stay distinct.** Computing a characteristic polynomial over ℚ is
complete and exact for that object — a proof about that instance, modulo CAS bugs. Checking
10,000 cases of a universal statement is evidence. Collapsing these destroys the distinction the
system exists to track.

### 3.2 Agent

Who or what made the assertion: a named human, an AI system (model and version), a paper
(DOI/arXiv reference), or a system relator (implementation and version). Includes *where* and
*why* where applicable.

### 3.3 Corroboration

How many independent routes agree, and which. A result computed two different ways that agree is
stronger than either alone. This is recorded, not inferred.

---

## 4. Software layer

### 4.1 Verifier

A collection of CAS routines that answer: **does this object satisfy this property?** Writes
predicate membership (`is X` / `is not X`) and attribute values, each with a badge recording how
it was established.

### 4.2 Relator

Answers: **what is this object related to?** — e.g. compute the characteristic polynomial of a
matrix. Operates in two modes:

- **Lookup** — compute the target, check whether it already exists in the database, and if so add
  the relation edge only.
- **Generate** — compute the target, insert it as a new object, then add the relation edge.

Generation is **priced higher than lookup** (§5). The mode is a scheduling decision, not a
property of the relator.

### 4.3 Attempt log

Separate from the property sets, which stay pure binary membership. The log records what was
attempted, by which relator or verifier, at what cost, and how it ended — success, timeout, CAS
failure, or inconclusive.

The primary justification is the conjecture layer. A statement like "every object with P also has
Q, with no counterexamples" is only as strong as the number of objects *actually checked*. Without
a log, 12-of-400-checked and 400-of-400-checked are indistinguishable, because absence is silent
and silence has two causes. The log turns a conjecture into a conjecture **with a support count**.

Secondary benefits: preventing endless retries of relevant-but-failing computations, and providing
the accounting TTL needs. CAS failures additionally propagate upward as operational signals.

---

## 5. The TTL economy

Verifiers and relators must not run indiscriminately across the whole database; doing so loops
forever and generates unbounded clutter. Monet meters computation with a **budget that decays
with distance from externally-grounded input**.

### 5.1 Rules

1. **Entry.** Anything entering from outside — a paper, a user request, a human entry — enters
   with **TTL = 1**.
2. **Price.** Every operation has a price. Cheaper: fundamental, easy to compute, bijective.
   More expensive: **generating** a new object rather than looking one up.
3. **Fan-out division.** A one-to-many relation **divides the parent's remaining budget among its
   n outputs**. If a finite group has many characters, each character receives a divided share.
   Division is *per fan-out relation*, not globally across everything leaving an object — a
   separate relation from the same parent draws on the parent's full budget.
4. **Accumulation is max, never sum.** An object reached by several derivation paths takes the
   maximum, so that TTL is **strictly non-increasing** except by explicit refresh. Summation would
   let heavily-connected objects print money.
5. **No collision refunds.** When a relator finds its target already present, this is *not* repaid
   as budget. Popular objects — x² + 1, S₅ — would otherwise become unbounded sources.
6. **Refresh.** A mathematician querying an object, or a new citation arriving, tops its budget
   back up. This is the mechanism by which human attention steers the frontier.
7. **Exhaustion.** At TTL 0 an object or property can afford no further operations.
8. **Cycle detection is independent of cost.** Near-free operations must not be able to spin
   forever around a cheap cycle.

### 5.2 Repricing, not refunding

When a region of the network is throttled because it sits too far from ground, the response is to
**note it and reduce the price of that category's relators** — not to refund budget locally. This
keeps the two instruments cleanly separated:

- **Cost** is a global, tunable policy knob attached to relation and property types.
- **TTL** is a strictly decreasing local resource attached to records.

### 5.3 Bijection policy

Bijections are near-free, **in moderation**. The governing rule:

> Generate isomorphisms **across types, not within type.**

Graph ↔ adjacency matrix is signal. Enumerating all vertex-orderings of a graph is clutter, and
explodes combinatorially while telling you nothing. Intra-type re-presentation is not generated.

### 5.4 Known tension

A tight budget suppresses clutter, but it also suppresses loop discovery — and loops are where
some of the conjectures are (§7), since a cycle only reveals itself if computation continues long
enough to close it. This tradeoff is accepted for now and revisited once the scheduler exists.

---

## 6. Autonomy and the Fetcher

**Out of scope for the first build, but the architecture must not preclude it.**

The Fetcher is an AI system that autonomously adds objects, relations and properties **together
with the verifiers and relators that accompany them.** This is the project's central thesis: the
database grows in schema and in code, not only in rows. New kinds of mathematical object arrive
along with the machinery to compute with them, without a human deciding in advance that elliptic
curves have conductors and writing the code to extract them.

Design consequences that must hold from the start:

- Object types, property types and relation types are **data**, not hardcoded enumerations.
- Verifiers and relators are **registrable artifacts** with declared preconditions, declared
  input/output types, and a declared price.
- Every record's badge must be able to name an AI agent as its author (§3.2).

---

## 7. Conjecture layer

**Future work.** Recorded here because it constrains the data model.

Anticipated conjecture shapes — the answer is expected to be *all of the following*:

- **Implications between properties.** "Every object with P has Q," carried with a support count
  drawn from the attempt log (§4.3).
- **Closed loops.** A derivation path returning to its origin asserts an identity.
- **Commuting diagrams.** Two distinct relation paths that always terminate at the same object.
- **Numerical coincidences.** Patterns among attribute values (§1.2).

---

## 8. Liveness

"Live" means **always growing** — continuously adding objects, relations and properties. The
intended steady state is that **most activity is driven by the requests of mathematicians**,
with autonomous background growth as the substrate rather than the main event. TTL refresh (§5.1.6)
is the mechanism connecting the two.

---

## 9. Non-goals

- Monet does not prove theorems. It records the epistemic status of claims, and never presents a
  finite or numerical check as a proof.
- Monet does not aim for completeness within any single domain. It is not a replacement for
  LMFDB, OEIS, or a domain-specific atlas.
- Monet is not a general-purpose computer algebra system. It orchestrates CAS routines; it does
  not reimplement them.

---

## 10. Deferred decisions

Explicitly out of scope for this spec, to be settled later:

| Decision | Notes |
|---|---|
| **Scheduler** | Affordability (cost) and priority (queue ordering) are different questions. TTL bounds depth but not breadth: one object with twenty cheap relators still spawns twenty children. Acknowledged as a significant design problem. |
| **When relators fire** | Lookup-vs-generate policy, and what triggers a run at all. |
| **Canonicalization per type** | Which types get a canonical form, which get a fast equivalence check, and which are (temporarily) unsolved and tolerate duplicates (§2). |
| **Promotion policy** | When a value earns promotion to a full object, given that promotion should stay rare (§1.2). |
| **Storage substrate** | Reviewable files vs. relational vs. graph store. |
| **CAS backends** | Which external systems (PARI/GP, GAP, SnapPy, Sage, Lean) and how they are integrated. |
| **TTL constants** | Entry value, price schedule, refresh amounts. |
| **Conjecture record shape** | §7 above. |
| **Fetcher design** | §6 above. |
