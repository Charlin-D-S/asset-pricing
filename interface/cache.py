# dashboard_cache.py
import streamlit as st
import os
#from concurrent.futures import ThreadPoolExecutor
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

# @st.cache_data
# def get_logo():
#     current_dir = os.path.dirname(os.path.abspath(__file__))
#     parent_dir = os.path.dirname(current_dir)
#     logo_path = os.path.join(parent_dir, "images", "logo_athling.jpg")
#     return Image.open(logo_path)
# logo = get_logo()

@st.cache_resource
def equity_loader():
    return EquityLoader


@st.cache_data
def curve():
    return YieldCurve.from_csv()
yield_curve = curve()

@st.cache_data
def get_historic(ticket):
    return YieldCurve.from_csv()




@st.cache_data
def charger_donnees(annees, mois, siren, secteurs):
    return dao.charger_donnees(annees, mois, siren, secteurs)