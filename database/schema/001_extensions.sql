-- ============================================================
-- Data & Security Copilot
-- PostgreSQL Extensions
-- ============================================================

-- UUID generation
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Vector similarity search for the AI/RAG layer
CREATE EXTENSION IF NOT EXISTS vector;