-- =========================================================
-- SignalDesk Historical Snapshot Seed Data
-- Adds 5 weekly historical snapshots for every seeded account
-- Compatible with the current wide account_signal_snapshots schema
-- Safe to rerun because of ON CONFLICT (account_id, snapshot_date) DO NOTHING
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
        -- Acme Corp (deteriorating)
        -- =====================================================
        ('Acme Corp', CURRENT_DATE - INTERVAL '35 days', 120,  4, 1,  3.00, 12.00, 0,  0.65, 4.20,   5.00,   4.00, FALSE, 75),
        ('Acme Corp', CURRENT_DATE - INTERVAL '28 days', 113,  6, 1,  4.00, 14.00, 0,  0.60, 4.10,   3.00,   2.00, FALSE, 72),
        ('Acme Corp', CURRENT_DATE - INTERVAL '21 days', 106,  8, 2,  6.00, 18.00, 0,  0.55, 4.00,   1.00,   0.00, FALSE, 70),
        ('Acme Corp', CURRENT_DATE - INTERVAL '14 days',  99, 11, 3,  7.00, 21.00, 1,  0.48, 3.90,  -2.00,  -3.00, TRUE,  65),
        ('Acme Corp', CURRENT_DATE - INTERVAL '7 days',   92, 14, 4,  9.00, 25.00, 1,  0.42, 3.80,  -5.00,  -6.00, TRUE,  60),

        -- =====================================================
        -- Northstar Health (improving)
        -- =====================================================
        ('Northstar Health', CURRENT_DATE - INTERVAL '35 days', 200, 16, 5, 12.00, 32.00, 1, 0.30, 3.50, -12.00, -10.00, TRUE,  48),
        ('Northstar Health', CURRENT_DATE - INTERVAL '28 days', 193, 15, 5, 11.00, 30.00, 1, 0.36, 3.60, -10.00,  -8.00, TRUE,  52),
        ('Northstar Health', CURRENT_DATE - INTERVAL '21 days', 186, 13, 4, 10.00, 28.00, 1, 0.42, 3.70,  -8.00,  -6.00, FALSE, 55),
        ('Northstar Health', CURRENT_DATE - INTERVAL '14 days', 179, 11, 3,  9.00, 24.00, 0, 0.50, 3.90,  -6.00,  -4.00, FALSE, 60),
        ('Northstar Health', CURRENT_DATE - INTERVAL '7 days',  172,  9, 3,  8.00, 21.00, 0, 0.58, 4.00,  -3.00,  -2.00, FALSE, 65),

        -- =====================================================
        -- BluePeak Software (stable healthy)
        -- =====================================================
        ('BluePeak Software', CURRENT_DATE - INTERVAL '35 days', 250,  6, 1, 5.00, 18.00, 0, 0.70, 4.20, 2.00, 3.00, FALSE, 80),
        ('BluePeak Software', CURRENT_DATE - INTERVAL '28 days', 243,  6, 1, 5.00, 18.00, 0, 0.72, 4.20, 2.00, 3.00, FALSE, 80),
        ('BluePeak Software', CURRENT_DATE - INTERVAL '21 days', 236,  5, 1, 5.00, 17.00, 0, 0.71, 4.20, 2.00, 2.00, FALSE, 81),
        ('BluePeak Software', CURRENT_DATE - INTERVAL '14 days', 229,  6, 1, 5.00, 18.00, 0, 0.70, 4.30, 3.00, 3.00, FALSE, 80),
        ('BluePeak Software', CURRENT_DATE - INTERVAL '7 days',  222,  5, 1, 5.00, 17.00, 0, 0.73, 4.30, 3.00, 3.00, FALSE, 82),

        -- =====================================================
        -- GreenField Logistics (gradually worsening)
        -- =====================================================
        ('GreenField Logistics', CURRENT_DATE - INTERVAL '35 days', 180,  5, 1,  4.00, 16.00, 0, 0.68, 4.20,  2.00,  2.00, FALSE, 78),
        ('GreenField Logistics', CURRENT_DATE - INTERVAL '28 days', 173,  6, 1,  5.00, 17.00, 0, 0.65, 4.10,  1.00,  1.00, FALSE, 75),
        ('GreenField Logistics', CURRENT_DATE - INTERVAL '21 days', 166,  7, 2,  6.00, 19.00, 0, 0.62, 4.00,  0.00,  0.00, FALSE, 72),
        ('GreenField Logistics', CURRENT_DATE - INTERVAL '14 days', 159,  9, 2,  7.00, 21.00, 1, 0.58, 3.90, -2.00, -3.00, FALSE, 68),
        ('GreenField Logistics', CURRENT_DATE - INTERVAL '7 days',  152, 11, 3,  8.00, 24.00, 1, 0.52, 3.80, -4.00, -5.00, TRUE,  65),

        -- =====================================================
        -- Summit Retail (declining engagement)
        -- =====================================================
        ('Summit Retail', CURRENT_DATE - INTERVAL '35 days', 150,  8, 2,  5.00, 18.00, 0, 0.40, 4.10,  1.00,  1.00, FALSE, 70),
        ('Summit Retail', CURRENT_DATE - INTERVAL '28 days', 143,  9, 2,  6.00, 19.00, 0, 0.32, 4.00, -2.00, -2.00, FALSE, 66),
        ('Summit Retail', CURRENT_DATE - INTERVAL '21 days', 136, 11, 3,  7.00, 21.00, 0, 0.20, 3.80, -5.00, -4.00, FALSE, 60),
        ('Summit Retail', CURRENT_DATE - INTERVAL '14 days', 129, 13, 3,  8.00, 24.00, 1, 0.08, 3.60, -8.00, -7.00, FALSE, 55),
        ('Summit Retail', CURRENT_DATE - INTERVAL '7 days',  122, 15, 4,  9.00, 26.00, 1, -0.05, 3.40, -12.00, -10.00, TRUE,  50),

        -- =====================================================
        -- BrightPath HR (healthy improving)
        -- =====================================================
        ('BrightPath HR', CURRENT_DATE - INTERVAL '35 days', 210, 2, 0, 1.50, 12.00, 0, 0.72, 4.60,  4.00,  4.00, FALSE, 84),
        ('BrightPath HR', CURRENT_DATE - INTERVAL '28 days', 203, 2, 0, 1.20, 11.00, 0, 0.76, 4.70,  6.00,  5.00, FALSE, 86),
        ('BrightPath HR', CURRENT_DATE - INTERVAL '21 days', 196, 1, 0, 1.00, 10.00, 0, 0.80, 4.75,  8.00,  7.00, FALSE, 88),
        ('BrightPath HR', CURRENT_DATE - INTERVAL '14 days', 189, 1, 0, 0.80,  9.00, 0, 0.84, 4.80, 10.00,  8.00, FALSE, 90),
        ('BrightPath HR', CURRENT_DATE - INTERVAL '7 days',  182, 1, 0, 0.60,  8.00, 0, 0.88, 4.85, 12.00, 10.00, FALSE, 92),

        -- =====================================================
        -- CloudMint (moderate improving)
        -- =====================================================
        ('CloudMint', CURRENT_DATE - INTERVAL '35 days', 160, 12, 4, 7.00, 28.00, 1, 0.05, 3.70, -10.00, -8.00, TRUE,  52),
        ('CloudMint', CURRENT_DATE - INTERVAL '28 days', 153, 10, 3, 6.00, 24.00, 1, 0.12, 3.80,  -8.00, -6.00, TRUE,  58),
        ('CloudMint', CURRENT_DATE - INTERVAL '21 days', 146,  8, 3, 5.00, 21.00, 0, 0.22, 3.90,  -5.00, -4.00, FALSE, 63),
        ('CloudMint', CURRENT_DATE - INTERVAL '14 days', 139,  6, 2, 4.50, 18.00, 0, 0.32, 4.00,  -3.00, -2.00, FALSE, 68),
        ('CloudMint', CURRENT_DATE - INTERVAL '7 days',  132,  5, 1, 4.00, 16.00, 0, 0.40, 4.10,  -1.00, -1.00, FALSE, 72),

        -- =====================================================
        -- PixelForge Studio (volatile)
        -- =====================================================
        ('PixelForge Studio', CURRENT_DATE - INTERVAL '35 days', 180,  5, 1, 2.00, 14.00, 0,  0.55, 4.40,  8.00,  7.00, FALSE, 88),
        ('PixelForge Studio', CURRENT_DATE - INTERVAL '28 days', 173,  9, 2, 4.00, 20.00, 0,  0.28, 4.00, -2.00, -1.00, FALSE, 75),
        ('PixelForge Studio', CURRENT_DATE - INTERVAL '21 days', 166, 14, 4, 8.00, 26.00, 1, -0.08, 3.50, -12.00, -10.00, TRUE, 58),
        ('PixelForge Studio', CURRENT_DATE - INTERVAL '14 days', 159,  8, 2, 3.00, 17.00, 0,  0.32, 4.10,  2.00,  1.00, FALSE, 78),
        ('PixelForge Studio', CURRENT_DATE - INTERVAL '7 days',  152,  4, 1, 1.50, 10.00, 0,  0.62, 4.70, 10.00,  8.00, FALSE, 90),

        -- =====================================================
        -- Vertex Financial (high risk worsening)
        -- =====================================================
        ('Vertex Financial', CURRENT_DATE - INTERVAL '35 days', 110, 14, 4, 10.00, 40.00, 1,  0.05, 3.40, -12.00, -10.00, TRUE, 45),
        ('Vertex Financial', CURRENT_DATE - INTERVAL '28 days', 103, 16, 5, 12.00, 52.00, 1, -0.08, 3.20, -18.00, -16.00, TRUE, 40),
        ('Vertex Financial', CURRENT_DATE - INTERVAL '21 days',  96, 18, 5, 14.00, 68.00, 2, -0.18, 3.00, -24.00, -22.00, TRUE, 35),
        ('Vertex Financial', CURRENT_DATE - INTERVAL '14 days',  89, 22, 6, 18.00, 92.00, 2, -0.32, 2.70, -32.00, -30.00, TRUE, 28),
        ('Vertex Financial', CURRENT_DATE - INTERVAL '7 days',   82, 26, 7, 22.00, 120.00, 3, -0.48, 2.40, -40.00, -38.00, TRUE, 22),

        -- =====================================================
        -- HarborOps (low risk stable)
        -- =====================================================
        ('HarborOps', CURRENT_DATE - INTERVAL '35 days', 95, 3, 0, 3.50, 26.00, 0, 0.30, 4.20, -1.00, -1.00, FALSE, 76),
        ('HarborOps', CURRENT_DATE - INTERVAL '28 days', 88, 3, 0, 3.20, 24.00, 0, 0.32, 4.25, -1.00, -1.00, FALSE, 77),
        ('HarborOps', CURRENT_DATE - INTERVAL '21 days', 81, 2, 0, 3.00, 22.00, 0, 0.34, 4.30,  0.00,  0.00, FALSE, 78),
        ('HarborOps', CURRENT_DATE - INTERVAL '14 days', 74, 2, 0, 2.80, 21.00, 0, 0.36, 4.30,  0.00,  0.00, FALSE, 79),
        ('HarborOps', CURRENT_DATE - INTERVAL '7 days',  67, 2, 0, 2.50, 20.00, 0, 0.38, 4.35,  1.00,  1.00, FALSE, 80)

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