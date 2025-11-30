from curves.yield_curve import YieldCurve
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

    def pv_fixed_leg(self, curve:YieldCurve,t=0):
        """
        Computes PV at `t` of the fixed leg using the zero-coupon curve.
        """
        pv = 0.0
        for i, time in enumerate(self.payment_times):
            if time-t>=0:
                if i == 0:
                    dt = time
                else:
                    dt = time - self.payment_times[i-1]

                df = curve.discount_factor(time-t)
                pv += dt * df

        return pv*self.fixed_rate*self.notional

    def pv_floating_leg(self, curve:YieldCurve,t=0):
        """
        Floating leg PV = Notional * (DF(t0) - DF(tN))
        """
        times = [time-t for time in self.payment_times if time-t>=0]
        t0 = times[0]
        tN = times[-1]

        df0 = curve.discount_factor(t0)  # = 1
        dfN = curve.discount_factor(tN)

        return self.notional * (df0 - dfN)
    
    def swap_rate(self,curve:YieldCurve,t=0):
        """
        Swap rate, rate that equalize fixed leg and floating leg.
        """
        times = [time-t for time in self.payment_times if time-t>=0]
        df0 = curve.discount_factor(times[0])
        dfT = curve.discount_factor(times[-1])
        pv = self.pv_fixed_leg(curve)/self.fixed_rate/self.notional
        return (df0 - dfT)/pv    


    def price(self, curve:YieldCurve,t=0):
        """
        Swap value (payer fixed, receiver float).
        """
        pv_fix = self.pv_fixed_leg(curve,t=t)
        pv_flt = self.pv_floating_leg(curve,t=t)

        return pv_flt - pv_fix
    
