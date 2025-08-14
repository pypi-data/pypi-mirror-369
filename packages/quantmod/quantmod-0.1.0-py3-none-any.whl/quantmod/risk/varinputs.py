import pandas as pd
from pydantic import BaseModel, Field, confloat
from typing import List, Optional


class RiskInputs(BaseModel):
    """
    Input object for risk calculations.

    Parameters
    ----------
    - confidence_level : float
        The confidence level for the VaR calculation.
        Must be between 0.90 and 1.0.
        Must be greater than or equal to 1.
    - num_simulations : int, default: 10000
        Number of Monte Carlo simulations.
        Must be between 1000 and 100000.
    - portfolio_weights : list of float, optional
        Weights of assets in the portfolio (None for single stock).
        Each weight must be between 0 and 1.
        The default is None.
    - portfolio_returns : pd.DataFrame
        Historical returns of portfolio assets or single stock.
    - is_single_stock : bool, default: False
        Flag to indicate single stock calculation.

    Returns
    -------
    RiskInputs
        Risk inputs parameters

    Raises
    ------
    ValueError
        If any of the input parameters are invalid
    """

    confidence_level: float = Field(
        ..., ge=0.90, le=1.0, description="The confidence level for the VaR calculation"
    )
    num_simulations: int = Field(
        10000, ge=1000, le=100000, description="Number of Monte Carlo simulations"
    )
    portfolio_weights: Optional[List[confloat(ge=0, le=1)]] = Field(
        None, description="Weights of assets in the portfolio (None for single stock)"
    )
    portfolio_returns: pd.DataFrame = Field(
        ..., description="Historical returns of portfolio assets or single stock"
    )
    is_single_stock: bool = Field(
        False, description="Flag to indicate single stock calculation"
    )

    # allow Pydantic to accept arbitrary Python types that are not part of the standard Pydantic types.
    class Config:
        arbitrary_types_allowed = True
