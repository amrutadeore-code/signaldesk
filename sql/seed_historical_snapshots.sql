-- =========================================================
-- Seed Historical Signal Snapshots (ALL ACCOUNTS)
-- =========================================================

-- NOTE:
-- We insert 5 historical snapshots per account
-- Dates: weekly intervals in the past

-- ---------------------------------------------------------
-- ACME CORP (Deteriorating)
-- ---------------------------------------------------------
INSERT INTO account_signal_snapshots (
    account_id, snapshot_date,
    open_tickets, reopened_tickets, sla_breach_count,
    csat_score, sentiment_score,
    days_since_last_engagement, upcoming_renewal_days,
    arr_usd
)
SELECT id, CURRENT_DATE - INTERVAL '35 days', 5, 1, 0, 8.5, 0.6, 5, 120, 120000
FROM accounts WHERE account_name = 'Acme Corp';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '28 days', 8, 2, 1, 7.8, 0.4, 7, 110, 120000
FROM accounts WHERE account_name = 'Acme Corp';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '21 days', 12, 3, 2, 7.0, 0.2, 10, 95, 120000
FROM accounts WHERE account_name = 'Acme Corp';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '14 days', 18, 4, 3, 6.5, -0.1, 12, 80, 120000
FROM accounts WHERE account_name = 'Acme Corp';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '7 days', 25, 6, 5, 6.0, -0.3, 15, 60, 120000
FROM accounts WHERE account_name = 'Acme Corp';


-- ---------------------------------------------------------
-- NORTHSTAR HEALTH (Improving)
-- ---------------------------------------------------------
INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '35 days', 20, 5, 4, 6.0, -0.2, 20, 90, 90000
FROM accounts WHERE account_name = 'Northstar Health';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '28 days', 15, 4, 3, 6.8, 0.0, 18, 85, 90000
FROM accounts WHERE account_name = 'Northstar Health';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '21 days', 12, 3, 2, 7.2, 0.2, 14, 80, 90000
FROM accounts WHERE account_name = 'Northstar Health';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '14 days', 8, 2, 1, 7.8, 0.4, 10, 70, 90000
FROM accounts WHERE account_name = 'Northstar Health';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '7 days', 5, 1, 0, 8.5, 0.6, 6, 60, 90000
FROM accounts WHERE account_name = 'Northstar Health';


-- ---------------------------------------------------------
-- BLUEPEAK SOFTWARE (Stable medium risk)
-- ---------------------------------------------------------
INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '35 days', 10, 2, 1, 7.5, 0.2, 10, 120, 75000
FROM accounts WHERE account_name = 'BluePeak Software';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '28 days', 11, 2, 1, 7.4, 0.1, 11, 115, 75000
FROM accounts WHERE account_name = 'BluePeak Software';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '21 days', 9, 2, 1, 7.6, 0.2, 9, 110, 75000
FROM accounts WHERE account_name = 'BluePeak Software';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '14 days', 10, 3, 1, 7.3, 0.1, 10, 105, 75000
FROM accounts WHERE account_name = 'BluePeak Software';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '7 days', 11, 2, 1, 7.5, 0.2, 11, 100, 75000
FROM accounts WHERE account_name = 'BluePeak Software';


-- ---------------------------------------------------------
-- GREENFIELD LOGISTICS (Spiking issues)
-- ---------------------------------------------------------
INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '35 days', 6, 1, 0, 8.0, 0.5, 6, 140, 60000
FROM accounts WHERE account_name = 'GreenField Logistics';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '28 days', 7, 1, 0, 7.8, 0.4, 7, 130, 60000
FROM accounts WHERE account_name = 'GreenField Logistics';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '21 days', 9, 2, 1, 7.2, 0.2, 9, 120, 60000
FROM accounts WHERE account_name = 'GreenField Logistics';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '14 days', 14, 3, 2, 6.8, 0.0, 11, 110, 60000
FROM accounts WHERE account_name = 'GreenField Logistics';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '7 days', 20, 5, 3, 6.5, -0.2, 14, 95, 60000
FROM accounts WHERE account_name = 'GreenField Logistics';


-- ---------------------------------------------------------
-- SUMMIT RETAIL (Declining engagement)
-- ---------------------------------------------------------
INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '35 days', 8, 2, 1, 7.8, 0.3, 5, 150, 50000
FROM accounts WHERE account_name = 'Summit Retail';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '28 days', 9, 2, 1, 7.5, 0.2, 10, 140, 50000
FROM accounts WHERE account_name = 'Summit Retail';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '21 days', 10, 2, 1, 7.2, 0.1, 15, 130, 50000
FROM accounts WHERE account_name = 'Summit Retail';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '14 days', 12, 3, 2, 6.8, -0.1, 20, 120, 50000
FROM accounts WHERE account_name = 'Summit Retail';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '7 days', 14, 3, 2, 6.5, -0.2, 25, 110, 50000
FROM accounts WHERE account_name = 'Summit Retail';


