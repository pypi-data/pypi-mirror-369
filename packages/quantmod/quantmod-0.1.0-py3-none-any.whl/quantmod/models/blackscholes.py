from pydantic import BaseModel, Field
import numpy as np
from scipy.stats import norm
from scipy.optimize import brentq
from typing import Tuple
from .optioninputs import OptionInputs


class BlackScholesOptionPricing:
    """
    A class implementing the Black-Scholes option pricing model.

    This class calculates option prices and Greeks (sensitivity measures) using
    the Black-Scholes formula for European-style options.

    Parameters
    ----------
    inputs : OptionInputs
        Object containing the following option parameters:
        - spot : float
            Current price of the underlying asset
        - strike : float
            Strike price of the option
        - rate : float
            Risk-free interest rate (as a decimal)
        - ttm : float
            Time to maturity in years
        - volatility : float
            Implied volatility of the underlying asset (as a decimal)
        - callprice : float, optional
            Market price of call option (used for implied volatility calculation)
        - putprice : float, optional
            Market price of put option (used for implied volatility calculation)

    Attributes
    ----------
    call_price : float
        Price of the call option
    put_price : float
        Price of the put option
    call_delta : float
        Delta of the call option (sensitivity to underlying price)
    put_delta : float
        Delta of the put option (sensitivity to underlying price)
    gamma : float
        Gamma of the option (second derivative with respect to underlying price)
    vega : float
        Vega of the option (sensitivity to volatility changes)
    call_theta : float
        Theta of the call option (sensitivity to time decay)
    put_theta : float
        Theta of the put option (sensitivity to time decay)
    call_rho : float
        Rho of the call option (sensitivity to interest rate changes)
    put_rho : float
        Rho of the put option (sensitivity to interest rate changes)
    impvol : float
        Implied volatility calculated from market price (if provided)

    Notes
    -----
    All Greeks are calculated using the analytical formulas from the
    Black-Scholes model. Theta is expressed in price change per day,
    and vega and rho are expressed per 1% change in their respective parameters.
    """

    def __init__(self, inputs: OptionInputs) -> None:
        self.inputs = inputs
        self.S = self.inputs.spot
        self.K = self.inputs.strike
        self.r = self.inputs.rate
        self.t = self.inputs.ttm
        self.sigma = self.inputs.volatility

        # Calculate common terms used across methods
        self.time_sqrt = np.sqrt(self.t)
        self.discount_factor = np.exp(-self.r * self.t)

        # Calculate d1 and d2 parameters
        self.d1 = self._calculate_d1()
        self.d2 = self.d1 - self.sigma * self.time_sqrt

        # Calculate all option Greeks and prices
        self.call_price, self.put_price = self._price()
        self.call_delta, self.put_delta = self._delta()
        self.gamma = self._gamma()
        self.vega = self._vega()
        self.call_theta, self.put_theta = self._theta()
        self.call_rho, self.put_rho = self._rho()
        self.impvol = self._impvol()

    def _calculate_d1(self) -> float:
        """
        Calculate the d1 parameter for Black-Scholes formula.

        The d1 parameter is used in the Black-Scholes option pricing formula and represents
        the standardized moneyness of the option adjusted for time value.

        Returns
        -------
        float
            The d1 parameter calculated as:
            d1 = (ln(S/K) + (r + σ²/2)t) / (σ√t)
            where:
            S = spot price
            K = strike price
            r = risk-free rate
            σ = volatility
            t = time to maturity

        Notes
        -----
        This is a private method used internally by the Black-Scholes pricing model
        to calculate option prices and Greeks.
        """
        return (np.log(self.S / self.K) + (self.r + (self.sigma**2) / 2) * self.t) / (
            self.sigma * self.time_sqrt
        )

    def _price(self) -> Tuple[float, float]:
        """
        Calculate the Black-Scholes option prices for both call and put options.

        The Black-Scholes pricing formulas are:
        Call = S * N(d1) - K * e^(-rT) * N(d2)
        Put = K * e^(-rT) * N(-d2) - S * N(-d1)

        Returns
        -------
        Tuple[float, float]
            A tuple containing (call_price, put_price)
            - call_price : float
                The price of the call option
            - put_price : float
                The price of the put option

        Notes
        -----
        The method uses pre-calculated values of d1 and d2:
        - d1 = (ln(S/K) + (r + σ²/2)t) / (σ√t)
        - d2 = d1 - σ√t

        where:
        S = spot price
        K = strike price
        r = risk-free rate
        σ = volatility
        t = time to maturity
        N(x) = cumulative standard normal distribution function
        """
        d1_cdf = norm.cdf(self.d1)
        d2_cdf = norm.cdf(self.d2)

        call = self.S * d1_cdf - self.K * self.discount_factor * d2_cdf
        put = self.K * self.discount_factor * norm.cdf(-self.d2) - self.S * norm.cdf(
            -self.d1
        )
        return call, put

    def _delta(self) -> Tuple[float, float]:
        """
        Calculate the Black-Scholes delta for both call and put options.

        Delta measures the rate of change of the option price with respect to the
        underlying asset price. It represents the first partial derivative of the
        option price with respect to the spot price.

        Returns
        -------
        Tuple[float, float]
            A tuple containing (call_delta, put_delta)
            - call_delta : float
                The delta of the call option, ranges from 0 to 1
            - put_delta : float
                The delta of the put option, ranges from -1 to 0

        Notes
        -----
        The formulas used are:
        - Call Delta = N(d1)
        - Put Delta = N(d1) - 1 = -N(-d1)

        where:
        - N(x) is the cumulative standard normal distribution function
        - d1 = (ln(S/K) + (r + σ²/2)t) / (σ√t)
        """
        d1_cdf = norm.cdf(self.d1)
        return d1_cdf, -norm.cdf(-self.d1)

    def _gamma(self) -> float:
        """
        Calculate the Black-Scholes gamma for both call and put options.

        Gamma measures the rate of change of delta with respect to the underlying
        asset price. It represents the second partial derivative of the option
        price with respect to the spot price. Gamma is the same for both call
        and put options.

        Returns
        -------
        float
            The gamma value of the option, which represents the convexity
            or curvature of the option's value in relation to the
            underlying price.

        Notes
        -----
        The formula used is:
        Gamma = N'(d1) / (S * σ * √t)

        where:
        - N'(x) is the standard normal probability density function
        - S is the spot price
        - σ is the volatility
        - t is the time to maturity
        - d1 = (ln(S/K) + (r + σ²/2)t) / (σ√t)
        """
        return norm.pdf(self.d1) / (self.S * self.sigma * self.time_sqrt)

    def _vega(self) -> float:
        """
        Calculate the Black-Scholes vega for both call and put options.

        Vega measures the rate of change of the option price with respect to
        the volatility. It represents the first partial derivative of the
        option price with respect to volatility. Vega is the same for both
        call and put options.

        Returns
        -------
        float
            The vega value of the option (divided by 100 to express in percentage terms),
            which represents the change in option price for a 1% change in volatility.

        Notes
        -----
        The formula used is:
        Vega = S * N'(d1) * √t / 100

        where:
        - N'(x) is the standard normal probability density function
        - S is the spot price
        - t is the time to maturity
        - d1 = (ln(S/K) + (r + σ²/2)t) / (σ√t)
        """
        return self.S * norm.pdf(self.d1) * self.time_sqrt / 100

    def _theta(self) -> Tuple[float, float]:
        """
        Calculate the Black-Scholes theta for both call and put options.

        Theta measures the rate of change of the option price with respect to
        time, representing the time decay of the option's value. The values
        are expressed in price change per day.

        Returns
        -------
        Tuple[float, float]
            A tuple containing (call_theta, put_theta)
            - call_theta : float
                The theta of the call option (per day)
            - put_theta : float
                The theta of the put option (per day)

        Notes
        -----
        The formulas used are:
        Call Theta = [-S*N'(d1)*σ/(2√t) - rKe^(-rt)*N(d2)] / 365
        Put Theta = [-S*N'(d1)*σ/(2√t) + rKe^(-rt)*N(-d2)] / 365

        where:
        - N(x) is the cumulative standard normal distribution function
        - N'(x) is the standard normal probability density function
        - S is the spot price
        - K is the strike price
        - r is the risk-free rate
        - t is the time to maturity
        - σ is the volatility
        """
        spot_term = -self.S * norm.pdf(self.d1) * self.sigma / (2 * self.time_sqrt)
        call_rate_term = -self.r * self.K * self.discount_factor * norm.cdf(self.d2)
        put_rate_term = self.r * self.K * self.discount_factor * norm.cdf(-self.d2)

        return (spot_term + call_rate_term) / 365, (spot_term + put_rate_term) / 365

    def _rho(self) -> Tuple[float, float]:
        """
        Calculate the Black-Scholes rho for both call and put options.

        Rho measures the rate of change of the option price with respect to
        the risk-free interest rate. It represents the first partial derivative
        of the option price with respect to the interest rate. The values are
        divided by 100 to express the change in option price for a 1% change
        in interest rate.

        Returns
        -------
        Tuple[float, float]
            A tuple containing (call_rho, put_rho)
            - call_rho : float
                The rho of the call option (per 1% change in rate)
            - put_rho : float
                The rho of the put option (per 1% change in rate)

        Notes
        -----
        The formulas used are:
        Call Rho = K * t * e^(-rt) * N(d2) / 100
        Put Rho = -K * t * e^(-rt) * N(-d2) / 100

        where:
        - N(x) is the cumulative standard normal distribution function
        - K is the strike price
        - t is the time to maturity
        - r is the risk-free rate
        """
        call = self.K * self.t * self.discount_factor * norm.cdf(self.d2) / 100
        put = -self.K * self.t * self.discount_factor * norm.cdf(-self.d2) / 100
        return call, put

    def _impvol(self) -> float:
        """
        Calculate the implied volatility of an option using the Black-Scholes model.

        This method uses a root-finding algorithm (Brent's method) to determine the
        volatility that would result in the Black-Scholes model price matching the
        market price of the option. If no market price (callprice or putprice) is
        provided, returns the input volatility.

        Returns
        -------
        float
            The implied volatility value that makes the model price equal to the market price.
            Returns the input volatility if no market price is provided.
            Returns np.nan if no solution is found within the bounds [0.00001, 5.0].

        Notes
        -----
        The method uses the following approach:
        1. If no market price is provided, returns the input volatility
        2. Otherwise, uses Brent's method to find the volatility that minimizes
           the difference between model price and market price
        3. The search is bounded between 0.001% and 500% volatility
        4. A minimum value of 0.001% is enforced on the result

        See Also
        --------
        scipy.optimize.brentq : The root-finding method used to solve for implied volatility

        Examples
        --------
        >>> option = BlackScholesOptionPricing(
        ...     OptionInputs(
        ...         spot=100,
        ...         strike=100,
        ...         rate=0.05,
        ...         ttm=1.0,
        ...         volatility=0.2,
        ...         callprice=10.0
        ...     )
        ... )
        >>> option.impvol
        0.2  # Returns the implied volatility that produces a call price of 10.0
        """
        if self.inputs.callprice is None and self.inputs.putprice is None:
            return self.sigma
        else:

            def f(sigma: float) -> float:
                option = BlackScholesOptionPricing(
                    OptionInputs(
                        spot=self.S,
                        strike=self.K,
                        rate=self.r,
                        ttm=self.t,
                        volatility=sigma,
                    )
                )
                if self.inputs.callprice is not None:
                    model_call_price = option.call_price
                    return model_call_price - self.inputs.callprice
                else:
                    model_put_price = option.put_price
                    return model_put_price - self.inputs.putprice

            try:
                implied_vol = brentq(
                    f, a=1e-5, b=5.0, xtol=1e-8, rtol=1e-8, maxiter=100
                )
                implied_vol = max(implied_vol, 1e-5)
            except ValueError:
                implied_vol = np.nan
            return implied_vol
