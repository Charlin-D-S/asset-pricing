import streamlit as st
import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from data_loader.yield_curve_loader import YieldCurveLoader
from data_loader.equity_loader import EquityLoader
from curves.yield_curve import YieldCurve


# ----------------------------------------------------------
# 🎨 PAGE CONFIGURATION
# ----------------------------------------------------------
st.set_page_config(
    page_title="Asset Pricing Platform",
    page_icon="📊",
    layout="wide"
)

st.markdown(
    """
    <style>
        .big-title { font-size: 38px !important; font-weight: 700; }
        .sub { font-size: 20px; color: #666; }
        .card {
            padding: 20px;
            border-radius: 15px;
            background-color: #f7f7f9;
            border: 1px solid #eee;
            margin-bottom: 20px;
        }
    </style>
    """,
    unsafe_allow_html=True
)


st.markdown("<div class='big-title'>📊 Asset Pricing Platform</div>", unsafe_allow_html=True)
st.markdown("<div class='sub'>Explore financial assets, visualise markets and access pricing tools.</div>", unsafe_allow_html=True)
st.write("")


# ----------------------------------------------------------
# 1️⃣ LOAD YIELD CURVE
# ----------------------------------------------------------
@st.cache_data
def load_curve():
    yc = YieldCurve.from_csv()
    df = pd.DataFrame({"maturity": yc.maturities, "rate": yc.zero_rates})
    return yc, df

yield_curve, yield_curve_df = load_curve()


# ----------------------------------------------------------
# 2️⃣ SEARCH FOR STOCKS / INDEXES
# ----------------------------------------------------------
st.header("🔍 Search Equity or Index")

text = st.text_input("Enter a stock name or ticker (e.g. total, MSFT, cac 40, Renault):")

@st.cache_data
def find_stock(text):
    return EquityLoader().find(text)
@st.cache_data
def get_historic(ticker, period="1y"):
    data = EquityLoader().get_historic(ticker, period)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [c[0] for c in data.columns]
    data["date"] = pd.to_datetime(data.index)
    data = data.reset_index(drop=True)
    return data[["date", "Close", "High", "Low", "Open", "Volume"]]


# search_df = None
# ticker = None

# # ============================================================
# # 2️⃣ Result list with styling
# # ============================================================
# if text:
#     try:
#         search_df = find_stock(text)

#         st.subheader("🔎 Search Results")

#         # ---- TABLEAU STYLISÉ ----
#         styled_df = search_df.style.set_properties(
#             **{
#                 "background-color": "#f7f7f9",
#                 "border-color": "#d3d3d3",
#                 "border-width": "1px",
#             }
#         ).hide(axis="index")

#         st.dataframe(
#             styled_df,
#             use_container_width=True,
#             height=250
#         )

#         # ======================================================
#         # 3️⃣ Selectbox (nom) + mapping vers ticker
#         # ======================================================
#         st.subheader("🎯 Choose a Stock")

#         choix = st.selectbox(
#             "Select a stock:",
#             options=list(search_df["Nom"]),
#             index=0 if len(search_df) > 0 else None
#         )

#         # mapping choix → ticker
#         ticker = search_df.loc[search_df["Nom"] == choix, "Symbole"].values[0]

#         st.success(f"📌 Selected: **{choix} ({ticker})**")

#     except Exception as e:
#         st.error(f"Error during search: {e}")

# else:
#     st.info("Type something above to search for a stock.")
search_df = None
if text:
    try:
        search_df = find_stock(text)

        # ---- 2️⃣ Affichage du résultat de recherche ----
        st.subheader("🔎 Search Results")
        st.dataframe(search_df, use_container_width=True)

        # ---- 3️⃣ Selectbox pour sélectionner le titre ----
        st.subheader("🎯 Choose a Stock")

        # On remplit la liste avec le nom complet (beau pour l'utilisateur)
        choix = st.selectbox(
            "Select a stock:",
            options=list(search_df["Nom"]),
            index=0 if len(search_df) > 0 else None
        )

        # On convertit le choix en ticker
        # (on retrouve la ligne)
        ticker = search_df.loc[search_df["Nom"] == choix, "Symbole"].values[0]

        st.success(f"📌 You selected: **{choix} ({ticker})**")

    except Exception as e:
        st.error(f"Error during search: {e}")
        ticker = None

else:
    st.info("Type something above to search for a stock.")
    ticker = None


# ---- 4️⃣ Tu peux maintenant utiliser le ticker sélectionné ----
if ticker:
    st.write("✔ The selected ticker can now be used for pricing modules.")


# ----------------------------------------------------------
# 3️⃣ HISTORICAL DATA VISUALIZATION
# ----------------------------------------------------------
if ticker:

    st.markdown(f"### 📈 Price Chart — {ticker}")

    try:
        data = get_historic(ticker)

        # 📊 Beautiful line chart
        st.area_chart(data, x="date", y="Close", height=300)

        # 🧱 Display table
        with st.expander("Show recent data"):
            st.dataframe(data.tail(), use_container_width=True)

        # 📊 Stats
        colA, colB, colC = st.columns(3)
        colA.metric("Last Close", f"{data['Close'].iloc[-1]:.2f}")
        colB.metric("1M Return", f"{100*(data['Close'].iloc[-1]/data['Close'].iloc[-22]-1):.2f}%")
        colC.metric("Volatility (20D)", f"{data['Close'].pct_change().std()*np.sqrt(252):.2%}")

    except Exception as e:
        st.error(f"Error: {e}")


# ----------------------------------------------------------
# 4️⃣ EURO RISK-FREE YIELD CURVE
# ----------------------------------------------------------
st.header("📉 Euro Area Risk-Free Yield Curve")

st.line_chart(yield_curve_df, x="maturity", y="rate", height=280)

with st.expander("Show curve data"):
    st.dataframe(yield_curve_df, use_container_width=True)


# ----------------------------------------------------------
# 5️⃣ NAVIGATION TO PRICERS
# ----------------------------------------------------------
st.header("🧭 Pricing Tools")

st.markdown("""
<div class="card">
    <ul>
        <li>📈 <b>Option Pricer</b> — Black–Scholes, Monte Carlo</li>
        <li>💵 <b>Bond Pricer</b> — price, duration, convexity</li>
        <li>📉 <b>Future Pricer</b></li>
        <li>🔁 <b>Swap Pricer</b></li>
    </ul>
</div>
""", unsafe_allow_html=True)
