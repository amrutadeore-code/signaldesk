from typing import Any


METRIC_DIRECTIONS = {
    "open_tickets_30d": "higher_is_worse",
    "reopened_tickets_30d": "higher_is_worse",
    "avg_first_response_hrs": "higher_is_worse",
    "avg_resolution_hrs": "higher_is_worse",
    "sev1_tickets_30d": "higher_is_worse",
    "sentiment_score": "lower_is_worse",
    "usage_change_pct_30d": "lower_is_worse",
    "login_change_pct_30d": "lower_is_worse",
    "days_to_renewal": "lower_is_worse",
    "csm_health_score": "lower_is_worse",
    "known_bug_flag": "boolean_flag",
}


METRIC_LABELS = {
    "open_tickets_30d": "high open ticket volume",
    "reopened_tickets_30d": "repeated ticket reopenings",
    "avg_first_response_hrs": "slow first response times",
    "avg_resolution_hrs": "slow resolution times",
    "sev1_tickets_30d": "severity 1 incidents",
    "sentiment_score": "negative customer sentiment",
    "usage_change_pct_30d": "product usage decline",
    "login_change_pct_30d": "login activity decline",
    "days_to_renewal": "renewal is approaching",
    "csm_health_score": "low customer health score",
    "known_bug_flag": "known bug impacting account",
}


def get_risk_band(total_score: float) -> str:
    if total_score <= 24:
        return "Low"
    if total_score <= 49:
        return "Medium"
    if total_score <= 74:
        return "High"
    return "Critical"


def evaluate_metric(value: Any, rule: dict[str, Any], direction: str) -> float:
    weight = float(rule["weight"])

    if direction == "boolean_flag":
        bool_value = 1 if value else 0
        if bool_value >= 1:
            return rule["points_critical"] * weight
        return 0.0

    low = rule["threshold_low"]
    medium = rule["threshold_medium"]
    high = rule["threshold_high"]

    if value is None:
        return 0.0

    if direction == "higher_is_worse":
        if value > high:
            return rule["points_critical"] * weight
        if value >= medium:
            return rule["points_high"] * weight
        if value >= low:
            return rule["points_medium"] * weight
        if value > 0:
            return rule["points_low"] * weight
        return 0.0

    if direction == "lower_is_worse":
        if value < high:
            return rule["points_critical"] * weight
        if value <= medium:
            return rule["points_high"] * weight
        if value <= low:
            return rule["points_medium"] * weight
        return 0.0

    return 0.0


def build_recommended_actions(contributions: list[tuple[str, float]]) -> list[str]:
    if not contributions:
        return ["Continue monitoring account health"]

    top_driver = contributions[0][0]
    print("DEBUG top_driver:", top_driver)

    if top_driver == "open_tickets_30d":
        return ["Assign a senior support engineer to reduce ticket backlog"]

    elif top_driver == "avg_resolution_hrs":
        return ["Escalate to engineering leadership to address resolution delays"]

    elif top_driver == "reopened_tickets_30d":
        return ["Perform root cause analysis to prevent recurring issues"]

    elif top_driver == "sentiment_score":
        return ["Schedule executive check-in to address customer concerns"]

    elif top_driver == "csat_avg_90d":
        return ["Launch a structured customer recovery plan"]

    elif top_driver in ("usage_change_pct_30d", "login_change_pct_30d"):
        return ["Conduct product adoption and engagement review"]

    elif top_driver == "days_to_renewal":
        return ["Initiate renewal risk mitigation plan with CSM team"]

    elif top_driver in ("known_bug_flag", "sev1_tickets_30d"):
        return ["Prioritize bug resolution and communicate timeline to customer"]

    else:
        return ["Monitor account and maintain engagement cadence"]


def score_account(snapshot: dict[str, Any], rules: dict[str, dict[str, Any]]) -> dict[str, Any]:
    contributions: list[tuple[str, float]] = []

    for metric_name, rule in rules.items():
        direction = METRIC_DIRECTIONS.get(metric_name)
        if not direction:
            continue

        value = snapshot.get(metric_name)
        points = evaluate_metric(value, rule, direction)
        contributions.append((metric_name, round(points, 2)))

    contributions.sort(key=lambda x: x[1], reverse=True)

    total_score = round(sum(points for _, points in contributions), 2)
    total_score = min(total_score, 100.0)

    risk_band = get_risk_band(total_score)

    top_drivers = [
        METRIC_LABELS.get(metric_name, metric_name)
        for metric_name, points in contributions
        if points > 0
    ][:3]

    actions = build_recommended_actions(contributions)

    return {
        "total_score": total_score,
        "risk_band": risk_band,
        "contributions": contributions,
        "top_driver_1": top_drivers[0] if len(top_drivers) > 0 else None,
        "top_driver_2": top_drivers[1] if len(top_drivers) > 1 else None,
        "top_driver_3": top_drivers[2] if len(top_drivers) > 2 else None,
        "recommended_action_1": actions[0] if len(actions) > 0 else None,
        "recommended_action_2": actions[1] if len(actions) > 1 else None,
        "recommended_action_3": actions[2] if len(actions) > 2 else None,
    }