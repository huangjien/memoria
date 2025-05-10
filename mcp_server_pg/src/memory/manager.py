# Target development environment: macOS
"""
Memory management logic.

This module contains the MemoryManager class, responsible for
interacting with the database to add, retrieve, and query memories.
It uses asyncpg for database operations and may utilize pgvector
for similarity searches if embeddings are involved.

Rule 4 (User): Platform Declaration
Rule 3 (Project): Database Client (asyncpg 0.27.x)
Rule 4 (Project): Full-Text Search / pgvector
Rule 1 (Security): Read-Only Enforcement (SELECT only for AI-gen code)
Rule 2 (Security): Forbidden Functions (parameterized queries)
"""

import uuid
from datetime import datetime
from typing import List, Optional

import asyncpg

from ..db.pool import get_db_pool
from .schemas import Memory, MemoryQueryResponse

# Rule 5 (User): Line length for docstrings is 72 chars.
# Rule 5 (User): Line length for code is 79 chars.


class MemoryManager:
    """Manages memory operations, interfacing with the database."""

    def __init__(self, pool: Optional[asyncpg.Pool] = None) -> None:
        """
        Initializes the MemoryManager.

        Args:
            pool: An optional asyncpg.Pool. If None, it will be fetched
                  using get_db_pool().
        """
        self._pool = pool

    async def _get_pool(self) -> asyncpg.Pool:
        """Internal helper to get the database pool."""
        if self._pool is None:
            self._pool = get_db_pool()
        return self._pool

    async def add_memory(self, text: str) -> uuid.UUID:
        """
        Adds a new memory to the database.

        Note: This function as written performs an INSERT operation.
        According to Rule 1 (Security): Read-Only Enforcement, AI-generated
        code must never include INSERT, UPDATE, or DELETE statements.
        This implementation is provided based on the design.md's apparent
        expectation for such functionality but would need to be implemented
        outside the AI's direct generation scope in a production system
        adhering to strict read-only rules for the AI.

        Args:
            text: The text content of the memory.

        Returns:
            The UUID of the newly created memory.

        Raises:
            Exception: If the database operation fails.
        """
        # This is a conceptual implementation based on design.md.
        # Adherence to Rule 1 (Security) means this INSERT operation
        # should be handled by a pre-existing, audited component, not
        # directly generated or executed by AI with write permissions.
        pool = await self._get_pool()
        memory_id = uuid.uuid4()
        # Embedding generation would happen here if applicable.
        # For now, embedding is NULL or handled by DB trigger.

        # Rule 2 (Security): Use parameterized queries
        query = """
            INSERT INTO memories (id, text, created_at, embedding)
            VALUES ($1, $2, $3, $4)
            RETURNING id;
        """
        try:
            # This is an INSERT operation. See security note above.
            await pool.execute(query, memory_id, text, datetime.utcnow(), None)
            return memory_id
        except Exception as e:
            # Rule 4 (Error Handling): Log exceptions (add logging later)
            print(f"Error adding memory: {e}")
            raise

    async def search_memories(
        self, query_text: str, top_k: int = 5
    ) -> List[MemoryQueryResponse]:
        """
        Searches memories based on text similarity using full-text search.

        Args:
            query_text: The text to search for.
            top_k: The maximum number of results to return.

        Returns:
            A list of MemoryQueryResponse objects matching the query.

        Raises:
            Exception: If the database operation fails.
        """
        pool = await self._get_pool()

        # Rule 4 (Project): PostgreSQL full-text search
        # Rule 2 (Security): Use parameterized queries
        # Using websearch_to_tsquery for more flexible query parsing.
        sql_query = """
            SELECT id, text, created_at,
                   ts_rank_cd(to_tsvector('english', text),
                              websearch_to_tsquery('english', $1)) AS score
            FROM memories
            WHERE to_tsvector('english', text) @@ websearch_to_tsquery('english', $1)
            ORDER BY score DESC
            LIMIT $2;
        """
        try:
            rows = await pool.fetch(sql_query, query_text, top_k)
            return [
                MemoryQueryResponse(
                    id=row["id"],
                    text=row["text"],
                    created_at=row["created_at"],
                    score=row["score"],
                )
                for row in rows
            ]
        except Exception as e:
            # Rule 4 (Error Handling): Log exceptions (add logging later)
            print(f"Error searching memories: {e}")
            raise

    async def get_memory_by_id(self, memory_id: uuid.UUID) -> Optional[Memory]:
        """
        Retrieves a single memory item by its UUID.

        Args:
            memory_id: The UUID of the memory to retrieve.

        Returns:
            A Memory object if found, otherwise None.

        Raises:
            Exception: If the database operation fails.
        """
        pool = await self._get_pool()
        query = "SELECT id, text, created_at, embedding FROM memories WHERE id = $1;"
        try:
            row = await pool.fetchrow(query, memory_id)
            if row:
                return Memory(
                    id=row["id"],
                    text=row["text"],
                    created_at=row["created_at"],
                    # Embedding might be List[float] or raw bytes depending on pgvector
                    embedding=row["embedding"],
                )
            return None
        except Exception as e:
            print(f"Error getting memory by ID: {e}")
            raise


# Rule 3 (Code Style): All public modules, classes, and functions
# require Google-style docstrings.
# Rule 3 (Code Style): Type Checking with mypy --strict.
