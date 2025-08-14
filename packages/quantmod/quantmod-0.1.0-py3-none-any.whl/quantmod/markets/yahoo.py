import pandas as pd
import yfinance as yf
import joblib
import hashlib
import os
from typing import Union, List

# # Directory to store cache files
# CACHE_DIR = '.cache'

# def _get_cache_file_name(tickers: Union[str, List[str]], start_date: str, end_date: str, period: str, interval: str) -> str:
#     """
#     Generate a cache file name based on the parameters.
#     """
#     if isinstance(tickers, str):
#         tickers = [tickers]
#     key = f"{','.join(tickers)}_{start_date}_{end_date}_{period}_{interval}"
#     cache_key = hashlib.md5(key.encode()).hexdigest()
#     return os.path.join(CACHE_DIR, f"{cache_key}.pkl")


# def getData(tickers: Union[str, List[str]], start_date: str = None, end_date: str = None, period: str = '1mo', interval: str = '1d') -> pd.DataFrame:
#     """
#     Retrieve data from yfinance library for specified tickers, with caching.

#     Parameters
#     ----------
#     tickers : str or list
#         Symbol or list of symbols.
#     start_date : str, optional
#         Start date, by default None.
#     end_date : str, optional
#         End date, by default None.
#     period : str, optional
#         Period, by default '1mo'.
#         Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max.
#     interval : str, optional
#         Interval, by default '1d', max 60 days.
#         Valid intervals: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo.

#     Returns
#     -------
#     pd.DataFrame
#         DataFrame with OHLC[A]V (Open, High, Low, Close, Adj Close, Volume).
#     """
#     # Ensure cache directory exists
#     if not os.path.exists(CACHE_DIR):
#         os.makedirs(CACHE_DIR)

#     cache_file = _get_cache_file_name(tickers, start_date, end_date, period, interval)

#     # Check if cached file exists
#     if os.path.exists(cache_file):
#         # print(f"Loading data from cache: {cache_file}")
#         return joblib.load(cache_file)

#     try:
#         # Download data from yfinance
#         data = yf.download(tickers, start=start_date, end=end_date, auto_adjust=True, progress=False, period=period, interval=interval)

#         # Save data to cache
#         joblib.dump(data, cache_file)
#         # print(f"Data cached to: {cache_file}")

#     except Exception as e:
#         print(f"Error downloading data: {e}")
#         raise

#     return data


def getData(
    tickers: Union[str, List[str]],
    start_date: str = None,
    end_date: str = None,
    period: str = "1mo",
    interval: str = "1d",
) -> pd.DataFrame:
    """
    Retrieve data using yfinance library for specified tickers.

    Parameters
    ----------
    tickers : str or list
        symbol or list of symbols
    start : str, optional
        start date, by default None
    end : str, optional
        end date, by default None
    period : str, optional
        period, by default '1mo'
        valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    interval : str, optional
        interval, by default '1d', max 60 days
        valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo

    Returns
    -------
    pd.DataFrame
        DataFrame with OHLC[A]V (Open, High, Low, Close, Adj Close, Volume).
    """

    cols = ["Open", "High", "Low", "Close", "Volume"]
    data = yf.download(
        tickers,
        start=start_date,
        end=end_date,
        auto_adjust=True,
        progress=False,
        multi_level_index=False,
        period=period,
        interval=interval,
    )

    return data[cols]


# Retrieve ticker object using yfinance library
def getTicker(ticker: str) -> yf.Ticker:
    """
    Retrieve ticker object using yfinance library.

    Parameters
    ----------
    ticker : str
        symbol

    Returns
    -------
    yf.Ticker
        Ticker object
    """

    # for all available options, refer yfinance
    # .info
    # .history
    # .actions
    # .dividends
    # .splits
    # .financials
    # .quarterly_financials
    # .major_holders
    # .institutional_holders
    # .balance_sheet
    # .quarterly_balance_sheet
    # .cashflow
    # .quarterly_cashflow
    # .earnings
    # .quarterly_earnings
    # .sustainability
    # .recommendations
    # .calendar
    # .earnings_dates
    # .isin
    # .options
    # . option_chain('YYYY-MM-DD')
    # .news

    return yf.Ticker(ticker)
