# PRD - Math Object NETwork

## The vision

**Mathematicians have a modern calling.**
Human mathematicians are finding meaning in collaborative work on the understanding and discovery of new mathematics. Mathematicians are rewarded for making interesting mistakes publicly, and are getting credit for the process of their work, rather than only for a successful proof. Foundational work is recognised instead of only last-mile proofs. More people can become mathematicians.

**Mathematics is organized.**
AI is assisting not only in proofs, but also in communication and organization of mathematical ideas. conjectures can be tested extensively, and it is accessible to search for interesting phenomena and connections between fields. The communication of advanced mathematical ideas is done through interactive means. Equivalent ideas are shown to be so. It is simple to know if a mathematical result is known or not. Literature search is formalized and easy. This new structure inspires better/alternative understanding of concepts.

## The problems

Progress/meaning in mathematics has been correlated to resolving longstanding conjectures. Mathematicians need an alternative, meaningful aim where they are needed.

Math is historically non collaborative. Fear of AI scooping is making this worse. Mathematicians need Human-AI collaborations to not come at the expense of Human-Human collaboration.

Errors in math are hard to find by hand, making mistakes expensive, and reputation valuable. However, LLMs and formalization serve as alternatives, and this anxiety discourages experimentation, and publication of partial results. Mathematicians need an appropriate and streamlined way to share interesting mistakes and partial results.

Proper credit in math serves both as a currency and as valuable background. LLMs (and often humans) omit/miss citations. Mathematicians need a structured way to give proper credit to the originators of ideas.

Research mathematics in academic institutions is an enterprise which has attracted a very specific type of person. This, arguably, due to the highly technical nature of proofs, the patience required to work on a single problem for months, the ability to read and comprehend highly abstract (often badly written) material, and the inherent privilege needed to attend the several levels of education needed for accreditation. Mathematicians need to find avenues for more diverse perspectives to enter the field.

Mathematical knowledge (theorems, objects, techniques, and perspectives) exists mostly in books, papers, and the minds of experts. This is not sustainable given recent acceleration of growth. Searching and testing conjectures is hard, work is repeated, and it is impossible to be up-to-date. Mathematics needs a complimentary more structured way of keeping knowledge.

The number of (human and AI) agents exploring mathematics has grown substantially <numbers again>. This makes coordination and communication much harder. Mathematics needs to accommodate many more actors.

Math communication, either between experts, or for the training mathematician, is hard and lacking. Most math communication is done through papers and books, while math is best communicated through 1-on-1 conversations, and experiences. Learning a new field takes up a substantial percentage of a mathematician's time. Mathematics needs an easier way to learn interactively.

## Solutions

The problems above can be tackled by building a mathematics wiki database, which will include formalizations of objects, their properties and connections, and the knowledge about them. This will span most/all mathematical fields, and will be searchable, updateable, and educational. It will also allow for complicated symbolic experiments, testing and generating conjectures. LLMs will assist in the translation of the current paper-based paradigm to the new db form, giving due credit to originators of ideas, in a formal way.

## Users

Users of MONET include:

- Early career mathematicians (PhD students)
- Math professors (Field experts)
- Mathematicians in the process of changing field
- Recreational mathematicians with some formal training.
- …

## Features (to be filtered later)

A way to search for all math objects of type X … and run code on them.
Objects and types will have pages with comments, links, etc etc

### Objects

- Types (polynomials, knots, fields, braid words (knots, but not up to isomorphism) …)
- Maps (char poly: Matrices->Polys, Generating function: sequence -> Analytic(?) func around 0)
- Instances (1+x+x^2, trefoil, Q[sqrt(2)])
- Edges ([1,1;0,1]->x^2-x-1)
- Composite edges as composite definitions:
  - Alex poly is a composition of determinant with some other stuff,
- Theorems ( alex poly is a knot invariant. Etc etc). These will preferably have a DB realization (example - map from knot->poly, instead of just from braidword->poly)
- Claims (conjectures, theorems, refuted claims) - not in the first POC, but the design should leave room for them. A claim holds its statement (words, LaTeX, Lean when there is one) and a test against the DB: a query whose results are counterexamples (example - "the determinant of a singular matrix is 0" = every singular matrix whose determinant is not 0).
  - claims are kept separate from objects (no types or subtypes), but have their own pages, comments and layers - this may change
  - the test reports three counts, not a yes/no: supported (checked and holds), refuted (counterexamples), unknown (the hypothesis holds but the conclusion was never computed) - an empty result only means no counterexample among what is recorded
  - a conjecture is a claim with no counterexample; a theorem is a conjecture with a Lean formulation or a literature link; a refuted claim keeps its counterexamples (interesting mistakes)
  - the test is stored in a structured form (for every x in type T, map(x) ...) and compiled to a query, so it survives changes to the DB

