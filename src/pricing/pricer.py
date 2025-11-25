"""
Generic pricer router.

Usage idea:
    pr = Pricer()
    result = pr.price(product, model=model, curve=curve)

The function tries several strategies, in order:
 1. If product has a .price(...) method, call it.
 2. If product looks like an Option (has 'strike' and 'maturity'), call model.call_price / put_price.
 3. If product has attribute 'forward' or similar, fallback to product.price() without args.
It will also try to compute Greeks if the provided model implements them.
"""

from typing import Any, Dict, Optional


class Pricer:
    def __init__(self):
        pass

    def price(self,
              product: Any,
              model: Optional[Any] = None,
              curve: Optional[Any] = None,
              market_price: Optional[float] = None,
              compute_greeks: bool = True) -> Dict[str, Any]:
        """
        Price a product and (optionally) return Greeks.

        Parameters
        ----------
        product : object
            Product instance (Bond, Swap, Future, Option, ...)
        model : object, optional
            Pricing model (e.g. BlackScholesModel) - required for options
        curve : object, optional
            Yield curve - required for discounting-based products (if product.price requires it)
        market_price : float, optional
            Market price (handy for implied vol routines or checks)
        compute_greeks : bool
            If True and model supports Greeks, compute them for options.

        Returns
        -------
        dict
            dictionary with keys:
              - 'price' : float or None
              - 'greeks' : dict (may be empty)
              - 'method' : string describing how it was priced
        """
        res = {"price": None, "greeks": {}, "method": None}

        # 1) If the product provides its own price(...) method, prefer that.
        # Try calling with (curve) or without args depending on signature.
        try:
            if hasattr(product, "price"):
                # Try price(curve) if curve provided
                if curve is not None:
                    try:
                        price = product.price(curve)
                        res.update({"price": price, "method": "product.price(curve)"})
                        # if product.price returns also greeks as tuple/dict, handle gracefully
                        if isinstance(price, tuple) and len(price) == 2 and isinstance(price[1], dict):
                            res["price"], res["greeks"] = price
                        return res
                    except TypeError:
                        # product.price may not accept curve; fall back
                        pass

                # Try price(model) if model provided
                if model is not None:
                    try:
                        price = product.price(model)
                        res.update({"price": price, "method": "product.price(model)"})
                        return res
                    except TypeError:
                        pass

                # Finally try parameterless price()
                try:
                    price = product.price()
                    res.update({"price": price, "method": "product.price()"})
                    return res
                except TypeError:
                    # price exists but requires other args; continue to other strategies
                    pass
        except Exception as e:
            # don't fail hard here; we'll try other ways
            # but log in the result
            res["error_product_price_call"] = str(e)

        # 2) If it resembles an Option (has strike & maturity), use the model
        if hasattr(product, "strike") and hasattr(product, "maturity"):
            if model is None:
                raise ValueError("An option-like product requires a model (e.g. BlackScholesModel).")

            # Detect call vs put by class name (EuropeanCall, EuropeanPut, etc.)
            clsname = product.__class__.__name__.lower()
            try:
                if "call" in clsname:
                    price = model.call_price(product, getattr(product, "vol", None))
                    res.update({"price": price, "method": "model.call_price"})
                elif "put" in clsname:
                    price = model.put_price(product, getattr(product, "vol", None))
                    res.update({"price": price, "method": "model.put_price"})
                else:
                    # If unknown option type, try call_price then put_price
                    try:
                        price = model.call_price(product, getattr(product, "vol", None))
                        res.update({"price": price, "method": "model.call_price (fallback)"})
                    except Exception:
                        price = model.put_price(product, getattr(product, "vol", None))
                        res.update({"price": price, "method": "model.put_price (fallback)"})
            except Exception as e:
                raise RuntimeError(f"Error pricing option with model: {e}")

            # Greeks (if requested and model provides them)
            if compute_greeks:
                greeks = {}
                # try delta
                try:
                    if "call" in clsname and hasattr(model, "call_delta"):
                        greeks["delta"] = model.call_delta(product, getattr(product, "vol", None))
                    elif "put" in clsname and hasattr(model, "put_delta"):
                        greeks["delta"] = model.put_delta(product, getattr(product, "vol", None))
                    elif hasattr(model, "delta"):
                        greeks["delta"] = model.delta(product, getattr(product, "vol", None))
                except Exception:
                    pass

                # gamma
                try:
                    if hasattr(model, "gamma"):
                        greeks["gamma"] = model.gamma(product, getattr(product, "vol", None))
                except Exception:
                    pass

                # vega
                try:
                    if hasattr(model, "vega"):
                        greeks["vega"] = model.vega(product, getattr(product, "vol", None))
                except Exception:
                    pass

                # theta, rho if available
                try:
                    if hasattr(model, "theta"):
                        greeks["theta"] = model.theta(product, getattr(product, "vol", None))
                except Exception:
                    pass
                try:
                    if hasattr(model, "rho"):
                        greeks["rho"] = model.rho(product, getattr(product, "vol", None))
                except Exception:
                    pass

                res["greeks"] = greeks

            return res

        # 3) Finally: try some common fallback patterns
        # - If product has forward/spot attributes and model is provided, try simple cost-of-carry
        try:
            if hasattr(product, "spot") and hasattr(product, "maturity") and model is not None:
                # If it's an EquityFuture-like with a price() method that uses its own parameters, call it first
                try:
                    price = product.price()
                    res.update({"price": price, "method": "product.price() (fallback spot/mat)"})
                    return res
                except Exception:
                    pass

            # If product has start & end and a curve is provided, try product.price(curve)
            if hasattr(product, "start") and hasattr(product, "end") and curve is not None:
                try:
                    price = product.price(curve)
                    res.update({"price": price, "method": "product.price(curve) fallback"})
                    return res
                except Exception:
                    pass
        except Exception:
            pass

        # If nothing worked, raise an informative error
        raise RuntimeError("Could not price product: no compatible pricing route found. "
                           "Make sure the product exposes .price(...) or pass an appropriate model/curve.")
