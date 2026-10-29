from seed_data.build import Source

OEIS = Source(
    name="OEIS",
    homepage="https://oeis.org",
    license="CC BY-SA 4.0",
    obtained="read by hand from each sequence's entry",
    page="https://oeis.org/{}",
)

FINDSTAT = Source(
    name="FindStat",
    homepage="https://www.findstat.org",
    license="© The FindStatCrew, no license stated; Monet keeps only values of maps and statistics",
    obtained="each entry's text export, fetched once by scripts/import_findstat.py",
    page="https://www.findstat.org/{}",
)

LMFDB = Source(
    name="LMFDB",
    homepage="https://www.lmfdb.org",
    license="CC BY-SA 4.0",
    obtained="search-result downloads and each group's GAP download, at most one request per "
    "30 s as its robots.txt asks, which also rules out its API",
    page="https://www.lmfdb.org/{}",
)

CREMONA = Source(
    name="Cremona's tables",
    homepage="https://johncremona.github.io/ecdata/",
    license="Artistic License 2.0",
    obtained="the first allgens file of the ecdata repository on GitHub",
    page="https://github.com/JohnCremona/ecdata/blob/master/{}",
)

SMALL_GROUPS = Source(
    name="Small Groups library",
    homepage="http://www.icm.tu-bs.de/ag_algebra/software/small/",
    license="Artistic License 2.0, as the GAP package SmallGrp",
    obtained="its [order, index] identifiers, read from LMFDB's abstract group labels",
)

ATLAS = Source(
    name="ATLAS of Group Representations",
    homepage="http://brauer.maths.qmul.ac.uk/Atlas/v3/",
    license="none stated",
    obtained="the GAP files of the standard generators of a few permutation representations",
    page="http://brauer.maths.qmul.ac.uk/Atlas/v3/permrep/{}",
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
