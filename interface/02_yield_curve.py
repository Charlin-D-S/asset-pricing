import streamlit as st
import pandas as pd
import sys
import os
import plotly.express as px
import numpy as np

# Add src/ to PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from curves.yield_curve import YieldCurve

# -----------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------
st.set_page_config(
    page_title="Yield Curve Viewer",
    page_icon="📉",
    layout="wide"
)

st.title("📉 Euro Area Yield Curve (ECB)")
st.write("Explore the risk-free term structure used for pricing fixed-income and derivative products.")

# -----------------------------------------------------
# LOAD YIELD CURVE
# -----------------------------------------------------
@st.cache_data
def load_curve():
    yc = YieldCurve.from_csv()
    df = pd.DataFrame({
        "Maturity (years)": yc.maturities,
        "Zero Rate (%)": yc.zero_rates
    })
    return yc, df

yield_curve, curve_df = load_curve()

# -----------------------------------------------------
# DISPLAY DATAFRAME
# -----------------------------------------------------
# with st.expander("Show Zero-Coupon Yield Curve Data"):
#     #st.dataframe(price_df.style.format({"Bond Price": "{:.4f}", "Rate Shift (bps)": "{:.0f}"}))
#     #st.subheader("📋 Zero-Coupon Yield Curve Data")
#     st.dataframe(
#         curve_df.style.format({
#             "Zero Rate (%)": "{:.4f}"
#         }).highlight_min("Zero Rate (%)", color="#d4f4dd")
#         .highlight_max("Zero Rate (%)", color="#ffd4d4"),
#         use_container_width=True
#     )

# -----------------------------------------------------
# TABS FOR VISUALIZATIONS
# -----------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📈 Zero Curve", "💸 Discount Factors", "🔀 Forward Rates"])

# -----------------------------------------------------
# TAB 1 — ZERO RATE CURVE
# -----------------------------------------------------
with tab1:
    st.subheader("📈 Zero-Coupon Yield Curve")

    fig = px.line(
        curve_df,
        x="Maturity (years)",
        y="Zero Rate (%)",
        markers=True,
        title="ECB Zero-Coupon Yield Curve",
    )

    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)
    with st.expander("Show Zero-Coupon Yield Curve Data"):
#     #st.dataframe(price_df.style.format({"Bond Price": "{:.4f}", "Rate Shift (bps)": "{:.0f}"}))
#
        st.dataframe(
            curve_df.style.format({
                "Zero Rate (%)": "{:.4f}"
            }).highlight_min("Zero Rate (%)", color="#d4f4dd")
            .highlight_max("Zero Rate (%)", color="#ffd4d4"),
            use_container_width=True
        )

# -----------------------------------------------------
# TAB 2 — DISCOUNT FACTORS
# -----------------------------------------------------
with tab2:
    st.subheader("💸 Discount Factors")

    # Compute DF
    discount_df = curve_df.copy()
    discount_df["Discount Factor"] = np.exp(
        -discount_df["Zero Rate (%)"] * discount_df["Maturity (years)"]
    )

    fig_df = px.line(
        discount_df,
        x="Maturity (years)",
        y="Discount Factor",
        markers=True,
        title="Discount Factor Curve"
    )

    fig_df.update_layout(height=450)
    st.plotly_chart(fig_df, use_container_width=True)
    with st.expander("Show Discount Factor Yield Curve Data"):
#   
        st.dataframe(
            discount_df.style.format({
                "Zero Rate (%)": "{:.4f}",
                "Discount Factor": "{:.6f}"
            }),
            use_container_width=True
        )

# -----------------------------------------------------
# TAB 3 — FORWARD RATES
# -----------------------------------------------------
with tab3:
    st.subheader("🔀 Instantaneous Forward Rates (approx.)")

    fwd_df = curve_df.copy()
    maturities = fwd_df["Maturity (years)"].values
    zeros = fwd_df["Zero Rate (%)"].values

    # numerical forward rate approximation: f(t) = r(t) + t*r'(t)
    deriv = np.gradient(zeros, maturities)
    forward = zeros + maturities * deriv

    fwd_df["Forward Rate (%)"] = forward

    fig_fwd = px.line(
        fwd_df,
        x="Maturity (years)",
        y="Forward Rate (%)",
        markers=True,
        title="Instantaneous Forward Rate Curve"
    )

    fig_fwd.update_layout(height=450)
    st.plotly_chart(fig_fwd, use_container_width=True)
    with st.expander("Show Forward Rate Yield Curve Data"):
#   
        st.dataframe(
            fwd_df.style.format({
                "Zero Rate (%)": "{:.4f}",
                "Forward Rate (%)": "{:.4f}"
            }),
            use_container_width=True
        )

# -----------------------------------------------------
# FOOTER
# -----------------------------------------------------
st.markdown("---")
st.caption("Data source: ECB.")
