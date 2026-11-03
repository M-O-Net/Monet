import json
from typing import Annotated, Any

from pydantic import AfterValidator, BaseModel, ConfigDict, Field

MAX_DATA_CHARACTERS = 100_000
MAX_ITEMS = 50


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


def _blank_as_none(name: str | None) -> str | None:
    stripped = (name or "").strip()
    return stripped or None


def _bounded(data: dict[str, Any] | None) -> dict[str, Any] | None:
    if data is not None and len(json.dumps(data)) > MAX_DATA_CHARACTERS:
        raise ValueError(f"data is longer than {MAX_DATA_CHARACTERS} characters")
    return data


Contributor = Annotated[str | None, Field(max_length=200), AfterValidator(_blank_as_none)]
Latex = Annotated[str, Field(max_length=20_000)]
Prose = Annotated[str, Field(max_length=10_000)]
Label = Annotated[str, Field(max_length=300)]
Url = Annotated[str, Field(max_length=2_000)]
Code = Annotated[str, Field(max_length=100_000)]
Data = Annotated[dict[str, Any] | None, AfterValidator(_bounded)]
