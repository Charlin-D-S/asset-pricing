import numpy as np
from products.option import Option

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

    def __init__(self, spot: float, rate: float, dividend_yield: float = 0.0,vol = 1.0,n_sims=10_000, seed=42):
        self.spot = spot
        self.rate = rate
        self.q = dividend_yield
        self.vol = vol
        self.n_sims = n_sims
        self.rng = np.random.default_rng(seed)

    def simulate_terminal_price(self, spot, rate, maturity,vol,dividend_yield=0.0):
        """Simulate S_T using the exact solution."""
        z = self.rng.normal(size=self.n_sims)
        drift = (rate - dividend_yield - 0.5 * vol**2) * maturity
        diffusion = vol * np.sqrt(maturity) * z
        return spot * np.exp(drift + diffusion)

    def price(self, option:Option,spot=None,vol=None, rate=None, maturity = None):  

        spot = spot if spot is not None else self.spot
        vol = vol if vol is not None else self.vol
        rate = rate if rate is not None else self.rate
        maturity = maturity if maturity is not None else option.maturity

        ST = self.simulate_terminal_price(spot=spot, rate=rate, maturity=maturity,vol=vol)
        vec_f = np.vectorize(option.payoff)
        payoffs = vec_f(ST)
        return np.exp(-self.rate * maturity) * payoffs.mean()

    # ---------- Greeks ----------
    def delta(self, option:Option, eps=1e-4):
        price_up = self.price(option,spot=self.spot + eps)
        price_down = self.price(option, spot=self.spot - eps)
        return (price_up - price_down) / (2 * eps)

    def gamma(self, option:Option, eps=1e-4):
        price_up = self.price(option, spot=self.spot + eps)
        price_mid = self.price(option, spot=self.spot)
        price_down = self.price(option, spot=self.spot - eps)
        return (price_up - 2 * price_mid + price_down) / (eps ** 2)

    def vega(self, option:Option, eps=1e-4):
        price_up = self.price(option, vol=self.vol + eps)
        price_down = self.price(option, vol=self.vol - eps)
        return (price_up - price_down) / (2 * eps)

    def rho(self, option:Option, eps=1e-4):
        price_up = self.price(option, rate=self.rate + eps)
        price_down = self.price(option, rate=self.rate - eps)
        return (price_up - price_down) / (2 * eps)
