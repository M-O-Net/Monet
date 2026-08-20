import asyncio
from urllib.parse import urlparse

import asyncpg

from monet_api.core.config import settings

TEST_DB_NAME = "monet_test"


async def main() -> None:
    url = urlparse(settings.database_url.replace("postgresql+asyncpg", "postgresql"))
    dbname = url.path.lstrip("/")
    if dbname != TEST_DB_NAME:
        raise SystemExit(
            f"refusing to drop {dbname!r}: this script recreates {TEST_DB_NAME!r} and nothing "
            "else. Run `just test-api`, which points the test service at it."
        )
    admin = await asyncpg.connect(
        host=url.hostname,
        port=url.port or 5432,
        user=url.username,
        password=url.password,
        database="postgres",
    )
    try:
        await admin.execute(f'DROP DATABASE IF EXISTS "{dbname}" WITH (FORCE)')
        await admin.execute(f'CREATE DATABASE "{dbname}"')
        print(f"recreated database {dbname}")
    finally:
        await admin.close()


if __name__ == "__main__":
    asyncio.run(main())
