from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


def _blank_as_none(name: str | None) -> str | None:
    stripped = (name or "").strip()
    return stripped or None


Contributor = Annotated[str | None, AfterValidator(_blank_as_none)]
