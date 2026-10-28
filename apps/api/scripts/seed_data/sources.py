from seed_data.build import Source

OEIS = Source(
    name="OEIS",
    homepage="https://oeis.org",
    license="CC BY-SA 4.0",
    obtained="read by hand from each sequence's entry",
    page="https://oeis.org/{}",
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
