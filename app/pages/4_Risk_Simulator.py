import os
from typing import Any

import pandas as pd
import psycopg
import streamlit as st
from dotenv import load_dotenv

from engine.rules_loader import load_active_scoring_config, load_scoring_rules
from engine.scoring_logic import score_account
from db.db_connection import get_db_connection


load_dotenv()

st.set_page_config(
    page_title="Risk Simulator | SignalDesk",
    page_icon="🧪",
    layout="wide",
)

from engine.explanation_engine import (
    generate_action_rationale,
    generate_executive_summary,
    generate_risk_explanation,
)

SIMULATABLE_FIELDS = [
    "open_tickets_30d",
    "reopened_tickets_30d",
    "avg_first_response_hrs",
    "avg_resolution_hrs",
    "sev1_tickets_30d",
    "sentiment_score",
    "usage_change_pct_30d",
    "login_change_pct_30d",
    "days_to_renewal",
    "known_bug_flag",
    "csm_health_score",
]

FIELD_LABELS = {
    "open_tickets_30d": "Open Tickets (30d)",
    "reopened_tickets_30d": "Reopened Tickets (30d)",
    "avg_first_response_hrs": "Avg First Response (hrs)",
    "avg_resolution_hrs": "Avg Resolution (hrs)",
    "sev1_tickets_30d": "Severity 1 Tickets (30d)",
    "sentiment_score": "Sentiment Score",
    "usage_change_pct_30d": "Usage Change % (30d)",
    "login_change_pct_30d": "Login Change % (30d)",
    "days_to_renewal": "Days to Renewal",
    "known_bug_flag": "Known Bug Flag",
    "csm_health_score": "CSM Health Score",
}

FIELD_INFO = {
    "open_tickets_30d": "How many tickets are currently open for the account in the last 30 days.",
    "reopened_tickets_30d": "How many tickets had to be reopened, often a strong sign of unresolved friction.",
    "avg_first_response_hrs": "Average time taken to send the first reply.",
    "avg_resolution_hrs": "Average time taken to fully resolve issues.",
    "sev1_tickets_30d": "Critical severity incidents affecting the account.",
    "sentiment_score": "Customer sentiment from -1.0 to 1.0. Lower is worse.",
    "usage_change_pct_30d": "Change in product usage over the last 30 days. Negative is worse.",
    "login_change_pct_30d": "Change in login activity over the last 30 days. Negative is worse.",
    "days_to_renewal": "Days remaining until renewal. Lower can increase urgency.",
    "known_bug_flag": "Whether a known bug is currently impacting the account.",
    "csm_health_score": "Customer Success health score from 0 to 100. Lower is worse.",
}

RISK_BAND_COLORS = {
    "Low": "#16a34a",
    "Medium": "#ca8a04",
    "High": "#ea580c",
    "Critical": "#dc2626",
}



