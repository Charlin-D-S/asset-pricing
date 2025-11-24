class InterestRateSwap:
    """
    Plain vanilla interest rate swap:
    - Pay fixed
    - Receive floating
    """

    def __init__(self,
                 notional: float,
                 fixed_rate: float,
                 payment_times: list):
        """
        Parameters
        ----------
        notional : float
            Swap notional.
        fixed_rate : float
            Annual fixed rate K of the swap.
        payment_times : list of float
            Payment schedule in years (e.g. [0.5, 1.0, 1.5, 2.0]).
        """
        self.notional = notional
        self.fixed_rate = fixed_rate
        self.payment_times = payment_times

    def pv_fixed_leg(self, curve):
        """
        Computes PV of the fixed leg using the zero-coupon curve.
        """
        pv = 0.0
        for i, t in enumerate(self.payment_times):
            if i == 0:
                dt = t
            else:
                dt = t - self.payment_times[i-1]

            df = curve.discount_factor(t)
            pv += dt * df

        return pv*self.fixed_rate*self.notional

    def pv_floating_leg(self, curve):
        """
        Floating leg PV = Notional * (DF(t0) - DF(tN))
        """
        t0 = 0
        tN = self.payment_times[-1]

        df0 = curve.discount_factor(t0)  # = 1
        dfN = curve.discount_factor(tN)

        return self.notional * (df0 - dfN)

    def price(self, curve):
        """
        Swap value (payer fixed, receiver float).
        """
        pv_fix = self.pv_fixed_leg(curve)
        pv_flt = self.pv_floating_leg(curve)

        return pv_flt - pv_fix
