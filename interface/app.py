import streamlit as st
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


def main():
    st.title("European Option Pricer")

    st.header("Inputs")

    spot = st.number_input("Spot price", 0.0, value=100.0)
    strike = st.number_input("Strike", 0.0, value=100.0)
    maturity = st.number_input("Maturity (years)", 0.0, value=1.0)
    vol = st.number_input("Volatility", 0.0, value=0.2)
    rate = st.number_input("Interest rate", 0.0, value=0.02)

    model = BlackScholesModel(spot, rate)
    option = EuropeanCall(strike=strike, maturity=maturity)

    price = model.call_price(option, vol)

    st.header("Results")
    st.write(f"Price = **{price:.4f}**")




if __name__ == "__main__":
    main()