# /// script
# requires-python = ">=3.13"
# dependencies = ["httpx==0.28.1", "sympy==1.14.0"]
# ///
"""Snapshot number fields, elliptic curves and small groups from LMFDB, Cremona and the ATLAS.

Run from apps/api/scripts with `uv run import_fields_curves_groups.py --cache <dir>`. Every
response is cached in that directory, so a second run touches no network.
"""

import argparse
import hashlib
import json
import pathlib
import re
import time
import urllib.parse
from collections import Counter
from collections.abc import Callable
from typing import Any

import httpx
from seed_data import groups as monet_groups

SCRIPTS = pathlib.Path(__file__).resolve().parent
SNAPSHOT = SCRIPTS / "seed_data" / "sources"
SANDBOX = SCRIPTS.parents[1] / "web" / "src" / "sandbox"
IMPLEMENTATIONS = SCRIPTS / "implementations"

USER_AGENT = "Monet-import/1.0 (+https://monet.wiki)"
LMFDB = "https://www.lmfdb.org"
CRAWL_DELAY = {"www.lmfdb.org": 31.0}
DEFAULT_DELAY = 1.1
CREMONA_FILE = "allgens/allgens.00000-09999"
CREMONA = f"https://raw.githubusercontent.com/JohnCremona/ecdata/master/{CREMONA_FILE}"
ATLAS = "http://brauer.maths.qmul.ac.uk/Atlas"
CYCLOTOMIC = ["4.0.125.1", "4.0.256.1", "6.0.16807.1", "3.3.49.1", "4.0.144.1", "6.0.19683.1"]
SIMPLE = ["60.5", "168.42", "360.118", "504.156", "660.13"]
MAX_CONDUCTOR = 50
ATLAS_REPS = {
    "alt/A5": ["A5G1-p5B0", "A5G1-p6B0"],
    "lin/L27": ["L27G1-p8B0"],
    "alt/A6": ["A6G1-p6aB0", "A6G1-p10B0"],
    "lin/L28": ["L28G1-p9B0"],
    "lin/L211": ["L211G1-p11aB0", "L211G1-p12B0"],
    "spor/M11": ["M11G1-p11B0", "M11G1-p12B0"],
}
ATLAS_SAME_AS = {"A5G1-p5B0": "a5"}
CHALLENGED = {
    "13.1": {"permgroup": {"degree": 13, "generators": [[*range(1, 13), 0]]}},
    "16.7": {
        "permgroup": {
            "degree": 8,
            "generators": [[*range(1, 8), 0], [(8 - i) % 8 for i in range(8)]],
        }
    },
}


class Fetcher:
    def __init__(self, cache: pathlib.Path) -> None:
        self.cache = cache
        self.requests = Counter[str]()
        self.last: dict[str, float] = {}

    def __call__(self, url: str) -> str:
        target = self.cache / hashlib.sha256(url.encode()).hexdigest()
        if target.exists():
            return target.read_text()
        host = urllib.parse.urlparse(url).hostname or ""
        delay = CRAWL_DELAY.get(host, DEFAULT_DELAY)
        for attempt in range(4):
            time.sleep(max(0.0, self.last.get(host, 0.0) + delay - time.monotonic()))
            response = httpx.get(url, headers={"User-Agent": USER_AGENT}, timeout=120)
            self.last[host] = time.monotonic()
            self.requests[host] += 1
            if response.status_code not in (429, 500, 502, 503, 504):
                break
            time.sleep(delay * 2 ** (attempt + 1))
        response.raise_for_status()
        if "recaptcha" in response.text.lower():
            raise RuntimeError(f"{host} answered {url} with a challenge: stop, do not retry")
        self.cache.mkdir(parents=True, exist_ok=True)
        target.write_text(response.text)
        return response.text


def _search(path: str, params: dict[str, str], query: dict[str, Any], showcol: str = "") -> str:
    shown = {"showcol": showcol} if showcol else {}
    arguments = {**params, **shown, "download": "1", "query": str(query), "Submit": "text"}
    return f"{LMFDB}/{path}/?{urllib.parse.urlencode(arguments)}"


def _download_rows(text: str) -> list[list[Any]]:
    return [
        [json.loads(cell) for cell in line.split("\t")]
        for line in text.splitlines()
        if "\t" in line and not line.startswith("#")
    ]


def _sandbox() -> dict[str, Any]:
    scope: dict[str, Any] = {"__name__": "__main__"}
    for name in ("prelude.py", "runner.py"):
        exec(compile((SANDBOX / name).read_text(), name, "exec"), scope)  # noqa: S102
    return scope