@st.cache_data(ttl=60)
def load_all_accounts() -> list[str]:
    query = """
    SELECT account_name
    FROM accounts
    ORDER BY account_name;
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
    return [row[0] for row in rows]


@st.cache_data(ttl=60)
def load_latest_account_snapshot(account_name: str) -> dict[str, Any] | None:
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
    WHERE a.account_name = %s
    ORDER BY s.snapshot_date DESC, s.snapshot_id DESC
    LIMIT 1;
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (account_name,))
            row = cur.fetchone()

    if not row:
        return None

    return {
        "account_id": row[0],
        "account_name": row[1],
        "segment": row[2],
        "arr_usd": float(row[3]),
        "strategic_account": row[4],
        "snapshot_id": row[5],
        "snapshot_date": row[6],
        "days_to_renewal": int(row[7]),
        "open_tickets_30d": int(row[8]),
        "reopened_tickets_30d": int(row[9]),
        "avg_first_response_hrs": float(row[10]),
        "avg_resolution_hrs": float(row[11]),
        "sev1_tickets_30d": int(row[12]),
        "sentiment_score": float(row[13]),
        "csat_avg_90d": float(row[14]),
        "usage_change_pct_30d": float(row[15]),
        "login_change_pct_30d": float(row[16]),
        "known_bug_flag": bool(row[17]),
        "csm_health_score": int(row[18]),
    }


def risk_badge_html(risk_band: str) -> str:
    color = RISK_BAND_COLORS.get(risk_band, "#6b7280")
    return f"""
    <div style="
        display:inline-block;
        background-color:{color};
        color:white;
        padding:6px 12px;
        border-radius:999px;
        font-size:0.9rem;
        font-weight:600;
        margin-top:6px;
    ">
        {risk_band}
    </div>
    """


def format_currency(value: float) -> str:
    return f"${value:,.0f}"


def build_comparison_table(
    current_snapshot: dict[str, Any],
    simulated_snapshot: dict[str, Any],
) -> pd.DataFrame:
    rows = []
    for field in SIMULATABLE_FIELDS:
        current_value = current_snapshot[field]
        simulated_value = simulated_snapshot[field]
        rows.append(
            {
                "Metric": FIELD_LABELS[field],
                "Current": current_value,
                "Simulated": simulated_value,
                "Changed": "Yes" if current_value != simulated_value else "No",
            }
        )
    return pd.DataFrame(rows)


def render_inputs(base_snapshot: dict[str, Any]) -> dict[str, Any]:
    simulated = dict(base_snapshot)

    st.markdown("### Scenario Inputs")
    st.caption("Adjust the inputs below to simulate how the account risk changes.")

    with st.container(border=True):
        col1, col2 = st.columns(2)

        with col1:
            simulated["open_tickets_30d"] = st.number_input(
                FIELD_LABELS["open_tickets_30d"],
                min_value=0,
                value=int(base_snapshot["open_tickets_30d"]),
                help=FIELD_INFO["open_tickets_30d"],
            )
            simulated["reopened_tickets_30d"] = st.number_input(
                FIELD_LABELS["reopened_tickets_30d"],
                min_value=0,
                value=int(base_snapshot["reopened_tickets_30d"]),
                help=FIELD_INFO["reopened_tickets_30d"],
            )
            simulated["avg_first_response_hrs"] = st.number_input(
                FIELD_LABELS["avg_first_response_hrs"],
                min_value=0.0,
                value=float(base_snapshot["avg_first_response_hrs"]),
                step=0.5,
                help=FIELD_INFO["avg_first_response_hrs"],
            )
            simulated["avg_resolution_hrs"] = st.number_input(
                FIELD_LABELS["avg_resolution_hrs"],
                min_value=0.0,
                value=float(base_snapshot["avg_resolution_hrs"]),
                step=1.0,
                help=FIELD_INFO["avg_resolution_hrs"],
            )
            simulated["sev1_tickets_30d"] = st.number_input(
                FIELD_LABELS["sev1_tickets_30d"],
                min_value=0,
                value=int(base_snapshot["sev1_tickets_30d"]),
                help=FIELD_INFO["sev1_tickets_30d"],
            )
            simulated["known_bug_flag"] = st.checkbox(
                FIELD_LABELS["known_bug_flag"],
                value=bool(base_snapshot["known_bug_flag"]),
                help=FIELD_INFO["known_bug_flag"],
            )

        with col2:
            simulated["sentiment_score"] = st.slider(
                FIELD_LABELS["sentiment_score"],
                min_value=-1.0,
                max_value=1.0,
                value=float(base_snapshot["sentiment_score"]),
                step=0.01,
                help=FIELD_INFO["sentiment_score"],
            )
            simulated["usage_change_pct_30d"] = st.slider(
                FIELD_LABELS["usage_change_pct_30d"],
                min_value=-100.0,
                max_value=100.0,
                value=float(base_snapshot["usage_change_pct_30d"]),
                step=1.0,
                help=FIELD_INFO["usage_change_pct_30d"],
            )
            simulated["login_change_pct_30d"] = st.slider(
                FIELD_LABELS["login_change_pct_30d"],
                min_value=-100.0,
                max_value=100.0,
                value=float(base_snapshot["login_change_pct_30d"]),
                step=1.0,
                help=FIELD_INFO["login_change_pct_30d"],
            )
            simulated["days_to_renewal"] = st.number_input(
                FIELD_LABELS["days_to_renewal"],
                min_value=0,
                value=int(base_snapshot["days_to_renewal"]),
                help=FIELD_INFO["days_to_renewal"],
            )
            simulated["csm_health_score"] = st.slider(
                FIELD_LABELS["csm_health_score"],
                min_value=0,
                max_value=100,
                value=int(base_snapshot["csm_health_score"]),
                step=1,
                help=FIELD_INFO["csm_health_score"],
            )

    return simulated


def main():
    st.title("Risk Simulator")
    st.caption("Test how account risk changes under different support and customer conditions")

    account_names = load_all_accounts()
    default_account = st.session_state.get("selected_account_name")

    options = ["Select an account..."] + account_names
    default_index = options.index(default_account) if default_account in account_names else 0

    selected_account = st.selectbox(
        "Choose an account to simulate",
        options=options,
        index=default_index,
    )

    if selected_account == "Select an account...":
        st.info("Select an account to begin simulation.")
        return

    st.session_state["selected_account_name"] = selected_account

    try:
        active_config = load_active_scoring_config()
        rules = load_scoring_rules(active_config["scoring_config_id"])
        latest_snapshot = load_latest_account_snapshot(selected_account)
    except Exception as exc:
        st.error(f"Failed to load simulator data: {exc}")
        return

    if not latest_snapshot:
        st.warning("No latest snapshot found for the selected account.")
        return

    current_result = score_account(latest_snapshot, rules)
    simulated_snapshot = render_inputs(latest_snapshot)

    simulate_clicked = st.button("Run Simulation", type="primary", width="stretch")

    if not simulate_clicked:
        st.info("Adjust any inputs above, then click Run Simulation.")
        return

    simulated_result = score_account(simulated_snapshot, rules)

    current_score = current_result["total_score"]
    simulated_score = simulated_result["total_score"]
    score_delta = simulated_score - current_score
    delta_text = f"{score_delta:+.2f}"

    st.divider()
    st.markdown("### Scenario Comparison")

    left_col, right_col = st.columns(2)

    with left_col:
        st.markdown("#### Current State")
        st.metric("Risk Score", f"{current_score:.2f}")
        st.markdown(risk_badge_html(current_result["risk_band"]), unsafe_allow_html=True)
        st.caption(
            f"{latest_snapshot['segment']} • ARR {format_currency(latest_snapshot['arr_usd'])} • "
            f"Renewal in {latest_snapshot['days_to_renewal']} days"
        )

        current_drivers = [
            current_result.get("top_driver_1"),
            current_result.get("top_driver_2"),
            current_result.get("top_driver_3"),
        ]
        current_drivers = [d for d in current_drivers if d]

        st.markdown("**Top Drivers**")
        for driver in current_drivers:
            st.write(f"- {driver}")

    with right_col:
        st.markdown("#### Simulated State")
        st.metric("Risk Score", f"{simulated_score:.2f}", delta=delta_text)
        st.markdown(risk_badge_html(simulated_result["risk_band"]), unsafe_allow_html=True)
        st.caption(
            f"{simulated_snapshot['segment']} • ARR {format_currency(simulated_snapshot['arr_usd'])} • "
            f"Renewal in {simulated_snapshot['days_to_renewal']} days"
        )

        simulated_drivers = [
            simulated_result.get("top_driver_1"),
            simulated_result.get("top_driver_2"),
            simulated_result.get("top_driver_3"),
        ]
        simulated_drivers = [d for d in simulated_drivers if d]

        st.markdown("**Top Drivers**")
        for driver in simulated_drivers:
            st.write(f"- {driver}")

        st.divider()

    explanation_col1, explanation_col2 = st.columns(2)

    with explanation_col1:
        st.markdown("### Current Explanation")
        with st.container(border=True):
            st.write(generate_executive_summary(latest_snapshot, current_result))
            st.write("")
            st.write(generate_risk_explanation(latest_snapshot, current_result))
            st.write("")
            st.write(generate_action_rationale(latest_snapshot, current_result))

    with explanation_col2:
        st.markdown("### Simulated Explanation")
        with st.container(border=True):
            st.write(generate_executive_summary(simulated_snapshot, simulated_result))
            st.write("")
            st.write(generate_risk_explanation(simulated_snapshot, simulated_result))
            st.write("")
            st.write(generate_action_rationale(simulated_snapshot, simulated_result))

    st.divider()

    st.markdown("### Recommended Actions")

    action_col1, action_col2 = st.columns(2)

    with action_col1:
        st.markdown("**Current Actions**")
        for action in [
            current_result.get("recommended_action_1"),
            current_result.get("recommended_action_2"),
            current_result.get("recommended_action_3"),
        ]:
            if action:
                st.write(f"- {action}")

    with action_col2:
        st.markdown("**Simulated Actions**")
        for action in [
            simulated_result.get("recommended_action_1"),
            simulated_result.get("recommended_action_2"),
            simulated_result.get("recommended_action_3"),
        ]:
            if action:
                st.write(f"- {action}")

    st.divider()

    st.markdown("### Input Comparison")
    comparison_df = build_comparison_table(latest_snapshot, simulated_snapshot)
    st.dataframe(comparison_df, width="stretch", hide_index=True)


if __name__ == "__main__":
    main()