import pytest
import uuid
from asyncpg import Pool
from memory.manager import MemoryManager
from unittest.mock import AsyncMock

@pytest.fixture(scope="function")
async def mock_pool() -> Pool:
    pool = AsyncMock(Pool)
    return pool

@pytest.fixture(scope="function")
async def memory_manager(mock_pool: Pool) -> MemoryManager:
    return MemoryManager(pool=mock_pool)

async def test_add_memory(memory_manager: MemoryManager):
    memory_id = await memory_manager.add_memory("Test memory")
    assert isinstance(memory_id, uuid.UUID)

async def test_search_memories(memory_manager: MemoryManager):
    results = await memory_manager.search_memories("Test", top_k=3)
    assert isinstance(results, list)
    assert len(results) <= 3

async def test_get_memory_by_id(memory_manager: MemoryManager):
    memory_id = uuid.uuid4()
    memory = await memory_manager.get_memory_by_id(memory_id)
    assert memory is None