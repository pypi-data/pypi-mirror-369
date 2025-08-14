import pandas as pd
import numpy as np
from scipy import stats
from tabulate import tabulate
from .varinputs import RiskInputs


class VaRAnalyzer:
    """
    Class to perform a backtest for Value at Risk (VaR) calculations with non-overlapping windows

    Parameters
    ----------
    inputs : RiskInputs
        Object containing the following option parameters:
        - confidence_level : float
            The confidence level for the VaR calculation.
        - num_simulations : int
            The number of Monte Carlo simulations.
        - portfolio_returns : pd.DataFrame
            Historical returns of portfolio assets or single stock.
        - is_single_stock : bool
            Flag to indicate single stock calculation.
        - portfolio_weights : list of float, optional
            Weights of assets in the portfolio (None for single stock).
    window_volatility : int, optional
        The window size for the rolling volatility calculation, by default 21
    window_forward : int, optional
        The window size for the rolling forward calculation, by default 10

    Attributes
    -------
    run: str
        The run attribute contains the results of the VaR backtest.
    """

    def __init__(
        self, inputs: RiskInputs, window_volatility: int = 21, window_forward: int = 10
    ) -> pd.DataFrame:
        self.confidence_level = inputs.confidence_level
        self.returns = inputs.portfolio_returns
        self.window_volatility = window_volatility
        self.window_forward = window_forward
        self.run = self._runbacktest()

    def _runbacktest(self) -> str:
        """
        Perform VaR backtest with non-overlapping windows

        Returns
        -------
        str
           A tabular output containing the results of the backtest
        """
        # Get the first column name dynamically
        column_name = self.returns.columns[0]

        # Rename the column to 'returns'
        data = self.returns.rename(columns={column_name: "returns"})

        # Calculate rolling VaR
        data["VaR"] = (
            data["returns"].rolling(self.window_volatility).std()
            * np.sqrt(self.window_forward)
            * stats.norm.ppf(1 - self.confidence_level)
        )

        # Calculate forward returns
        data["shifted_returns"] = data["returns"].shift(-2)  # non overlapping window
        data["forward_returns"] = (
            data["shifted_returns"].rolling(window=self.window_forward).sum()
        )
        data["shifted_forward_returns"] = data["forward_returns"].shift(
            -self.window_forward + 2
        )

        # Identify breaches
        data["breach"] = data["shifted_forward_returns"] < data["VaR"]

        # Calculate number and percentage of breaches
        total_breaches = data["breach"].sum()
        total_observations = len(data) - self.window_volatility - self.window_forward
        percentage_breaches = (
            (total_breaches / total_observations) * 100
            if total_observations > 0
            else np.nan
        )

        # Calculate continuous breaches
        data["breach_shift"] = data["breach"].shift(1)
        data["continuous_breaches"] = (
            data["breach"] & (data["breach"] == data["breach_shift"])
        ).astype(int)
        number_continuous_breaches = data["continuous_breaches"].sum()

        # # Print data of breaches
        # print(data[data['breach']])

        # Conditional probability of breaches
        non_nan_breaches = data["breach"].dropna()
        conditional_probability = (
            non_nan_breaches.mean() if len(non_nan_breaches) > 0 else np.nan
        )

        # Ouput results in tabular format
        header = ["Backtest Results", "Values"]
        table = [
            ["Actual Breaches", total_breaches],
            ["Percentage of Actual Breaches", percentage_breaches],
            [
                "Expected Breaches",
                int(total_observations * (1 - self.confidence_level)),
            ],
            [
                "Percentage of Expected Breaches",
                (1 - self.confidence_level) * 100,
            ],
            ["Number of Continuous Breaches", number_continuous_breaches],
            ["Conditional Probability of Breaches", conditional_probability * 100],
        ]

        # return data
        return tabulate(table, headers=header, floatfmt=(".2f"))
