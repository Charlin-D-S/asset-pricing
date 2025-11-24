class Option:
    """
    Generic option base class.
    """
    def __init__(self, strike, maturity):
        self.strike = strike
        self.maturity = maturity


class EuropeanCall(Option):
    """
    European Call Option.
    """
    def payoff(self, S):
        return max(S - self.strike, 0)


class EuropeanPut(Option):
    """
    European Put Option.
    """
    def payoff(self, S):
        return max(self.strike - S, 0)
