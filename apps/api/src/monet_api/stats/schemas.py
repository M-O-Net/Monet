import datetime
from typing import Literal

from pydantic import BaseModel

StorageCategory = Literal["instances", "edges", "maps", "types", "activity", "other", "overhead"]


class StorageCategoryOut(BaseModel):
    category: StorageCategory
    size_bytes: int
    rows: int
    tables: list[str]


class StorageStatsOut(BaseModel):
    database_bytes: int
    categories: list[StorageCategoryOut]
    image_links: int
    image_link_bytes: int
    measured_at: datetime.datetime
