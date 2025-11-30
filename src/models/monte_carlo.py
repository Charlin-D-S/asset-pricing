import numpy as np
from products.option import EuropeanCall, EuropeanPut, Option

class MonteCarloPricer:
    r"""
    Monte Carlo pricer for European options under the Black–Scholes model.

    The underlying follows the stochastic differential equation (SDE):

    .. math::
        dS_t = S_t \left( (r - q)\,dt + \sigma\,dW_t \right)

    where  
    - \( S_t \) : spot price  
    - \( r \) : risk-free interest rate  
    - \( q \) : dividend yield (or repo rate for futures)  
    - \( \sigma \) : volatility  

    Exact solution:

    .. math::
        S_T = S_0 \exp\left[\left(r - q - \frac{1}{2}\sigma^2\right)T
                + \sigma\sqrt{T}Z \right]

    European call payoff:

    .. math::
        \text{Payoff} = \max(S_T - K, 0)

    Monte Carlo price:

    .. math::
        C = e^{-rT} \mathbb{E}[\max(S_T - K, 0)]
    """

    def __init__(self, spot: float, rate: float, dividend_yield: float = 0.0,vol = 1.0,n_sims=1_000):
        self.spot = spot
        self.r = rate
        self.q = dividend_yield
        self.vol = vol
        self.n_sims = n_sims

    def simulate_terminal_price(self, option:Option):
        """Simulate S_T using the exact solution."""
        z = np.random.normal(size=self.n_sims)
        drift = (self.r - self.q - 0.5 * self.vol**2) * option.maturity
        diffusion = self.vol * np.sqrt(option.maturity) * z
        return self.spot * np.exp(drift + diffusion)

    def price(self, option:Option):
        """Monte Carlo price of a European option."""
        ST = self.simulate_terminal_price(option = option)
        vec_f = np.vectorize(option.payoff)
        payoffs = vec_f(ST)
        return np.exp(-self.r * option.maturity) * payoffs.mean()

    # ---------- Greeks ----------
    def delta(self, option:Option, eps=1e-4):
        price_up = self.price(option.strike, spot=self.spot + eps)
        price_down = self.price(option.strike, spot=self.spot - eps)
        return (price_up - price_down) / (2 * eps)

    def gamma(self, option:Option, eps=1e-4):
        price_up = self.price(option.strike, spot=self.spot + eps)
        price_mid = self.price(option.strike, spot=self.spot)
        price_down = self.price(option.strike, spot=self.spot - eps)
        return (price_up - 2 * price_mid + price_down) / (eps ** 2)

    def vega(self, option:Option, eps=1e-4):
        price_up = self.price(option.strike, vol=self.vol + eps)
        price_down = self.price(option.strike, vol=self.vol - eps)
        return (price_up - price_down) / (2 * eps)

    def rho(self, option:Option, eps=1e-4):
        price_up = self.price(option.strike, rate=self.rate + eps)
        price_down = self.price(option.strike, rate=self.rate - eps)
        return (price_up - price_down) / (2 * eps)
