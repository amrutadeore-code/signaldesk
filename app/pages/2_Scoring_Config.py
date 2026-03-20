import os
from typing import Any

import pandas as pd
import psycopg
import streamlit as st
from dotenv import load_dotenv

from engine.scoring_engine import run_scoring
from engine.scoring_logic import score_account
from db.db_connection import get_db_connection


METRIC_GROUPS = {
    "open_tickets_30d": "Support Signals",
    "reopened_tickets_30d": "Support Signals",
    "avg_first_response_hrs": "Support Signals",
    "avg_resolution_hrs": "Support Signals",
    "sev1_tickets_30d": "Support Signals",
    "sentiment_score": "Sentiment & Usage",
    "usage_change_pct_30d": "Sentiment & Usage",
    "login_change_pct_30d": "Sentiment & Usage",
    "days_to_renewal": "Renewal & Health",
    "csm_health_score": "Renewal & Health",
    "known_bug_flag": "Renewal & Health",
}

GROUP_ORDER = [
    "Support Signals",
    "Sentiment & Usage",
    "Renewal & Health",
]

METRIC_LABELS = {
    "open_tickets_30d": "Open Tickets (30d)",
    "reopened_tickets_30d": "Reopened Tickets (30d)",
    "avg_first_response_hrs": "Avg First Response (hrs)",
    "avg_resolution_hrs": "Avg Resolution (hrs)",
    "sev1_tickets_30d": "Severity 1 Tickets (30d)",
    "sentiment_score": "Sentiment Score",
    "usage_change_pct_30d": "Usage Change % (30d)",
    "login_change_pct_30d": "Login Change % (30d)",
    "days_to_renewal": "Days to Renewal",
    "csm_health_score": "CSM Health Score",
    "known_bug_flag": "Known Bug Flag",
}

METRIC_INFO = {
    "open_tickets_30d": "Number of open support tickets in the last 30 days. Higher values indicate growing support pressure.",
    "reopened_tickets_30d": "Number of tickets reopened in the last 30 days. Reopens often signal unresolved customer issues.",
    "avg_first_response_hrs": "Average time taken to send the first response. Slower responses increase escalation risk.",
    "avg_resolution_hrs": "Average total time to resolve tickets. Longer resolution cycles may frustrate customers.",
    "sev1_tickets_30d": "Number of severity 1 or critical incidents in the last 30 days.",
    "sentiment_score": "Customer sentiment derived from support interactions. Lower values indicate more negative sentiment.",
    "usage_change_pct_30d": "Percent change in product usage over the last 30 days. Negative values may indicate disengagement.",
    "login_change_pct_30d": "Percent change in login activity over the last 30 days. Lower activity may indicate declining adoption.",
    "days_to_renewal": "Days remaining until renewal. Accounts closer to renewal may need faster intervention.",
    "csm_health_score": "Customer Success health score from 0 to 100. Lower values indicate weaker account health.",
    "known_bug_flag": "Indicates whether a known product bug is currently affecting the account.",
}

RISK_BAND_ORDER = ["Low", "Medium", "High", "Critical"]


load_dotenv()

st.set_page_config(
    page_title="Scoring Config | SignalDesk",
    page_icon="⚙️",
    layout="wide",
)


