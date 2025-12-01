import math
import pandas as pd
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(BASE_DIR, "data", "yield_curve.csv")
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
        Returns the zero-coupon rate for maturity t in years using linear interpolation.
        """
        # If exact maturity exists
        if t in self.maturities:
            return self.zero_rates[self.maturities.index(t)]

        # If t is outside the curve range → flat extrapolation
        if t <= self.maturities[0]:
            return self.zero_rates[0]*t/self.maturities[0]
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

    def move_rate(self,dr=0):
        """
        move the curve rate by doing a translation 
        
        :param dr: the number to remove to each zero rate
        """
        maturities=[]
        zero_rates=[]

        for m,r in zip(self.maturities,self.zero_rates):
            if r-dr>=0:
                maturities.append(m)
                zero_rates.append(r-dr)

        return YieldCurve(maturities=maturities,zero_rates=zero_rates)

    def move_time(self,dt=0):
        """
        move the curve rate by doing a time translation 
        
        :param dt: the number of years to remove to each maturity
        """
        max = max(self.maturities)
        maturities=[]
        zero_rates=[]

        for t in self.maturities:
            if t-dt>=0 and t-dt<max:
                maturities.append(t-dt)
                zero_rates.append(self.zero_rate(t-dt))

        return YieldCurve(maturities=maturities,zero_rates=zero_rates)

    @classmethod
    def from_csv(cls, directory = DATA_PATH):
        """
        Build a YieldCurve from csv data.
        """
        df = pd.read_csv(directory)
        return cls(maturities=list(df.maturity), zero_rates=list(df.rate/100))

