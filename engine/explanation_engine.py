from typing import Any


RISK_TONE = {
    "Low": "stable",
    "Medium": "watchlist",
    "High": "elevated",
    "Critical": "urgent",
}


def _clean_items(items: list[str | None]) -> list[str]:
    return [item for item in items if item and str(item).strip()]


def _join_natural(items: list[str]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return f"{', '.join(items[:-1])}, and {items[-1]}"


def generate_risk_explanation(snapshot: dict[str, Any], score_result: dict[str, Any]) -> str:
    account_name = snapshot.get("account_name", "This account")
    risk_band = score_result.get("risk_band", "Unknown")
    risk_score = float(score_result.get("total_score", 0.0))
    tone = RISK_TONE.get(risk_band, "monitored")

    drivers = _clean_items(
        [
            score_result.get("top_driver_1"),
            score_result.get("top_driver_2"),
            score_result.get("top_driver_3"),
        ]
    )

    actions = _clean_items(
        [
            score_result.get("recommended_action_1"),
            score_result.get("recommended_action_2"),
            score_result.get("recommended_action_3"),
        ]
    )

    days_to_renewal = snapshot.get("days_to_renewal")
    known_bug_flag = snapshot.get("known_bug_flag")
    strategic_account = snapshot.get("strategic_account")

    opening = (
        f"{account_name} is currently assessed as {risk_band.lower()} risk "
        f"with a score of {risk_score:.2f}, indicating a {tone} account state."
    )

    driver_sentence = ""
    if drivers:
        driver_sentence = f" The primary risk drivers are {_join_natural(drivers)}."

    renewal_sentence = ""
    if days_to_renewal is not None:
        if days_to_renewal <= 30:
            renewal_sentence = f" Renewal is approaching in {days_to_renewal} days, which increases intervention urgency."
        elif days_to_renewal <= 60:
            renewal_sentence = f" The account renews in {days_to_renewal} days, so proactive stabilization is important."

    bug_sentence = ""
    if known_bug_flag:
        bug_sentence = " A known product issue is also affecting the account."

    strategic_sentence = ""
    if strategic_account:
        strategic_sentence = " This is a strategic account and should be monitored closely."

    action_sentence = ""
    if actions:
        action_sentence = f" Recommended next step: {actions[0]}."

    return (
        opening
        + driver_sentence
        + renewal_sentence
        + bug_sentence
        + strategic_sentence
        + action_sentence
    )


def generate_executive_summary(snapshot: dict[str, Any], score_result: dict[str, Any]) -> str:
    account_name = snapshot.get("account_name", "Account")
    risk_band = score_result.get("risk_band", "Unknown")
    risk_score = float(score_result.get("total_score", 0.0))

    drivers = _clean_items(
        [
            score_result.get("top_driver_1"),
            score_result.get("top_driver_2"),
        ]
    )

    days_to_renewal = snapshot.get("days_to_renewal")

    summary = f"{account_name}: {risk_band} risk ({risk_score:.2f})."

    if drivers:
        summary += f" Main drivers: {_join_natural(drivers)}."

    if days_to_renewal is not None and days_to_renewal <= 60:
        summary += f" Renewal in {days_to_renewal} days."

    return summary


def generate_action_rationale(snapshot: dict[str, Any], score_result: dict[str, Any]) -> str:
    actions = _clean_items(
        [
            score_result.get("recommended_action_1"),
            score_result.get("recommended_action_2"),
            score_result.get("recommended_action_3"),
        ]
    )

    drivers = _clean_items(
        [
            score_result.get("top_driver_1"),
            score_result.get("top_driver_2"),
            score_result.get("top_driver_3"),
        ]
    )

    if not actions:
        return "No intervention is currently required beyond routine monitoring."

    if not drivers:
        return f"Recommended action: {actions[0]}."

    return (
        f"{actions[0]} is recommended because the account is being driven by "
        f"{_join_natural(drivers)}."
    )