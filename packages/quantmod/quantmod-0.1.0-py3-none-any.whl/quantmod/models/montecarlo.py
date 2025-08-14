import numpy as np
from pydantic import Field
from typing import Optional
from .optioninputs import OptionInputs, OptionType, ExerciseStyle, BarrierType


class MonteCarloOptionPricing:
    """
    Monte Carlo Pricing for options.

    Parameters
    ----------
    inputs : OptionInputs
        The inputs for the option pricing model.
    nsims : int, optional
        Number of simulations (default is Field(..., gt=0)).
    timestep : int, optional
        Time step (default is Field(..., gt=0)).
    option_type : OptionType
        Type of option (Call or Put).
    exercise_style : ExerciseStyle
        Style of exercise (American, European, or Barrier).
    barrier_level : float, optional
        Barrier level for barrier options (default is None).
    barrier_rebate : int, optional
        Barrier rebate for barrier options (default is None).
    barrier_type : BarrierType, optional
        Type of barrier option (default is None).

    Attributes
    ----------
    option_price : float
        The calculated option price.

    Raises
    ------
    ValueError
        If an unsupported exercise style or barrier type is provided.
    """

    def __init__(
        self,
        inputs: OptionInputs,
        nsims: int = Field(..., gt=0, description="Number of simulations"),
        timestep: int = Field(..., gt=0, description="Time step"),
        option_type: OptionType = Field(..., description="Call or Put"),
        exercise_style: ExerciseStyle = Field(
            ..., description="American or European or Barrier"
        ),
        barrier_level: Optional[float] = Field(
            None, gt=0, description="Barrier level (for barrier options)"
        ),
        barrier_rebate: Optional[int] = Field(
            None, gt=0, description="Barrier rebate (for barrier options)"
        ),
        barrier_type: Optional[BarrierType] = Field(
            None, description="Type of barrier option"
        ),
    ) -> None:
        self.inputs = inputs
        self.spot = self.inputs.spot
        self.strike = self.inputs.strike
        self.rate = self.inputs.rate
        self.ttm = self.inputs.ttm
        self.sigma = self.inputs.volatility

        self.nsims = nsims
        self.timestep = timestep
        self.option_type = option_type
        self.exercise_style = exercise_style
        self.barrier_level = barrier_level
        self.barrier_rebate = barrier_rebate
        self.barrier_type = barrier_type

        # Calculate the price immediately upon initialization
        self._calculate_price()

    def _calculate_price(self):
        """
        Calculate the option price using Monte Carlo simulation.

        Returns
        -------
        float
            The calculated option price.
        """
        dt = self.ttm / self.timestep
        discount_factor = np.exp(-self.rate * self.ttm)

        # Simulate price paths
        price_paths = np.zeros((self.nsims, self.timestep + 1))
        price_paths[:, 0] = self.spot

        for t in range(1, self.timestep + 1):
            z = np.random.standard_normal(self.nsims)
            price_paths[:, t] = price_paths[:, t - 1] * np.exp(
                (self.rate - 0.5 * self.sigma**2) * dt + self.sigma * np.sqrt(dt) * z
            )

        # Calculate payoff based on option style
        if self.exercise_style == ExerciseStyle.EUROPEAN:
            if self.option_type == OptionType.CALL:
                payoff = np.maximum(price_paths[:, -1] - self.strike, 0)
            else:
                payoff = np.maximum(self.strike - price_paths[:, -1], 0)
        elif self.exercise_style == ExerciseStyle.ASIAN:
            avg_price = np.mean(price_paths, axis=1)
            if self.option_type == OptionType.CALL:
                payoff = np.maximum(avg_price - self.strike, 0)
            else:
                payoff = np.maximum(self.strike - avg_price, 0)
        elif self.exercise_style == ExerciseStyle.BARRIER:
            if self.barrier_type == BarrierType.UP_AND_OUT:
                barrier_shift = self.barrier_level * np.exp(
                    0.5826 * self.sigma * np.sqrt(self.ttm / self.timestep)
                )
                if self.option_type == OptionType.CALL:
                    payoff = np.where(
                        np.max(price_paths, axis=1) < barrier_shift,
                        np.maximum(price_paths[:, -1] - self.strike, 0),
                        self.barrier_rebate,
                    )
                else:
                    payoff = np.where(
                        np.max(price_paths, axis=1) < barrier_shift,
                        np.maximum(self.strike - price_paths[:, -1], 0),
                        self.barrier_rebate,
                    )
            else:
                raise ValueError("Currently only supports Up-and-out barrier options.")
        else:
            raise ValueError(f"Unsupported exercise style: {self.exercise_style}")

        # Calculate option price
        self.option_price = discount_factor * np.mean(payoff)
        return self.option_price
