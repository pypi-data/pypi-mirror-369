import pandas as pd


def ATR(df: pd.DataFrame, lookback: int = 14) -> pd.Series:
    """
    Calculate the Average True Range (ATR).

    ATR is a volatility indicator that measures the average of the true range values
    over a specified period. An expanding ATR indicates increased volatility, while
    a low ATR value indicates a series of periods with small price ranges.

    Parameters
    ----------
    df : pd.DataFrame
        dataFrame with OHLC (Open, High, Low, Close) price data
    lookback : int, optional
        number of periods to use for ATR calculation, by default 14

    Returns
    -------
    pd.Series
        series containing the ATR values for each period
    """

    df = df.copy()
    df.rename(columns=str.lower, inplace=True)

    df["H-L"] = abs(df["high"] - df["low"])
    df["H-PC"] = abs(df["high"] - df["close"].shift(1))
    df["L-PC"] = abs(df["low"] - df["close"].shift(1))

    df["TR"] = df[["H-L", "H-PC", "L-PC"]].max(axis=1, skipna=False)
    df["ATR"] = df["TR"].rolling(lookback).mean()

    data = df.drop(["H-L", "H-PC", "L-PC"], axis=1)  # drop columns

    return data["ATR"]


def BBands(series: pd.Series, lookback: int, multiplier: float = 2) -> pd.Series:
    """
    Calculate Bollinger Bands for a given DataFrame

    Parameters
    ----------
    series : pd.Series
        price series
    lookback : int
        lookback period for the bollinger bands
    multiplier : float, optional
        multiplier for the standard deviation, by default 2

    Returns
    -------
    pd.Series
        lower, middle, upper bands for the given series
    """

    # Calculate rolling mean and standard deviation
    rolling_mean = series.rolling(window=lookback).mean()
    rolling_std = series.rolling(window=lookback).std()

    # Calculate upper and lower bands
    upper = rolling_mean + (rolling_std * multiplier)
    middle = rolling_mean
    lower = rolling_mean - (rolling_std * multiplier)

    return lower, middle, upper


def SMA(series: pd.Series, lookback: int) -> pd.Series:
    """
    Moving Average

    Parameters
    ----------
    series : pd.Series
        time series to calculate the Moving Average for
    lookback : int
        lookback period for the Moving Average

    Returns
    -------
    pd.Series
        series containing the Moving Average
    """

    return series.rolling(lookback).mean()


def EMA(series: pd.Series, lookback: int) -> pd.Series:
    """
    Exponential Moving Average

    Parameters
    ----------
    series : pd.Series
        time series to calculate the Exponential Moving Average for
    lookback : int
        lookback period for the Exponential Moving Average

    Returns
    -------
    pd.Series
        series containing the Exponential Moving Average
    """

    return series.ewm(span=lookback, adjust=False).mean()


def MACD(series: pd.Series, lookback: int, fast: int, slow: int) -> pd.Series:
    """
    Moving Average Convergence Divergence

    Parameters
    ----------
    series : pd.Series
        time series to calculate the MACD for
    lookback : int
        lookback period for the MACD
    fast : int
        fast period for the MACD
    slow : int
        slow period for the MACD

    Returns
    -------
    pd.Series
        series containing the MACD
    """

    # Calculate MACD line
    macd = (
        series.ewm(span=fast, adjust=False).mean()
        - series.ewm(span=slow, adjust=False).mean()
    )

    # Calculate Signal line from the MACD line
    signal = macd.ewm(span=lookback, adjust=False).mean()

    return macd, signal


def RSI(series: pd.Series, lookback: int) -> pd.Series:
    """
    Relative Strength Index

    Parameters
    ----------
    series : pd.Series
        time series to calculate the RSI for
    lookback : int
        lookback period for the RSI

    Returns
    -------
    pd.Series
        series containing the RSI
    """

    # Calculate price changes
    delta = series.diff()
    delta.where(delta > 0, 0)
    # Separate gains and losses
    gain = (delta.where(delta > 0, 0)).rolling(window=lookback).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=lookback).mean()

    # Calculate the Relative Strength (RS)
    rs = gain / loss

    # Calculate RSI
    return 100 - (100 / (1 + rs))
