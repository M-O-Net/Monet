from seed_data.build import Data, Instance, Reference, RelationSpec, abelian, small_group
from seed_data.lmfdb import MONET, snapshot, subgroup_key
from seed_data.sources import ATLAS, LMFDB, SMALL_GROUPS

GROUPS = {
    "A5": ("a5", "60.5", "A_{5}"),
    "L27": ("psl27", "168.42", r"\mathrm{PSL}(2, 7)"),
    "A6": ("a6", "360.118", "A_{6}"),
    "L28": ("psl28", "504.156", r"\mathrm{PSL}(2, 8)"),
    "L211": ("psl211", "660.13", r"\mathrm{PSL}(2, 11)"),
    "M11": ("m11", None, "M_{11}"),
}
M11_ORDER = 7920
ORDERS = {row["label"]: row["order"] for row in snapshot("lmfdb/abstract_groups.tsv")}

INSTANCES: dict[str, Instance] = {}
REFERENCES: dict[str, list[Reference]] = {}
RELATIONS: list[RelationSpec] = []
ASSERTED: list[RelationSpec] = []


def _seeded(key: str) -> bool:
    return key in INSTANCES or any(key in getattr(area, "INSTANCES", {}) for area in MONET)


def _simple_group(group: str, permutation: Data, cite: list[Reference]) -> str:
    key, label, latex = GROUPS[group]
    facets = [("PermutationGroups", permutation)]
    REFERENCES[key] = cite
    if label is None:
        RELATIONS.append(("GroupOrder", [key], [M11_ORDER], cite))
    else:
        identifier = small_group(*map(int, label.split(".")))
        facets.append(("SimpleGroups", identifier))
        source = [LMFDB.cite(f"Groups/Abstract/{label}", label)]
        REFERENCES[key] += [*source, SMALL_GROUPS.cite()]
        RELATIONS.append(("GroupOrder", [key], [ORDERS[label]], source))
        ASSERTED.append(("CompositionFactors", [key], [identifier], source))
    INSTANCES[key] = (latex, None, facets)
    return key


def _representation(group: str, permutation: Data, cite: list[Reference]) -> str:
    main, label, latex = GROUPS[group]
    degree = permutation["permgroup"]["degree"]
    key = f"{main}_on_{degree}"
    INSTANCES[key] = (rf"{latex} \leq S_{{{degree}}}", None, [("PermutationGroups", permutation)])
    REFERENCES[key] = cite
    RELATIONS.append(("GroupOrder", [key], [M11_ORDER if label is None else ORDERS[label]]))
    if label is not None:
        identifier = small_group(*map(int, label.split(".")))
        ASSERTED.append(("SmallGroupID", [key], [identifier], [*cite, SMALL_GROUPS.cite()]))
        ASSERTED.append(("CompositionFactors", [key], [identifier]))
    return key


for _row in snapshot("atlas/permutation_representations.tsv"):
    _cite = [ATLAS.cite(_row["representation"])]
    _main = GROUPS[_row["group"]][0]
    if _row["same_as"] is not None:
        _key = _row["same_as"]
        REFERENCES[_key] = _cite
    elif not _seeded(_main):
        _key = _simple_group(_row["group"], _row["permutation"], _cite)
    else:
        _key = _representation(_row["group"], _row["permutation"], _cite)
    RELATIONS.append(("Abelianisation", [_key], [abelian(0, [])]))
    if _row["centre"] is not None:
        RELATIONS.append(("Centre", [_key], [subgroup_key(_row["centre"], f"centre_{_key}")]))
