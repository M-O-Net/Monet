import asyncio
import datetime

from sqlmodel.ext.asyncio.session import AsyncSession

from monet_api.stats import repository
from monet_api.stats.schemas import StorageCategory, StorageCategoryOut, StorageStatsOut

CATEGORY_TABLES: dict[StorageCategory, frozenset[str]] = {
    "instances": frozenset(
        {"objects", "memberships", "object_references", "section_filings", "top_level_objects"}
    ),
    "edges": frozenset({"relations", "relation_input", "relation_output", "relation_references"}),
    "maps": frozenset({"implementations", "signatures", "operator_displays"}),
    "types": frozenset({"types", "subtypes"}),
    "activity": frozenset({"comments", "events"}),
}

FRESH_FOR = datetime.timedelta(seconds=60)

_lock = asyncio.Lock()
_cached: StorageStatsOut | None = None


async def get_storage_stats(session: AsyncSession) -> StorageStatsOut:
    global _cached
    async with _lock:
        now = datetime.datetime.now(datetime.UTC)
        if _cached is None or now - _cached.measured_at >= FRESH_FOR:
            _cached = await _measure(session, now)
        return _cached


async def _measure(session: AsyncSession, now: datetime.datetime) -> StorageStatsOut:
    database_bytes = await repository.database_size(session)
    tables = await repository.list_table_sizes(session)
    images = await repository.estimate_column_fill(session, "objects", "image_url")

    categories = [
        StorageCategoryOut(
            category=category,
            size_bytes=sum(table.size_bytes for table in tables if table.name in names),
            rows=sum(table.rows for table in tables if table.name in names),
            tables=sorted(table.name for table in tables if table.name in names),
        )
        for category, names in CATEGORY_TABLES.items()
    ]
    classified = frozenset().union(*CATEGORY_TABLES.values())
    unclassified = [table for table in tables if table.name not in classified]
    categories.append(
        StorageCategoryOut(
            category="other",
            size_bytes=max(0, database_bytes - sum(c.size_bytes for c in categories)),
            rows=sum(table.rows for table in unclassified),
            tables=sorted(table.name for table in unclassified),
        )
    )
    return StorageStatsOut(
        database_bytes=database_bytes,
        categories=categories,
        image_links=images.rows,
        image_link_bytes=images.size_bytes,
        measured_at=now,
    )
