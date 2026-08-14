# Monet

**Mathematical Object Network** — a live, connected, autonomous database of mathematical objects.

Monet stores mathematical **objects** (a specific polynomial, a specific group, a specific knot),
the **properties** they satisfy, and the **relations** that connect them — across all of
mathematics rather than a single domain. Properties and relations are computed automatically, and
objects come to point at one another through those computations: a matrix yields its
characteristic polynomial, a polynomial induces a Galois group, a finite graph is equivalent to an
adjacency matrix.

Every record carries its own provenance and a **verification badge** recording how the claim was
established — a formal proof, an exact symbolic computation, numerical evidence, a citation, or a
bare assertion — and by whom, human or machine.

The distinguishing claim is that Monet grows not only in rows but in **schema and in code**: new
kinds of mathematical object, and the machinery to compute with them, are intended to be added
autonomously by AI agents rather than hand-curated in advance.

The end goal is not the database. It is what becomes possible once the network is dense enough:
searching for conjectures, and then verifying them.

## Status

Early design. No implementation yet.

The product specification is in [`docs/SPEC.md`](docs/SPEC.md). It is settled on the data model,
identity and equivalence, the verification badge, the verifier/relator software layer, and the
TTL economy that meters computation. Scheduling, storage substrate, CAS backends, the conjecture
layer, and the autonomous Fetcher are explicitly deferred and tracked in §10 of the spec.
