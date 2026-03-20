from typing import Any


GET_ACTIVE_SCORING_CONFIG = """
SELECT
    scoring_config_id,
    config_name,
    description,
    is_active,
    is_default,
    is_editable
FROM scoring_configs
WHERE is_active = TRUE
ORDER BY scoring_config_id
LIMIT 1;
"""


GET_SCORING_RULES = """
SELECT
    scoring_rule_id,
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
FROM scoring_rules
WHERE scoring_config_id = %s
ORDER BY metric_name;
"""


GET_LATEST_ACCOUNT_SNAPSHOTS = """
SELECT
    a.account_id,
    a.account_name,
    a.segment,
    a.arr_usd,
    a.strategic_account,
    s.snapshot_id,
    s.snapshot_date,
    s.days_to_renewal,
    s.open_tickets_30d,
    s.reopened_tickets_30d,
    s.avg_first_response_hrs,
    s.avg_resolution_hrs,
    s.sev1_tickets_30d,
    s.sentiment_score,
    s.csat_avg_90d,
    s.usage_change_pct_30d,
    s.login_change_pct_30d,
    s.known_bug_flag,
    s.csm_health_score
FROM accounts a
JOIN (
    SELECT DISTINCT ON (account_id)
        snapshot_id,
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
    FROM account_signal_snapshots
    ORDER BY account_id, snapshot_date DESC, snapshot_id DESC
) s
    ON a.account_id = s.account_id
ORDER BY a.account_name;
"""


UPSERT_RISK_SCORE = """
INSERT INTO risk_scores (
    account_id,
    snapshot_id,
    scoring_config_id,
    total_score,
    risk_band,
    top_driver_1,
    top_driver_2,
    top_driver_3,
    recommended_action_1,
    recommended_action_2,
    recommended_action_3
)
VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
)
ON CONFLICT (snapshot_id, scoring_config_id)
DO UPDATE SET
    account_id = EXCLUDED.account_id,
    total_score = EXCLUDED.total_score,
    risk_band = EXCLUDED.risk_band,
    top_driver_1 = EXCLUDED.top_driver_1,
    top_driver_2 = EXCLUDED.top_driver_2,
    top_driver_3 = EXCLUDED.top_driver_3,
    recommended_action_1 = EXCLUDED.recommended_action_1,
    recommended_action_2 = EXCLUDED.recommended_action_2,
    recommended_action_3 = EXCLUDED.recommended_action_3,
    scored_at = CURRENT_TIMESTAMP;
"""


GET_ALL_ACCOUNT_SNAPSHOTS = """
SELECT
    a.account_id,
    a.account_name,
    a.segment,
    a.arr_usd,
    a.strategic_account,
    s.snapshot_id,
    s.snapshot_date,
    s.days_to_renewal,
    s.open_tickets_30d,
    s.reopened_tickets_30d,
    s.avg_first_response_hrs,
    s.avg_resolution_hrs,
    s.sev1_tickets_30d,
    s.sentiment_score,
    s.csat_avg_90d,
    s.usage_change_pct_30d,
    s.login_change_pct_30d,
    s.known_bug_flag,
    s.csm_health_score
FROM accounts a
JOIN account_signal_snapshots s
    ON a.account_id = s.account_id
ORDER BY a.account_name, s.snapshot_date ASC, s.snapshot_id ASC;
"""