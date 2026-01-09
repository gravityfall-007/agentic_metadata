
# Agent Events Table
CREATE TABLE IF NOT EXISTS agent_events (
    event_id String,
    agent_id String,
    step_type LowCardinality(String),
    model LowCardinality(String),
    tokens_in UInt32,
    tokens_out UInt32,
    cost_usd Float32,
    duration_ms UInt32,
    status LowCardinality(String),
    error_type LowCardinality(String),
    timestamp DateTime,
    received_at DateTime
)
ENGINE = MergeTree
PARTITION BY toDate(timestamp)
ORDER BY (agent_id, step_type, timestamp);
