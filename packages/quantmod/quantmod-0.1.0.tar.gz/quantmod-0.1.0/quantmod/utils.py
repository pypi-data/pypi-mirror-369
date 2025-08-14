import pandas as pd

def convert_date_format(df: pd.DataFrame, date_column: str) -> pd.DataFrame:
    """
    Convert date column from 'dd/mm/yyyy' to 'yyyy-mm-dd' format
    
    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to convert the date column
    date_column : str
        The name of the date column to convert
        
    Returns
    -------
    pd.DataFrame
        The DataFrame with the date column converted to 'yyyy-mm-dd' format
    """
    
    # Convert the date column from 'dd/mm/yyyy' to datetime
    df[date_column] = pd.to_datetime(df[date_column], format='%d/%m/%Y')

    # Convert datetime to 'yyyy-mm-dd' format
    df[date_column] = df[date_column].dt.strftime('%Y-%m-%d')
    
    return df