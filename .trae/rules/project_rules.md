# project_rules.md

This document defines the technical standards and development guidelines the AI assistant (Claude) should follow for the **MemoriaMCP** project.

## 1. Framework & Dependencies

1. **Python Version**: Use **Python 3.12.10** exclusively.
2. **FastMCP**: Pin to version **2.0.x** in `pyproject.toml`.
3. **Database Client**: Use **asyncpg** version **0.27.x** for PostgreSQL interaction.
4. **Full-Text Search**: Utilize PostgreSQL’s built-in full-text search (`to_tsvector`, `websearch_to_tsquery`) or **pgvector** extension **0.4.x** if enabled.
5. **Dependency Management**: Use `uv` v0.6.x for all package installation and environment management; maintain `uv.lock` for reproducibility.

## 2. Testing Framework

1. **pytest**: Require **pytest ≥ 7.1.0**; configure with `--strict-markers` and `--maxfail=1`.
2. **Database Fixtures**: Use `pytest-postgresql` to spin up a temporary Postgres instance; isolate DB state per test via transactional fixtures.
3. **Mocking**: Leverage `pytest-mock` for unit tests mocking `asyncpg` connections and query results.
4. **Coverage**: Enforce ≥ **90%** code coverage; fail CI if threshold not met.

## 3. Code Style & Quality

1. **PEP 8**: Adhere strictly with `flake8` and `black` formatting.
2. **Type Checking**: Use `mypy` with strict settings (`--strict`); all functions must have type annotations.
3. **Docstrings**: All public modules, classes, and functions require Google-style docstrings.
4. **Linters**: Run `flake8`, `mypy`, and `black --check` in pre-commit hooks.

## 4. Security & API Restrictions

1. **Read-Only Enforcement**: Database user must have **SELECT** privileges only; AI-generated code must never include `INSERT`, `UPDATE`, or `DELETE` statements.
2. **Forbidden Functions**: Disallow use of `eval()`, `exec()`, or dynamic SQL string concatenation; use parameterized queries only.
3. **Credential Management**: Load credentials via environment variables; never hard-code passwords or connection strings.
4. **Error Handling**: Catch and log exceptions without sensitive data; use structured JSON logging.

## 5. Deployment & Operations

1. **Docker Compose**: Follow the provided `docker-compose.yml` (Compose v3.8) for local and CI environments.
2. **Configuration**: All configuration via environment variables; no config files with secrets in the repo.
3. **Health Checks**: Implement a `/health` MCP resource that returns service and DB connectivity status.
4. **Monitoring**: Expose Prometheus metrics endpoint (`/metrics`) for tracking request rates and DB latency.

## 6. CI/CD

1. **GitHub Actions**: Define workflows to:
   - Install dependencies (`uv sync`)
   - Start Postgres service
   - Run `pytest --cov --strict-markers`
   - Lint and type-check
2. **Required Checks**: Pull requests must pass all CI checks before merging.
3. **Release Process**: Tag releases with semantic versioning (`vMAJOR.MINOR.PATCH`); automate PyPI publish of `memoria-mcp` on GitHub Releases.

