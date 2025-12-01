import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional

# ensure src is importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

# local project imports (adapt paths if your project differs)
from data_loader.equity_loader import EquityLoader
from data_loader.yield_curve_loader import YieldCurveLoader
from curves.yield_curve import YieldCurve
from models.black_scholes import BlackScholesModel
from models.monte_carlo import MonteCarloPricer
from products.option import EuropeanCall, EuropeanPut

# -----------------------------------------------------
# Page config
# -----------------------------------------------------
st.set_page_config(page_title="Option Pricer", page_icon="📘", layout="wide")
st.title("🧮 Option Pricer — Black–Scholes & Monte Carlo")
st.markdown("Price European options and compute Greeks. Use market implied vol or override manually.")

# -----------------------------------------------------
# Helpers / cached loaders
# -----------------------------------------------------
@st.cache_resource
def get_black_scholes_model(spot,rate,vol,repo_rate=0,dividend_yield=0):
    return BlackScholesModel(spot=spot,rate=rate,vol=vol,repo_rate=repo_rate,dividend_yield=dividend_yield)

@st.cache_resource
def get_monte_carlo_model(spot,rate,vol,dividend_yield=0):
    return MonteCarloPricer(spot=spot,rate=rate,vol=vol,dividend_yield=dividend_yield)

@st.cache_data
def load_yield_curve():
    # Use your loader that returns a YieldCurve object
    # If you have a loader class, adapt: YieldCurve.from_csv() or YieldCurveLoader().load_latest()
    try:
        yc = YieldCurve.from_csv()
    except Exception:
        raise RuntimeError("Could not load yield curve. Check YieldCurve.from_csv() or YieldCurveLoader.")
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

@st.cache_data
def get_market_iv(ticker: str, is_call: bool, maturity: float) -> Optional[float]:
    try:
        iv = EquityLoader().get_implied_volatility(ticker_symbol=ticker, call=is_call, T=maturity)
        return float(iv)
    except Exception:
        return None

# -----------------------------------------------------
# Load yield curve once
# -----------------------------------------------------
try:
    yield_curve, yield_df = load_yield_curve()
except Exception as e:
    st.error(f"Yield curve load error: {e}")
    yield_curve, yield_df = None, pd.DataFrame({"maturity":[], "rate": []})

# -----------------------------------------------------
# Sidebar: Underlying selection & navigation
# -----------------------------------------------------
st.sidebar.header("Underlying & Data")
search_query = st.sidebar.text_input("Search asset (name or ticker)", value="")

search_results = pd.DataFrame()
if search_query:
    try:
        search_results = search_assets(search_query)
    except Exception as e:
        st.sidebar.error(f"Search failed: {e}")

if not search_results.empty:
    st.sidebar.markdown("**Search results**")
    # display small table
    st.sidebar.dataframe(search_results[["Nom","Symbole","Type"]].head(8), height=200)
    chosen_name = st.sidebar.selectbox("Choose from results", options=list(search_results["Nom"]))
    ticker = search_results.loc[search_results["Nom"] == chosen_name, "Symbole"].values[0]
else:
    ticker = st.sidebar.text_input("Or enter ticker directly (e.g. AAPL, ^FCHI):", value="^FCHI")

# -----------------------------------------------------
# Main layout: left for inputs, right for charts & results
# -----------------------------------------------------



underlying_spot = None
data_preview = get_historic(ticker, period="1y")
if ticker:
    try:
        if not data_preview.empty:
            underlying_spot = float(data_preview["Close"].iloc[-1])
    except Exception:
        underlying_spot = None

# display spot (or let user fill)
#spot = st.number_input("Spot price (S₀)", value=float(underlying_spot) if underlying_spot is not None else 100.0, format="%.2f")

st.subheader("Underlying preview")

if ticker:
    try:
        if not data_preview.empty:
            # price area chart
            st.plotly_chart(
                px.area(data_preview, x="date", y="Close", title=f"{ticker} — last 1y"),
                use_container_width=True
            )
            # show latest quotes
            c1, c2, c3,c4 = st.columns(4)
            c1.metric("Last close", f"{data_preview['Close'].iloc[-1]:.2f}")
            ret_1m = 100*(data_preview['Close'].iloc[-1] / data_preview['Close'].iloc[-22] - 1) if len(data_preview) > 22 else 0.0
            c2.metric("1M return", f"{ret_1m:.2f}%")
            vol20 = data_preview['Close'].pct_change().std()*np.sqrt(252)
            c3.metric("Est. vol (20d)", f"{vol20:.2f}")
            #c4.metric("Implied Vol", f"{vol:.2f}")
        else:
            st.info("No historical data available for this ticker.")
    except Exception as e:
        st.error(f"Historic load error: {e}")
