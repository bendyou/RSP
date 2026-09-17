-- Лабораторная работа №1. PostgreSQL 16+. Выполнять в пустой базе.
BEGIN;

CREATE TABLE roles (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE CHECK (code IN ('admin','operator','viewer')),
    name VARCHAR(100) NOT NULL
);

CREATE TABLE users (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    role_id BIGINT NOT NULL REFERENCES roles(id),
    email VARCHAR(254) NOT NULL UNIQUE CHECK (email = lower(email)),
    password_hash TEXT NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE servers (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    hostname VARCHAR(253) NOT NULL UNIQUE,
    agent_identity VARCHAR(200) NOT NULL UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_seen_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE metric_types (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    unit VARCHAR(20) NOT NULL
);

CREATE TABLE metric_samples (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    server_id BIGINT NOT NULL REFERENCES servers(id),
    metric_type_id BIGINT NOT NULL REFERENCES metric_types(id),
    collected_at TIMESTAMPTZ NOT NULL,
    value NUMERIC(14,4) NOT NULL CHECK (value >= 0 AND value < 'Infinity'::numeric),
    UNIQUE (server_id, metric_type_id, collected_at)
);

CREATE TABLE alert_rules (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    server_id BIGINT NOT NULL REFERENCES servers(id),
    metric_type_id BIGINT NOT NULL REFERENCES metric_types(id),
    name VARCHAR(150) NOT NULL,
    threshold NUMERIC(14,4) NOT NULL CHECK (threshold >= 0 AND threshold < 'Infinity'::numeric),
    duration_seconds INTEGER NOT NULL CHECK (duration_seconds BETWEEN 30 AND 86400),
    severity VARCHAR(10) NOT NULL CHECK (severity IN ('warning','critical')),
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (server_id, name)
);

CREATE TABLE alerts (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    rule_id BIGINT NOT NULL REFERENCES alert_rules(id),
    opened_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    acknowledged_by BIGINT REFERENCES users(id),
    acknowledged_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    CHECK ((acknowledged_by IS NULL) = (acknowledged_at IS NULL)),
    CHECK (acknowledged_at IS NULL OR acknowledged_at >= opened_at),
    CHECK (resolved_at IS NULL OR resolved_at >= opened_at)
);

CREATE TABLE recommendations (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    server_id BIGINT NOT NULL REFERENCES servers(id),
    metric_type_id BIGINT NOT NULL REFERENCES metric_types(id),
    algorithm_version VARCHAR(50) NOT NULL,
    window_start TIMESTAMPTZ NOT NULL,
    window_end TIMESTAMPTZ NOT NULL,
    anomaly_score NUMERIC(12,4) NOT NULL CHECK (anomaly_score >= 0 AND anomaly_score < 'Infinity'::numeric),
    explanation TEXT NOT NULL,
    suggested_action TEXT NOT NULL,
    status VARCHAR(12) NOT NULL DEFAULT 'new' CHECK (status IN ('new','reviewed','dismissed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (window_end > window_start),
    UNIQUE (server_id, metric_type_id, algorithm_version, window_end)
);

CREATE TABLE operations (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    server_id BIGINT NOT NULL REFERENCES servers(id),
    requested_by BIGINT NOT NULL REFERENCES users(id),
    kind VARCHAR(30) NOT NULL CHECK (kind IN ('restart_service','collect_diagnostics')),
    service_name VARCHAR(100),
    status VARCHAR(12) NOT NULL DEFAULT 'queued' CHECK (status IN ('queued','running','succeeded','failed','unknown')),
    requested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    result_summary TEXT,
    CHECK ((kind = 'restart_service' AND service_name IS NOT NULL AND length(trim(service_name)) > 0) OR (kind = 'collect_diagnostics' AND service_name IS NULL)),
    CHECK (started_at IS NULL OR started_at >= requested_at),
    CHECK (finished_at IS NULL OR finished_at >= COALESCE(started_at, requested_at)),
    CHECK ((status = 'queued' AND started_at IS NULL AND finished_at IS NULL) OR (status = 'running' AND started_at IS NOT NULL AND finished_at IS NULL) OR (status = 'succeeded' AND started_at IS NOT NULL AND finished_at IS NOT NULL) OR (status IN ('failed','unknown') AND finished_at IS NOT NULL))
);

CREATE TABLE audit_events (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    actor_id BIGINT REFERENCES users(id),
    event_type VARCHAR(80) NOT NULL,
    description TEXT NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_users_role ON users (role_id);
CREATE INDEX idx_samples_metric ON metric_samples (metric_type_id);
CREATE INDEX idx_rules_metric ON alert_rules (metric_type_id);
CREATE UNIQUE INDEX uq_alerts_open_rule ON alerts (rule_id) WHERE resolved_at IS NULL;
CREATE INDEX idx_alerts_rule_time ON alerts (rule_id, opened_at DESC);
CREATE INDEX idx_alerts_actor ON alerts (acknowledged_by);
CREATE INDEX idx_recommendations_metric ON recommendations (metric_type_id);
CREATE INDEX idx_recommendations_status_time ON recommendations (status, created_at DESC);
CREATE INDEX idx_operations_server_time ON operations (server_id, requested_at DESC);
CREATE INDEX idx_operations_user ON operations (requested_by);
CREATE INDEX idx_operations_queue ON operations (status, requested_at) WHERE status IN ('queued','running');
CREATE INDEX idx_audit_actor_time ON audit_events (actor_id, occurred_at DESC);
CREATE INDEX idx_audit_time ON audit_events (occurred_at DESC);

INSERT INTO roles (code, name) VALUES ('admin','Администратор'), ('operator','Оператор'), ('viewer','Наблюдатель');
INSERT INTO metric_types (code, name, unit) VALUES
('cpu_usage','Загрузка CPU','percent'),
('memory_usage','Использование RAM','percent'),
('disk_usage','Использование корневого раздела','percent'),
('load_average','Средняя нагрузка за минуту','ratio');

COMMIT;
