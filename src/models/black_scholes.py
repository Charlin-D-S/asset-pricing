import math
from math import log, sqrt, exp
from scipy.stats import norm
from products.option import Option, EuropeanCall, EuropeanPut

class BlackScholesModel:
    """
    Black-Scholes model for European options.
    """

    def __init__(self, spot, rate, vol=1.0, dividend_yield=0.0,repo_rate=0.0):
        self.spot = spot
        self.rate = rate
        self.q = dividend_yield
        self.repo_rate = repo_rate
        self.vol = vol

    def d1(self, strike, maturity):
        return (log(self.spot / strike) + (self.rate - self.q - self.repo_rate + 0.5 * self.vol**2) * maturity) \
               / (self.vol * sqrt(maturity))

    def d2(self, strike, maturity):
        return self.d1(strike, maturity, self.vol) - self.vol * sqrt(maturity)

    def price(self, option:Option):
        if isinstance(option, EuropeanCall):
            return self.call_price(option)
        if isinstance(option, EuropeanPut):
            return self.put_price(option)
        
    def delta(self, option:Option):
        if isinstance(option, EuropeanCall):
            return self.call_delta(option)
        if isinstance(option, EuropeanPut):
            return self.put_delta(option)

    def call_price(self, option:Option):
        d1 = self.d1(option.strike, option.maturity)
        d2 = d1 - self.vol * sqrt(option.maturity)

        return (self.spot * norm.cdf(d1)
               - option.strike * exp(-self.rate * option.maturity) * norm.cdf(d2))

    def put_price(self, option:Option):
        d1 = self.d1(option.strike, option.maturity)
        d2 = d1 - self.vol * sqrt(option.maturity)

        return (option.strike * exp(-self.rate * option.maturity) * norm.cdf(-d2)
               - self.spot * norm.cdf(-d1))

    def call_delta(self, option:Option):
        d1 = self.d1(option.strike, option.maturity)
        return norm.cdf(d1)#exp(-self.q * option.maturity) * 

    def put_delta(self, option:Option):
        d1 = self.d1(option.strike, option.maturity)
        return (norm.cdf(d1) - 1)#exp(-self.q * option.maturity) * 

    def gamma(self, option:Option):
        d1 = self.d1(option.strike, option.maturity)
        return (norm.pdf(d1)) / (self.spot * self.vol * sqrt(option.maturity))

    def vega(self, option:Option):
        d1 = self.d1(option.strike, option.maturity)
        return self.spot * norm.pdf(d1) * sqrt(option.maturity)
