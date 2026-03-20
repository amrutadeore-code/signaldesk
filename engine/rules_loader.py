from typing import Any

from db.db_connection import db_cursor
from db.queries import GET_ACTIVE_SCORING_CONFIG, GET_SCORING_RULES


def load_active_scoring_config() -> dict[str, Any]:
    with db_cursor() as (_, cursor):
        cursor.execute(GET_ACTIVE_SCORING_CONFIG)
        row = cursor.fetchone()

    if not row:
        raise ValueError("No active scoring configuration found.")

    return {
        "scoring_config_id": row[0],
        "config_name": row[1],
        "description": row[2],
        "is_active": row[3],
        "is_default": row[4],
        "is_editable": row[5],
    }


def load_scoring_rules(scoring_config_id: int) -> dict[str, dict[str, Any]]:
    with db_cursor() as (_, cursor):
        cursor.execute(GET_SCORING_RULES, (scoring_config_id,))
        rows = cursor.fetchall()

    if not rows:
        raise ValueError(f"No scoring rules found for config_id={scoring_config_id}")

    rules: dict[str, dict[str, Any]] = {}
    for row in rows:
        metric_name = row[2]
        rules[metric_name] = {
            "scoring_rule_id": row[0],
            "scoring_config_id": row[1],
            "metric_name": metric_name,
            "weight": float(row[3]),
            "threshold_low": float(row[4]) if row[4] is not None else None,
            "threshold_medium": float(row[5]) if row[5] is not None else None,
            "threshold_high": float(row[6]) if row[6] is not None else None,
            "points_low": float(row[7]),
            "points_medium": float(row[8]),
            "points_high": float(row[9]),
            "points_critical": float(row[10]),
        }

    return rules