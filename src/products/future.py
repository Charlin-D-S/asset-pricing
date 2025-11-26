import math

class EquityFuture:
    """
    A class to model the pricing of an equity or financial future using the cost-of-carry model.

    This class calculates the theoretical price of a future contract based on the spot price,
    risk-free interest rate, dividend yield, and time to maturity.
    """

    def __init__(self, spot, rate, dividend_yield=0.0, maturity=1):
        """
        Initialize the EquityFuture class with the underlying asset's parameters.

        Parameters
        ----------
        spot : float
            Current spot price of the underlying asset.
        rate : float
            Risk-free interest rate (annualized).
        dividend_yield : float, optional
            Continuous dividend yield (annualized). Default is 0.0.
        maturity : float, optional
            Time to expiration in years. Default is 1.
        """
        self.spot = spot
        self.q = dividend_yield
        self.rate = rate
        self.maturity = maturity

    def price(self):
        """
        Calculate the theoretical price of the future contract using the cost-of-carry model.

        The formula used is:
        F0 = S0 * exp((r - q) * T)

        Returns
        -------
        float
            Theoretical price of the future contract.
        """
        dq = math.exp((self.rate - self.q) * self.maturity)
        return self.spot * dq

    #@classmethod
    def long_value(self, t, St, curve):
        """
        Calculate the value of a long position in the future contract at time t.

        The formula used is:
        Vt = St * exp(-q * (T-t)) - F0 * DF(T-t)

        Parameters
        ----------
        t : float
            Current time in years.
        St : float
            Spot price of the underlying asset at time t.
        curve : object
            A YieldCurve object with a method `discount_factor(T)` to compute the discount factor
            for a given time to maturity T.

        Returns
        -------
        float
            Value of the long position in the future contract at time t.
        """
        q = self.q
        T = self.maturity
        F = self.price()
        df = curve.discount_factor(T - t)
        Vt = St * math.exp(-q * (T - t)) - F * df
        return Vt
