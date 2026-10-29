import re

from seed_data.build import Reference, RelationSpec, abelian
from seed_data.lmfdb import holder, snapshot
from seed_data.sources import CREMONA

TABLE = "allgens/allgens.00000-09999"
CURVES = {tuple(row["ainvs"]): row["curve"] for row in snapshot("lmfdb/elliptic_curves.tsv")}

REFERENCES: dict[str, list[Reference]] = {}
ASSERTED: list[RelationSpec] = []

for _row in snapshot("cremona/allgens.tsv"):
    _curve = CURVES.get(tuple(_row["ainvs"]))
    _key = None if _curve is None else holder(_curve)
    if _curve is None or _key is None:
        raise ValueError(f"no curve has Cremona's {_row['label']} coefficients {_row['ainvs']}")
    _cite = [CREMONA.cite(TABLE, _row["label"])]
    REFERENCES[_key] = _cite
    _conductor = int(re.findall(r"^\d+", _row["label"])[0])
    ASSERTED.append(("Conductor", [_curve], [_conductor], _cite))
    ASSERTED.append(("TorsionSubgroup", [_curve], [abelian(0, _row["torsion"])], _cite))
