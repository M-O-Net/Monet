import uuid

from pydantic import BaseModel

from monet_api.core.schemas import ORMModel
from monet_api.objects.schemas import ObjectOut


class ImplementationOut(ORMModel):
    id: uuid.UUID
    operator_id: uuid.UUID
    code: str


class ImplementationDetailOut(BaseModel):
    """An implementation with its operator inlined.

    Lets an object page label a button without a second round trip per implementation.
    """

    id: uuid.UUID
    operator: ObjectOut
    code: str


class ImplementationWrite(BaseModel):
    operator_id: uuid.UUID
    code: str