### Layers

- DB - actual table, accessible and downloadable
- CAS - implementations of instances, types, maps and edges in sympy/equiv. Better at the level of types and maps.
- Formal - Lean verifications of the objects and theorems.
- Commentary - community interest, ideas, perspective, and other things which are not formalizeable in the DB (and things which are, but benefit from explanation)
- External links - links to papers introducing the concept, books, videos, lectures, etc etc.
- Trust/source - where did this computation/definition/instance come from? LLM? CAS computation? Is it formalized? Etc etc.
- Interest index - some quantification of how interesting is an object. Is it published? A secondary object coming from something else? Is it at the intersection of a few fields? Has anybody commented on it? Searched for it? This will be used to decide if to explore it further.

### Interfaces/views

- Object page - may look different depending on whether it's an instance or a type (map vs edge). And instances of different types/subtypes will also look different.
- Claim page - the statement, its status (conjecture / theorem / refuted), the supported / refuted / unknown counts, the counterexamples and exceptional objects, and its Lean proof or literature link
  - Comments
  - "Properties" (how are these saved? Are they specific edges?)
  - Images
  - Explainers (like when you float over a term, etc)
  - Links to talks and papers and books etc
  - A chat interface which allows you to ask questions, or make suggestions
  - Similar objects based on other people searching…
  - Lean
- Search box
  - Search by book paper or keywords
  - Search by object ID
  - Search by latex notation like integer sequences or sets or anything like that
  - Search with free text using llms to turn free text into a formalised query
  - by person, contributor etc
  - note: object metadata must support this kind of searching
- contribution page
  - contribute an instance
  - contribute an edge
  - contribute a type or subtype etc
  - contribute a map
  - contribute a claim (a conjecture: its statement and its test, optionally a Lean formulation or a literature link)
  - the above will have to include or satisfy some basic requirements. for example, contributing an instance of the type matrix must come with the entries of the matrix, its degrees, etc. explicitly and contributing a new type of ring must include yada yada yada
  - contribute not a new but rather to an existing instance. edge map or type for example contribute code or lean formalisation or other layers which are missing or edit an existing layer etc
  - contribute a suggestion for an object or something like that. this is similar to the contribution box in the object page, but a version of that should exist elsewhere. in the case where an object doesn't exist, maybe the edit of an object which I mentioned and above should actually be on the object page and not on the contribution page. we should only be to add a proper new object
- feed
  - New recently added objects
  - recently found relations
  - recent comments
  - recent citations of Monet in the literature
  - claims refuted, newly supported, or proven
  - what is currently running
- personal page
  - contributions, comments, etc
  - status of recent suggestions or contributions
  - What's running on personal runners which will get to in a moment
- graph view
  - show connections between instances and objects in a visual way which can be personalised by the user
  - you can click on neighbouring instances to see their object page or recenter the graph page around them
- about page contact page etc
  - about page would include this document
  - contact page would include emails and board members and their responsibilities
  - help us page or jobs page would include positions to be filled and CV, uploads etc
  - to do page would include tasks which are important as deemed by the community and the board. these would hopefully be completed by willing members of the community.

### Runner and Explorer

- runner
  - the runner will do. computer algebra type calculations these will add instances and edges. enriching the network and calculate properties generate views like figures or anything else which can be made autonomously
  - note that in future these runners will also include not only symbolic calculations but also llm calculations, meaning some calculations which cannot or do not yet have algorithmic ways of calculation. or if this these algorithms are too slow will be set to an llm to calculate autonomously using judgement
  - runner budget will be contributed by grants or other contributors and budgets will be set based on board decision or other metrics of popularity of other contributions made by the same user
  - users would be allowed to and encouraged to donate computer time for these calculations and will be credited and rewarded if their machine found an interesting connection. this implies a need for a calculation distribution system like gimps
- explorer or conjecture generator
  - this will use the DB structure as well as the plethora of instances and edges generated to look for interesting coincidences in the form of loops in the graph
  - for example, the idea that the Alexander polynomial of some tourist knots can is can also be generated by looking at the cyclotomic polynomial of some order is a loop in the graph in the sense that we have two different ways of pointing from some integer to that cyclical atomic polynomial one is through the cyclical atomic construction and another is through the knot and then through the Alexander polynomial calculation
  - it can also propose claims of the stored form from patterns in the DB (every instance of a type mapping into the same set), which become conjectures to test and discuss

### Backend

here are features which are needed, but may not be visible to users

- auto simplification (two equiv ways of calculation - Keep the simpler)
- theorems as health checks: the runner re-tests claims against newly added facts; a theorem with a counterexample flags a wrong fact, a wrong implementation, or a theorem stored without a needed hypothesis, and is triaged

## Goals, and success metrics

Here we list goals for the project, as well as