else:
    st.info("No ticker selected. Enter a ticker on the left or use search.")

##################################
st.markdown("---")
st.subheader("Option Parameters")
option_type = st.radio("Option type", ["Call", "Put"])
spot = underlying_spot#st.number_input("Spot price (S₀)", value=float(underlying_spot) if underlying_spot is not None else 100.0, format="%.2f")

a1, a2, a3 = st.columns(3)
with a1:
    strike = st.number_input("Strike (K)", value=float(spot), format="%.2f")
with a2:
    maturity = st.number_input("Maturity (years)", min_value=0.01, value=0.25, format="%.2f")
with a3:
    dividend_yield = st.number_input("Dividend yield (q)", value=0.0, format="%.2f")

if ticker:
    vol = get_market_iv(ticker, is_call=(option_type=="Call"), maturity=maturity)
c4.metric("Implied Vol", f"{vol:.2f}")
# interest rate from yield curve (zero rate at maturity). fallback to manual entry
if yield_curve is not None:
    try:
        r_guess = yield_curve.zero_rate(t=maturity)
    except Exception:
        r_guess = 0.01
else:
    r_guess = 0.01
st.markdown("---")
st.subheader("Pricing Model")
model_choice = st.selectbox("Model", ["Black-Scholes (analytical)", "Monte Carlo (simulation)"])
rate = r_guess#st.number_input("Risk-free rate (%)", value=float(r_guess), format="%.2f")

compute = st.button("Compute Price & Greeks")


    # st.markdown("---")
    # st.subheader("Yield curve (short view)")
    # if not yield_df.empty:
    #     st.line_chart(yield_df, x="maturity", y="rate", height=220)
    # else:
    #     st.info("Yield curve not loaded.")

# -----------------------------------------------------
# Compute pricing when user clicks
# -----------------------------------------------------
option = EuropeanCall(strike=strike, maturity=maturity) if option_type == "Call" else EuropeanPut(strike=strike, maturity=maturity)

if compute:
    st.info("Pricing... this may take a few seconds for Monte Carlo.")
    # build option product
    # instantiate models
    try:
        if model_choice.startswith("Black"):
            bs = get_black_scholes_model(spot=spot, rate=rate/100, dividend_yield=dividend_yield,vol=vol/100)
            # try prices and greeks using common names
            # support different method names
            price = bs.price(option)
    
            # Greeks
            delta = bs.delta(option)
            gamma = bs.gamma(option)
            vega = bs.vega(option)
            result = {
                "price": float(price),
                "delta": float(delta) if delta is not None else None,
                "gamma": float(gamma) if gamma is not None else None,
                "vega": float(vega) if vega is not None else None,
                "model": "Black–Scholes"
            }

            st.success(f"Price (BS): {result['price']:.2f}")

            # show greeks
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Delta", f"{result['delta']:.2f}" if result["delta"] is not None else "N/A")
            col2.metric("Gamma", f"{result['gamma']:.2f}" if result["gamma"] is not None else "N/A")
            col3.metric("Vega", f"{result['vega']:.2f}" if result["vega"] is not None else "N/A")
            col4.metric("Risk free rate used", f"{rate/100:.2%}")
            col5.metric("Implied volatility used", f"{vol/100:.2%}")

        else:
            # Monte Carlo
            mc = get_monte_carlo_model(spot=spot, rate=rate/100, vol=vol/100, dividend_yield=dividend_yield)
            price = mc.price(option=option)
            delta = mc.delta(option=option)
            gamma = mc.gamma(option=option)
            vega = mc.vega(option=option)
            st.success(f"Price (MC): {price:.2f}")
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Delta (est.)", f"{delta:.2f}")
            c2.metric("Gamma (est.)", f"{gamma:.2f}")
            c3.metric("Vega (est.)", f"{vega:.2f}")
            c4.metric("Risk free rate used(%)", f"{rate/100:.2%}")
            c5.metric("Implied volatility used", f"{vol/100:.2%}")

    except Exception as e:
        st.error(f"Pricing error: {e}")

st.markdown("---")
# ------------------------------------------------------------
# 📈 Payoff Curve
# ------------------------------------------------------------
st.subheader("Payoff Curve at Maturity")

# Generate underlying price range for the payoff curve
S_min = max(0, spot * 0.5)
S_max = spot * 1.5
S_values = np.linspace(S_min, S_max, 200)

# Compute payoff depending on option type
payoff_values = np.array([option.payoff(S) for S in S_values])

# Create DataFrame for Streamlit chart
payoff_df = pd.DataFrame({
    "Underlying Price": S_values,
    "Payoff": payoff_values
})

st.line_chart(payoff_df, x="Underlying Price", y="Payoff")
