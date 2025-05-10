# Target development environment: macOS
"""
Main application file for MemoriaMCP.

This module initializes and configures the FastMCP application,
defines MCP tools and resources, and handles application startup
and serving.
"""

from fastmcp import FastMCP, Context
from typing import List  # Added for type hints

# Actual imports for database pool and memory manager.
from .db.pool import (
    init_db_pool,
    close_db_pool,
    get_db_pool,
)  # Added close_db_pool and get_db_pool
from .memory.manager import MemoryManager
from .memory.schemas import (
    AddMemoryResponse,
    MemoryQueryResponse,
    Memory,
    HealthResponse,
    MetricsResponse,
)
import uuid  # For memory_id type hint

app = FastMCP(name="MemoriaMCP")  # PyPI: memoria-mcp (Rule 8 User)


@app.on_startup()
async def startup() -> None:
    """
    Initialize resources on application startup.

    This function is called once when the FastMCP application starts.
    It initializes the database connection pool and the memory manager.
    """
    # Initialize the database pool using environment variables by default.
    await init_db_pool()
    # Initialize MemoryManager, it will use get_db_pool internally.
    app.state.mem_mgr = MemoryManager()
    # For /health check, store db pool for direct access if needed
    # Alternatively, MemoryManager could expose a check_db_status method
    app.state.db_pool = get_db_pool()


@app.on_shutdown()
async def shutdown() -> None:
    """
    Clean up resources on application shutdown.

    This function is called once when the FastMCP application shuts down.
    It closes the database connection pool.
    """
    await close_db_pool()


@app.tool()
async def add_memory(ctx: Context, text: str) -> AddMemoryResponse:
    """
    Adds a new memory item.

    Args:
        ctx: The FastMCP context object.
        text: The text content of the memory to add.

    Returns:
        An AddMemoryResponse object containing the ID of the new memory.
    """
    mem_mgr: MemoryManager = ctx.app.state.mem_mgr
    memory_id = await mem_mgr.add_memory(text)
    return AddMemoryResponse(id=memory_id)


@app.resource("/search/memories")  # Changed path for clarity
async def search_memories(
    ctx: Context, query: str, top_k: int = 5
) -> List[MemoryQueryResponse]:
    """
    Searches memories based on text similarity.

    Args:
        ctx: The FastMCP context.
        query: The text to search for.
        top_k: The maximum number of results to return.

    Returns:
        A list of MemoryQueryResponse objects matching the query.
    """
    mem_mgr: MemoryManager = ctx.app.state.mem_mgr
    return await ctx.app.state.mem_mgr.search_memories(query, top_k)


@app.resource("/memory/{memory_id}")
async def get_memory(ctx: Context, memory_id: uuid.UUID) -> Memory | None:
    """
    Retrieves a specific memory item by its ID.

    Args:
        ctx: The FastMCP context.
        memory_id: The UUID of the memory to retrieve.

    Returns:
        The Memory object if found, otherwise None (FastMCP handles 404).
    """
    memory_item = await ctx.app.state.mem_mgr.get_memory_by_id(memory_id)
    return memory_item


@app.resource("/health")
async def health_check(ctx: Context) -> HealthResponse:
    """
    Performs a health check of the service and its dependencies.

    Currently checks database connectivity.

    Args:
        ctx: The FastMCP context.

    Returns:
        A HealthResponse object with service and DB status.
    """
    db_status = "OK"
    try:
        pool = await ctx.app.state.mem_mgr._get_pool()  # Access via manager
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
    except Exception:
        db_status = "Error"

    return HealthResponse(status="OK", db_status=db_status)


@app.resource("/metrics")
async def metrics(ctx: Context) -> MetricsResponse:
    """
    Provides application metrics (placeholder).

    Args:
        ctx: The FastMCP context.

    Returns:
        A MetricsResponse object.
    """
    # In a real application, this would collect and return actual metrics.
    return MetricsResponse(placeholder="Metrics not yet implemented")


if __name__ == "__main__":
    app.serve("0.0.0.0", port=8000)
