-- =========================================================
-- SignalDesk V1 Seed Defaults
-- Inserts:
--   1. Default scoring configuration
--   2. Default scoring rules
-- =========================================================

BEGIN;

-- =========================================================
-- 1. Insert default scoring configuration
-- =========================================================
INSERT INTO scoring_configs (
    config_name,
    description,
    is_active,
    is_default,
    is_editable
)
VALUES (
    'Default V1 Model',
    'Baseline scoring model for SignalDesk V1. Designed for general B2B SaaS support risk detection.',
    TRUE,
    TRUE,
    TRUE
)
ON CONFLICT (config_name) DO NOTHING;

-- =========================================================
-- 2. Insert default scoring rules
-- =========================================================
-- Notes:
-- - weight acts as a multiplier
-- - thresholds represent low / medium / high breakpoints
-- - points_critical applies when value exceeds threshold_high
-- - scoring engine should interpret thresholds based on metric type
-- =========================================================

INSERT INTO scoring_rules (
    scoring_config_id,
    metric_name,
    weight,
    threshold_low,
    threshold_medium,
    threshold_high,
    points_low,
    points_medium,
    points_high,
    points_critical
)
SELECT
    sc.scoring_config_id,
    v.metric_name,
    v.weight,
    v.threshold_low,
    v.threshold_medium,
    v.threshold_high,
    v.points_low,
    v.points_medium,
    v.points_high,
    v.points_critical
FROM scoring_configs sc
JOIN (
    VALUES
        -- -------------------------------------------------
        -- Support volume signals
        -- -------------------------------------------------
        ('open_tickets_30d',        1.00,  2.00,   4.00,   7.00,   5.00,  10.00,  15.00,  20.00),
        ('reopened_tickets_30d',    1.00,  1.00,   2.00,   3.00,   5.00,  10.00,  15.00,  20.00),

        -- -------------------------------------------------
        -- Response and resolution delays
        -- -------------------------------------------------
        ('avg_first_response_hrs',  1.00,  2.00,   8.00,  24.00,   3.00,   6.00,  10.00,  15.00),
        ('avg_resolution_hrs',      1.00, 24.00,  72.00, 120.00,   4.00,   7.00,  10.00,  15.00),

        -- -------------------------------------------------
        -- Critical incident volume
        -- -------------------------------------------------
        ('sev1_tickets_30d',        1.00,  1.00,   2.00,   3.00,   5.00,  10.00,  15.00,  20.00),

        -- -------------------------------------------------
        -- Sentiment
        -- For this metric, lower values are worse.
        -- The scoring engine should handle it as an inverse metric.
        -- Example interpretation:
        -- threshold_low    = 0.30
        -- threshold_medium = 0.00
        -- threshold_high   = -0.30
        -- -------------------------------------------------
        ('sentiment_score',         1.00,  0.30,   0.00,  -0.30,   4.00,   9.00,  15.00,  20.00),

        -- -------------------------------------------------
        -- Product usage decline
        -- Lower values are worse.
        -- Example interpretation:
        -- threshold_low    = -5
        -- threshold_medium = -15
        -- threshold_high   = -30
        -- -------------------------------------------------
        ('usage_change_pct_30d',    1.00, -5.00, -15.00, -30.00,   3.00,   6.00,  10.00,  15.00),

        -- -------------------------------------------------
        -- Login activity decline
        -- Lower values are worse.
        -- -------------------------------------------------
        ('login_change_pct_30d',    0.75, -5.00, -15.00, -30.00,   2.00,   5.00,   8.00,  12.00),

        -- -------------------------------------------------
        -- Renewal proximity
        -- Lower values are worse.
        -- Example interpretation:
        -- threshold_low    = 90
        -- threshold_medium = 60
        -- threshold_high   = 30
        -- -------------------------------------------------
        ('days_to_renewal',         1.00, 90.00,  60.00,  30.00,   1.00,   3.00,   5.00,  10.00),

        -- -------------------------------------------------
        -- Customer success health
        -- Lower values are worse.
        -- Example interpretation:
        -- threshold_low    = 70
        -- threshold_medium = 50
        -- threshold_high   = 30
        -- -------------------------------------------------
        ('csm_health_score',        1.00, 70.00,  50.00,  30.00,   3.00,   6.00,  10.00,  15.00),

        -- -------------------------------------------------
        -- Known bug flag
        -- Boolean-style metric. The engine can treat:
        -- 0 = no impact, 1 = impacted
        -- Only points_critical really matters here.
        -- -------------------------------------------------
        ('known_bug_flag',          1.00,  0.00,   0.00,   1.00,   0.00,   0.00,   5.00,  10.00)

) AS v(
    metric_name,
    weight,
    threshold_low,
    threshold_medium,
    threshold_high,
    points_low,
    points_medium,
    points_high,
    points_critical
)
ON sc.config_name = 'Default V1 Model'
ON CONFLICT (scoring_config_id, metric_name) DO NOTHING;

COMMIT;