@st.cache_data(ttl=60)
def load_active_config() -> dict:
    query = """
    SELECT
        scoring_config_id,
        config_name,
        description,
        is_active,
        is_default,
        is_editable,
        created_at
    FROM scoring_configs
    WHERE is_active = TRUE
    ORDER BY scoring_config_id
    LIMIT 1;
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            row = cur.fetchone()

    if not row:
        raise ValueError("No active scoring configuration found.")

    return {
        "scoring_config_id": row[0],
        "config_name": row[1],
        "description": row[2],
        "is_active": row[3],
        "is_default": row[4],
        "is_editable": row[5],
        "created_at": row[6],
    }


@st.cache_data(ttl=60)
def load_scoring_rules(scoring_config_id: int) -> pd.DataFrame:
    query = """
    SELECT
        scoring_rule_id,
        metric_name,
        weight,
        threshold_low,
        threshold_medium,
        threshold_high,
        points_low,
        points_medium,
        points_high,
        points_critical,
        created_at
    FROM scoring_rules
    WHERE scoring_config_id = %s
    ORDER BY metric_name;
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (scoring_config_id,))
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            df = pd.DataFrame(rows, columns=columns)

    if df.empty:
        return df

    numeric_columns = [
        "weight",
        "threshold_low",
        "threshold_medium",
        "threshold_high",
        "points_low",
        "points_medium",
        "points_high",
        "points_critical",
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["metric_label"] = df["metric_name"].map(METRIC_LABELS).fillna(df["metric_name"])
    df["metric_info"] = df["metric_name"].map(METRIC_INFO).fillna("No description available.")
    df["metric_group"] = df["metric_name"].map(METRIC_GROUPS).fillna("Other")

    return df


@st.cache_data(ttl=60)
def load_latest_account_snapshots() -> pd.DataFrame:
    query = """
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
    ORDER BY a.account_id, s.snapshot_date DESC, s.snapshot_id DESC;
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]

    df = pd.DataFrame(rows, columns=columns)

    if df.empty:
        return df

    numeric_columns = [
        "arr_usd",
        "days_to_renewal",
        "open_tickets_30d",
        "reopened_tickets_30d",
        "avg_first_response_hrs",
        "avg_resolution_hrs",
        "sev1_tickets_30d",
        "sentiment_score",
        "csat_avg_90d",
        "usage_change_pct_30d",
        "login_change_pct_30d",
        "csm_health_score",
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"], errors="coerce")

    latest_df = (
        df.sort_values(["account_id", "snapshot_date", "snapshot_id"], ascending=[True, False, False])
        .drop_duplicates(subset=["account_id"], keep="first")
        .copy()
    )

    return latest_df


def save_scoring_rules(updated_df: pd.DataFrame, scoring_config_id: int) -> None:
    update_query = """
    UPDATE scoring_rules
    SET
        weight = %s,
        threshold_low = %s,
        threshold_medium = %s,
        threshold_high = %s,
        points_low = %s,
        points_medium = %s,
        points_high = %s,
        points_critical = %s
    WHERE scoring_rule_id = %s
      AND scoring_config_id = %s;
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            for _, row in updated_df.iterrows():
                cur.execute(
                    update_query,
                    (
                        float(row["weight"]) if pd.notna(row["weight"]) else None,
                        float(row["threshold_low"]) if pd.notna(row["threshold_low"]) else None,
                        float(row["threshold_medium"]) if pd.notna(row["threshold_medium"]) else None,
                        float(row["threshold_high"]) if pd.notna(row["threshold_high"]) else None,
                        float(row["points_low"]) if pd.notna(row["points_low"]) else 0.0,
                        float(row["points_medium"]) if pd.notna(row["points_medium"]) else 0.0,
                        float(row["points_high"]) if pd.notna(row["points_high"]) else 0.0,
                        float(row["points_critical"]) if pd.notna(row["points_critical"]) else 0.0,
                        int(row["scoring_rule_id"]),
                        scoring_config_id,
                    ),
                )
        conn.commit()


def clear_streamlit_caches():
    load_active_config.clear()
    load_scoring_rules.clear()
    load_latest_account_snapshots.clear()
    st.cache_data.clear()


def render_rule_editor_for_group(group_name: str, group_df: pd.DataFrame, editor_key: str) -> pd.DataFrame:
    st.markdown(f"### {group_name}")

    editable_columns = [
        "scoring_rule_id",
        "metric_name",
        "metric_label",
        "metric_info",
        "weight",
        "threshold_low",
        "threshold_medium",
        "threshold_high",
        "points_low",
        "points_medium",
        "points_high",
        "points_critical",
    ]

    edited_group_df = st.data_editor(
        group_df[editable_columns],
        width="stretch",
        hide_index=True,
        num_rows="fixed",
        column_config={
            "scoring_rule_id": None,
            "metric_name": None,
            "metric_label": st.column_config.TextColumn(
                "Metric",
                disabled=True,
                width="medium",
            ),
            "metric_info": st.column_config.TextColumn(
                "Info",
                disabled=True,
                width="large",
            ),
            "weight": st.column_config.NumberColumn("Weight", min_value=0.0, step=0.1, format="%.2f"),
            "threshold_low": st.column_config.NumberColumn("Low Threshold", step=0.1, format="%.2f"),
            "threshold_medium": st.column_config.NumberColumn("Medium Threshold", step=0.1, format="%.2f"),
            "threshold_high": st.column_config.NumberColumn("High Threshold", step=0.1, format="%.2f"),
            "points_low": st.column_config.NumberColumn("Low Points", min_value=0.0, step=0.5, format="%.2f"),
            "points_medium": st.column_config.NumberColumn("Medium Points", min_value=0.0, step=0.5, format="%.2f"),
            "points_high": st.column_config.NumberColumn("High Points", min_value=0.0, step=0.5, format="%.2f"),
            "points_critical": st.column_config.NumberColumn("Critical Points", min_value=0.0, step=0.5, format="%.2f"),
        },
        key=editor_key,
    )

    st.divider()
    return edited_group_df


def rules_df_to_rule_dict(rules_df: pd.DataFrame, scoring_config_id: int) -> dict[str, dict[str, Any]]:
    rules: dict[str, dict[str, Any]] = {}

    for _, row in rules_df.iterrows():
        metric_name = row["metric_name"]

        rules[metric_name] = {
            "scoring_rule_id": int(row["scoring_rule_id"]),
            "scoring_config_id": scoring_config_id,
            "metric_name": metric_name,
            "weight": float(row["weight"]) if pd.notna(row["weight"]) else 1.0,
            "threshold_low": float(row["threshold_low"]) if pd.notna(row["threshold_low"]) else None,
            "threshold_medium": float(row["threshold_medium"]) if pd.notna(row["threshold_medium"]) else None,
            "threshold_high": float(row["threshold_high"]) if pd.notna(row["threshold_high"]) else None,
            "points_low": float(row["points_low"]) if pd.notna(row["points_low"]) else 0.0,
            "points_medium": float(row["points_medium"]) if pd.notna(row["points_medium"]) else 0.0,
            "points_high": float(row["points_high"]) if pd.notna(row["points_high"]) else 0.0,
            "points_critical": float(row["points_critical"]) if pd.notna(row["points_critical"]) else 0.0,
        }

    return rules


def compare_band_severity(old_band: str, new_band: str) -> str:
    band_order = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}

    old_rank = band_order.get(old_band, 0)
    new_rank = band_order.get(new_band, 0)

    if new_rank > old_rank:
        return "Higher Risk"
    if new_rank < old_rank:
        return "Lower Risk"
    return "No Change"


