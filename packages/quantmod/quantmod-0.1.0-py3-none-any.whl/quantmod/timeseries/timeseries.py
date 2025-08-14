import numpy as np
import pandas as pd
from typing import Union


def seriesHi(series: pd.Series) -> pd.DataFrame:
    """Return the high of a given series."""
    return pd.DataFrame({"SeriesHi": [series.max()]}, index=[series.idxmax()])


def seriesLo(series: pd.Series) -> pd.DataFrame:
    """Return the low of a given series."""
    return pd.DataFrame({"SeriesLo": [series.min()]}, index=[series.idxmin()])


def _lowercase_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Helper function to lowercase column names."""
    return df.rename(columns=str.lower)


def Op(df: pd.DataFrame) -> pd.Series:
    """Filter open price"""
    df = _lowercase_columns(df)
    return df["open"]


def Hi(df: pd.DataFrame) -> pd.Series:
    """Filter high price"""
    df = _lowercase_columns(df)
    return df["high"]


def Lo(df: pd.DataFrame) -> pd.Series:
    """Filter low price"""
    df = _lowercase_columns(df)
    return df["low"]


def Cl(df: pd.DataFrame) -> pd.Series:
    """Filter close price"""
    df = _lowercase_columns(df)
    return df["close"]


def Vo(df: pd.DataFrame) -> pd.Series:
    """Filter volume"""
    df = _lowercase_columns(df)
    return df["volume"]


def Ad(df: pd.DataFrame) -> pd.Series:
    """Filter adj close price"""
    df = _lowercase_columns(df)
    return df["adj close"]


def OpCl(df: pd.DataFrame) -> pd.Series:
    """Open to Close difference"""
    return Op(df) - Cl(df)


def OpHi(df: pd.DataFrame) -> pd.Series:
    """Open to High difference"""
    return Op(df) - Hi(df)


def OpLo(df: pd.DataFrame) -> pd.Series:
    """Open to Low difference"""
    return Op(df) - Lo(df)


def HiCl(df: pd.DataFrame) -> pd.Series:
    """High to Close difference"""
    return Hi(df) - Cl(df)


def HiLo(df: pd.DataFrame) -> pd.Series:
    """High to Low difference"""
    return Hi(df) - Lo(df)


def LoCl(df: pd.DataFrame) -> pd.Series:
    """Low to Close difference"""
    return Lo(df) - Cl(df)


def Gap(df: pd.DataFrame) -> pd.Series:
    """Measure Gap up / down in percentage"""
    return (Op(df) / lag(Cl(df)) - 1).dropna()


def lag(series: pd.Series, period: int = 1) -> pd.Series:
    """Return previous value of input series"""
    return series.shift(period)


def lead(series: pd.Series, period: int = 1) -> pd.Series:
    """Return next value of input series"""
    return series.shift(-period)


def last(series: pd.Series) -> float:
    """Return last value of input series"""
    if series.empty:
        raise IndexError("The Series is empty and has no elements.")
    return series.iloc[-1]


def first(series: pd.Series) -> float:
    """Return first value of input series"""
    if series.empty:
        raise IndexError("The Series is empty and has no elements.")
    return series.iloc[0]


def trend_score(df: Union[pd.DataFrame, pd.Series]) -> float:
    """
    Calculate trend score, a statistical measure to identify the strength of the time series.
    Range between -1 to +1.
    """
    if isinstance(df, pd.DataFrame):
        df = Cl(df)  # Assume we use closing prices for trend score

    log_returns = np.diff(np.log(df))

    mean = np.mean(log_returns)
    std = np.std(log_returns)
    n = len(log_returns)
    t_stat = mean / (std / np.sqrt(n))

    return np.clip(t_stat, a_max=1, a_min=-1)
