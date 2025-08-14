import numpy as np
from pydantic import Field
import matplotlib.pyplot as plt
from typing import Optional
from .optioninputs import OptionInputs, OptionType, ExerciseStyle


# Class for Binomial Option Pricing
class BinomialOptionPricing:
    """
    Class for Binomial Option Pricing.

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
    nsteps : int
        Number of steps
    option_type : OptionType
        Option type, either 'call' or 'put'
    exercise_style : ExerciseStyle
        Exercise style, either 'american' or 'european'
    output : str, optional
        Output type ('price', 'payoff', 'value', 'delta'), by default 'payoff'


    Attributes
    ----------
    binomialoption : np.ndarray
        The calculated option prices (depends on the selected output type)

    Methods
    -------
    plot_tree()
        Plots the binomial tree based on the selected output type
    """

    def __init__(
        self,
        inputs: OptionInputs,
        nsteps: int = Field(..., gt=0, description="Number of steps"),
        option_type: OptionType = Field(..., description="Call or Put"),
        exercise_style: ExerciseStyle = Field(..., description="American or European"),
        output: Optional[str] = "payoff",
    ) -> None:
        self.inputs = inputs
        self.nsteps = nsteps
        self.option_type = option_type
        self.exercise_style = exercise_style
        self.output = output

        # Prameters
        self.dt = self.inputs.ttm / self.nsteps
        self.u = np.exp(self.inputs.volatility * np.sqrt(self.dt))
        self.v = 1 / self.u

        self.p = (np.exp(self.inputs.rate * self.dt) - self.v) / (self.u - self.v)
        self.df = np.exp(-self.inputs.rate * self.dt)

        # Initialize arrays
        self.price = np.zeros((self.nsteps + 1, self.nsteps + 1))
        self.payoff = np.zeros((self.nsteps + 1, self.nsteps + 1))
        self.value = np.zeros((self.nsteps + 1, self.nsteps + 1))
        self.delta = np.zeros((self.nsteps + 1, self.nsteps + 1))

        # Calculate option values
        self.binomialoption = self._binomialoption()

    def _binomialoption(self) -> np.ndarray:
        # Forward loop
        for j in range(self.nsteps + 1):
            for i in range(j + 1):
                self.price[i, j] = (
                    self.inputs.spot * np.power(self.v, i) * np.power(self.u, j - i)
                )
                if self.option_type == OptionType.CALL:
                    self.payoff[i, j] = np.maximum(
                        self.price[i, j] - self.inputs.strike, 0
                    )
                else:
                    self.payoff[i, j] = np.maximum(
                        self.inputs.strike - self.price[i, j], 0
                    )

        # Reverse loop
        for j in range(self.nsteps, -1, -1):
            for i in range(j + 1):
                if j == self.nsteps:
                    self.value[i, j] = self.payoff[i, j]
                    if self.option_type == OptionType.CALL:
                        self.delta[i, j] = (
                            1 if self.price[i, j] > self.inputs.strike else 0
                        )
                    else:
                        self.delta[i, j] = (
                            -1 if self.price[i, j] < self.inputs.strike else 0
                        )
                else:
                    continuation_value = self.df * (
                        self.p * self.value[i, j + 1]
                        + (1 - self.p) * self.value[i + 1, j + 1]
                    )
                    self.value[i, j] = np.maximum(
                        self.payoff[i, j] * 1
                        if self.exercise_style == ExerciseStyle.AMERICAN
                        else 0,
                        continuation_value,
                    )
                    self.delta[i, j] = (
                        self.value[i, j + 1] - self.value[i + 1, j + 1]
                    ) / (self.price[i, j + 1] - self.price[i + 1, j + 1])

        if self.output == "price":
            return np.around(self.price, 4)
        if self.output == "payoff":
            return np.around(self.payoff, 4)
        elif self.output == "value":
            return np.around(self.value, 4)
        elif self.output == "delta":
            return np.around(self.delta, 4)
        else:
            raise ValueError(
                "Invalid output type. Must be one of: 'price', 'payoff', 'value', 'delta'"
            )

    def plot_tree(self):
        """Plot the binomial tree with option values"""
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.set_title(
            f"Binomial Tree \n\n {self.option_type}  - {self.exercise_style} - {self.output}"
        )

        output_values = getattr(self, self.output)

        for j in range(self.nsteps + 1):
            for i in range(j + 1):
                x = j
                y = (j - 2 * i) / 2

                node_text = f"Spot: {self.price[i, j]:.2f}\n{self.output}: {output_values[i, j]:.4f}"
                ax.text(
                    x,
                    y,
                    node_text,
                    ha="center",
                    va="center",
                    bbox=dict(facecolor="white", alpha=0.8),
                )

                if j < self.nsteps:
                    ax.plot([x, x + 1], [y, y + 0.5], "k-", lw=0.5)  # Up movement
                    ax.plot([x, x + 1], [y, y - 0.5], "k-", lw=0.5)  # Down movement

        ax.set_xlim(-0.5, self.nsteps + 0.5)
        ax.set_ylim(-self.nsteps / 2 - 0.5, self.nsteps / 2 + 0.5)
        ax.axis("off")
        plt.show()
