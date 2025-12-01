import streamlit as st

# ----------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------
st.set_page_config(
    page_title="Asset Pricing Platform",
    page_icon="📊",
    layout="wide"
)

# ----------------------------------------------------------
# HEADER
# ----------------------------------------------------------
st.title("📊 Asset Pricing Platform")
st.markdown(
    """
    Welcome to your financial analytics and pricing environment.  
    Explore markets, visualize yield curves, and value derivatives and fixed-income products.
    """
)

st.divider()

# ----------------------------------------------------------
# DASHBOARD CARDS
# ----------------------------------------------------------
st.subheader("🧭 Navigation")

col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

# -------- EQUITY EXPLORER ----------
with col1:
    st.markdown("### 📈 Equity Explorer")
    st.markdown("Search for stocks or indices, view historical data, and analyze markets.")
    st.page_link("pages/01_equity.py", label="➡️ Open", icon="🔍")
    st.write("")

# -------- OPTION PRICER ----------
with col2:
    st.markdown("### 🧮 Option Pricer")
    st.markdown("Black–Scholes, Greeks, Monte Carlo simulations…")
    st.page_link("pages/03_option_pricer.py", label="➡️ Open Option Pricer", icon="📘")

# -------- BOND ANALYTICS ----------
with col3:
    st.markdown("### 💵 Bond Analytics")
    st.markdown("Compute price, duration, convexity, and sensitivity.")
    st.page_link("pages/bond.py", label="➡️ Open Bond Analytics", icon="💼")

# -------- YIELD CURVE ----------
with col4:
    st.markdown("### 📉 Yield Curve Explorer")
    st.markdown("Visualize interest rate curves and build custom curves.")
    st.page_link("pages/02_yield_curve.py", label="➡️ Open Yield Curve Viewer", icon="📉")

st.divider()

# ----------------------------------------------------------
# FOOTER
# ----------------------------------------------------------
st.markdown(
    """
    <p style='text-align: center; color: gray; font-size: 12px;'>
    Asset Pricing Platform — Developed by Charlin © 2025  
    </p>
    """,
    unsafe_allow_html=True
)
