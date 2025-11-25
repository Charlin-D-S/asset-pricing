import math

class EquityFuture:
    """
    Equity or financial future priced using cost-of-carry model.
    """
    def __init__(self, spot,rate, dividend_yield, maturity):
        """
        Parameters
        ----------
        spot : float
            Current spot price of the underlying asset.
        rate : float
            Risk-free interest rate (annualized).
        dividend_yield : float
            Continuous dividend yield (annualized).
        maturity : float
            Time to expiration in years.
        """
        self.spot = spot
        self.q = dividend_yield
        self.rate = rate
        self.maturity = maturity

    def price(self):
        """
        Returns F0 = S0 * exp((r - q) * T)
        """
        dq = math.exp((self.rate-self.q)*self.maturity)
        return self.spot*dq

