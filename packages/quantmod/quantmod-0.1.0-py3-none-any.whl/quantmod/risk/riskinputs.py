from pydantic import BaseModel, Field, field_validator
from typing import List

class RiskInputs(BaseModel):
    """
    RiskInputs parameters

    Parameters
    ----------
    returns : List[float]
        List of historical returns
    confidence_level : float
        The confidence level for the VaR calculation

    Returns
    -------
    RiskInputs
        RiskInputs parameters

    Raises
    ------
    ValueError
        If any of the input parameters are invalid

    """
    returns: List[float] = Field(..., description="List of historical returns")
    confidence_level: float = Field(..., ge=0.0, le=1.0, description="The confidence level for the VaR calculation")

    class Config:
        arbitrary_types_allowed = True

@field_validator('returns')
def check_returns(cls, v):
    if len(v) <= 252: # Assuming at least one year of daily data
        raise ValueError("At least 252 returns are required for meaningful backtest")
    return v