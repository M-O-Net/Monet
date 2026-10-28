import ast
import hashlib
import itertools
import json
import pathlib
import sys
import time
from collections.abc import Callable
from typing import Any

import httpx
from seed_data import combinatorics, graphs

SITE = "https://www.findstat.org"
SNAPSHOT = pathlib.Path(__file__).parent / "seed_data" / "sources" / "findstat.json"
CRAWL_DELAY_SECONDS = 21
ENTRIES = {
    "Mp00044": "conjugate",
    "Mp00059": "Robinson-Schensted insertion tableau",
    "Mp00064": "reverse",
    "Mp00066": "inverse",
    "Mp00067": "Foata bijection",
    "Mp00069": "complement",
    "Mp00070": "Robinson-Schensted recording tableau",
    "Mp00081": "reading word permutation",
    "Mp00083": "shape",
    "Mp00084": "conjugate",
    "Mp00085": "Schützenberger involution",
    "Mp00108": "cycle type",
    "Mp00312": "Glaisher-Franklin",
    "Mp00037": "to partition of connected components",
    "Mp00111": "complement",
    "St000003": "number of standard Young tableaux",
    "St000004": "major index",
    "St000010": "length of the partition",
    "St000018": "number of inversions",
    "St000021": "number of descents",
    "St000022": "number of fixed points",
    "St000031": "number of cycles",
    "St000037": "sign",
    "St000058": "order",
    "St000062": "longest increasing subsequence",
    "St000147": "largest part",
    "St000183": "Durfee square",
}
RESTRICTED_TO = {"Mp00312": lambda partition: all(part % 2 for part in partition)}
Value = int | list[int] | list[list[int]] | tuple[list[tuple[int, int]], int] | dict[str, Any]
LARGEST_PERMUTATION = 4
LARGEST_PARTITION = 6
LARGEST_TABLEAU = 4


def _url(entry: str) -> str:
    folder = "MapsDatabase" if entry.startswith("Mp") else "StatisticsDatabase"
    return f"{SITE}/{folder}/{entry}.txt"


def fetch(url: str, cache: pathlib.Path) -> str:
    path = cache / hashlib.sha256(url.encode()).hexdigest()
    if not path.exists():
        for attempt in range(5):
            time.sleep(CRAWL_DELAY_SECONDS * 2**attempt)
            response = httpx.get(
                url, headers={"User-Agent": "Monet-import/1.0 (+https://monet.wiki)"}, timeout=60
            )
            if response.status_code not in {429, 500, 502, 503, 504}:
                break
        response.raise_for_status()
        path.write_bytes(response.content)
    return path.read_text()


def values(export: str) -> list[tuple[Any, Any]]:
    _, table = export.split("Map images:" if "Map images:" in export else "Statistic values:")
    pairs = []
    for line in table.splitlines():
        if "=>" in line:
            element, image = line.split("=>")
            pairs.append((ast.literal_eval(element.strip()), ast.literal_eval(image.strip())))
    return pairs


def _held(kind: str) -> list[Any]:
    return [
        data[kind]
        for area in (combinatorics, graphs)
        for _, _, facets in area.INSTANCES.values()
        for data in [facets[0][1]]
        if kind in data
    ]


SEEDED_PERMUTATIONS = [[i + 1 for i in p] for p in _held("perm")]
SEEDED_PARTITIONS = _held("partition")
SEEDED_TABLEAUX = _held("tableau")
SEEDED_GRAPHS = _held("graph")


def _kept_permutation(p: list[int]) -> bool:
    return 0 < len(p) <= LARGEST_PERMUTATION or p in SEEDED_PERMUTATIONS


def _kept_partition(p: list[int]) -> bool:
    return 0 < sum(p) <= LARGEST_PARTITION or p in SEEDED_PARTITIONS


def _kept_tableau(t: list[list[int]]) -> bool:
    return 0 < sum(map(len, t)) <= LARGEST_TABLEAU or t in SEEDED_TABLEAUX


def _kept(value: Value, collection: str) -> bool:
    return {
        "Permutations": _kept_permutation,
        "Integer partitions": _kept_partition,
        "Standard tableaux": _kept_tableau,
        "Integer": lambda _: True,
    }[collection](value)


def _collection(export: str, field: str) -> str:
    return export.split(f"{field}:")[1].split("\n")[0].strip()


def _edges(edges: list[tuple[int, int]]) -> set[tuple[int, int]]:
    return {(min(e), max(e)) for e in edges}


def _isomorphic(seeded: dict[str, Any], found: tuple[list[tuple[int, int]], int]) -> bool:
    edges, order = found
    if seeded["order"] != order or len(seeded["edges"]) != len(edges):
        return False
    target = _edges([tuple(e) for e in seeded["edges"]])
    source = _edges(edges)
    return any(
        _edges([(relabel[u], relabel[v]) for u, v in source]) == target
        for relabel in itertools.permutations(range(order))
    )


def _graph_pairs(
    pairs: list[tuple[Any, Any]], image: Callable[[dict[str, Any], Value], Value | None]
) -> list[tuple[dict[str, Any], Any, Any]]:
    found = []
    for seeded in SEEDED_GRAPHS:
        if seeded["order"] > 7:
            continue
        for element, value in pairs:
            if _isomorphic(seeded, element):
                found.append((seeded, element, image(seeded, value)))
    return found


def _complement(seeded: dict[str, Any], value: Value) -> dict[str, Any] | None:
    present = _edges([tuple(e) for e in seeded["edges"]])
    order = seeded["order"]
    missing = [[u, v] for u, v in itertools.combinations(range(order), 2) if (u, v) not in present]
    held = {"order": order, "edges": missing}
    return held if held in SEEDED_GRAPHS and _isomorphic(held, value) else None


def _notation(value: Value) -> str | int:
    return value if isinstance(value, int) else json.dumps(value, separators=(",", ":"))


def snapshot(cache: pathlib.Path) -> dict[str, Any]:
    entries: dict[str, Any] = {}
    for entry in ENTRIES:
        export = fetch(_url(entry), cache)
        domain = _collection(export, "Domain" if entry.startswith("Mp") else "Collection")
        codomain = _collection(export, "Codomain") if entry.startswith("Mp") else "Integer"
        pairs = values(export)
        if domain == "Graphs":
            image = (lambda _, value: value) if codomain != "Graphs" else _complement
            kept = [
                [seeded, value]
                for seeded, _, value in _graph_pairs(pairs, image)
                if value is not None and (codomain == "Graphs" or _kept(value, codomain))
            ]
        else:
            kept = [
                [element, value]
                for element, value in pairs
                if _kept(element, domain)
                and _kept(value, codomain)
                and RESTRICTED_TO.get(entry, lambda _: True)(element)
            ]
        entries[entry] = {
            "domain": domain,
            "codomain": codomain,
            "values": {_notation(element): _notation(value) for element, value in kept},
        }
        print(f"{entry} ({ENTRIES[entry]}): {len(kept)} of {len(pairs)} values kept")
    return entries


if __name__ == "__main__":
    SNAPSHOT.parent.mkdir(exist_ok=True)
    SNAPSHOT.write_text(
        json.dumps(snapshot(pathlib.Path(sys.argv[1])), indent=2, ensure_ascii=False) + "\n"
    )
