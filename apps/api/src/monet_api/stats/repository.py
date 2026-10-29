from typing import NamedTuple

import sqlalchemy as sa
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

_user_tables = sa.table(
    "pg_stat_user_tables",
    sa.column("relid", sa.BigInteger),
    sa.column("schemaname", sa.String),
    sa.column("relname", sa.String),
    sa.column("n_live_tup", sa.BigInteger),
)
_column_stats = sa.table(
    "pg_stats",
    sa.column("schemaname", sa.String),
    sa.column("tablename", sa.String),
    sa.column("attname", sa.String),
    sa.column("null_frac", sa.Float),
    sa.column("avg_width", sa.Integer),
)


class TableSize(NamedTuple):
    name: str
    size_bytes: int
    rows: int


class ColumnFill(NamedTuple):
    rows: int
    size_bytes: int


async def database_size(session: AsyncSession) -> int:
    result = await session.exec(select(sa.func.pg_database_size(sa.func.current_database())))
    return int(result.one())


async def list_table_sizes(session: AsyncSession) -> list[TableSize]:
    tables = _user_tables.c
    result = await session.exec(
        select(
            tables.relname, sa.func.pg_total_relation_size(tables.relid), tables.n_live_tup
        ).where(tables.schemaname == sa.func.current_schema())
    )
    return [TableSize(str(name), int(size), int(rows)) for name, size, rows in result.all()]


async def estimate_column_fill(session: AsyncSession, table: str, column: str) -> ColumnFill:
    tables, stats = _user_tables.c, _column_stats.c
    result = await session.exec(
        select(tables.n_live_tup * (1 - stats.null_frac), stats.avg_width)
        .select_from(
            _user_tables.join(
                _column_stats,
                sa.and_(stats.schemaname == tables.schemaname, stats.tablename == tables.relname),
            )
        )
        .where(
            tables.schemaname == sa.func.current_schema(),
            tables.relname == table,
            stats.attname == column,
        )
    )
    row = result.one_or_none()
    if row is None:
        return ColumnFill(0, 0)
    filled, width = row
    return ColumnFill(round(filled), round(filled * width))
