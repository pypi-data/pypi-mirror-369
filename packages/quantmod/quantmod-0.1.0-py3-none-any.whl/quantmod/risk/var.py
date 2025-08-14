import numpy as np
from scipy.stats import norm
from .varinputs import RiskInputs


# Risk Metrics
class VaRMetrics:
    """
    Class to calculate various Value at Risk (VaR) metrics.

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

    Attributes
    ----------
    parametric_var : float
        The parametric VaR value.
    historical_var : float
        The historical VaR value.
    monte_carlo_var : float
        The Monte Carlo VaR value.
    expected_shortfall : float
        The expected shortfall value.

    """

    def __init__(self, inputs: RiskInputs):
        self.confidence_level = inputs.confidence_level
        self.num_simulations = inputs.num_simulations
        self.is_single_stock = inputs.is_single_stock
            
        # Convert returns to NumPy array and ensure 2D shape
        self.returns = inputs.portfolio_returns.to_numpy()
        if self.is_single_stock:
            self.returns = self.returns.reshape(-1, 1)  # Ensure 2D for consistency
            self.weights = np.array([1.0])
        else:
            if inputs.portfolio_weights is None:
                raise ValueError("Portfolio weights must be provided for portfolio VaR")
            self.weights = np.array(inputs.portfolio_weights)
            if len(self.weights) != self.returns.shape[1]:
                raise ValueError("Portfolio weights must match the number of assets")
            if not np.all(self.weights >= 0):
                raise ValueError("Portfolio weights must be non-negative")
            if not np.isclose(np.sum(self.weights), 1.0, rtol=1e-3):
                raise ValueError("Portfolio weights must sum to 1")
            
        # Precompute portfolio returns for efficiency
        self.portfolio_returns = (
            self.returns if self.is_single_stock else self.returns @ self.weights
        )
        
        if np.any(np.isnan(self.portfolio_returns)) or np.any(np.isinf(self.portfolio_returns)):
            raise ValueError("portfolio_returns contains NaN or infinite values")

        # Compute risk metrics
        self.parametric_var = self._parametric_var()
        self.historical_var = self._historical_var()
        self.monte_carlo_var = self._monte_carlo_var()
        self.expected_shortfall = self._expected_shortfall()


    def _parametric_var(self) -> float:
        """
        Calculate parametric VaR using normal distribution.

        Returns
        -------
        float
            Parametric VaR value.
        """
        mean_returns = np.mean(self.portfolio_returns)
        std_returns = np.std(self.portfolio_returns, ddof=1) # Use sample standard deviation
        return norm.ppf(1 - self.confidence_level, loc=mean_returns, scale=std_returns)

    def _historical_var(self) -> float:
        """
        Calculate historical VaR based on empirical distribution.

        Returns
        -------
        float
            Historical VaR value.
        """
        return np.percentile(self.portfolio_returns, 100 * (1 - self.confidence_level))

    def _monte_carlo_var(self) -> float:
        """
        Calculate Monte Carlo VaR using simulated returns.

        Returns
        -------
        float
            Monte Carlo VaR value.
        """
        mean_returns = np.mean(self.returns, axis=0)
        
        if self.is_single_stock:
            std_returns = np.std(self.returns[:, 0])
            simulated_returns = np.random.normal(
                mean_returns[0], std_returns, self.num_simulations
            )
        else:
            cov_matrix = np.cov(self.returns.T)
            # Regularize covariance matrix
            cov_matrix += np.eye(cov_matrix.shape[0]) * 1e-6
            simulated_returns = np.random.multivariate_normal(
                mean_returns, cov_matrix, self.num_simulations
            )
            simulated_returns = simulated_returns @ self.weights

        return np.percentile(simulated_returns, 100 * (1 - self.confidence_level))
    
    def _expected_shortfall(self) -> float:
        """
        Calculate expected shortfall (conditional VaR).

        Returns
        -------
        float
            Expected shortfall value. Returns NaN if no returns are below VaR.
        """
        var = self._historical_var()
        tail_returns = self.portfolio_returns[self.portfolio_returns <= var]
        return np.mean(tail_returns) if tail_returns.size > 0 else np.nan