class Monet:
    def __init__(self) -> None:
        self.scope = _sandbox()

    def compute(self, implementation: str, data: dict[str, Any]) -> list[dict[str, Any]]:
        code = (IMPLEMENTATIONS / f"{implementation}.py").read_text()
        result = self.scope["run"](code, json.dumps([{"latex": "", "data": data}]))
        return [output["data"] for output in json.loads(result)["outputs"]]

    def canonical(self, data: dict[str, Any]) -> dict[str, Any]:
        code = (IMPLEMENTATIONS / "centre.py").read_text()
        canonical: Callable[[Any], Any] = self.scope["_load"](code)["_canonical"]
        result: dict[str, Any] = self.scope["to_data"](canonical(self.scope["from_data"](data)))
        return result

    def curve(self, ainvs: list[int]) -> dict[str, Any]:
        x, y, eq = self.scope["_X"], self.scope["_Y"], self.scope["sympy"].Eq
        a1, a2, a3, a4, a6 = ainvs
        equation = eq(y**2 + a1 * x * y + a3 * y, x**3 + a2 * x**2 + a4 * x + a6)
        result: dict[str, Any] = self.scope["to_data"](equation)
        return result

    def subgroup_equal(self, left: dict[str, Any], right: dict[str, Any]) -> bool:
        first, second = (self.scope["from_data"](d) for d in (left, right))
        return bool(
            first.degree == second.degree
            and first.order() == second.order()
            and all(second.contains(g) for g in first.generators)
        )


def _permutations(cycles_text: str, degree: int) -> list[list[int]]:
    generators = []
    for generator in re.split(r",\s*(?=\()", cycles_text.strip()):
        image = list(range(degree))
        for cycle in re.findall(r"\(([\d,\s]+)\)", generator):
            points = [int(p) - 1 for p in cycle.split(",")]
            for source, target in zip(points, points[1:] + points[:1], strict=True):
                image[source] = target
        generators.append(image)
    return generators


def _points(cycles_text: str) -> int:
    return max(int(p) for p in re.findall(r"\d+", cycles_text))


def _abelian_invariants(name: str) -> list[int]:
    if name == "C_1":
        return []
    primary: list[int] = []
    for factor in name.replace("\\times", "*").split("*"):
        match = re.fullmatch(r"\s*C_\{?(\d+)\}?(?:\^\{?(\d+)\}?)?\s*", factor)
        if match is None:
            raise ValueError(f"{name} is not a product of cyclic groups")
        primary += _primary([int(match.group(1))] * int(match.group(2) or 1))
    return _invariant_factors(primary)


def _invariant_factors(primary: list[int]) -> list[int]:
    by_prime: dict[int, list[int]] = {}
    for power in primary:
        prime = next(p for p in range(2, power + 1) if power % p == 0)
        by_prime.setdefault(prime, []).append(power)
    columns = [sorted(powers, reverse=True) for powers in by_prime.values()]
    depth = max((len(column) for column in columns), default=0)
    factors = [1] * depth
    for column in columns:
        for k, power in enumerate(column):
            factors[k] *= power
    return sorted(factors)


