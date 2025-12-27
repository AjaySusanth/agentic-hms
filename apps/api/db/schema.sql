-- Run schema.sql once on your DB
CREATE TABLE agent_sessions (
    session_id UUID PRIMARY KEY,
    agent_name TEXT NOT NULL,
    state JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
