import os

import pandas as pd
import psycopg
import streamlit as st
import matplotlib.pyplot as plt
from db.db_connection import get_db_connection
from dotenv import load_dotenv


load_dotenv()

st.set_page_config(
    page_title="Account Detail | SignalDesk",
    page_icon="📊",
    layout="wide",
)

from engine.explanation_engine import (
    generate_action_rationale,
    generate_executive_summary,
    generate_risk_explanation,
)


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
def load_account_history(account_name: str) -> pd.DataFrame:
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
        s.csm_health_score,
        rs.total_score,
        rs.risk_band,
        rs.top_driver_1,
        rs.top_driver_2,
        rs.top_driver_3,
        rs.recommended_action_1,
        rs.recommended_action_2,
        rs.recommended_action_3,
        rs.scored_at
    FROM risk_scores rs
    JOIN accounts a
        ON rs.account_id = a.account_id
    JOIN account_signal_snapshots s
        ON rs.snapshot_id = s.snapshot_id
    JOIN scoring_configs sc
        ON rs.scoring_config_id = sc.scoring_config_id
    WHERE sc.is_active = TRUE
      AND a.account_name = %s
    ORDER BY s.snapshot_date ASC, rs.scored_at ASC;
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (account_name,))
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
        "total_score",
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"], errors="coerce")
    df["scored_at"] = pd.to_datetime(df["scored_at"], errors="coerce")

    return df


def risk_band_color(risk_band: str) -> str:
    mapping = {
        "Low": "#16a34a",
        "Medium": "#ca8a04",
        "High": "#ea580c",
        "Critical": "#dc2626",
    }
    return mapping.get(risk_band, "#6b7280")


def format_currency(value: float) -> str:
    return f"${value:,.0f}"


def compute_delta(history_df: pd.DataFrame, col_name: str) -> str | None:
    valid = history_df[[col_name]].dropna()
    if len(valid) < 2:
        return None

    current = valid.iloc[-1][col_name]
    previous = valid.iloc[-2][col_name]
    delta = current - previous

    if abs(delta) < 0.01:
        return "0.00"

    sign = "+" if delta > 0 else ""
    return f"{sign}{delta:.2f}"


def render_styled_trend_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    y_label: str,
    threshold_lines: list[float] | None = None,
    background_zones: list[tuple[float, float]] | None = None,
    y_limits: tuple[float, float] | None = None,
    marker: str = "o",
    line_width: float = 2.0,
):
    chart_df = df[[x_col, y_col]].dropna().copy()

    if chart_df.empty:
        st.info(f"No data available for {title.lower()}.")
        return

    fig, ax = plt.subplots(figsize=(8, 4))

    if background_zones:
        for start, end in background_zones:
            ax.axhspan(start, end, alpha=0.08)

    if threshold_lines:
        for line in threshold_lines:
            ax.axhline(line, linestyle="--", linewidth=1)

    ax.plot(chart_df[x_col], chart_df[y_col], marker=marker, linewidth=line_width)

    ax.set_title(title)
    ax.set_xlabel("Snapshot Date")
    ax.set_ylabel(y_label)

    if y_limits:
        ax.set_ylim(y_limits[0], y_limits[1])

    ax.grid(True, alpha=0.3)
    fig.autofmt_xdate()

    st.pyplot(fig)


