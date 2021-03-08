from typing import Optional

import aiomysql
import dsnparse
from aiomysql import Pool


class DatabasePool:
    def __init__(self) -> None:
        self._pool: Optional[Pool] = None

    def __call__(self) -> Pool:
        if self._pool is None:
            raise ValueError(
                "The connect method must have been called before using the __call__ "
                "method."
            )
        return self._pool

    async def connect(self, dsn: str) -> None:
        r = dsnparse.parse(dsn)
        self._pool = await aiomysql.create_pool(
            host=r.host,
            port=r.port,
            user=r.username,
            password=r.password,
            db=r.database,
        )

    async def close(self) -> None:
        if self._pool:
            self._pool.close()
            await self._pool.wait_closed()
