import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional
from datetime import date, datetime

# ensure src is importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

# local project imports
from data_loader.equity_loader import EquityLoader
from data_loader.yield_curve_loader import YieldCurveLoader
from curves.yield_curve import YieldCurve
from products.future import EquityFuture   # ADD THIS CLASS
from products.option import EuropeanCall, EuropeanPut  # maybe needed if reused


# -----------------------------------------------------
# Page config
# -----------------------------------------------------
st.set_page_config(page_title="Futures Pricer", page_icon="📘", layout="wide")
st.title("📘 Equity Futures Pricer — Cost of Carry Model")
st.markdown("Compute theoretical future price, long/short value, and payoff curves.")


# -----------------------------------------------------
# Helper loaders
# -----------------------------------------------------
@st.cache_data
def load_yield_curve():
    try:
        yc = YieldCurve.from_csv()
    except Exception:
        raise RuntimeError("Could not load yield curve.")

    df = pd.DataFrame({"maturity": yc.maturities, "rate": yc.zero_rates})
    return yc, df


@st.cache_data
def search_assets(query: str) -> pd.DataFrame:
    return EquityLoader().find(query)


@st.cache_data
def get_historic(ticker: str, period: str = "1y") -> pd.DataFrame:
    df = EquityLoader().get_historic(ticker, period=period)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]
    df["date"] = pd.to_datetime(df.index)
    return df



# -----------------------------------------------------
# Load yield curve once
# -----------------------------------------------------
try:
    yield_curve, yield_df = load_yield_curve()
except Exception as e:
    st.error(f"Yield curve load error: {e}")
    yield_curve, yield_df = None, pd.DataFrame()


# -----------------------------------------------------
# Sidebar: Underlying selection
# -----------------------------------------------------
st.sidebar.header("Underlying & Data")
search_query = st.sidebar.text_input("Search asset", value="")

search_results = pd.DataFrame()
if search_query:
    try:
        search_results = search_assets(search_query)
    except Exception as e:
        st.sidebar.error(f"Search failed: {e}")

if not search_results.empty:
    st.sidebar.dataframe(search_results[["Nom","Symbole","Type"]].head(10), height=200)
    chosen = st.sidebar.selectbox("Choose from results", list(search_results["Nom"]))
    ticker = search_results.loc[search_results["Nom"] == chosen, "Symbole"].iloc[0]
else:
    ticker = st.sidebar.text_input("Ticker", value="^FCHI")



# -----------------------------------------------------
# Main: underlying preview
# -----------------------------------------------------
underlying_spot = None

st.subheader("Underlying preview")

if ticker:
    try:
        data_preview = get_historic(ticker, "1y")
        if not data_preview.empty:
            underlying_spot = float(data_preview["Close"].iloc[-1])

            st.plotly_chart(
                px.area(data_preview, x="date", y="Close",
                        title=f"{ticker} — last 1y"),
                use_container_width=True
            )

            c1, c2, c3 = st.columns(3)
            c1.metric("Last close", f"{underlying_spot:.2f}")
            ret1m = 100*(data_preview['Close'].iloc[-1] /
                         data_preview['Close'].iloc[-22] - 1) if len(data_preview) > 22 else 0
            c2.metric("1M return", f"{ret1m:.2f}%")
            vol20 = data_preview['Close'].pct_change().std()*np.sqrt(252)
            c3.metric("Est. vol (20d)", f"{vol20:.2f}")

        else:
            st.info("No historical data available.")

    except Exception as e:
        st.error(f"Historic load error: {e}")

else:
    st.info("No ticker selected.")



# -----------------------------------------------------
# FUTURE PARAMETERS
# -----------------------------------------------------
st.markdown("---")
st.subheader("Future Contract Parameters")
#st.subheader("Contract Maturity")

# Calendar date picker
# maturity_date = st.date_input(
#     "Select maturity date",
#     value=date.today(),
#     min_value=date.today()
# )



spot = underlying_spot if underlying_spot is not None else 100.0

a1, a2, a3 = st.columns(3)

with a1:
    spot = st.number_input("Spot price (S₀)", value=float(spot), format="%.2f")
with a2:
    maturity_date = st.date_input(
    "Select maturity date",
    value=date.today(),
    min_value=date.today()
    )
    # Convert to year fraction
    today = date.today()
    days_to_maturity = (maturity_date - today).days
    maturity = days_to_maturity / 365.25
    st.caption(f"Time to maturity (years) {maturity:.4f}")
with a3:
    dividend_yield = st.number_input("Dividend yield (q)", value=0.0, step=0.01, format="%.2f")

# risk-free rate taken from the curve
try:
    rate = yield_curve.zero_rate(maturity)
except:
    rate = 0.02


st.metric("Rate used (from yield curve)", f"{rate:.2%}")



# -----------------------------------------------------
# PRICE FUTURE
# -----------------------------------------------------
st.markdown("---")
st.subheader("📈 Theoretical Future Price")

future = EquityFuture(
    spot=spot, 
    rate=rate,
    dividend_yield=dividend_yield,
    maturity=maturity
)

future_price = future.price()
st.success(f"F₀ = {future_price:.2f}")

st.caption("Formula:  **F₀ = S₀ × exp((r − q) × T)**")



# -----------------------------------------------------
# LONG / SHORT VALUE OVER TIME
# -----------------------------------------------------
st.markdown("---")
st.subheader("📊 Possible Long / Short Future value at specific time")

time = st.date_input("Select valuation date",
                    value=maturity_date,
                    min_value=date.today(),
                    max_value=maturity_date
                    )

days_to_time = (time - today).days
t = maturity
st.caption(f"days to valuation time {t:.4f}")
S_min = spot * 0.5
S_max = spot * 1.5
S_values = np.linspace(S_min, S_max, 200)
long_values = np.array([
    future.long_value(t, s, yield_curve) for s in S_values
])
short_values = -long_values

df_val = pd.DataFrame({
    "Spot values": S_values,
    "Long Value": long_values,
    "Short Value": short_values
})

fig = go.Figure()
fig.add_trace(go.Scatter(x=df_val["Spot values"], y=df_val["Long Value"],
                         mode="lines", name="Long"))
fig.add_trace(go.Scatter(x=df_val["Spot values"], y=df_val["Short Value"],
                         mode="lines", name="Short"))

fig.update_layout(template="plotly_white", height=380)
st.plotly_chart(fig, use_container_width=True)



# -----------------------------------------------------
# PAYOFF CURVE AT MATURITY
# -----------------------------------------------------
# st.markdown("---")
# st.subheader("💰 Payoff at Maturity")

# S_range = np.linspace(spot * 0.7, spot * 1.3, 200)
# payoff = S_range - future_price

# df_payoff = pd.DataFrame({"Underlying Price": S_range, "Payoff": payoff})

# fig2 = go.Figure()
# fig2.add_trace(go.Scatter(
#     x=df_payoff["Underlying Price"],
#     y=df_payoff["Payoff"],
#     mode="lines",
#     name="Payoff"
# ))

# fig2.update_layout(template="plotly_white", height=350)
# st.plotly_chart(fig2, use_container_width=True)

st.info("The long value of the contract is:  \n\n**value = S(t) − F₀exp(-(r-q)(T-t))**")
