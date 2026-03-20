import os

import pandas as pd
import psycopg
import streamlit as st
import matplotlib.pyplot as plt
from dotenv import load_dotenv

from db.db_connection import get_db_connection


load_dotenv()

st.set_page_config(
    page_title="Reports | SignalDesk",
    page_icon="📑",
    layout="wide",
)

from engine.explanation_engine import generate_risk_explanation

RISK_BAND_ORDER = ["Low", "Medium", "High", "Critical"]


@st.cache_data(ttl=60)
def load_report_data() -> pd.DataFrame:
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
    ORDER BY s.snapshot_date DESC, rs.scored_at DESC;
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
        "total_score",
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"], errors="coerce")
    df["scored_at"] = pd.to_datetime(df["scored_at"], errors="coerce")

    return df


def get_latest_snapshot_per_account(df: pd.DataFrame) -> pd.DataFrame:
    latest_df = (
        df.sort_values(["account_id", "snapshot_date", "scored_at"], ascending=[True, False, False])
        .drop_duplicates(subset=["account_id"], keep="first")
        .copy()
    )

    latest_df["risk_band"] = pd.Categorical(
        latest_df["risk_band"],
        categories=RISK_BAND_ORDER,
        ordered=True,
    )

    return latest_df.sort_values(["risk_band", "total_score"], ascending=[False, False])


def format_currency(value: float) -> str:
    return f"${value:,.0f}"


def render_risk_distribution_chart(df: pd.DataFrame):
    st.subheader("Risk Distribution")

    counts = (
        df["risk_band"]
        .astype(str)
        .value_counts()
        .reindex(RISK_BAND_ORDER, fill_value=0)
    )

    chart_df = counts.reset_index()
    chart_df.columns = ["Risk Band", "Count"]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(chart_df["Risk Band"], chart_df["Count"])
    ax.set_title("Accounts by Risk Band")
    ax.set_xlabel("Risk Band")
    ax.set_ylabel("Account Count")
    ax.grid(True, axis="y", alpha=0.3)

    st.pyplot(fig)


def render_arr_at_risk_chart(df: pd.DataFrame):
    st.subheader("ARR by Risk Band")

    arr_summary = (
        df.groupby("risk_band", observed=False)["arr_usd"]
        .sum()
        .reindex(RISK_BAND_ORDER, fill_value=0)
        .reset_index()
    )

    arr_summary.columns = ["Risk Band", "ARR"]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(arr_summary["Risk Band"], arr_summary["ARR"])
    ax.set_title("ARR Distribution by Risk Band")
    ax.set_xlabel("Risk Band")
    ax.set_ylabel("ARR (USD)")
    ax.grid(True, axis="y", alpha=0.3)

    st.pyplot(fig)


def render_kpis(df: pd.DataFrame):
    total_accounts = len(df)
    critical_accounts = int((df["risk_band"].astype(str) == "Critical").sum())
    high_accounts = int((df["risk_band"].astype(str) == "High").sum())
    arr_at_risk = df[df["risk_band"].astype(str).isin(["High", "Critical"])]["arr_usd"].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Accounts", total_accounts)
    col2.metric("Critical Risk", critical_accounts)
    col3.metric("High Risk", high_accounts)
    col4.metric("ARR at Risk", format_currency(arr_at_risk))


def render_renewals_at_risk(df: pd.DataFrame):
    st.subheader("Renewals at Risk")

    renewals_df = df[
        (df["days_to_renewal"] <= 60)
        & (df["risk_band"].astype(str).isin(["High", "Critical"]))
    ].copy()

    renewals_df = renewals_df.sort_values(
        by=["days_to_renewal", "total_score"],
        ascending=[True, False],
    )

    if renewals_df.empty:
        st.info("No high-risk renewals within the next 60 days.")
        return

    display_df = renewals_df[
        [
            "account_name",
            "segment",
            "arr_usd",
            "days_to_renewal",
            "total_score",
            "risk_band",
            "top_driver_1",
        ]
    ].rename(
        columns={
            "account_name": "Account",
            "segment": "Segment",
            "arr_usd": "ARR (USD)",
            "days_to_renewal": "Days to Renewal",
            "total_score": "Risk Score",
            "risk_band": "Risk Band",
            "top_driver_1": "Primary Driver",
        }
    )

    st.dataframe(
        display_df,
        width="stretch",
        hide_index=True,
        column_config={
            "ARR (USD)": st.column_config.NumberColumn(format="$%.0f"),
            "Risk Score": st.column_config.NumberColumn(format="%.2f"),
        },
    )