def simulate_portfolio_band_changes(
    current_rules_df: pd.DataFrame,
    edited_rules_df: pd.DataFrame,
    scoring_config_id: int,
) -> pd.DataFrame:
    latest_snapshots_df = load_latest_account_snapshots()

    if latest_snapshots_df.empty:
        return pd.DataFrame()

    current_rules = rules_df_to_rule_dict(current_rules_df, scoring_config_id)
    edited_rules = rules_df_to_rule_dict(edited_rules_df, scoring_config_id)

    comparison_rows = []

    for _, row in latest_snapshots_df.iterrows():
        snapshot = row.to_dict()

        current_result = score_account(snapshot, current_rules)
        simulated_result = score_account(snapshot, edited_rules)

        current_band = current_result["risk_band"]
        simulated_band = simulated_result["risk_band"]

        current_score = float(current_result["total_score"])
        simulated_score = float(simulated_result["total_score"])
        score_delta = round(simulated_score - current_score, 2)

        raw_band_change = compare_band_severity(current_band, simulated_band)

        if current_band != simulated_band:
            comparison_rows.append(
                {
                    "Account": snapshot["account_name"],
                    "Segment": snapshot["segment"],
                    "ARR (USD)": snapshot["arr_usd"],
                    "Current Score": current_score,
                    "Simulated Score": simulated_score,
                    "Score Delta": score_delta,
                    "Current Band": current_band,
                    "Simulated Band": simulated_band,
                    "Raw Band Change": raw_band_change,
                    "Band Change": band_change_with_arrow(raw_band_change),
                    "Current Driver": current_result.get("top_driver_1"),
                    "Simulated Driver": simulated_result.get("top_driver_1"),
                }
            )

    preview_df = pd.DataFrame(comparison_rows)
    
    if not preview_df.empty:
        preview_df["Why Changed"] = preview_df.apply(explain_band_change, axis=1)

    if preview_df.empty:
        return preview_df

    preview_df["Current Band"] = pd.Categorical(
        preview_df["Current Band"],
        categories=RISK_BAND_ORDER,
        ordered=True,
    )
    preview_df["Simulated Band"] = pd.Categorical(
        preview_df["Simulated Band"],
        categories=RISK_BAND_ORDER,
        ordered=True,
    )

    return preview_df


