from seed_data.build import Source

OEIS = Source(
    name="OEIS",
    homepage="https://oeis.org",
    license="CC BY-SA 4.0",
    obtained="read by hand from each sequence's entry",
    page="https://oeis.org/{}",
)

KNOTINFO = Source(
    name="KnotInfo",
    homepage="https://knotinfo.org",
    license="none stated; cite as C. Livingston and A. H. Moore, KnotInfo: Table of Knot "
    "Invariants. The database_knotinfo package that carries it is GPL-3.0",
    obtained="the database_knotinfo 2026.10.5 package from PyPI, read by "
    "scripts/snapshot_knotinfo.py",
    page="https://knotinfo.org/results.php?searchmode=singleknot&desktopmode=0&singleknot={}",
)

MCKAY = Source(
    name="McKay's Combinatorial Data",
    homepage="https://users.cecs.anu.edu.au/~bdm/data/",
    license="CC BY 4.0",
    obtained="the graph6 and tree files downloaded from the collection, read by "
    "scripts/snapshot_mckay.py",
    page="https://users.cecs.anu.edu.au/~bdm/data/{}",
)
