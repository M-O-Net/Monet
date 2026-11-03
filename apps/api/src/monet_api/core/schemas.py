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
    if data is None:
        return None
    try:
        written = json.dumps(data, allow_nan=False)
    except ValueError as error:
        raise ValueError("data must be finite: no NaN or infinity") from error
    if len(written) > MAX_DATA_CHARACTERS:
        raise ValueError(f"data is longer than {MAX_DATA_CHARACTERS} characters")
    if "\\u0000" in written:
        raise ValueError("data must not contain a null character")
    return data


def _no_null_character(text: str | None) -> str | None:
    if text is not None and "\x00" in text:
        raise ValueError("text must not contain a null character")
    return text


Text = AfterValidator(_no_null_character)


Contributor = Annotated[str | None, Field(max_length=200), Text, AfterValidator(_blank_as_none)]
Latex = Annotated[str, Field(max_length=20_000), Text]
Prose = Annotated[str, Field(max_length=10_000), Text]
Label = Annotated[str, Field(max_length=300), Text]
Url = Annotated[str, Field(max_length=2_000), Text]
Code = Annotated[str, Field(max_length=100_000), Text]
Data = Annotated[dict[str, Any] | None, AfterValidator(_bounded)]
