-- Target development environment: macOS
-- Rule 4 (User): Platform Declaration

-- Rule 4 (Project): Full-Text Search / pgvector
-- Enable pgvector if used (as per design.md)
CREATE EXTENSION IF NOT EXISTS vector;

-- DDL for the memories table (as per design.md)
CREATE TABLE IF NOT EXISTS memories (
  id UUID PRIMARY KEY,
  text TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  embedding VECTOR(1536) -- Assuming OpenAI's text-embedding-ada-002 dimension
);

-- Index for full-text search (as per design.md)
CREATE INDEX IF NOT EXISTS idx_memories_text
  ON memories USING GIN (to_tsvector('english', text));

-- Note: Ensure the database user has appropriate permissions.
-- Rule 1 (Security): Read-Only Enforcement (SELECT only for AI-gen code).
-- The DDL itself requires higher privileges to execute initially.