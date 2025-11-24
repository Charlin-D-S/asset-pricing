import math

class EquityFuture:
    """
    Equity or financial future priced using cost-of-carry model.
    """
    def __init__(self, spot, dividend_yield, maturity):
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
        self.maturity = maturity

    def price(self,curve):
        """
        Returns F0 = S0 * exp((r - q) * T)
        """
        df = curve.discount_factor(self.maturity)
        dq = math.exp(-self.q*self.maturity)
        return self.spot*dq/df

