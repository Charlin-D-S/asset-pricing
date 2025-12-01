import streamlit as st
import numpy as np
import pandas as pd
from datetime import date, datetime, timedelta
from curves.yield_curve import YieldCurve
from products.swap import InterestRateSwap  # ton fichier
from dateutil.relativedelta import relativedelta
@st.cache_data
def load_yield_curve():
    try:
        yc = YieldCurve.from_csv()
    except Exception:
        raise RuntimeError("Could not load yield curve.")

    df = pd.DataFrame({"maturity": yc.maturities, "rate": yc.zero_rates})
    return yc, df

st.title("💹 Interest Rate Swap Pricing (IRS)")

st.markdown("---")
st.subheader("📅 Swap Inputs")

# -------------------------------
# USER INPUTS
# -------------------------------
c1, c2, c3 = st.columns(3)

with c1:
    notional = st.number_input("Notional", value=1_000_000.0, step=10000.0)

with c2:
    fixed_rate = st.number_input("Fixed Rate (K)", value=0.03, format="%.4f")

with c3:
    freq = st.selectbox("Payment Frequency", ["Monthly","Quarterly", "Semi-Annual","Annual"])
    freq_map = {"Annual": 1, "Semi-Annual": 2, "Quarterly": 4,"Monthly": 12}
    n_pay = freq_map[freq]

# --- Select maturity date ---
maturity_date = st.date_input("Maturity Date", value=date.today()+ relativedelta(months=3))

# Compute year fraction
today = date.today()
days = (maturity_date - today).days
T = days / 365

st.caption("Time to maturity (years) "+ f"{T:.4f}")

# Generate payment schedule
dt = 1 / n_pay
payment_times = [round(dt * i, 6) for i in range(1, int(T * n_pay) + 1)]

#st.write("**Payment Times (years)**:", payment_times)


# -----------------------------------------------------
# Load yield curve once
# -----------------------------------------------------
try:
    curve, curve_df = load_yield_curve()
except Exception as e:
    st.error(f"Yield curve load error: {e}")
    curve, curve_df = None, pd.DataFrame()

st.markdown("---")
st.subheader("💰 Swap Pricing")

# Build IRS
swap = InterestRateSwap(
    notional=notional,
    fixed_rate=fixed_rate,
    payment_times=payment_times
)

# Compute legs
pv_fixed = swap.pv_fixed_leg(curve)
pv_float = swap.pv_floating_leg(curve)
swap_value = swap.price(curve)
swap_rate = swap.swap_rate(curve)

colA, colB, colC = st.columns(3)

colA.metric("PV Fixed Leg", f"{pv_fixed:,.2f}")
colB.metric("PV Floating Leg", f"{pv_float:,.2f}")
colC.metric("Swap Value (Receiver Float)", f"{swap_value:,.2f}")

st.metric("Implied Swap Rate", f"{swap_rate:.4%}")

# ------------------------------------------------------------
# CHART : Cashflow PV over time
# ------------------------------------------------------------
st.markdown("---")
st.subheader("🔍 Fixed Leg PV by Payment")

dfs = []
for t in payment_times:
    df = curve.discount_factor(t)
    dt = t - (0 if payment_times.index(t) == 0 else payment_times[payment_times.index(t)-1])
    cf_pv = notional * fixed_rate * dt * df
    dfs.append([t, cf_pv])

chart_df = pd.DataFrame(dfs, columns=["Time (years)", "PV Fixed Cashflow"])

st.bar_chart(chart_df, x="Time (years)", y="PV Fixed Cashflow")
