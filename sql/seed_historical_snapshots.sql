-- =========================================================
-- SignalDesk Historical Snapshot Seed Data
-- Adds 5 weekly historical snapshots for every seeded account
-- Tuned to create better driver/action variety in the demo
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
    d.snapshot_date,
    d.days_to_renewal,
    d.open_tickets_30d,
    d.reopened_tickets_30d,
    d.avg_first_response_hrs,
    d.avg_resolution_hrs,
    d.sev1_tickets_30d,
    d.sentiment_score,
    d.csat_avg_90d,
    d.usage_change_pct_30d,
    d.login_change_pct_30d,
    d.known_bug_flag,
    d.csm_health_score
FROM accounts a
JOIN (
    VALUES
        -- =====================================================
        -- Acme Corp (ticket pressure worsening)
        -- =====================================================
        ('Acme Corp', CURRENT_DATE - INTERVAL '35 days', 56,  8, 1, 3.00, 18.00, 0, 0.45, 4.00,  2.00,  2.00, FALSE, 70),
        ('Acme Corp', CURRENT_DATE - INTERVAL '28 days', 49, 10, 1, 4.00, 22.00, 0, 0.38, 3.95,  0.00, -1.00, FALSE, 67),
        ('Acme Corp', CURRENT_DATE - INTERVAL '21 days', 42, 13, 2, 5.00, 28.00, 0, 0.30, 3.90, -2.00, -2.00, FALSE, 64),
        ('Acme Corp', CURRENT_DATE - INTERVAL '14 days', 35, 17, 2, 6.00, 34.00, 0, 0.24, 3.80, -4.00, -4.00, FALSE, 61),
        ('Acme Corp', CURRENT_DATE - INTERVAL '7 days',  28, 20, 3, 7.00, 38.00, 0, 0.20, 3.75, -6.00, -5.00, FALSE, 59),

        -- =====================================================
        -- Northstar Health (SLA deterioration)
        -- =====================================================
        ('Northstar Health', CURRENT_DATE - INTERVAL '35 days', 103, 4, 1,  8.00, 48.00, 0, 0.36, 4.10, -1.00, -1.00, FALSE, 72),
        ('Northstar Health', CURRENT_DATE - INTERVAL '28 days',  96, 4, 1, 10.00, 60.00, 0, 0.32, 4.00, -2.00, -2.00, FALSE, 70),
        ('Northstar Health', CURRENT_DATE - INTERVAL '21 days',  89, 5, 1, 12.00, 74.00, 0, 0.28, 3.95, -3.00, -2.00, FALSE, 68),
        ('Northstar Health', CURRENT_DATE - INTERVAL '14 days',  82, 5, 1, 14.00, 88.00, 0, 0.25, 3.90, -4.00, -3.00, FALSE, 66),
        ('Northstar Health', CURRENT_DATE - INTERVAL '7 days',   75, 5, 1, 16.00, 100.00,0, 0.22, 3.85, -5.00, -4.00, FALSE, 65),

        -- =====================================================
        -- BluePeak Software (healthy stable)
        -- =====================================================
        ('BluePeak Software', CURRENT_DATE - INTERVAL '35 days', 148, 3, 0, 2.50, 18.00, 0, 0.48, 4.35, 3.00, 3.00, FALSE, 82),
        ('BluePeak Software', CURRENT_DATE - INTERVAL '28 days', 141, 3, 0, 2.30, 17.00, 0, 0.50, 4.40, 4.00, 4.00, FALSE, 83),
        ('BluePeak Software', CURRENT_DATE - INTERVAL '21 days', 134, 2, 0, 2.20, 17.00, 0, 0.52, 4.42, 4.00, 4.00, FALSE, 84),
        ('BluePeak Software', CURRENT_DATE - INTERVAL '14 days', 127, 2, 0, 2.10, 16.00, 0, 0.54, 4.46, 5.00, 5.00, FALSE, 85),
        ('BluePeak Software', CURRENT_DATE - INTERVAL '7 days',  120, 2, 0, 2.00, 16.00, 0, 0.55, 4.48, 6.00, 5.00, FALSE, 86),

        -- =====================================================
        -- GreenField Logistics (reopen-driven worsening)
        -- =====================================================
        ('GreenField Logistics', CURRENT_DATE - INTERVAL '35 days', 70, 5, 2, 4.00, 22.00, 0, 0.32, 3.90,  1.00,  1.00, FALSE, 70),
        ('GreenField Logistics', CURRENT_DATE - INTERVAL '28 days', 63, 6, 3, 4.50, 26.00, 0, 0.28, 3.85,  0.00,  0.00, FALSE, 67),
        ('GreenField Logistics', CURRENT_DATE - INTERVAL '21 days', 56, 6, 4, 5.00, 30.00, 0, 0.24, 3.80, -1.00, -1.00, FALSE, 65),
        ('GreenField Logistics', CURRENT_DATE - INTERVAL '14 days', 49, 7, 5, 5.50, 34.00, 0, 0.20, 3.72, -3.00, -2.00, FALSE, 63),
        ('GreenField Logistics', CURRENT_DATE - INTERVAL '7 days',  42, 8, 6, 6.00, 38.00, 0, 0.18, 3.65, -5.00, -3.00, FALSE, 61),

        -- =====================================================
        -- Summit Retail (renewal + usage decline)
        -- =====================================================
        ('Summit Retail', CURRENT_DATE - INTERVAL '35 days', 46, 4, 1, 3.50, 20.00, 0, 0.28, 4.00, -10.00, -8.00, FALSE, 68),
        ('Summit Retail', CURRENT_DATE - INTERVAL '28 days', 39, 4, 1, 3.50, 22.00, 0, 0.22, 3.92, -15.00, -12.00,FALSE, 65),
        ('Summit Retail', CURRENT_DATE - INTERVAL '21 days', 32, 4, 1, 3.80, 24.00, 0, 0.18, 3.84, -22.00, -18.00,FALSE, 62),
        ('Summit Retail', CURRENT_DATE - INTERVAL '14 days', 25, 4, 1, 4.00, 26.00, 0, 0.14, 3.78, -28.00, -24.00,FALSE, 59),
        ('Summit Retail', CURRENT_DATE - INTERVAL '7 days',  18, 4, 1, 4.00, 27.00, 0, 0.12, 3.72, -32.00, -28.00,FALSE, 58),

        -- =====================================================
        -- BrightPath HR (very healthy)
        -- =====================================================
        ('BrightPath HR', CURRENT_DATE - INTERVAL '35 days', 238, 1, 0, 1.20, 10.00, 0, 0.72, 4.60,  8.00,  8.00, FALSE, 88),
        ('BrightPath HR', CURRENT_DATE - INTERVAL '28 days', 231, 1, 0, 1.10,  9.00, 0, 0.74, 4.65, 10.00,  9.00, FALSE, 89),
        ('BrightPath HR', CURRENT_DATE - INTERVAL '21 days', 224, 1, 0, 1.00,  9.00, 0, 0.77, 4.70, 11.00, 10.00, FALSE, 90),
        ('BrightPath HR', CURRENT_DATE - INTERVAL '14 days', 217, 1, 0, 0.90,  8.50, 0, 0.80, 4.75, 12.00, 11.00, FALSE, 91),
        ('BrightPath HR', CURRENT_DATE - INTERVAL '7 days',  210, 1, 0, 0.80,  8.00, 0, 0.82, 4.78, 13.00, 12.00, FALSE, 92),

        -- =====================================================
        -- CloudMint (sentiment-driven worsening)
        -- =====================================================
        ('CloudMint', CURRENT_DATE - INTERVAL '35 days', 91, 3, 1, 2.50, 18.00, 0, -0.10, 3.80,  1.00,  1.00, FALSE, 72),
        ('CloudMint', CURRENT_DATE - INTERVAL '28 days', 84, 3, 1, 2.50, 18.00, 0, -0.22, 3.65, -1.00, -1.00, FALSE, 70),
        ('CloudMint', CURRENT_DATE - INTERVAL '21 days', 77, 4, 1, 2.80, 19.00, 0, -0.35, 3.50, -2.00, -2.00, FALSE, 69),
        ('CloudMint', CURRENT_DATE - INTERVAL '14 days', 70, 4, 1, 3.00, 20.00, 0, -0.48, 3.30, -3.00, -2.00, FALSE, 67),
        ('CloudMint', CURRENT_DATE - INTERVAL '7 days',  63, 4, 1, 3.00, 20.00, 0, -0.58, 3.15, -4.00, -3.00, FALSE, 66),

        -- =====================================================
        -- PixelForge Studio (bug / critical incident-driven)
        -- =====================================================
        ('PixelForge Studio', CURRENT_DATE - INTERVAL '35 days', 83, 2, 0, 2.50, 14.00, 0,  0.20, 3.90, -1.00, -1.00, FALSE, 66),
        ('PixelForge Studio', CURRENT_DATE - INTERVAL '28 days', 76, 2, 0, 2.80, 15.00, 0,  0.10, 3.75, -2.00, -2.00, FALSE, 63),
        ('PixelForge Studio', CURRENT_DATE - INTERVAL '21 days', 69, 2, 1, 3.00, 16.00, 1,  0.02, 3.60, -3.00, -3.00, TRUE,  60),
        ('PixelForge Studio', CURRENT_DATE - INTERVAL '14 days', 62, 3, 1, 3.00, 17.00, 1, -0.04, 3.50, -4.00, -4.00, TRUE,  57),
        ('PixelForge Studio', CURRENT_DATE - INTERVAL '7 days',  55, 3, 1, 3.00, 18.00, 1, -0.06, 3.42, -5.00, -5.00, TRUE,  55),

        -- =====================================================
        -- Vertex Financial (critical multi-factor)
        -- =====================================================
        ('Vertex Financial', CURRENT_DATE - INTERVAL '35 days', 49,  8, 2, 10.00, 70.00, 1, -0.30, 3.20, -20.00, -18.00, TRUE, 38),
        ('Vertex Financial', CURRENT_DATE - INTERVAL '28 days', 42,  9, 3, 12.00, 88.00, 1, -0.40, 3.00, -24.00, -22.00, TRUE, 34),
        ('Vertex Financial', CURRENT_DATE - INTERVAL '21 days', 35, 10, 3, 14.00,105.00, 2, -0.52, 2.85, -28.00, -26.00, TRUE, 31),
        ('Vertex Financial', CURRENT_DATE - INTERVAL '14 days', 28, 11, 4, 16.00,122.00, 2, -0.62, 2.70, -33.00, -30.00, TRUE, 28),
        ('Vertex Financial', CURRENT_DATE - INTERVAL '7 days',  21, 12, 4, 18.00,138.00, 2, -0.68, 2.55, -36.00, -33.00, TRUE, 25),

        -- =====================================================
        -- HarborOps (response-time-driven moderate)
        -- =====================================================
        ('HarborOps', CURRENT_DATE - INTERVAL '35 days', 123, 2, 0,  5.00, 22.00, 0, 0.42, 4.30, 1.00, 1.00, FALSE, 80),
        ('HarborOps', CURRENT_DATE - INTERVAL '28 days', 116, 2, 0,  7.00, 23.00, 0, 0.40, 4.28, 0.00, 0.00, FALSE, 79),
        ('HarborOps', CURRENT_DATE - INTERVAL '21 days', 109, 2, 0,  9.00, 24.00, 0, 0.38, 4.25, -1.00,-1.00, FALSE, 78),
        ('HarborOps', CURRENT_DATE - INTERVAL '14 days', 102, 2, 0, 10.00, 25.00, 0, 0.36, 4.22, -1.00,-1.00, FALSE, 77),
        ('HarborOps', CURRENT_DATE - INTERVAL '7 days',   95, 2, 0, 11.00, 26.00, 0, 0.35, 4.20, -2.00,-1.00, FALSE, 77)

) AS d(
    account_name,
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
ON a.account_name = d.account_name
ON CONFLICT (account_id, snapshot_date) DO NOTHING;