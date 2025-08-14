import numpy as np
import pandas as pd


def repeat_rows(df: pd.DataFrame, n: int) -> pd.DataFrame:
    """
    Repeat each row of a DataFrame a specified number of times.

    Args:
        df (pd.DataFrame): The input DataFrame whose rows will be repeated.
        n (int): The number of times to repeat each row.

    Returns:
        pd.DataFrame: A new DataFrame with each row repeated `n` times.
    """
    return pd.DataFrame(np.repeat(df.values, n, axis=0), columns=df.columns)
