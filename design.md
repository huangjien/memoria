# MemoriaMCP Project Design Documentation

This document describes the complete design of the **FastMCP-based MCP server** using **PostgreSQL** for persistent storage, developed in **Python 3.12.10** and orchestrated via **Docker Compose**, with a streamlined **VS Code** development setup.

## 1. Summary

The server leverages **FastMCP 2.0** as its core framework, exposing read-only memory tools and resources over MCP (Model Context Protocol) ([github.com](https://github.com/jlowin/fastmcp?utm_source=chatgpt.com)). User “memories” are stored in a PostgreSQL `memories` table with full-text search indices or an optional pgvector extension for similarity queries ([github.com](https://github.com/pgvector/pgvector?utm_source=chatgpt.com), [supabase.com](https://supabase.com/docs/guides/database/extensions/pgvector?utm_source=chatgpt.com)). The application uses **asyncpg** for high-performance asynchronous connection pooling ([magicstack.github.io](https://magicstack.github.io/asyncpg/current/usage.html?utm_source=chatgpt.com)). A `docker-compose.yml` defines separate containers for the MCP server and PostgreSQL (Compose v3.8) ([forums.docker.com](https://forums.docker.com/t/docker-compose-version-3-8-or-3-9-for-latest/102439?utm_source=chatgpt.com)). Development and debugging occur in **VS Code**, using official Python and Docker extensions for linting, debugging, and testing with **pytest** ([magicstack.github.io](https://magicstack.github.io/asyncpg/current/api/index.html?utm_source=chatgpt.com)).

## 2. Architecture Overview

### 2.1 FastMCP Server Core
- Utilizes **FastMCP 2.0** to define tools and resources via decorators (`@app.tool()`, `@app.resource()`) ([gofastmcp.com](https://gofastmcp.com/getting-started/welcome?utm_source=chatgpt.com)).
- Startup hook (`@app.on_startup()`) initializes the database pool before serving requests.

### 2.2 PostgreSQL Storage
- **Table Schema** in `db/schema.sql`:
  - `id UUID PRIMARY KEY`
  - `text TEXT NOT NULL`
  - `created_at TIMESTAMP WITH TIME ZONE DEFAULT now()`
  - Optional `embedding VECTOR(1536)` column when using pgvector ([github.com](https://github.com/pgvector/pgvector?utm_source=chatgpt.com), [timescale.com](https://www.timescale.com/blog/similarity-search-on-postgresql-using-openai-embeddings-and-pgvector?utm_source=chatgpt.com)).
- **Full-text search** index on `to_tsvector(text)` for keyword queries ([datacamp.com](https://www.datacamp.com/tutorial/pgvector-tutorial?utm_source=chatgpt.com)).
- **Read-only role** `memory_reader` granted `SELECT` only to enforce no-writes at the DB level.

### 2.3 Embedding & Similarity Search (Optional)
- **pgvector** extension enables high-dimensional vector storage and k-NN search within PostgreSQL ([enterprisedb.com](https://enterprisedb.com/blog/what-is-pgvector?lang=en&utm_source=chatgpt.com), [medium.com](https://medium.com/%40mahadevan.varadhan/postgres-pgvector-store-in-llm-question-answers-5c693109f4be?utm_source=chatgpt.com)).
- Enables semantic similarity queries via SQL: `ORDER BY embedding <-> $1 LIMIT $2`.

### 2.4 Connection Pooling
- **asyncpg.create_pool()** is used to create a reusable pool of connections for low-latency, high-throughput operations ([magicstack.github.io](https://magicstack.github.io/asyncpg/current/usage.html?utm_source=chatgpt.com)).
- Pool parameters tuned (`min_size`, `max_size`) for anticipated load.

## 3. Technology Stack

| Component              | Specification                                                        |
|------------------------|----------------------------------------------------------------------|
| **Language**           | Python 3.12.10                                                          |
| **MCP Framework**      | FastMCP 2.0                                                          |
| **ASGI Server**        | Uvicorn                                                              |
| **DB**                 | PostgreSQL 14+ (+ pgvector)                                          |
| **DB Client**          | asyncpg                                                              |
| **Search**             | PostgreSQL full-text or pgvector                                     |
| **Testing**            | pytest ≥ 7.0.0                                                       |
| **Dev Environment**    | VS Code (+ Python, Docker, Pylance extensions)                       |
| **Compose Format**     | Docker Compose v3.8                                                   |

## 4. Project Structure

```
mcp_server_pg/
├── src/
│   ├── main.py            # FastMCP entrypoint
│   ├── db/
│   │   ├── pool.py        # asyncpg pool init
│   │   └── schema.sql     # DDL (memories table, pgvector)
│   ├── memory/
│   │   ├── manager.py     # insert & query logic
│   │   └── schemas.py     # Pydantic models
│   └── embeddings.py      # (opt) embed via OpenAI
├── tests/
│   ├── test_manager.py    # Unit tests (mock asyncpg)
│   └── test_main.py       # Integration tests via pytest-postgresql ([sheshbabu.com](https://www.sheshbabu.com/posts/fastapi-without-orm-getting-started-with-asyncpg/?utm_source=chatgpt.com))
├── Dockerfile            # Builds the MCP server image
├── docker-compose.yml    # Orchestrates server & Postgres
├── pyproject.toml        # Metadata & deps
├── uv.lock               # Locked dependencies
└── README.md             # Setup & usage
```

## 5. Database Schema

```sql
-- Enable pgvector if used
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS memories (
  id UUID PRIMARY KEY,
  text TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  embedding VECTOR(1536)
);

CREATE INDEX IF NOT EXISTS idx_memories_text
  ON memories USING GIN (to_tsvector('english', text));
```

## 6. Core Code Snippets

### 6.1 Connection Pool (`db/pool.py`)
```python
import os
from asyncpg import create_pool

_pool = None

async def init_db_pool():
    global _pool
    _pool = await create_pool(
        dsn=os.getenv("DATABASE_URL"),
        min_size=5,
        max_size=20
    )
    return _pool

def get_db_pool():
    return _pool
```
> Uses `asyncpg.create_pool()` for efficient asyncio-based DB access ([magicstack.github.io](https://magicstack.github.io/asyncpg/current/usage.html?utm_source=chatgpt.com)).

### 6.2 Memory Manager (`memory/manager.py`)
```python
from uuid import uuid4
from db.pool import get_db_pool
from embeddings import embed_text  # optional

class MemoryManager:
    def __init__(self):
        self.pool = get_db_pool()

    async def add_memory(self, text: str, embedding=None):
        async with self.pool.acquire() as conn:
            mem_id = uuid4()
            if embedding:
                await conn.execute(
                    "INSERT INTO memories(id, text, embedding) VALUES($1,$2,$3)",
                    mem_id, text, embedding
                )
            else:
                await conn.execute(
                    "INSERT INTO memories(id, text) VALUES($1,$2)",
                    mem_id, text
                )
            return str(mem_id)

    async def query_memory(self, query: str, top_k=5):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, text,
                       ts_rank_cd(to_tsvector(text), websearch_to_tsquery($1)) AS rank
                FROM memories
                WHERE to_tsvector(text) @@ websearch_to_tsquery($1)
                ORDER BY rank DESC
                LIMIT $2
                """,
                query, top_k
            )
            return [dict(r) for r in rows]
```
> Full-text search via `ts_rank_cd` and `websearch_to_tsquery` ([datacamp.com](https://www.datacamp.com/tutorial/pgvector-tutorial?utm_source=chatgpt.com)).

### 6.3 FastMCP Server (`src/main.py`)
```python
from fastmcp import FastMCP, Context
from db.pool import init_db_pool
from memory.manager import MemoryManager

app = FastMCP(name="MemoriaMCP")  # PyPI package name: memoria-mcp

@app.on_startup()
async def startup():
    await init_db_pool()
    app.state.mem_mgr = MemoryManager()

@app.tool()
async def add_memory(ctx: Context, text: str):
    id_ = await ctx.app.state.mem_mgr.add_memory(text)
    return {"id": id_}

@app.resource()
async def list_memory(ctx: Context, query: str, top_k: int = 5):
    return await ctx.app.state.mem_mgr.query_memory(query, top_k)

if __name__ == "__main__":
    app.serve("0.0.0.0", port=8000)
```
> FastMCP decorators automatically expose MCP-compliant endpoints ([pypi.org](https://pypi.org/project/fastmcp/2.0.0/?utm_source=chatgpt.com)).

## 7. Docker Compose Configuration

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_USER: memory_reader
      POSTGRES_PASSWORD: secret_password
      POSTGRES_DB: memories_db
    volumes:
      - pgdata:/var/lib/postgresql/data
    networks:
      - mcp-network

  mcp-server:
    build: .
    depends_on:
      - postgres
    environment:
      DATABASE_URL: postgresql://memory_reader:secret_password@postgres:5432/memories_db
    ports:
      - "8000:8000"
    networks:
      - mcp-network

volumes:
  pgdata:

networks:
  mcp-network:
    driver: bridge
```
> Uses Compose spec v3.8 for service orchestration ([forums.docker.com](https://forums.docker.com/t/docker-compose-version-3-8-or-3-9-for-latest/102439?utm_source=chatgpt.com)).

## 8. VS Code Development Setup

- **Extensions**: Python, Pylance, Docker, pytest.
- **Launch Config** (`.vscode/launch.json`):
  ```json
  {
    "configurations": [
      {
        "name": "Debug MCP Server",
        "type": "python",
        "request": "launch",
        "module": "uvicorn",
        "args": ["src.main:app", "--reload"]
      }
    ]
  }
  ```
- **Tasks** (`.vscode/tasks.json`):
  - Install deps: `uv sync`
  - Run tests: `pytest --cov=src --cov-fail-under=90`
  - Lint: `flake8`

## 9. Testing & CI

- **pytest** ≥ 7.0.0 with `pytest-postgresql` plugin for integration tests ([sheshbabu.com](https://www.sheshbabu.com/posts/fastapi-without-orm-getting-started-with-asyncpg/?utm_source=chatgpt.com)).
- **Fixtures** in `conftest.py` for pool setup/teardown.
- **GitHub Actions** pipeline:
  1. `uv sync`
  2. Start PostgreSQL service via `services`
  3. `pytest --cov`
  4. `flake8` & `mypy`

---

This `design.md` encapsulates the end-to-end architecture, technology choices, project organization, and operational setup to build and run your MCP server reliably and consistently.

## 10. License

This project, packaged as `memoria-mcp` on PyPI, is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---


