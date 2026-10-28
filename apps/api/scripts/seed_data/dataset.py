import json
import math
from fractions import Fraction
from typing import Any

from seed_data import (
    analysis,
    combinatorics,
    fields,
    geometry,
    graphs,
    groups,
    linear_algebra,
    numbers,
    polynomials,
    sequences,
    topology,
)
from seed_data.build import (
    Data,
    Endpoint,
    Instance,
    Reference,
    Specimen,
    fraction,
    instance,
    integer,
    rational,
)
from seed_data.catalogue import FILINGS as CATALOGUE_FILINGS
from seed_data.catalogue import SECTIONS as CATALOGUE_SECTIONS
from seed_data.catalogue import TOP_LEVEL, TYPES

AREAS = (
    numbers,
    sequences,
    linear_algebra,
    polynomials,
    analysis,
    combinatorics,
    graphs,
    groups,
    fields,
    topology,
    geometry,
)


def _merged(name: str, base: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for area in AREAS:
        for key, value in getattr(area, name, {}).items():
            if key in merged:
                raise ValueError(f"{area.__name__} redefines {name} entry {key}")
            merged[key] = value
    return merged


def _concatenated(name: str) -> list[Any]:
    return [entry for area in AREAS for entry in getattr(area, name, [])]


def fingerprint(data: Data) -> str:
    return json.dumps(data, sort_keys=True)


def _is_prime(n: int) -> bool:
    return n > 1 and all(n % d for d in range(2, math.isqrt(n) + 1))


def _literal(value: int | Fraction) -> tuple[str, Instance]:
    if isinstance(value, Fraction) and value.denominator != 1:
        latex, data = fraction(value.numerator, value.denominator)
        return str(value), instance(latex, data, ["RationalNumbers"])
    n = int(value)
    kind = "PrimeNumbers" if _is_prime(n) else "PositiveIntegers" if n > 0 else "Integers"
    return str(n), instance(str(n), integer(n), [kind])


def _literal_data(value: int | Fraction) -> Data:
    if isinstance(value, Fraction) and value.denominator != 1:
        return rational(value.numerator, value.denominator)
    return integer(int(value))


SECTIONS: dict[str, Specimen] = _merged("SECTIONS", CATALOGUE_SECTIONS)
OPERATORS: dict[str, Specimen] = _merged("OPERATORS", {})
IMPLEMENTATIONS: dict[str, str] = _merged("IMPLEMENTATIONS", {})
DISPLAYS: dict[str, tuple[str | None, bool]] = _merged("DISPLAYS", {})
REFERENCES: dict[str, list[Reference]] = _merged("REFERENCES", {})
IMAGES: dict[str, str] = _merged("IMAGES", {})
SIGNATURES: list[tuple[str, str, str]] = _concatenated("SIGNATURES")
INSTANCES: dict[str, Instance] = _merged("INSTANCES", {})

FILINGS: dict[str, list[str]] = {
    section: list(filed) for section, filed in CATALOGUE_FILINGS.items()
}
for _area in AREAS:
    for _section, _filed in getattr(_area, "FILINGS", {}).items():
        FILINGS.setdefault(_section, []).extend(_filed)

OWNERS: dict[str, str] = {}
for _key, (_, _, _facets) in INSTANCES.items():
    for _type, _data in _facets:
        _kind = TYPES[_type][2]
        if _kind is not None and next(iter(_data)) != _kind:
            raise ValueError(f"{_key} files {_data} under {_type}, which holds {_kind} data")
        _owner = OWNERS.setdefault(fingerprint(_data), _key)
        if _owner != _key:
            raise ValueError(f"{_owner} and {_key} hold the same data {_data}")


def _resolve(endpoint: Endpoint) -> str:
    if isinstance(endpoint, str):
        if endpoint not in INSTANCES and endpoint not in OPERATORS and endpoint not in TYPES:
            raise ValueError(f"no object is keyed {endpoint}")
        return endpoint
    if isinstance(endpoint, bool):
        raise TypeError("name a truth value by its key, true or false")
    owner = OWNERS.get(fingerprint(_literal_data(endpoint)))
    if owner is not None:
        return owner
    key, created = _literal(endpoint)
    INSTANCES[key] = created
    OWNERS[fingerprint(_literal_data(endpoint))] = key
    return key


RELATIONS: list[tuple[str, list[str], list[str]]] = [
    (operator, [_resolve(e) for e in inputs], [_resolve(e) for e in outputs])
    for operator, inputs, outputs in _concatenated("RELATIONS")
]

for _operator, _domain, _codomain in SIGNATURES:
    if _operator not in OPERATORS or _domain not in TYPES or _codomain not in TYPES:
        raise ValueError(f"signature {_operator}: {_domain} -> {_codomain} names an unknown key")
for _operator in [*IMPLEMENTATIONS, *DISPLAYS]:
    if _operator not in OPERATORS:
        raise ValueError(f"{_operator} is not an operator")

OBJECTS: dict[str, Specimen] = {
    **SECTIONS,
    **{key: (latex, description) for key, (latex, description, _, _) in TYPES.items()},
    **{key: (latex, description) for key, (latex, description, _) in INSTANCES.items()},
    **OPERATORS,
}
if len(OBJECTS) != len(SECTIONS) + len(TYPES) + len(INSTANCES) + len(OPERATORS):
    raise ValueError("a key names two different kinds of object")
for _section, _filed in FILINGS.items():
    for _key in [_section, *_filed]:
        if _key not in OBJECTS:
            raise ValueError(f"filing names unknown key {_key}")
for _key in [*REFERENCES, *IMAGES, *TOP_LEVEL]:
    if _key not in OBJECTS:
        raise ValueError(f"{_key} is not an object")
