-- =========================================================
-- SignalDesk V1 Database Schema
-- PostgreSQL
-- =========================================================

-- Optional: uncomment if you want to reset everything locally
-- DROP TABLE IF EXISTS risk_scores CASCADE;
-- DROP TABLE IF EXISTS scoring_rules CASCADE;
-- DROP TABLE IF EXISTS scoring_configs CASCADE;
-- DROP TABLE IF EXISTS account_signal_snapshots CASCADE;
-- DROP TABLE IF EXISTS accounts CASCADE;

-- =========================================================
-- 1. accounts
-- =========================================================
CREATE TABLE accounts (
    account_id SERIAL PRIMARY KEY,
    account_name VARCHAR(255) NOT NULL UNIQUE,
    segment VARCHAR(50) NOT NULL
        CHECK (segment IN ('SMB', 'Mid-Market', 'Enterprise')),
    arr_usd NUMERIC(12,2) NOT NULL DEFAULT 0,
    strategic_account BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================
-- 2. account_signal_snapshots
-- =========================================================
CREATE TABLE account_signal_snapshots (
    snapshot_id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL
        REFERENCES accounts(account_id)
        ON DELETE CASCADE,
    snapshot_date DATE NOT NULL,

    days_to_renewal INTEGER NOT NULL
        CHECK (days_to_renewal >= 0),

    open_tickets_30d INTEGER NOT NULL DEFAULT 0
        CHECK (open_tickets_30d >= 0),

    reopened_tickets_30d INTEGER NOT NULL DEFAULT 0
        CHECK (reopened_tickets_30d >= 0),

    avg_first_response_hrs NUMERIC(8,2) NOT NULL DEFAULT 0
        CHECK (avg_first_response_hrs >= 0),

    avg_resolution_hrs NUMERIC(8,2) NOT NULL DEFAULT 0
        CHECK (avg_resolution_hrs >= 0),

    sev1_tickets_30d INTEGER NOT NULL DEFAULT 0
        CHECK (sev1_tickets_30d >= 0),

    sentiment_score NUMERIC(5,2) NOT NULL
        CHECK (sentiment_score >= -1.00 AND sentiment_score <= 1.00),

    csat_avg_90d NUMERIC(3,2) NOT NULL
        CHECK (csat_avg_90d >= 1.00 AND csat_avg_90d <= 5.00),

    usage_change_pct_30d NUMERIC(6,2) NOT NULL,
    login_change_pct_30d NUMERIC(6,2) NOT NULL,

    known_bug_flag BOOLEAN NOT NULL DEFAULT FALSE,

    csm_health_score INTEGER NOT NULL
        CHECK (csm_health_score >= 0 AND csm_health_score <= 100),

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_account_snapshot UNIQUE (account_id, snapshot_date)
);

-- =========================================================
-- 3. scoring_configs
-- =========================================================
CREATE TABLE scoring_configs (
    scoring_config_id SERIAL PRIMARY KEY,
    config_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    is_editable BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================
-- 4. scoring_rules
-- =========================================================
CREATE TABLE scoring_rules (
    scoring_rule_id SERIAL PRIMARY KEY,
    scoring_config_id INTEGER NOT NULL
        REFERENCES scoring_configs(scoring_config_id)
        ON DELETE CASCADE,

    metric_name VARCHAR(100) NOT NULL,
    weight NUMERIC(6,2) NOT NULL DEFAULT 1.0,

    threshold_low NUMERIC(10,2),
    threshold_medium NUMERIC(10,2),
    threshold_high NUMERIC(10,2),

    points_low NUMERIC(6,2) NOT NULL DEFAULT 0,
    points_medium NUMERIC(6,2) NOT NULL DEFAULT 0,
    points_high NUMERIC(6,2) NOT NULL DEFAULT 0,
    points_critical NUMERIC(6,2) NOT NULL DEFAULT 0,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_config_metric UNIQUE (scoring_config_id, metric_name)
);

-- =========================================================
-- 5. risk_scores
-- =========================================================
CREATE TABLE risk_scores (
    risk_score_id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL
        REFERENCES accounts(account_id)
        ON DELETE CASCADE,

    snapshot_id INTEGER NOT NULL
        REFERENCES account_signal_snapshots(snapshot_id)
        ON DELETE CASCADE,

    scoring_config_id INTEGER NOT NULL
        REFERENCES scoring_configs(scoring_config_id)
        ON DELETE RESTRICT,

    total_score NUMERIC(5,2) NOT NULL
        CHECK (total_score >= 0 AND total_score <= 100),

    risk_band VARCHAR(20) NOT NULL
        CHECK (risk_band IN ('Low', 'Medium', 'High', 'Critical')),

    top_driver_1 VARCHAR(255),
    top_driver_2 VARCHAR(255),
    top_driver_3 VARCHAR(255),

    recommended_action_1 VARCHAR(255),
    recommended_action_2 VARCHAR(255),
    recommended_action_3 VARCHAR(255),

    scored_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_risk_score_per_snapshot_config
        UNIQUE (snapshot_id, scoring_config_id)
);

-- =========================================================
-- Indexes
-- =========================================================
CREATE INDEX idx_account_signal_snapshots_account_id
    ON account_signal_snapshots(account_id);

CREATE INDEX idx_account_signal_snapshots_snapshot_date
    ON account_signal_snapshots(snapshot_date);

CREATE INDEX idx_risk_scores_account_id
    ON risk_scores(account_id);

CREATE INDEX idx_risk_scores_snapshot_id
    ON risk_scores(snapshot_id);

CREATE INDEX idx_risk_scores_scoring_config_id
    ON risk_scores(scoring_config_id);

CREATE INDEX idx_risk_scores_risk_band
    ON risk_scores(risk_band);

CREATE INDEX idx_scoring_rules_config_id
    ON scoring_rules(scoring_config_id);

CREATE INDEX idx_scoring_configs_is_active
    ON scoring_configs(is_active);

CREATE INDEX idx_scoring_configs_is_default
    ON scoring_configs(is_default);