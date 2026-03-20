import os

import pandas as pd
import psycopg
import streamlit as st
from db.db_connection import get_db_connection
from dotenv import load_dotenv


load_dotenv()

st.set_page_config(
    page_title="Signal Desk | Home",
    page_icon="📈",
    layout="wide",
)


RISK_BAND_ORDER = ["Low", "Medium", "High", "Critical"]
RISK_BAND_COLORS = {
    "Low": "#16a34a",
    "Medium": "#ca8a04",
    "High": "#ea580c",
    "Critical": "#dc2626",
}


@st.cache_data(ttl=60)
def load_dashboard_data() -> pd.DataFrame:
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
    ORDER BY rs.total_score DESC, a.account_name;
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            df = pd.DataFrame(rows, columns=columns)

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

    if "snapshot_date" in df.columns:
        df["snapshot_date"] = pd.to_datetime(df["snapshot_date"], errors="coerce")

    if "scored_at" in df.columns:
        df["scored_at"] = pd.to_datetime(df["scored_at"], errors="coerce")

    df["risk_band"] = pd.Categorical(df["risk_band"], categories=RISK_BAND_ORDER, ordered=True)

    return df


def format_currency(value: float) -> str:
    return f"${value:,.0f}"


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
    ">
        {risk_band}
    </div>
    """


def build_executive_summary(df: pd.DataFrame) -> list[str]:
    critical_count = int((df["risk_band"] == "Critical").sum())
    high_count = int((df["risk_band"] == "High").sum())
    at_risk_arr = df[df["risk_band"].isin(["High", "Critical"])]["arr_usd"].sum()

    soon_renewals = df[(df["days_to_renewal"] <= 30) & (df["risk_band"].isin(["High", "Critical"]))]
    soon_renewal_count = len(soon_renewals)

    top_driver = None
    if not df.empty:
        driver_series = pd.concat(
            [
                df["top_driver_1"],
                df["top_driver_2"],
                df["top_driver_3"],
            ],
            ignore_index=True,
        ).dropna()

        if not driver_series.empty:
            top_driver = driver_series.value_counts().idxmax()

    summary_points = [
        f"{critical_count} critical-risk accounts are currently flagged.",
        f"{high_count} high-risk accounts require attention.",
        f"Estimated ARR exposed to elevated risk: {format_currency(at_risk_arr)}.",
    ]

    if soon_renewal_count > 0:
        summary_points.append(
            f"{soon_renewal_count} high-risk accounts renew within the next 30 days."
        )

    if top_driver:
        summary_points.append(
            f"The most common active risk driver is <strong>{top_driver}</strong>."
        )

    return summary_points


def build_filtered_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filters")

    segment_options = ["All"] + sorted(df["segment"].dropna().unique().tolist())
    selected_segment = st.sidebar.selectbox("Segment", segment_options)

    risk_band_options = ["All"] + [band for band in RISK_BAND_ORDER if band in df["risk_band"].astype(str).unique()]
    selected_risk_band = st.sidebar.selectbox("Risk Band", risk_band_options)

    strategic_only = st.sidebar.checkbox("Strategic accounts only", value=False)

    max_days_to_renewal = int(df["days_to_renewal"].max()) if not df["days_to_renewal"].isna().all() else 365
    selected_days = st.sidebar.slider(
        "Days to renewal (max)",
        min_value=0,
        max_value=max_days_to_renewal,
        value=max_days_to_renewal,
    )

    min_score, max_score = 0.0, 100.0
    selected_score_range = st.sidebar.slider(
        "Risk score range",
        min_value=min_score,
        max_value=max_score,
        value=(min_score, max_score),
        step=1.0,
    )

    filtered_df = df.copy()

    if selected_segment != "All":
        filtered_df = filtered_df[filtered_df["segment"] == selected_segment]

    if selected_risk_band != "All":
        filtered_df = filtered_df[filtered_df["risk_band"].astype(str) == selected_risk_band]

    if strategic_only:
        filtered_df = filtered_df[filtered_df["strategic_account"] == True]

    filtered_df = filtered_df[filtered_df["days_to_renewal"] <= selected_days]
    filtered_df = filtered_df[
        (filtered_df["total_score"] >= selected_score_range[0]) &
        (filtered_df["total_score"] <= selected_score_range[1])
    ]

    return filtered_df


def render_kpis(df: pd.DataFrame):
    total_accounts = len(df)
    critical_accounts = int((df["risk_band"] == "Critical").sum())
    high_accounts = int((df["risk_band"] == "High").sum())
    arr_at_risk = df[df["risk_band"].isin(["High", "Critical"])]["arr_usd"].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Accounts in View", total_accounts)
    col2.metric("Critical Risk", critical_accounts)
    col3.metric("High Risk", high_accounts)
    col4.metric("ARR at Risk", format_currency(arr_at_risk))


def render_dashboard_table(df: pd.DataFrame):
    display_df = df[
        [
            "account_name",
            "segment",
            "arr_usd",
            "days_to_renewal",
            "total_score",
            "risk_band",
            "top_driver_1",
            "top_driver_2",
            "top_driver_3",
            "recommended_action_1",
        ]
    ].copy()

    display_df = display_df.rename(
        columns={
            "account_name": "Account",
            "segment": "Segment",
            "arr_usd": "ARR (USD)",
            "days_to_renewal": "Days to Renewal",
            "total_score": "Risk Score",
            "risk_band": "Risk Band",
            "top_driver_1": "Top Driver 1",
            "top_driver_2": "Top Driver 2",
            "top_driver_3": "Top Driver 3",
            "recommended_action_1": "Recommended Action",
        }
    )

    st.subheader("Ranked Account Risk Dashboard")
    st.dataframe(
        display_df,
        width="stretch",
        hide_index=True,
        column_config={
            "ARR (USD)": st.column_config.NumberColumn(format="$%.0f"),
            "Risk Score": st.column_config.NumberColumn(format="%.2f"),
        },
    )


def render_top_accounts(df: pd.DataFrame):
    st.subheader("Top 5 At-Risk Accounts")

    top5 = df.sort_values(by="total_score", ascending=False).head(5)[
        ["account_name", "risk_band", "total_score", "top_driver_1", "recommended_action_1"]
    ]

    if top5.empty:
        st.info("No accounts match the current filters.")
        return

    for _, row in top5.iterrows():
        with st.container(border=True):
            badge_html = risk_badge_html(str(row["risk_band"]))
            st.markdown(f"**{row['account_name']}**", unsafe_allow_html=True)
            st.markdown(badge_html, unsafe_allow_html=True)
            st.write(f"Risk Score: {row['total_score']:.2f}")
            st.write(f"Primary Driver: {row['top_driver_1']}")
            st.write(f"Recommended Action: {row['recommended_action_1']}")


def render_renewals_at_risk(df: pd.DataFrame):
    st.subheader("Renewals at Risk")

    renewals_df = df[
        (df["days_to_renewal"] <= 60) &
        (df["risk_band"].isin(["High", "Critical"]))
    ].copy()

    renewals_df = renewals_df.sort_values(by=["days_to_renewal", "total_score"], ascending=[True, False])

    if renewals_df.empty:
        st.info("No high-risk renewals within the next 60 days.")
        return

    display_df = renewals_df[
        ["account_name", "segment", "days_to_renewal", "total_score", "risk_band", "top_driver_1"]
    ].rename(
        columns={
            "account_name": "Account",
            "segment": "Segment",
            "days_to_renewal": "Days to Renewal",
            "total_score": "Risk Score",
            "risk_band": "Risk Band",
            "top_driver_1": "Primary Driver",
        }
    )

    st.dataframe(display_df, width="stretch", hide_index=True)


def render_recurring_drivers(df: pd.DataFrame):
    st.subheader("Most Common Active Risk Drivers")

    drivers = pd.concat(
        [df["top_driver_1"], df["top_driver_2"], df["top_driver_3"]],
        ignore_index=True,
    ).dropna()

    if drivers.empty:
        st.info("No risk driver data available.")
        return

    driver_counts = (
        drivers.value_counts()
        .reset_index()
        .rename(columns={"index": "Driver", "count": "Count"})
    )

    # Compatibility-safe rename
    if list(driver_counts.columns) != ["Driver", "Count"]:
        driver_counts.columns = ["Driver", "Count"]

    st.dataframe(driver_counts.head(10), width="stretch", hide_index=True)


def render_quick_account_picker(df: pd.DataFrame):
    st.subheader("Quick Account Lookup")

    account_names = df["account_name"].dropna().sort_values().tolist()
    selected_account = st.selectbox(
        "Select an account to inspect",
        ["Select an account..."] + account_names,
        key="home_quick_account_lookup",
    )

    if selected_account != "Select an account...":
        st.session_state["selected_account_name"] = selected_account
        st.switch_page("pages/1_Account_Detail.py")


def main():
    st.title("Signal Desk")
    st.caption("Customer Signal Intelligence for Proactive Support")

    top_col1, top_col2 = st.columns([1, 6])
    with top_col1:
        if st.button("Refresh Data", width="stretch"):
            st.cache_data.clear()
            st.rerun()

    try:
        df = load_dashboard_data()

        # Keep only the latest snapshot per account
        df = (
            df.sort_values(
                ["account_id", "snapshot_date", "scored_at"],
                ascending=[True, False, False],
            )
            .drop_duplicates(subset=["account_id"], keep="first")
        )

        # Rank accounts by highest risk first
        df = df.sort_values("total_score", ascending=False)

    except Exception as exc:
        st.error(f"Failed to load dashboard data: {exc}")
        return

    if df.empty:
        st.warning("No scored account data found. Run the scoring engine first.")
        return

    filtered_df = build_filtered_dataframe(df)

    st.markdown("### Executive Summary")

    summary_points = build_executive_summary(filtered_df)
    bullet_html = "".join([f"<li>{p}</li>" for p in summary_points])

    st.markdown(
        f"""
        <div style="
            background-color:#f1f5f9;
            padding:16px 20px;
            border-radius:12px;
            border:1px solid #e2e8f0;
            margin-bottom:10px;
        ">
            <ul style="margin:0; padding-left:18px;">
                {bullet_html}
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_kpis(filtered_df)

    st.divider()
    render_quick_account_picker(filtered_df)

    st.divider()
    render_dashboard_table(filtered_df)

    st.divider()
    left_col, right_col = st.columns([1.2, 1])

    with left_col:
        render_renewals_at_risk(filtered_df)

    with right_col:
        render_top_accounts(filtered_df)

    st.divider()
    render_recurring_drivers(filtered_df)


if __name__ == "__main__":
    main()