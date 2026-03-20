-- =========================================================
-- SignalDesk V1 Demo Data Seed
-- Inserts:
--   1. Demo accounts
--   2. Demo account signal snapshots
-- =========================================================

BEGIN;

-- =========================================================
-- 1. Insert demo accounts
-- =========================================================
INSERT INTO accounts (
    account_name,
    segment,
    arr_usd,
    strategic_account
)
VALUES
    ('Acme Corp',              'Enterprise', 250000.00, TRUE),
    ('Northstar Health',       'Enterprise', 180000.00, TRUE),
    ('BluePeak Software',      'Mid-Market',  85000.00, FALSE),
    ('GreenField Logistics',   'Mid-Market',  62000.00, FALSE),
    ('Summit Retail',          'Mid-Market',  71000.00, TRUE),
    ('BrightPath HR',          'SMB',         18000.00, FALSE),
    ('CloudMint',              'SMB',         12000.00, FALSE),
    ('PixelForge Studio',      'SMB',          9000.00, FALSE),
    ('Vertex Financial',       'Enterprise', 320000.00, TRUE),
    ('HarborOps',              'Mid-Market',  54000.00, FALSE)
ON CONFLICT (account_name) DO NOTHING;

-- =========================================================
-- 2. Insert demo account signal snapshots
-- One snapshot per account for today
-- Tuned for better variety in top drivers and actions
-- =========================================================
INSERT INTO account_signal_snapshots (
    account_id,
    snapshot_date,
    days_to_renewal,
    open_tickets_30d,
    reopened_tickets_30d,
    avg_first_response_hrs,
    avg_resolution_hrs,
    sev1_tickets_30d,
    sentiment_score,
    csat_avg_90d,
    usage_change_pct_30d,
    login_change_pct_30d,
    known_bug_flag,
    csm_health_score
)
SELECT
    a.account_id,
    CURRENT_DATE,
    v.days_to_renewal,
    v.open_tickets_30d,
    v.reopened_tickets_30d,
    v.avg_first_response_hrs,
    v.avg_resolution_hrs,
    v.sev1_tickets_30d,
    v.sentiment_score,
    v.csat_avg_90d,
    v.usage_change_pct_30d,
    v.login_change_pct_30d,
    v.known_bug_flag,
    v.csm_health_score
FROM accounts a
JOIN (
    VALUES
        -- account_name,            days_to_renewal, open_tickets_30d, reopened_tickets_30d, avg_first_response_hrs, avg_resolution_hrs, sev1_tickets_30d, sentiment_score, csat_avg_90d, usage_change_pct_30d, login_change_pct_30d, known_bug_flag, csm_health_score

        -- Ticket-volume-driven
        ('Acme Corp',                    28, 22, 3,  8.00,  42.00, 0,  0.18, 3.70,  -8.00,  -6.00, FALSE, 58),

        -- SLA / slow resolution-driven
        ('Northstar Health',             75,  5, 1, 18.00, 110.00, 0,  0.20, 3.80,  -5.00,  -4.00, FALSE, 64),

        -- Healthy / low-risk
        ('BluePeak Software',           120,  2, 0,  2.00,  16.00, 0,  0.55, 4.50,   6.00,   5.00, FALSE, 86),

        -- Reopen-driven
        ('GreenField Logistics',         42,  8, 7,  6.00,  40.00, 0,  0.16, 3.60,  -6.00,  -4.00, FALSE, 60),

        -- Renewal + usage decline
        ('Summit Retail',                18,  4, 1,  4.00,  28.00, 0,  0.10, 3.70, -34.00, -30.00, FALSE, 57),

        -- Very healthy
        ('BrightPath HR',               210,  1, 0,  0.80,   8.00, 0,  0.82, 4.80,  14.00,  12.00, FALSE, 93),

        -- Sentiment-driven
        ('CloudMint',                    63,  4, 1,  3.00,  20.00, 0, -0.62, 3.10,  -4.00,  -3.00, FALSE, 66),

        -- Known-bug / critical incident-driven
        ('PixelForge Studio',            55,  3, 1,  3.00,  18.00, 1, -0.08, 3.40,  -6.00,  -5.00, TRUE,  54),

        -- Multi-factor critical
        ('Vertex Financial',             21, 12, 4, 20.00, 145.00, 2, -0.70, 2.50, -38.00, -34.00, TRUE,  24),

        -- Moderate / response-time-driven
        ('HarborOps',                    95,  2, 0, 12.00,  26.00, 0,  0.34, 4.20,  -2.00,  -1.00, FALSE, 77)

) AS v(
    account_name,
    days_to_renewal,
    open_tickets_30d,
    reopened_tickets_30d,
    avg_first_response_hrs,
    avg_resolution_hrs,
    sev1_tickets_30d,
    sentiment_score,
    csat_avg_90d,
    usage_change_pct_30d,
    login_change_pct_30d,
    known_bug_flag,
    csm_health_score
)
ON a.account_name = v.account_name
ON CONFLICT (account_id, snapshot_date) DO NOTHING;

COMMIT;