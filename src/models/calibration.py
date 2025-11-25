import numpy as np
from scipy.optimize import brentq

class ImpliedVolatilitySolver:
    """
    Computes implied volatility for European options using Brent's method.
    """

    def __init__(self, model):
        self.model = model

    def implied_vol_call(self, option, market_price, eps=1e-8):
        """
        Compute implied volatility for European Call using Brent.
        """

        def objective(vol):
            return self.model.call_price(option, vol) - market_price

        # Bounds for vol (0.0001 to 500% vol)
        vol_low = 1e-6
        vol_high = 5.0

        try:
            return brentq(objective, vol_low, vol_high, xtol=eps)
        except ValueError:
            return np.nan   # No solution

    def implied_vol_put(self, option, market_price, eps=1e-8):
        """
        Compute implied volatility for European Put using Brent.
        """

        def objective(vol):
            return self.model.put_price(option, vol) - market_price

        vol_low = 1e-6
        vol_high = 5.0

        try:
            return brentq(objective, vol_low, vol_high, xtol=eps)
        except ValueError:
            return np.nan
