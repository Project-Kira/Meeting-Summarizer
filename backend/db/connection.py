import asyncpg
from typing import Optional
from contextlib import asynccontextmanager
from config import get_settings

_pool: Optional[asyncpg.Pool] = None


async def init_db_pool():
    global _pool
    settings = get_settings()
    _pool = await asyncpg.create_pool(
        settings.database_url,
        min_size=5,
        max_size=settings.database_pool_size,
        max_inactive_connection_lifetime=300,
    )
    return _pool


async def close_db_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


def get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("Database pool not initialized. Call init_db_pool() first.")
    return _pool


@asynccontextmanager
async def get_connection():
    pool = get_pool()
    async with pool.acquire() as connection:
        yield connection


@asynccontextmanager
async def get_transaction():
    pool = get_pool()
    async with pool.acquire() as connection:
        async with connection.transaction():
            yield connection
