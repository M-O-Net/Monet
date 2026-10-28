import importlib
import pathlib
import sys
from types import ModuleType, SimpleNamespace

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[1] / "scripts"


@pytest.fixture(scope="module")
def seed_data() -> SimpleNamespace:
    sys.path.insert(0, str(SCRIPTS))
    return SimpleNamespace(
        build=importlib.import_module("seed_data.build"),
        dataset=importlib.import_module("seed_data.dataset"),
    )


def _area(name: str, **exports: object) -> ModuleType:
    area = ModuleType(name)
    area.__dict__.update(exports)
    return area


def test_one_edge_from_two_modules_is_one_relation_crediting_both(
    seed_data: SimpleNamespace,
) -> None:
    source = seed_data.build.Source(
        "KnotInfo", "https://knotinfo.example", "CC BY", "csv", page="https://knotinfo.example/{}"
    )
    first = _area(
        "first",
        RELATIONS=[("Degree", ["P"], ["two"], [source.cite("P")])],
        ASSERTED=[("StemField", ["Phi5"], ["q_zeta5"])],
    )
    second = _area(
        "second",
        ASSERTED=[
            ("Degree", ["P"], [2], [("Atlas", "https://atlas.example/P"), source.cite("P")]),
            ("StemField", ["Phi5"], ["q_zeta5"], [source.cite()]),
        ],
    )

    relations, credits, asserted = seed_data.dataset.merged_relations([first, second])

    assert relations == [("Degree", ["P"], ["two"]), ("StemField", ["Phi5"], ["q_zeta5"])]
    assert credits == [
        [("KnotInfo P", "https://knotinfo.example/P"), ("Atlas", "https://atlas.example/P")],
        [("KnotInfo", "https://knotinfo.example")],
    ]
    assert list(asserted) == [1]


def test_a_deep_link_credit_names_its_entry(seed_data: SimpleNamespace) -> None:
    findstat = seed_data.build.Source(
        "FindStat", "https://www.findstat.org", "CC BY", "api", page="https://findstat.org/{}"
    )

    assert findstat.cite() == ("FindStat", "https://www.findstat.org")
    assert findstat.cite("Mp00059") == ("FindStat Mp00059", "https://findstat.org/Mp00059")
    assert findstat.cite("Mp00070", label="RSK") == ("FindStat RSK", "https://findstat.org/Mp00070")


def test_an_object_credited_from_two_modules_keeps_every_source_once(
    seed_data: SimpleNamespace,
) -> None:
    oeis = ("OEIS", "https://oeis.org/A000045")
    first = _area("first", REFERENCES={"fibonacci": [oeis]})
    second = _area(
        "second", REFERENCES={"fibonacci": [("OEIS A000045", oeis[1]), ("Wiki", "https://w")]}
    )

    merged = seed_data.dataset.merged_references([first, second])

    assert merged == {"fibonacci": [oeis, ("Wiki", "https://w")]}


def test_an_importer_finds_the_key_already_holding_its_data(seed_data: SimpleNamespace) -> None:
    topology = importlib.import_module("seed_data.topology")
    trefoil = seed_data.build.knot("3_1")

    assert seed_data.build.held_by(trefoil, topology) in seed_data.dataset.INSTANCES
    assert seed_data.build.held_by(seed_data.build.knot("not a knot"), topology) is None
