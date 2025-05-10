# Target development environment: macOS
"""
Database connection pool management using asyncpg.

This module provides functions to initialize, retrieve, and close
the asyncpg connection pool for the PostgreSQL database.

Rule 4 (User): Platform Declaration
Rule 3 (Project): Database Client (asyncpg 0.27.x)
Rule 3 (Credential Management): Load credentials via env vars.
"""

import os
import asyncpg
from typing import Optional, cast

# Rule 5 (User): Line length for docstrings is 72 chars.
# Rule 5 (User): Line length for code is 79 chars.

_pool: Optional[asyncpg.Pool] = None


async def init_db_pool(
    dsn: Optional[str] = None, min_size: int = 1, max_size: int = 10
) -> None:
    """
    Initializes the asyncpg connection pool.

    This function should be called once during application startup.
    It uses environment variables for database connection parameters
    if a DSN is not explicitly provided.

    Args:
        dsn: Optional database connection string. If None, connection
             parameters are read from environment variables:
             DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME.
        min_size: Minimum number of connections in the pool.
        max_size: Maximum number of connections in the pool.

    Raises:
        RuntimeError: If the pool is already initialized.
        ConnectionRefusedError: If connection to DB fails.
    """
    global _pool
    if _pool is not None:
        raise RuntimeError("Database pool already initialized.")

    if dsn:
        conn_dsn = dsn
    else:
        # Rule 3 (Credential Management): Load from env vars
        db_user = os.getenv("DB_USER", "postgres")
        db_password = os.getenv("DB_PASSWORD", "password")
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "memoria_db")
        conn_dsn = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    try:
        _pool = await asyncpg.create_pool(
            dsn=conn_dsn, min_size=min_size, max_size=max_size
        )
        # Rule 4 (Error Handling): Log exceptions (add logging later)
        print(f"Database pool initialized for {db_name} on {db_host}")
    except Exception as e:
        # Rule 4 (Error Handling): Log exceptions
        print(f"Failed to initialize database pool: {e}")
        # In a real app, use proper logging and possibly re-raise
        # or handle more gracefully.
        raise ConnectionRefusedError("Failed to connect to database") from e


def get_db_pool() -> asyncpg.Pool:
    """
    Retrieves the initialized asyncpg connection pool.

    Returns:
        The asyncpg.Pool instance.

    Raises:
        RuntimeError: If the pool has not been initialized.
    """
    if _pool is None:
        raise RuntimeError("Database pool not initialized. Call init_db_pool() first.")
    # The cast is safe due to the check above.
    return cast(asyncpg.Pool, _pool)


async def close_db_pool() -> None:
    """
    Closes the asyncpg connection pool.

    This function should be called during application shutdown.
    """
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
        print("Database pool closed.")


# Rule 3 (Code Style): All public modules, classes, and functions
# require Google-style docstrings.
# Rule 3 (Code Style): Type Checking with mypy --strict.
