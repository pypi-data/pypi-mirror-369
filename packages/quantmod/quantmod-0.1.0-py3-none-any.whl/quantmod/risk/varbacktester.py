import pandas as pd
import numpy as np
from scipy import stats
from tabulate import tabulate
from .riskinputs import RiskInputs


class VarBacktester:
    """
    Class to perform a backtest for Value at Risk (VaR) calculations with non-overlapping windows  

    Parameters
    ----------
    inputs : RiskInputs
        An instance of Risk inputs containing returns and confidence level
    window_volatility : int, optional
        The window size for the rolling volatility calculation, by default 21
    window_forward : int, optional
        The window size for the rolling forward calculation, by default 10

    Returns
    -------
    attributes: tabular output
        run
    """ 

    def __init__(self, inputs: RiskInputs, window_volatility:int = 21, window_forward: int = 10) -> pd.DataFrame:
        self.inputs = inputs
        self.returns = pd.Series(inputs.returns)
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
        # Create a dataframe with returns
        data = pd.DataFrame({'returns': self.returns})

        # Calculate rolling VaR
        data['VaR'] = data['returns'].rolling(self.window_volatility).std()*np.sqrt(self.window_forward)*stats.norm.ppf(1-self.inputs.confidence_level)
        
        # Calculate forward returns
        data['shifted_returns'] = data['returns'].shift(-2) # non overlapping window
        data['forward_returns'] = data['shifted_returns'].rolling(window=self.window_forward).sum()
        data['shifted_forward_returns'] = data['forward_returns'].shift(-self.window_forward+1)
        
        # Identify breaches
        data['breach'] = data['shifted_forward_returns'] < data['VaR']

        # Calculate number and percentage of breaches
        total_breaches = data['breach'].sum()
        total_observations = len(data) - self.window_volatility - self.window_forward 
        percentage_breaches = (total_breaches / total_observations) * 100 if total_observations > 0 else np.nan

        # Calculate continuous breaches
        data['breach_shift'] = data['breach'].shift(1)
        data['continuous_breaches'] = (data['breach'] & (data['breach'] == data['breach_shift'])).astype(int)
        number_continuous_breaches = data['continuous_breaches'].sum()

        # # Print data of breaches
        # print(data[data['breach']])

        # Conditional probability of breaches
        non_nan_breaches = data['breach'].dropna()
        conditional_probability = non_nan_breaches.mean() if len(non_nan_breaches) > 0 else np.nan

        # Ouput results in tabular format
        header = ['Backtest Results', 'Values']
        table = [
            ['Actual Breaches', total_breaches],
            ['Percentage of Actual Breaches', percentage_breaches],
            ['Expected Breaches', int(total_observations*(1-self.inputs.confidence_level))],
            ['Percentage of Expected Breaches', (1-self.inputs.confidence_level)*100],
            ['Number of Continuous Breaches', number_continuous_breaches],
            ['Conditional Probability of Breaches', conditional_probability*100]] 

        return tabulate(table,headers=header, floatfmt=(".2f"))
