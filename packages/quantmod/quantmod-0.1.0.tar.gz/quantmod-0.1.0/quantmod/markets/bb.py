# current under testing / development

import datetime
import pandas as pd
from openbb import obb
from typing import List, Union, Optional, Literal


def getData(symbol: Union[str, List[str]], 
            start_date: Union[datetime.date, None, str]=None ,
            end_date: Union[datetime.date, None, str]=None, 
            provider: str = 'yfinance',
            interval: str = '1d') -> pd.DataFrame:
    """
    Get historical price data for a given stock.

    Parameters
    ----------
    symbol : Union[str, List[str]]
        Symbol to get data for. Multiple comma separated items allowed for provider(s): fmp, polygon, tiingo, yfinance.
    start_date : Union[date, None, str]
        Start date of the data, in YYYY-MM-DD format.
    end_date : Union[date, None, str]
        End date of the data, in YYYY-MM-DD format.
    provider : str, optional
        The provider to use, by default 'yfinance'. If None, the priority list configured in the settings is used. Default priority: fmp, intrinio, polygon, tiingo, yfinance.
    interval : str, optional
        Time interval of the data to return. Default is '1d'.
        valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1W,1M,1Q

    Returns
    -------
    pd.DataFrame
        DataFrame with OHLC[A]V (Open, High, Low, Close, Adj Close, Volume).
    """

    output = obb.equity.price.historical(
        symbol, 
        start_date=start_date, 
        end_date=end_date,
        interval=interval
    ).to_df()

    return output.groupby('column')

if __name__ == "__main__":
    df = getData(["AAPL","SPY"], interval="1d")
    print(df.head())
