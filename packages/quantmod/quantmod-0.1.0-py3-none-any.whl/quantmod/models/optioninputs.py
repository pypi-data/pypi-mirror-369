from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional

class OptionType(str, Enum):
    CALL = "call"
    PUT = "put"

class ExerciseStyle(str, Enum):
    ASIAN = "asian"
    BARRIER = "barrier"
    EUROPEAN = "european"
    AMERICAN = "american"

class BarrierType(str, Enum):
    UP_AND_OUT = "up_and_out"

class OptionInputs(BaseModel):
    """
    Option inputs parameters

    Parameters
    ----------
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

    Returns
    -------
    OptionInputs
        Option inputs parameters

    Raises
    ------
    ValueError
        If any of the input parameters are invalid
    """

    spot: float = Field(..., gt=0, description="Spot price of the underlying asset")
    strike: float = Field(..., gt=0, description="Strike price of the option")
    rate: float = Field(..., ge=0, le=1, description="Risk-free interest rate")
    ttm: float = Field(..., gt=0, description="Time to maturity in years")
    volatility: float = Field(
        ..., gt=0, description="Volatility of the underlying asset"
    )
    callprice: Optional[float] = Field(
        default=None, ge=0, description="Market price of the call option"
    )
    putprice: Optional[float] = Field(
        default=None, ge=0, description="Market price of the put option"
    )
