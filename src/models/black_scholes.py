import math
from math import log, sqrt, exp
from scipy.stats import norm

class BlackScholesModel:
    """
    Black-Scholes model for European options.
    """

    def __init__(self, spot, rate, dividend_yield=0.0,repo_rate=0.0):
        self.spot = spot
        self.rate = rate
        self.q = dividend_yield
        self.repo_rate = repo_rate

    def d1(self, strike, maturity, vol):
        return (log(self.spot / strike) + (self.rate - self.q - self.repo_rate + 0.5 * vol**2) * maturity) \
               / (vol * sqrt(maturity))

    def d2(self, strike, maturity, vol):
        return self.d1(strike, maturity, vol) - vol * sqrt(maturity)

    def call_price(self, option, vol):
        d1 = self.d1(option.strike, option.maturity, vol)
        d2 = d1 - vol * sqrt(option.maturity)

        return (self.spot * norm.cdf(d1)
               - option.strike * exp(-self.rate * option.maturity) * norm.cdf(d2))

    def put_price(self, option, vol):
        d1 = self.d1(option.strike, option.maturity, vol)
        d2 = d1 - vol * sqrt(option.maturity)

        return (option.strike * exp(-self.rate * option.maturity) * norm.cdf(-d2)
               - self.spot * norm.cdf(-d1))

    def call_delta(self, option, vol):
        d1 = self.d1(option.strike, option.maturity, vol)
        return norm.cdf(d1)#exp(-self.q * option.maturity) * 

    def put_delta(self, option, vol):
        d1 = self.d1(option.strike, option.maturity, vol)
        return (norm.cdf(d1) - 1)#exp(-self.q * option.maturity) * 

    def gamma(self, option, vol):
        d1 = self.d1(option.strike, option.maturity, vol)
        return (norm.pdf(d1)) / (self.spot * vol * sqrt(option.maturity))

    def vega(self, option, vol):
        d1 = self.d1(option.strike, option.maturity, vol)
        return self.spot * norm.pdf(d1) * sqrt(option.maturity)
