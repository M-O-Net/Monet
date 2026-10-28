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
