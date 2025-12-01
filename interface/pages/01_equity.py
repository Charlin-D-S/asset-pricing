import streamlit as st
import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "../src")))
from data_loader.equity_loader import EquityLoader


# ----------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------
st.title("📈 Equity Explorer")
st.write("Search equities or indices, preview mini-charts, and explore historical data.")


# ----------------------------------------------------------
# SEARCH BAR
# ----------------------------------------------------------
st.subheader("🔍 Search Asset")

query = st.text_input(
    "Enter ticker or asset name (e.g., AAPL, MSFT, RNO.PA, ^FCHI):",
    placeholder="Type here..."
)

@st.cache_data
def search_assets(text):
    if not text:
        return pd.DataFrame()
    return EquityLoader().find(text)

results_df = search_assets(query)

# Display search results
if not results_df.empty:
    st.markdown("### 🔎 Search Results")

    styled_df = results_df.style.set_properties(
        **{
            "background-color": "#f8f9fa",
            "border-color": "black",
            "border-width": "1px",
            "border-style": "solid",
        }
    )

    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
    )

    # Symbol selection
    ticker = st.selectbox(
        "Select an asset from search results:",
        options=list(results_df["Symbole"])
    )
else:
    ticker = None


# ----------------------------------------------------------
# MINI-CHART PREVIEW
# ----------------------------------------------------------
if ticker:

    st.subheader("📉 Mini Chart Preview")

    @st.cache_data
    def load_preview(ticker):
        df = EquityLoader().get_historic(ticker, period="3mo")
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0] for c in df.columns]
        df["date"] = pd.to_datetime(df.index)
        return df[["date", "Close"]]

    preview_df = load_preview(ticker)

    if not preview_df.empty:
        st.line_chart(preview_df, x="date", y="Close", height=200)
    else:
        st.warning("No data available for preview.")


# ----------------------------------------------------------
# FULL HISTORICAL DATA
# ----------------------------------------------------------
if ticker:

    st.subheader("📘 Historical Price (2 years)")

    @st.cache_data
    def load_full_history(ticker):
        df = EquityLoader().get_historic(ticker, period="2y")
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0] for c in df.columns]
        df["date"] = pd.to_datetime(df.index)
        return df[["date", "Close", "High", "Low", "Open"]]

    hist_df = load_full_history(ticker)

    st.line_chart(hist_df, x="date", y="Close")

    st.markdown("### 📄 Raw Data")
    st.dataframe(hist_df.tail(20), use_container_width=True)


# ----------------------------------------------------------
# FOOTER
# ----------------------------------------------------------
st.markdown(
    """
    <p style='text-align: center; color: gray; font-size: 12px;'>
    Equity Explorer — Asset Pricing Platform © 2025
    </p>
    """,
    unsafe_allow_html=True
)
