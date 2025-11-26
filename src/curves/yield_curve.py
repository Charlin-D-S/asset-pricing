import math
import pandas as pd
class YieldCurve:
    """
    Zero-coupon yield curve with linear interpolation.
    """
    def __init__(self, maturities, zero_rates):
        """
        Parameters
        ----------
        maturities : list of float
            Maturities in years (e.g. [0.5, 1.0, 2.0]).
        zero_rates : list of float
            Corresponding annualized zero-coupon rates.
        """
        if len(maturities) != len(zero_rates):
            raise ValueError("Maturities and rates must have same length.")

        self.maturities = maturities
        self.zero_rates = zero_rates

    def zero_rate(self, t):
        """
        Returns the zero-coupon rate for maturity t using linear interpolation.
        """
        # If exact maturity exists
        if t in self.maturities:
            return self.zero_rates[self.maturities.index(t)]

        # If t is outside the curve range → flat extrapolation
        if t <= self.maturities[0]:
            return self.zero_rates[0]
        if t >= self.maturities[-1]:
            return self.zero_rates[-1]

        # Otherwise: find interval for t
        for i in range(len(self.maturities) - 1):
            t1, t2 = self.maturities[i], self.maturities[i + 1]
            r1, r2 = self.zero_rates[i], self.zero_rates[i + 1]

            if t1 <= t <= t2:
                # Linear interpolation
                w = (t - t1) / (t2 - t1)
                return r1 + w * (r2 - r1)

    def discount_factor(self, t):
        """
        Returns DF(t) = exp(-r(t) * t)
        """
        r = self.zero_rate(t)
        return math.exp(-r * t)


    @classmethod
    def from_csv(cls, directory = '../data/yield_curve.csv'):
        """
        Build a YieldCurve from csv data.
        """
        df = pd.read_csv(directory)
        return cls(maturities=list(df.maturity), zero_rates=list(df.rate))