def _write(path: pathlib.Path, header: list[str], rows: list[list[Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["\t".join(header)] + [
        "\t".join(json.dumps(cell, separators=(", ", ": ")) for cell in row) for row in rows
    ]
    path.write_text("\n".join(lines) + "\n")


def number_fields(fetch: Fetcher) -> None:
    quadratic = _search(
        "NumberField",
        {"degree": "2", "discriminant": "-100..100"},
        {"degree": 2, "disc_abs": {"$lte": 100}},
    )
    cubic = _search(
        "NumberField",
        {"degree": "3", "discriminant": "-300..300"},
        {"$or": [{"degree": 3, "disc_abs": {"$lte": 300}}, {"label": {"$in": CYCLOTOMIC}}]},
    )
    rows = _download_rows(fetch(quadratic)) + _download_rows(fetch(cubic))
    _write(
        SNAPSHOT / "lmfdb" / "number_fields.tsv",
        ["label", "coefficients", "discriminant", "galois_group", "class_group"],
        rows,
    )


def elliptic_curves(fetch: Fetcher, monet: Monet) -> None:
    url = _search(
        "EllipticCurve/Q",
        {"conductor": f"1-{MAX_CONDUCTOR}"},
        {"conductor": {"$lte": MAX_CONDUCTOR}},
        showcol="cremona_label.disc.ainvs",
    )
    rows = [
        [label, cremona, conductor, discriminant, torsion, ainvs, monet.curve(ainvs)]
        for label, cremona, _, conductor, discriminant, _, torsion, _, ainvs in _download_rows(
            fetch(url)
        )
    ]
    _write(
        SNAPSHOT / "lmfdb" / "elliptic_curves.tsv",
        ["label", "cremona_label", "conductor", "discriminant", "torsion", "ainvs", "curve"],
        rows,
    )
    cremona = []
    for line in fetch(CREMONA).splitlines():
        conductor, isogeny_class, number, ainvs, rank, torsion = line.split()[:6]
        if int(conductor) > MAX_CONDUCTOR:
            break
        cremona.append(
            [
                f"{conductor}{isogeny_class}{number}",
                json.loads(ainvs),
                int(rank),
                json.loads(torsion),
            ]
        )
    _write(SNAPSHOT / "cremona" / "allgens.tsv", ["label", "ainvs", "rank", "torsion"], cremona)


def _monet_permutation(label: str) -> dict[str, Any] | None:
    order, index = map(int, label.split("."))
    for _, _, facets in monet_groups.INSTANCES.values():
        if any(data == {"smallgroup": [order, index]} for _, data in facets):
            first = facets[0][1]
            return first if "permgroup" in first else None
    return None


def _held_by_monet(label: str) -> bool:
    order, index = map(int, label.split("."))
    return any(
        data == {"smallgroup": [order, index]}
        for _, _, facets in monet_groups.INSTANCES.values()
        for _, data in facets
    )


def abstract_groups(fetch: Fetcher, monet: Monet) -> None:
    url = _search(
        "Groups/Abstract",
        {"order": "1-16"},
        {"$or": [{"order": {"$lte": 16}}, {"label": {"$in": SIMPLE}}]},
        showcol="abelian_quotient.composition_length.permutation_degree",
    )
    rows = _download_rows(fetch(url))
    invariants = {
        label: _abelian_invariants(name)
        for label, name, *_, kind in rows
        if kind in ("Trivial", "Cyclic") or kind.startswith("Abelian")
    }
    snapshot = []
    for label, name, order, _, length, _, center, abelianization, _, kind in rows:
        permutation = None
        if label in CHALLENGED:
            permutation = monet.canonical(CHALLENGED[label])
        elif not _held_by_monet(label) and label not in SIMPLE:
            gap = fetch(f"{LMFDB}/Groups/Abstract/{label}/download/gap")
            cycles = re.search(r"^GPerm := Group\((.*)\);$", gap, re.MULTILINE)
            if cycles is None:
                raise ValueError(f"LMFDB's GAP download of {label} has no permutation group")
            degree = _points(cycles.group(1))
            lmfdb_permutation = {
                "permgroup": {
                    "degree": degree,
                    "generators": _permutations(cycles.group(1), degree),
                }
            }
            permutation = monet.canonical(lmfdb_permutation)
        computed_from = permutation or _monet_permutation(label)
        centre = factors = None
        if computed_from is not None:
            (centre,) = monet.compute("centre", computed_from)
            centre_order = monet.compute("group_order", centre)[0]["int"]
            centre_invariants = monet.compute("abelianisation", centre)[0]["abelian"]["torsion"]
            expected = invariants[center]
            if centre_order != int(center.split(".")[0]) or _primary(centre_invariants) != _primary(
                expected
            ):
                raise ValueError(f"{label}: Monet's centre {centre} is not LMFDB's {center}")
            if order != monet.compute("group_order", computed_from)[0]["int"]:
                raise ValueError(f"{label}: Monet's order differs from LMFDB's {order}")
            if kind not in ("Simple", "Trivial"):
                factors = [
                    data["smallgroup"]
                    for data in monet.compute("composition_factors", computed_from)
                ]
                if len(factors) != length:
                    raise ValueError(f"{label}: {len(factors)} composition factors, not {length}")
        snapshot.append(
            [
                label,
                name,
                order,
                center,
                abelianization,
                invariants.get(label),
                permutation,
                centre,
                factors,
            ]
        )
    _write(
        SNAPSHOT / "lmfdb" / "abstract_groups.tsv",
        [
            "label",
            "name",
            "order",
            "center",
            "abelianization",
            "abelian_invariants",
            "permutation",
            "centre",
            "composition_factors",
        ],
        snapshot,
    )


def _primary(torsion: list[int]) -> list[int]:
    primary = []
    for factor in torsion:
        n, p = factor, 2
        while n > 1:
            power = 1
            while n % p == 0:
                n //= p
                power *= p
            if power > 1:
                primary.append(power)
            p += 1
    return sorted(primary)


def atlas(fetch: Fetcher, monet: Monet) -> None:
    rows = []
    for family, names in ATLAS_REPS.items():
        for name in names:
            degree = int(re.findall(r"-p(\d+)", name)[0])
            cycles = [
                fetch(f"{ATLAS}/{family}/gap/{name}.g{k}").split(":=")[1].strip().rstrip(";")
                for k in (1, 2)
            ]
            data = {
                "permgroup": {
                    "degree": degree,
                    "generators": [_permutations(c, degree)[0] for c in cycles],
                }
            }
            same_as = ATLAS_SAME_AS.get(name)
            if same_as is not None:
                (_, _, facets) = monet_groups.INSTANCES[same_as]
                if not monet.subgroup_equal(data, facets[0][1]):
                    same_as = None
            centre = monet.compute("centre", data)[0] if degree <= 10 else None
            rows.append([family.split("/")[1], name, data, same_as, centre])
    _write(
        SNAPSHOT / "atlas" / "permutation_representations.tsv",
        ["group", "representation", "permutation", "same_as", "centre"],
        rows,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=pathlib.Path, required=True)
    fetch = Fetcher(parser.parse_args().cache)
    monet = Monet()
    number_fields(fetch)
    elliptic_curves(fetch, monet)
    abstract_groups(fetch, monet)
    atlas(fetch, monet)
    print(f"requests made: {dict(fetch.requests) or 'none, all cached'}")


if __name__ == "__main__":
    main()
