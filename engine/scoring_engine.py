from typing import Any

from db.db_connection import db_cursor
from db.queries import GET_ALL_ACCOUNT_SNAPSHOTS, UPSERT_RISK_SCORE
from engine.rules_loader import load_active_scoring_config, load_scoring_rules
from engine.scoring_logic import score_account


def fetch_all_snapshots() -> list[dict[str, Any]]:
    with db_cursor() as (_, cursor):
        cursor.execute(GET_ALL_ACCOUNT_SNAPSHOTS)
        rows = cursor.fetchall()

    snapshots: list[dict[str, Any]] = []
    for row in rows:
        snapshots.append(
            {
                "account_id": row[0],
                "account_name": row[1],
                "segment": row[2],
                "arr_usd": float(row[3]),
                "strategic_account": row[4],
                "snapshot_id": row[5],
                "snapshot_date": row[6],
                "days_to_renewal": row[7],
                "open_tickets_30d": row[8],
                "reopened_tickets_30d": row[9],
                "avg_first_response_hrs": float(row[10]),
                "avg_resolution_hrs": float(row[11]),
                "sev1_tickets_30d": row[12],
                "sentiment_score": float(row[13]),
                "csat_avg_90d": float(row[14]),
                "usage_change_pct_30d": float(row[15]),
                "login_change_pct_30d": float(row[16]),
                "known_bug_flag": row[17],
                "csm_health_score": row[18],
            }
        )
    return snapshots


def persist_risk_score(
    account_id: int,
    snapshot_id: int,
    scoring_config_id: int,
    result: dict[str, Any],
) -> None:
    values = (
        account_id,
        snapshot_id,
        scoring_config_id,
        result["total_score"],
        result["risk_band"],
        result["top_driver_1"],
        result["top_driver_2"],
        result["top_driver_3"],
        result["recommended_action_1"],
        result["recommended_action_2"],
        result["recommended_action_3"],
    )

    with db_cursor(commit=True) as (_, cursor):
        cursor.execute(UPSERT_RISK_SCORE, values)


def run_scoring() -> list[dict[str, Any]]:
    config = load_active_scoring_config()
    rules = load_scoring_rules(config["scoring_config_id"])
    snapshots = fetch_all_snapshots()

    results: list[dict[str, Any]] = []

    for snapshot in snapshots:
        scored = score_account(snapshot, rules)

        persist_risk_score(
            account_id=snapshot["account_id"],
            snapshot_id=snapshot["snapshot_id"],
            scoring_config_id=config["scoring_config_id"],
            result=scored,
        )

        results.append(
            {
                "account_name": snapshot["account_name"],
                "snapshot_date": snapshot["snapshot_date"],
                "total_score": scored["total_score"],
                "risk_band": scored["risk_band"],
                "top_driver_1": scored["top_driver_1"],
                "top_driver_2": scored["top_driver_2"],
                "top_driver_3": scored["top_driver_3"],
            }
        )

    return results