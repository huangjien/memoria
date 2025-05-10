# Target development environment: macOS
"""
Pydantic models for memory data structures.

This module defines the Pydantic models used for request and response
validation, and for data representation within the application, particularly
for memory items.

Rule 4 (User): Platform Declaration
Rule 3 (Code Style): All public modules, classes, and functions require
Google-style docstrings.
Rule 3 (Code Style): Type Checking with mypy --strict.
"""

import uuid
from datetime import datetime
from typing import List, Optional  # Added List for potential vector type

from pydantic import BaseModel, Field

# Rule 5 (User): Line length for docstrings is 72 chars.
# Rule 5 (User): Line length for code is 79 chars.


class MemoryBase(BaseModel):
    """Base model for memory attributes."""

    text: str = Field(..., description="The textual content of the memory.")


class MemoryCreate(MemoryBase):
    """Model for creating a new memory item."""

    # No additional fields needed for creation beyond 'text'
    pass


class Memory(MemoryBase):
    """
    Model representing a memory item, including database-generated fields.
    """

    id: uuid.UUID = Field(..., description="Unique identifier for the memory.")
    created_at: datetime = Field(
        ..., description="Timestamp of when the memory was created."
    )
    # The embedding field is often handled internally or is very large,
    # so it might not always be part of the standard API response model.
    # If it needs to be exposed, its type would be List[float].
    embedding: Optional[List[float]] = Field(
        None, description="Optional vector embedding of the memory text."
    )

    class Config:
        """Pydantic model configuration."""

        from_attributes = True  # Changed from orm_mode for Pydantic v2


class MemoryQueryResponse(BaseModel):
    """Model for the response when querying memories."""

    id: uuid.UUID
    text: str
    created_at: datetime
    # Add 'score' or 'similarity' if relevance scoring is part of query
    score: Optional[float] = Field(
        None, description="Relevance score from similarity search."
    )

    class Config:
        """Pydantic model configuration."""

        from_attributes = True


# Example of a model for adding memory, if different from MemoryCreate
class AddMemoryRequest(BaseModel):
    """Request model for adding a memory."""

    text: str = Field(..., min_length=1, description="Memory content.")


class AddMemoryResponse(BaseModel):
    """Response model after adding a memory."""

    id: uuid.UUID = Field(..., description="ID of the created memory.")


class HealthResponse(BaseModel):
    """Model for the /health endpoint response."""

    status: str = Field(..., description="Overall service status.")
    db_status: str = Field(..., description="Database connectivity status.")


class MetricsResponse(BaseModel):
    """Model for the /metrics endpoint response."""

    # Define specific metrics as needed, e.g.:
    # request_count: int
    # db_latency_avg_ms: float
    placeholder: str = Field(
        "Metrics not yet implemented", description="Placeholder for future metrics."
    )