def main():
    st.title("Account Detail")
    st.caption("Detailed account-level risk analysis")

    account_names = load_all_accounts()

    default_account = st.session_state.get("selected_account_name")
    default_index = 0
    options = ["Select an account..."] + account_names

    if default_account in account_names:
        default_index = options.index(default_account)

    selected_account = st.selectbox(
        "Choose an account",
        options=options,
        index=default_index,
    )

    if selected_account == "Select an account...":
        st.info("Select an account to view its risk details.")
        return

    st.session_state["selected_account_name"] = selected_account

    try:
        history_df = load_account_history(selected_account)
    except Exception as exc:
        st.error(f"Failed to load account details: {exc}")
        return

    if history_df.empty:
        st.warning("No scored data found for this account.")
        return

    latest_row = history_df.sort_values(["snapshot_date", "scored_at"], ascending=[False, False]).iloc[0]

    score_delta = compute_delta(history_df, "total_score")
    sentiment_delta = compute_delta(history_df, "sentiment_score")
    usage_delta = compute_delta(history_df, "usage_change_pct_30d")
    renewal_delta = compute_delta(history_df, "days_to_renewal")

    st.subheader(latest_row["account_name"])
    st.caption(f"{latest_row['segment']} account")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Risk Score", f"{latest_row['total_score']:.2f}", delta=score_delta)
    col2.metric("Risk Band", latest_row["risk_band"])
    col3.metric("Days to Renewal", int(latest_row["days_to_renewal"]), delta=renewal_delta)
    col4.metric("ARR", format_currency(float(latest_row["arr_usd"])))

    aux1, aux2 = st.columns(2)
    aux1.metric("Sentiment Score", f"{latest_row['sentiment_score']:.2f}", delta=sentiment_delta)
    aux2.metric("Usage Change %", f"{latest_row['usage_change_pct_30d']:.2f}", delta=usage_delta)

    st.markdown(
        f"""
        <div style="
            background-color:{risk_band_color(latest_row['risk_band'])};
            padding:12px 16px;
            border-radius:12px;
            color:white;
            font-weight:600;
            width:fit-content;
            margin-top:8px;
            margin-bottom:16px;
        ">
            Current Status: {latest_row['risk_band']} Risk
        </div>
        """,
        unsafe_allow_html=True,
    )

    info_col1, info_col2 = st.columns(2)

    with info_col1:
        st.markdown("### Top Risk Drivers")
        drivers = [
            latest_row["top_driver_1"],
            latest_row["top_driver_2"],
            latest_row["top_driver_3"],
        ]
        for driver in drivers:
            if driver:
                st.write(f"- {driver}")

    with info_col2:
        st.markdown("### Recommended Actions")
        actions = [
            latest_row["recommended_action_1"],
            latest_row["recommended_action_2"],
            latest_row["recommended_action_3"],
        ]
        for action in actions:
            if action:
                st.write(f"- {action}")

    st.divider()

    st.markdown("### Risk Trends")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        render_styled_trend_chart(
            history_df,
            x_col="snapshot_date",
            y_col="total_score",
            title="Risk Score Trend",
            y_label="Risk Score",
            threshold_lines=[25, 50, 75],
            background_zones=[(0, 24), (25, 49), (50, 74), (75, 100)],
            y_limits=(0, 100),
        )

    with chart_col2:
        render_styled_trend_chart(
            history_df,
            x_col="snapshot_date",
            y_col="sentiment_score",
            title="Sentiment Trend",
            y_label="Sentiment Score",
            threshold_lines=[-0.30, 0.00, 0.30],
            background_zones=[(-1.0, -0.30), (-0.30, 0.00), (0.00, 0.30), (0.30, 1.0)],
            y_limits=(-1.0, 1.0),
        )

    st.markdown("### Product Usage Trend")
    render_styled_trend_chart(
        history_df,
        x_col="snapshot_date",
        y_col="usage_change_pct_30d",
        title="Usage Change Trend",
        y_label="Usage Change (%)",
        threshold_lines=[-30, -15, -5],
        background_zones=[(-100, -30), (-30, -15), (-15, -5), (-5, 100)],
    )

    st.divider()

    st.markdown("### Historical Snapshot Table")

    history_table = history_df[
        [
            "snapshot_date",
            "total_score",
            "risk_band",
            "sentiment_score",
            "usage_change_pct_30d",
            "open_tickets_30d",
            "reopened_tickets_30d",
            "days_to_renewal",
        ]
    ].copy()

    history_table = history_table.rename(
        columns={
            "snapshot_date": "Snapshot Date",
            "total_score": "Risk Score",
            "risk_band": "Risk Band",
            "sentiment_score": "Sentiment",
            "usage_change_pct_30d": "Usage Change %",
            "open_tickets_30d": "Open Tickets (30d)",
            "reopened_tickets_30d": "Reopened Tickets (30d)",
            "days_to_renewal": "Days to Renewal",
        }
    )

    st.dataframe(
        history_table.sort_values("Snapshot Date", ascending=False),
        width="stretch",
        hide_index=True,
    )

    st.divider()

    st.markdown("### Latest Account Signal Snapshot")

    signal_data = pd.DataFrame(
        {
            "Metric": [
                "Open Tickets (30d)",
                "Reopened Tickets (30d)",
                "Avg First Response (hrs)",
                "Avg Resolution (hrs)",
                "Severity 1 Tickets (30d)",
                "Sentiment Score",
                "CSAT Avg (90d)",
                "Usage Change % (30d)",
                "Login Change % (30d)",
                "Known Bug Flag",
                "CSM Health Score",
                "Strategic Account",
                "Snapshot Date",
            ],
            "Value": [
                latest_row["open_tickets_30d"],
                latest_row["reopened_tickets_30d"],
                latest_row["avg_first_response_hrs"],
                latest_row["avg_resolution_hrs"],
                latest_row["sev1_tickets_30d"],
                latest_row["sentiment_score"],
                latest_row["csat_avg_90d"],
                latest_row["usage_change_pct_30d"],
                latest_row["login_change_pct_30d"],
                "Yes" if latest_row["known_bug_flag"] else "No",
                latest_row["csm_health_score"],
                "Yes" if latest_row["strategic_account"] else "No",
                latest_row["snapshot_date"].date() if pd.notna(latest_row["snapshot_date"]) else None,
            ],
        }
    )
    
    signal_data["Value"] = signal_data["Value"].astype(str)

    st.dataframe(signal_data, width="stretch", hide_index=True)

    st.divider()

    st.markdown("### AI Explanation")

    explanation_col1, explanation_col2 = st.columns(2)

    latest_snapshot_dict = latest_row.to_dict()
    latest_score_result = {
        "total_score": latest_row["total_score"],
        "risk_band": latest_row["risk_band"],
        "top_driver_1": latest_row["top_driver_1"],
        "top_driver_2": latest_row["top_driver_2"],
        "top_driver_3": latest_row["top_driver_3"],
        "recommended_action_1": latest_row["recommended_action_1"],
        "recommended_action_2": latest_row["recommended_action_2"],
        "recommended_action_3": latest_row["recommended_action_3"],
    }

    with explanation_col1:
        st.markdown("#### Executive Summary")
        with st.container(border=True):
            st.write(generate_executive_summary(latest_snapshot_dict, latest_score_result))

    with explanation_col2:
        st.markdown("#### Intervention Rationale")
        with st.container(border=True):
            st.write(generate_action_rationale(latest_snapshot_dict, latest_score_result))

    st.markdown("#### Full Account Narrative")
    with st.container(border=True):
        st.write(generate_risk_explanation(latest_snapshot_dict, latest_score_result))

    summary_parts = [
        f"{latest_row['account_name']} is currently rated {latest_row['risk_band'].lower()} risk with a score of {latest_row['total_score']:.2f}.",
        f"The account renews in {int(latest_row['days_to_renewal'])} days.",
    ]

    if latest_row["top_driver_1"]:
        summary_parts.append(f"The strongest driver is {latest_row['top_driver_1']}.")
    if latest_row["recommended_action_1"]:
        summary_parts.append(f"Recommended first step: {latest_row['recommended_action_1']}.")

    st.write(" ".join(summary_parts))


if __name__ == "__main__":
    main()