def main():
    st.title("Scoring Configuration")
    st.caption("Manage weights, thresholds, and points for the active risk model")

    try:
        config = load_active_config()
    except Exception as exc:
        st.error(f"Failed to load active scoring config: {exc}")
        return

    st.subheader(config["config_name"])
    st.write(config["description"] or "No description provided.")

    meta_col1, meta_col2, meta_col3, meta_col4 = st.columns(4)
    meta_col1.metric("Active", "Yes" if config["is_active"] else "No")
    meta_col2.metric("Default", "Yes" if config["is_default"] else "No")
    meta_col3.metric("Editable", "Yes" if config["is_editable"] else "No")
    meta_col4.metric("Config ID", str(config["scoring_config_id"]))

    if not config["is_editable"]:
        st.warning("This scoring config is not editable.")
        return

    st.divider()

    try:
        rules_df = load_scoring_rules(config["scoring_config_id"])
    except Exception as exc:
        st.error(f"Failed to load scoring rules: {exc}")
        return

    if rules_df.empty:
        st.warning("No scoring rules found for the active config.")
        return

    original_rules_df = rules_df.copy()

    st.markdown("### Edit Scoring Rules")
    st.write("Update rule values below, then save changes. You can optionally preview portfolio impact or rerun scoring after saving.")

    edited_groups = []

    for group_name in GROUP_ORDER:
        group_df = rules_df[rules_df["metric_group"] == group_name].copy()
        if not group_df.empty:
            edited_group_df = render_rule_editor_for_group(
                group_name=group_name,
                group_df=group_df,
                editor_key=f"scoring_rules_editor_{group_name}",
            )
            edited_groups.append(edited_group_df)

    other_df = rules_df[~rules_df["metric_group"].isin(GROUP_ORDER)].copy()
    if not other_df.empty:
        edited_group_df = render_rule_editor_for_group(
            group_name="Other",
            group_df=other_df,
            editor_key="scoring_rules_editor_other",
        )
        edited_groups.append(edited_group_df)

    edited_df = pd.concat(edited_groups, ignore_index=True) if edited_groups else pd.DataFrame()

    st.markdown("### Portfolio Impact Preview")
    st.write("Preview which accounts would change risk band if the edited scoring model were applied portfolio-wide.")

    preview_clicked = st.button("Preview Portfolio Band Changes", width="stretch")

    if preview_clicked:
        try:
            preview_df = simulate_portfolio_band_changes(
                current_rules_df=original_rules_df,
                edited_rules_df=edited_df,
                scoring_config_id=config["scoring_config_id"],
            )

            if preview_df.empty:
                st.success("No accounts would change risk bands under the edited scoring model.")
            else:
                higher_risk_count = int((preview_df["Raw Band Change"] == "Higher Risk").sum())
                lower_risk_count = int((preview_df["Raw Band Change"] == "Lower Risk").sum())

                metric_col1, metric_col2, metric_col3 = st.columns(3)
                metric_col1.metric("Accounts with Band Changes", len(preview_df))
                metric_col2.metric("Moving Higher", higher_risk_count)
                metric_col3.metric("Moving Lower", lower_risk_count)

                st.info(summarize_portfolio_preview(preview_df))

                top_impacted_df = build_top_impacted_accounts(preview_df, top_n=3)
                if not top_impacted_df.empty:
                    st.markdown("#### Top Impacted Accounts")
                    st.dataframe(
                        top_impacted_df[
                            [
                                "Account",
                                "Current Score",
                                "Simulated Score",
                                "Score Delta",
                                "Current Band",
                                "Simulated Band",
                                "Band Change",
                            ]
                        ],
                        width="stretch",
                        hide_index=True,
                        column_config={
                            "Current Score": st.column_config.NumberColumn(format="%.2f"),
                            "Simulated Score": st.column_config.NumberColumn(format="%.2f"),
                            "Score Delta": st.column_config.NumberColumn(format="%.2f"),
                        },
                    )

                st.markdown("#### Full Portfolio Preview")

                sorted_preview_df = preview_df.sort_values(
                    by=["Raw Band Change", "Score Delta", "Simulated Score"],
                    ascending=[False, False, False],
                ).reset_index(drop=True)

                styled_preview_df = build_preview_styler(
                    sorted_preview_df[
                        [
                            "Account",
                            "Segment",
                            "ARR (USD)",
                            "Current Score",
                            "Simulated Score",
                            "Score Delta",
                            "Current Band",
                            "Simulated Band",
                            "Band Change",
                            "Current Driver",
                            "Simulated Driver",
                            "Why Changed",
                        ]
                    ]
                )

                st.dataframe(
                    styled_preview_df,
                    width="stretch",
                    hide_index=True,
                )

                st.caption(
                    "This preview uses the latest snapshot for each account and compares the current active scoring rules "
                    "against the edited rules in memory. No database changes are applied during preview."
                )

        except Exception as exc:
            st.error(f"Failed to simulate portfolio band changes: {exc}")

    st.divider()

    action_col1, action_col2 = st.columns([1, 1])

    with action_col1:
        save_clicked = st.button("Save Rule Changes", type="primary", width="stretch")

    with action_col2:
        save_and_rerun_clicked = st.button("Save and Recalculate Scores", width="stretch")

    if save_clicked or save_and_rerun_clicked:
        try:
            save_scoring_rules(edited_df, config["scoring_config_id"])
            clear_streamlit_caches()
            st.success("Scoring rules updated successfully.")
        except Exception as exc:
            st.error(f"Failed to save scoring rules: {exc}")
            return

        if save_and_rerun_clicked:
            try:
                results = run_scoring()
                st.success(f"Scoring rerun completed for {len(results)} snapshots.")
            except Exception as exc:
                st.error(f"Rules saved, but scoring rerun failed: {exc}")
                return

    st.divider()

    st.markdown("### Notes")
    st.write(
        """
        - Higher values are worse for metrics like open tickets and response times.
        - Lower values are worse for metrics like sentiment score, usage change, and days to renewal.
        - Known bug flag behaves like a boolean-style risk signal.
        """
    )

