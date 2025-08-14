import pandas as pd
from quantmod.utils import convert_date_format

# import importlib.resources as pkg_resources
from importlib.resources import files
from . import data


def fetch_historical_data(
    symbol: str, start_date: str = None, end_date: str = None
) -> pd.DataFrame:
    """
    Load historical data for a given symbol

    Parameters
    ----------
    symbol : str
        The symbol to load data for, either 'spx' or 'nifty'
    start_date : str, optional
        The start date to load data for, in 'yyyy-mm-dd' format, by default None
    end_date : str, optional
        The end date to load data for, in 'yyyy-mm-dd' format, by default None

    Returns
    -------
    pd.DataFrame
        The historical data for the given symbol

    Raises
    ------
    ValueError
        If the symbol is invalid or the start date is greater than the end date
        If the start date is less than the first date in the dataset or the end date is greater than the last date in the dataset
        If the start date is greater than the last date in the dataset or the end date is less than the first date in the dataset
    """

    # def read_csv_file(filename):
    #     with pkg_resources.path(data, filename) as file_path:
    #         return pd.read_csv(file_path)

    def read_csv_file(filename):
        with files(data).joinpath(filename).open("r") as f:
            return pd.read_csv(f)

    if symbol.lower() == "spx":
        df = read_csv_file("spx.csv")
        # df = pd.read_csv("./data/spx.csv")
    elif symbol.lower() == "nifty":
        df = read_csv_file("nifty50.csv")
        # df = pd.read_csv("./data/nifty50.csv")
    else:
        raise ValueError("Invalid symbol. Only SPX & NIFTY is supported")

    df = df.rename(columns=str.lower)
    df = convert_date_format(df, "date")

    if start_date is None or end_date is None:
        return df

    elif start_date > end_date:
        raise ValueError("Start date should be less than or equal to end date")

    elif start_date < df.date.iloc[0] or end_date < df.date.iloc[0]:
        raise ValueError(f"Date should be greater than or equal to {df.date.iloc[0]}")

    elif start_date > df.date.iloc[-1] or end_date > df.date.iloc[-1]:
        raise ValueError(f"Date should be less than or equal to {df.date.iloc[-1]}")

    else:
        # Use query method for filtering based on date range
        query_str = f"date >= '{start_date}' and date <= '{end_date}'"
        return df.query(query_str)