def render_top_risk_accounts(df: pd.DataFrame):
    st.subheader("Highest-Risk Accounts")

    display_df = (
        df.sort_values(by="total_score", ascending=False)
        .head(10)[
            [
                "account_name",
                "segment",
                "arr_usd",
                "total_score",
                "risk_band",
                "top_driver_1",
                "recommended_action_1",
            ]
        ]
        .rename(
            columns={
                "account_name": "Account",
                "segment": "Segment",
                "arr_usd": "ARR (USD)",
                "total_score": "Risk Score",
                "risk_band": "Risk Band",
                "top_driver_1": "Primary Driver",
                "recommended_action_1": "Recommended Action",
            }
        )
    )

    st.dataframe(
        display_df,
        width="stretch",
        hide_index=True,
        column_config={
            "ARR (USD)": st.column_config.NumberColumn(format="$%.0f"),
            "Risk Score": st.column_config.NumberColumn(format="%.2f"),
        },
    )


def render_top_risk_drivers(df: pd.DataFrame):
    st.subheader("Top Recurring Risk Drivers")

    drivers = pd.concat(
        [df["top_driver_1"], df["top_driver_2"], df["top_driver_3"]],
        ignore_index=True,
    ).dropna()

    if drivers.empty:
        st.info("No risk driver data available.")
        return

    driver_counts = drivers.value_counts().reset_index()
    if len(driver_counts.columns) == 2:
        driver_counts.columns = ["Driver", "Count"]

    st.dataframe(
        driver_counts.head(10),
        width="stretch",
        hide_index=True,
    )


def render_downloadable_table(df: pd.DataFrame):
    st.subheader("Downloadable Summary")

    export_df = df[
        [
            "account_name",
            "segment",
            "arr_usd",
            "strategic_account",
            "snapshot_date",
            "days_to_renewal",
            "total_score",
            "risk_band",
            "top_driver_1",
            "top_driver_2",
            "top_driver_3",
            "recommended_action_1",
        ]
    ].copy()

    export_df = export_df.rename(
        columns={
            "account_name": "Account",
            "segment": "Segment",
            "arr_usd": "ARR_USD",
            "strategic_account": "Strategic_Account",
            "snapshot_date": "Snapshot_Date",
            "days_to_renewal": "Days_to_Renewal",
            "total_score": "Risk_Score",
            "risk_band": "Risk_Band",
            "top_driver_1": "Top_Driver_1",
            "top_driver_2": "Top_Driver_2",
            "top_driver_3": "Top_Driver_3",
            "recommended_action_1": "Recommended_Action_1",
        }
    )

    st.dataframe(export_df, width="stretch", hide_index=True)

    csv_data = export_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download CSV Report",
        data=csv_data,
        file_name="signaldesk_report.csv",
        mime="text/csv",
    )


def main():
    st.title("Reports")
    st.caption("Portfolio-wide risk reporting and operational insights")

    refresh_col1, refresh_col2 = st.columns([1, 6])
    with refresh_col1:
        if st.button("Refresh Data", width="stretch"):
            st.cache_data.clear()
            st.rerun()

    try:
        raw_df = load_report_data()
    except Exception as exc:
        st.error(f"Failed to load report data: {exc}")
        return

    if raw_df.empty:
        st.warning("No report data found. Run the scoring engine first.")
        return

    latest_df = get_latest_snapshot_per_account(raw_df)

    st.sidebar.header("Filters")

    segment_options = ["All"] + sorted(latest_df["segment"].dropna().unique().tolist())
    selected_segment = st.sidebar.selectbox("Segment", segment_options)

    risk_band_options = ["All"] + RISK_BAND_ORDER
    selected_risk_band = st.sidebar.selectbox("Risk Band", risk_band_options)

    strategic_only = st.sidebar.checkbox("Strategic accounts only", value=False)

    filtered_df = latest_df.copy()

    if selected_segment != "All":
        filtered_df = filtered_df[filtered_df["segment"] == selected_segment]

    if selected_risk_band != "All":
        filtered_df = filtered_df[filtered_df["risk_band"].astype(str) == selected_risk_band]

    if strategic_only:
        filtered_df = filtered_df[filtered_df["strategic_account"] == True]

    render_kpis(filtered_df)

    st.divider()

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        render_risk_distribution_chart(filtered_df)
    with chart_col2:
        render_arr_at_risk_chart(filtered_df)

    st.divider()

    left_col, right_col = st.columns(2)
    with left_col:
        render_renewals_at_risk(filtered_df)
    with right_col:
        render_top_risk_drivers(filtered_df)

    st.divider()

    render_top_risk_accounts(filtered_df)
    
    st.divider()
    st.subheader("Management Narrative")

    if not filtered_df.empty:
        top_account = filtered_df.sort_values("total_score", ascending=False).iloc[0]

        snapshot_dict = top_account.to_dict()
        score_result = {
            "total_score": top_account["total_score"],
            "risk_band": top_account["risk_band"],
            "top_driver_1": top_account["top_driver_1"],
            "top_driver_2": top_account["top_driver_2"],
            "top_driver_3": top_account["top_driver_3"],
            "recommended_action_1": top_account["recommended_action_1"],
            "recommended_action_2": top_account["recommended_action_2"],
            "recommended_action_3": top_account["recommended_action_3"],
        }

        with st.container(border=True):
            st.write(generate_risk_explanation(snapshot_dict, score_result))

    st.divider()

    render_downloadable_table(filtered_df)


if __name__ == "__main__":
    main()