def style_score_delta(val):
    if pd.isna(val):
        return ""
    if val > 0:
        return "background-color: #fee2e2; color: #991b1b; font-weight: 600;"
    if val < 0:
        return "background-color: #dcfce7; color: #166534; font-weight: 600;"
    return "background-color: #f8fafc; color: #475569;"


def style_band_change(val):
    if isinstance(val, str) and "Higher Risk" in val:
        return "background-color: #fee2e2; color: #991b1b; font-weight: 600;"
    if isinstance(val, str) and "Lower Risk" in val:
        return "background-color: #dcfce7; color: #166534; font-weight: 600;"
    return "background-color: #f8fafc; color: #475569;"


def build_preview_styler(preview_df: pd.DataFrame):
    return (
        preview_df.style
        .format(
            {
                "ARR (USD)": "${:,.0f}",
                "Current Score": "{:.2f}",
                "Simulated Score": "{:.2f}",
                "Score Delta": "{:+.2f}",
            }
        )
        .map(style_score_delta, subset=["Score Delta"])
        .map(style_band_change, subset=["Band Change"])
    )
    
def band_change_with_arrow(change: str) -> str:
    if change == "Higher Risk":
        return "▲ Higher Risk"
    if change == "Lower Risk":
        return "▼ Lower Risk"
    return "• No Change"


