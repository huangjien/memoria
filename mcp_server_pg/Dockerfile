# Target development environment: macOS
# Rule 4 (User): Platform Declaration

# Use an official Python runtime as a parent image
# Rule 1 (Project): Python 3.12.10
FROM python:3.12.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install uv for package management
# Rule 5 (Project): Use uv v0.6.x
RUN pip install uv>=0.6.0,<0.7.0

# Copy the project files into the container
COPY pyproject.toml uv.lock* README.md /app/
# If uv.lock does not exist yet, this might need adjustment or
# a step to generate it first if `uv sync` requires it.
# Assuming uv.lock will be generated and committed.

COPY src/ /app/src/
# COPY tests/ /app/tests/ # Tests usually not needed in production image

# Install project dependencies using uv
# Using --system to install into the global site-packages of the image's Python
RUN uv sync --system --no-dev

# Expose the port the app runs on
EXPOSE 8000

# Define the command to run the application
# This assumes your main application entrypoint is src/main.py
# and it can be run directly with python.
# If using a server like uvicorn/gunicorn, adjust accordingly.
# The design.md shows `if __name__ == "__main__": app.serve(...)`
# which is suitable for `python src/main.py` for development,
# but for production, a proper ASGI server is better.
# For now, sticking to the simpler direct execution as per main.py's current form.
# The VS Code launch config uses `uvicorn src.main:app --reload`,
# so for consistency, we might use uvicorn here too.
# Let's install uvicorn as part of main dependencies if it's the runner.
# FastMCP's app.serve() likely uses uvicorn internally or similar.

# If FastMCP's app.serve() is production-ready, this is fine:
CMD ["python", "src/main.py"]

# If a dedicated ASGI server like uvicorn is preferred for production:
# 1. Add "uvicorn" to pyproject.toml dependencies (not dev)
# 2. RUN uv pip install uvicorn (or ensure it's in uv sync)
# 3. CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
# For now, will assume `python src/main.py` is sufficient as per current main.py structure.