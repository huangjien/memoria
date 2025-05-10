# Target development environment: macOS
"""
Configuration for pytest.

This file defines shared fixtures and hooks for the test suite.
It's automatically discovered by pytest.

Rule 4 (User): Platform Declaration
Rule 2 (Testing): Database Fixtures (pytest-postgresql)
"""

import pytest
import asyncio
from typing import Generator

# from asyncpg import Pool # Uncomment when db.pool is implemented

# Rule 5 (User): Line length for docstrings is 72 chars.
# Rule 5 (User): Line length for code is 79 chars.


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Example fixture for a database pool (using pytest-postgresql)
# This will be expanded upon once db.pool.py is created.
# @pytest.fixture(scope="function")
# async def db_pool(postgresql: Any) -> AsyncGenerator[Pool, None]:
#     """
#     Provides a per-test database pool using pytest-postgresql.
#
#     Args:
#         postgresql: The pytest-postgresql fixture for managing a
#                     temporary PostgreSQL instance.
#
#     Yields:
#         An asyncpg.Pool connected to the temporary database.
#     """
#     # Note: Actual pool creation logic will depend on init_db_pool
#     # from db.pool.py and connection details from pytest-postgresql.
#     # For now, this is a placeholder structure.
#     # from db.pool import get_db_pool, close_db_pool
#
#     # DSN might be constructed like:
#     # dsn = f"postgresql://{postgresql.user}:{postgresql.password}@"
#     #       f"{postgresql.host}:{postgresql.port}/{postgresql.dbname}"
#     # await init_db_pool(dsn=dsn) # Assuming init_db_pool can take DSN
#     # pool = get_db_pool()
#     # yield pool
#     # await close_db_pool()
#     pass # Placeholder


# Add other shared fixtures here as needed.
# For example, a fixture for the MemoryManager instance:
# @pytest.fixture(scope="function")
# async def memory_manager(db_pool: Pool) -> MemoryManager:
#     """Provides a MemoryManager instance for tests."""
#     # from memory.manager import MemoryManager # Uncomment when available
#     # manager = MemoryManager(pool=db_pool) # Assuming manager takes pool
#     # return manager
#     pass # Placeholder


# Rule 3 (Code Style): All public modules, classes, and functions
# require Google-style docstrings.
# Rule 3 (Code Style): Type Checking with mypy --strict.
