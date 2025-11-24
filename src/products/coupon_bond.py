class CouponBond:
    """
    Plain vanilla coupon bond.
    """
    def __init__(self, 
                 nominal: float=1,
                 coupon_rate: float=0,
                 maturity: float=1,
                 payment_frequency: int = 1):
        """
        Parameters
        ----------
        nominal : float
            Face value of the bond.
        coupon_rate : float
            Annual coupon rate (e.g., 0.05 for 5%).
        maturity : float
            Time to maturity in years.
        payment_frequency : int
            Number of coupon payments per year (1, 2, 4...).
        """
        self.nominal = nominal
        self.coupon_rate = coupon_rate
        self.maturity = maturity
        self.freq = payment_frequency

    def cashflows(self):
        """
        Returns a list of (time, amount) for each coupon and the principal.
        """
        dt = 1 / self.freq #length of time between two coupon payments in year
        n_payments = int(self.maturity * self.freq)

        flows = []
        coupon_amount = self.nominal * self.coupon_rate * dt

        # coupon payments
        for i in range(1, n_payments + 1):
            t = i * dt
            amount = coupon_amount
            flows.append((t, amount))

        # add final principal repayment
        flows[-1] = (flows[-1][0], flows[-1][1] + self.nominal)

        return flows

    def price(self, curve):
        """
        Computes the present value of the bond using a yield curve object.
        
        The curve object must implement:
            discount_factor(t)
        """
        pv = 0.0
        
        for (t, cf) in self.cashflows():
            df = curve.discount_factor(t)
            pv += cf * df
        
        return pv
