import streamlit as st
import pandas as pd
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
def get_black_scholes_model(spot,rate,vol,repo_rate=0,dividend_yield=0):
    return BlackScholesModel(spot=spot,rate=rate,vol=vol,repo_rate=repo_rate,dividend_yield=dividend_yield)

@st.cache_resource
def get_monte_carlo_model(spot,rate,vol,dividend_yield=0):
    return MonteCarloPricer(spot=spot,rate=rate,vol=vol,dividend_yield=dividend_yield)

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

@st.cache_data
def get_volatility(ticker,text,maturity):
    b = text=='Call'
    return EquityLoader().get_implied_volatility(ticker_symbol=ticker,call=b,T=maturity)


@st.cache_data
def get_historic(ticker,period='2y'):
    data = EquityLoader().get_historic(ticker=ticker,period=period)
    data.columns = [ col[0] for col in data.columns.values]
    data['date'] = pd.to_datetime(data.index)
    return data[['date','Close','High','Low','Open']]
# ------------------------------------------------------------
# PAGE HEADER
# ------------------------------------------------------------
st.title("📈 Asset Pricing Application")
st.write("Interactive pricing of bonds and derivatives with live market data.")


# ------------------------------------------------------------
# 1. PRODUCT SELECTION
# ------------------------------------------------------------
product_type = st.selectbox(
    "Select a product type:",
    ["Derivative", "Bond"]
)


# ============================================================
#                 SECTION A — DERIVATIVES
# ============================================================
if product_type == "Derivative":

    st.header("🔹 Derivative Pricing")

    # -------------------------------
    # 2A. Select Underlying
    # -------------------------------
    ticker = st.selectbox(
        "Select underlying asset:",
        ["RNO.PA", "MCP.XD", "^FCHI", "LVC.PA", "CA10S.PA", "EURUSD=X"]
    )

    # -------------------------------
    # 3A. Download Market Data
    # -------------------------------
    st.subheader("Underlying Historical Price")

    data = get_historic(ticker=ticker,period='1y')
    # st.write("Colonnes du DataFrame :", data.columns.tolist())
    # st.dataframe(data.head())
    if not data.empty:
        st.line_chart(data = data,y='Close',x='date')
    else:
        st.warning("No market data available.")

    # -------------------------------
    # 4A. Option Parameters
    # -------------------------------
    st.subheader("Option Parameters")

    col1, col2, col3 = st.columns(3)

    strike = col1.number_input("Strike", value=100.0)
    maturity = col2.number_input("Maturity (years)", value=1.0)
    # vol = col3.number_input("Volatility", value=0.20)
    # rate = st.number_input("Interest rate", value=0.02)

    option_type = st.radio("Option type", ["Call", "Put"])
    st.write("Spot price:",data["Close"][-1])
    # Create option object
    if option_type == "Call":
        option = EuropeanCall(strike=strike, maturity=maturity)
    else:
        option = EuropeanPut(strike=strike, maturity=maturity)

    # -------------------------------
    # 5A. Pricing model selection
    # -------------------------------
    model_choice = st.selectbox("Pricing model", ["Black-Scholes", "Monte Carlo"])
    vol = get_volatility(ticker=ticker,text=option_type,maturity=maturity)
    rate=yield_curve.zero_rate(t=maturity)
    # -------------------------------
    # 6A. Pricing & Greeks
    # -------------------------------
    if st.button("Compute Price"):

        if model_choice == "Black-Scholes":
            model = get_black_scholes_model(spot=data["Close"][-1], rate=rate,vol=vol)
            price = model.price(option)
            delta = model.delta(option)
            gamma = model.gamma(option)
            vega = model.vega(option)

        else:  # Monte Carlo
            mc = get_monte_carlo_model(spot=data["Close"][-1], rate=rate,vol=vol)

            price = mc.price(option=option)
            delta = mc.delta(option=option)
            gamma = mc.gamma(option=option)
            vega = mc.vega(option=option)

        # -------------------------------
        # 7A. Display results
        # -------------------------------
        st.subheader("📊 Results")
        st.write(f"**Price:** {price:.4f}")
        st.write(f"Delta: {delta:.4f}")
        st.write(f"Gamma: {gamma:.4f}")
        st.write(f"Vega: {vega:.4f}")


# ============================================================
#                 SECTION B — BONDS
# ============================================================
else:
    st.header("🔹 Bond Pricing")

    # -------------------------------
    # 2B. Yield curve loading
    # -------------------------------
    st.subheader("Euro Area Risk-Free Yield Curve (ECB)")

    #if st.button("Load ECB curve"):
    st.line_chart(x='maturity',y='rate',data = yield_curve_df)

    # -------------------------------
    # 3B. Bond parameters
    # -------------------------------
    st.subheader("Bond Parameters")

    col1, col2, col3 = st.columns(3)
    nominal = col1.number_input("Nominal (£)", value=100.0)
    coupon_rate = col2.number_input("Coupon rate (%)", value=2.0)
    maturity = col3.number_input("Maturity (years)", value=5.0)

    freq = st.selectbox("Coupon frequency", ["Annual", "Semiannual"])
    frequency = 1 if freq=="Annual" else 2
    # -------------------------------
    # 4B. Pricing
    # -------------------------------
    if st.button("Price Bond"):
        bond = get_bond(nominal, coupon_rate, maturity, frequency)

        price = bond.price(yield_curve)
        duration = bond.duration(yield_curve)
        convexity = bond.convexity(yield_curve)

        # -------------------------------
        # 5B. Display results
        # -------------------------------
        st.subheader("📊 Bond Valuation")
        st.write(f"**Price:** {price:.4f}")
        st.write(f"Duration:** {duration:.4f}")
        st.write(f"Convexity:** {convexity:.4f}")


# def main():
#     st.title("European Option Pricer")

#     st.header("Inputs")

#     spot = st.number_input("Spot price", 0.0, value=100.0)
#     strike = st.number_input("Strike", 0.0, value=100.0)
#     maturity = st.number_input("Maturity (years)", 0.0, value=1.0)
#     vol = st.number_input("Volatility", 0.0, value=0.2)
#     rate = st.number_input("Interest rate", 0.0, value=0.02)

#     model = BlackScholesModel(spot, rate)
#     option = EuropeanCall(strike=strike, maturity=maturity)

#     price = model.call_price(option, vol)

#     st.header("Results")
#     st.write(f"Price = **{price:.4f}**")




# if __name__ == "__main__":
#     main()