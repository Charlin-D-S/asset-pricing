import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from curves.yield_curve import YieldCurve
from products.coupon_bond import CouponBond
from products.future import EquityFuture
from products.swap import InterestRateSwap
from products.option import EuropeanCall,Option,EuropeanPut
from models.black_scholes import BlackScholesModel
from data_loader.yield_curve_loader import YieldCurveLoader
from data_loader.equity_loader import EquityLoader
from models.monte_carlo import MonteCarloPricer



@st.cache_resource
def get_bond(nominal, coupon_rate, maturity, frequency):
    return CouponBond(nominal, coupon_rate, maturity, frequency)


@st.cache_data
def curve():
    yield_curve = YieldCurve.from_csv()
    yield_curve_df = pd.DataFrame({'maturity':yield_curve.maturities,
                                  'rate':yield_curve.zero_rates})
    return yield_curve,yield_curve_df
yield_curve,yield_curve_df = curve()

# -----------------------------------------------------
# Page config
# -----------------------------------------------------
st.set_page_config(page_title="Bond Pricer", page_icon="📘", layout="wide")
#st.title("🧮 Option Pricer — Black–Scholes & Monte Carlo")
st.title("Interactive pricing of risk free bonds with live market data.")


# ============================================================
#                 SECTION B — BONDS
# ============================================================

st.header("🔹 Bond Pricing")

# # -------------------------------
# # 2B. Yield curve loading
# # -------------------------------
# st.subheader("Euro Area Risk-Free Yield Curve (ECB)")

# #if st.button("Load ECB curve"):
# st.line_chart(x='maturity',y='rate',data = yield_curve_df)

# -------------------------------
# 3B. Bond parameters
# -------------------------------
st.subheader("Bond Parameters")

col1, col2, col3, col4 = st.columns(4)
nominal = col1.number_input("Nominal (£)", value=100.0)
coupon_rate = col2.number_input("Coupon rate (%)", value=2.0)
maturity = col3.number_input("Maturity (years)", value=5.0)
with col4:
    freq = st.selectbox("Coupon frequency", ["Annual", "Semiannual"])
frequency = 1 if freq=="Annual" else 2
# -------------------------------
# 4B. Pricing
# -------------------------------
bond = get_bond(nominal, coupon_rate, maturity, frequency)
if st.button("Price Bond"):
    price = bond.price(yield_curve)
    duration = bond.duration(yield_curve)
    convexity = bond.convexity(yield_curve)

    # -------------------------------
    # 5B. Display results
    # -------------------------------
    
    st.subheader("📊 Bond Valuation")
    c1, c2, c3, = st.columns(3)
    c1.metric("**Price:**", f"{price:.2f}")
    c2.metric("**Duration:**", f"{duration:.2f}")
    c3.metric("**Convexity:**", f"{convexity:.2f}")

st.markdown("### 📈 Bond Price Sensitivity to Interest Rate Shifts")
st.caption("Impact of parallel shifts in the yield curve on the bond price.")

st.markdown("---")

# ------------------------------------------------------------
# Generate rate shift range (in basis points)
# ------------------------------------------------------------

spread_values = np.linspace(-0.02, 0.02, 100)   # -2% to +2% rate shift
spread_bps = spread_values * 10000              # convert to basis points

# Compute bond price for each shifted curve
bond_prices = np.array([bond.price(yield_curve.move_rate(-ds)) for ds in spread_values])

# Build DataFrame for plotting
price_df = pd.DataFrame({
    "Rate Shift (bps)": spread_bps,
    "Bond Price": bond_prices
})

# ------------------------------------------------------------
# Plot
# ------------------------------------------------------------
st.line_chart(price_df, x="Rate Shift (bps)", y="Bond Price")

# Optional: compact table below
with st.expander("Show sensitivity data"):
    st.dataframe(price_df.style.format({"Bond Price": "{:.4f}", "Rate Shift (bps)": "{:.0f}"}))