def summarize_portfolio_preview(preview_df: pd.DataFrame) -> str:
    if preview_df.empty:
        return "No accounts would change risk bands under the edited scoring model."

    higher_df = preview_df[preview_df["Raw Band Change"] == "Higher Risk"]
    lower_df = preview_df[preview_df["Raw Band Change"] == "Lower Risk"]

    parts = []

    if not higher_df.empty:
        top_higher = higher_df.sort_values("Score Delta", ascending=False).iloc[0]
        parts.append(
            f"{len(higher_df)} account(s) would move to higher risk, "
            f"led by {top_higher['Account']} ({top_higher['Score Delta']:+.2f})."
        )

    if not lower_df.empty:
        top_lower = lower_df.sort_values("Score Delta", ascending=True).iloc[0]
        parts.append(
            f"{len(lower_df)} account(s) would move to lower risk, "
            f"led by {top_lower['Account']} ({top_lower['Score Delta']:+.2f})."
        )

    return " ".join(parts)


def explain_band_change(row: pd.Series) -> str:
    current_driver = row.get("Current Driver")
    simulated_driver = row.get("Simulated Driver")
    band_change = row.get("Raw Band Change")
    score_delta = row.get("Score Delta", 0.0)

    if band_change == "Higher Risk":
        if current_driver and simulated_driver and current_driver != simulated_driver:
            return (
                f"Band increased because the edited model amplified risk sensitivity, "
                f"shifting the leading driver from {current_driver} to {simulated_driver} "
                f"and increasing the score by {score_delta:+.2f}."
            )
        if simulated_driver:
            return (
                f"Band increased because the edited model placed more weight on {simulated_driver}, "
                f"raising the score by {score_delta:+.2f}."
            )
        return f"Band increased after the edited model raised the score by {score_delta:+.2f}."

    if band_change == "Lower Risk":
        if current_driver and simulated_driver and current_driver != simulated_driver:
            return (
                f"Band decreased because the edited model reduced the relative impact of {current_driver}, "
                f"with {simulated_driver} becoming the primary remaining driver and the score changing by {score_delta:+.2f}."
            )
        if current_driver:
            return (
                f"Band decreased because the edited model reduced the impact of {current_driver}, "
                f"lowering the score by {score_delta:+.2f}."
            )
        return f"Band decreased after the edited model changed the score by {score_delta:+.2f}."

    return "No band change."


def build_top_impacted_accounts(preview_df: pd.DataFrame, top_n: int = 3) -> pd.DataFrame:
    if preview_df.empty:
        return preview_df

    impacted_df = preview_df.copy()
    impacted_df["Abs Score Delta"] = impacted_df["Score Delta"].abs()

    top_df = (
        impacted_df.sort_values(["Abs Score Delta", "Simulated Score"], ascending=[False, False])
        .head(top_n)
        .drop(columns=["Abs Score Delta"])
        .copy()
    )

    return top_df

if __name__ == "__main__":
    main()