-- ---------------------------------------------------------
-- BRIGHTPATH HR (Healthy)
-- ---------------------------------------------------------
INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '35 days', 4, 1, 0, 8.8, 0.7, 3, 200, 40000
FROM accounts WHERE account_name = 'BrightPath HR';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '28 days', 3, 1, 0, 9.0, 0.8, 2, 190, 40000
FROM accounts WHERE account_name = 'BrightPath HR';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '21 days', 4, 1, 0, 8.9, 0.7, 3, 180, 40000
FROM accounts WHERE account_name = 'BrightPath HR';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '14 days', 3, 0, 0, 9.1, 0.9, 2, 170, 40000
FROM accounts WHERE account_name = 'BrightPath HR';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '7 days', 2, 0, 0, 9.2, 0.9, 2, 160, 40000
FROM accounts WHERE account_name = 'BrightPath HR';


-- ---------------------------------------------------------
-- CLOUDMINT (Moderate improving)
-- ---------------------------------------------------------
INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '35 days', 14, 4, 3, 6.5, -0.1, 12, 120, 85000
FROM accounts WHERE account_name = 'CloudMint';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '28 days', 12, 3, 2, 6.8, 0.0, 10, 110, 85000
FROM accounts WHERE account_name = 'CloudMint';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '21 days', 10, 3, 2, 7.2, 0.2, 9, 100, 85000
FROM accounts WHERE account_name = 'CloudMint';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '14 days', 8, 2, 1, 7.6, 0.4, 7, 90, 85000
FROM accounts WHERE account_name = 'CloudMint';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '7 days', 6, 2, 1, 8.0, 0.5, 6, 80, 85000
FROM accounts WHERE account_name = 'CloudMint';


-- ---------------------------------------------------------
-- PIXELFORGE STUDIO (Volatile)
-- ---------------------------------------------------------
INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '35 days', 7, 2, 1, 7.0, 0.1, 8, 100, 30000
FROM accounts WHERE account_name = 'PixelForge Studio';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '28 days', 15, 4, 3, 6.2, -0.3, 12, 95, 30000
FROM accounts WHERE account_name = 'PixelForge Studio';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '21 days', 9, 2, 1, 7.2, 0.2, 9, 90, 30000
FROM accounts WHERE account_name = 'PixelForge Studio';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '14 days', 18, 5, 4, 6.0, -0.4, 15, 85, 30000
FROM accounts WHERE account_name = 'PixelForge Studio';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '7 days', 10, 3, 2, 7.0, 0.1, 10, 80, 30000
FROM accounts WHERE account_name = 'PixelForge Studio';


-- ---------------------------------------------------------
-- VERTEX FINANCIAL (High risk stable)
-- ---------------------------------------------------------
INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '35 days', 25, 6, 5, 6.0, -0.3, 18, 70, 150000
FROM accounts WHERE account_name = 'Vertex Financial';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '28 days', 24, 6, 5, 6.1, -0.2, 17, 65, 150000
FROM accounts WHERE account_name = 'Vertex Financial';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '21 days', 26, 7, 6, 5.8, -0.4, 19, 60, 150000
FROM accounts WHERE account_name = 'Vertex Financial';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '14 days', 27, 7, 6, 5.7, -0.5, 20, 55, 150000
FROM accounts WHERE account_name = 'Vertex Financial';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '7 days', 28, 8, 7, 5.5, -0.6, 22, 50, 150000
FROM accounts WHERE account_name = 'Vertex Financial';


-- ---------------------------------------------------------
-- HARBOROPS (Low risk stable)
-- ---------------------------------------------------------
INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '35 days', 3, 0, 0, 9.0, 0.8, 2, 180, 45000
FROM accounts WHERE account_name = 'HarborOps';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '28 days', 3, 0, 0, 9.1, 0.9, 2, 170, 45000
FROM accounts WHERE account_name = 'HarborOps';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '21 days', 2, 0, 0, 9.2, 0.9, 1, 160, 45000
FROM accounts WHERE account_name = 'HarborOps';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '14 days', 2, 0, 0, 9.3, 0.9, 1, 150, 45000
FROM accounts WHERE account_name = 'HarborOps';

INSERT INTO account_signal_snapshots
SELECT id, CURRENT_DATE - INTERVAL '7 days', 2, 0, 0, 9.4, 1.0, 1, 140, 45000
FROM accounts WHERE account_name = 'HarborOps';