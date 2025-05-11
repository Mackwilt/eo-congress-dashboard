import streamlit as st
import pandas as pd
import altair as alt
import requests
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Gov Dashboard",
    layout="wide"
)

@st.cache_data(ttl=300)
def load_eo_summaries() -> pd.DataFrame:
    # 1) Hit your n8n node that returns {"texts": [ "<p>...</p>", ... ]}
    r = requests.get("https://mackwiltrout.app.n8n.cloud/webhook-test/65895fd9-6f95-4956-a66f-9f4e9ff0dae2")
    data = r.json()["texts"]
    # Turn it into a DataFrame with one summary per row
    return pd.DataFrame({"summary_html": data})

@st.cache_data(ttl=300)
def load_congress_summaries() -> pd.DataFrame:
    # 2) Hit your n8n node for congress summaries
    r = requests.get("https://mackwiltrout.app.n8n.cloud/webhook-test/05723c84-2472-4041-be33-ca5157e222e1")
    data = r.json()["texts"]
    return pd.DataFrame({"summary_html": data})

@st.cache_data(ttl=300)
def load_eo_counts() -> pd.DataFrame:
    # 3) Or compute counts yourself via another endpoint
    #    Here’s dummy data for illustration:
    df = pd.DataFrame({
        "date": pd.date_range(end=datetime.utcnow(), periods=7, freq="D"),
        "eo_count": [5, 3, 4, 6, 2, 8, 7]
    })
    return df

@st.cache_data(ttl=300)
def load_leg_counts() -> pd.DataFrame:
    df = pd.DataFrame({
        "date": pd.date_range(end=datetime.utcnow(), periods=7, freq="D"),
        "leg_count": [10, 12, 9, 15, 11, 14, 13]
    })
    return df

def main():
    st.title("🗂️ Government Tracking Dashboard")
    st.markdown("**Executive Orders** vs **Congressional Summaries** for the past week")

    # --- Top-row KPI cards ---
    eo_df = load_eo_summaries()
    leg_df = load_congress_summaries()
    col1, col2 = st.columns(2)
    col1.metric("EO Summaries", len(eo_df))
    col2.metric("Legislative Summaries", len(leg_df))

    # --- Time-series charts side by side ---
    eo_counts = load_eo_counts()
    leg_counts = load_leg_counts()
    chart_col1, chart_col2 = st.columns(2)

    chart_col1.subheader("EOs per Day")
    eo_chart = alt.Chart(eo_counts).mark_bar().encode(
        x="date:T", y="eo_count:Q"
    )
    chart_col1.altair_chart(eo_chart, use_container_width=True)

    chart_col2.subheader("Legislative Updates per Day")
    leg_chart = alt.Chart(leg_counts).mark_line(point=True).encode(
        x="date:T", y="leg_count:Q"
    )
    chart_col2.altair_chart(leg_chart, use_container_width=True)

    st.markdown("---")

    # --- Show raw summaries with expanders ---
    with st.expander("▶️ Executive Order Texts"):
        for i, row in eo_df.iterrows():
            st.markdown(row["summary_html"], unsafe_allow_html=True)
            st.write("—" * 40)

    with st.expander("▶️ Congressional Summaries"):
        for i, row in leg_df.iterrows():
            st.markdown(row["summary_html"], unsafe_allow_html=True)
            st.write("—" * 40)

if __name__ == "__main__":
    main()

