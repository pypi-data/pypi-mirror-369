from __future__ import annotations
import pandas as pd
import numpy as np

def ensure_df(data) -> pd.DataFrame:
    """Return a copy of the input as a pandas DataFrame.
    Accepts DataFrame, dict-like, list/ndarray of rows, or 1D arrays.
    """
    if isinstance(data, pd.DataFrame):
        return data.copy()
    if isinstance(data, dict):
        return pd.DataFrame(data)
    if isinstance(data, (list, tuple, np.ndarray)):
        arr = np.array(data, dtype=object)
        if arr.ndim == 1:
            return pd.DataFrame({ "value": arr })
        return pd.DataFrame(arr)
    raise TypeError("data must be a pandas DataFrame, dict, or array-like")


def numeric_cols(df: pd.DataFrame):
    return df.select_dtypes(include=["number"]).columns.tolist()


def categorical_cols(df: pd.DataFrame):
    return df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()


def datetime_cols(df: pd.DataFrame):
    return df.select_dtypes(include=["datetime", "datetime64[ns]", "datetimetz"]).columns.tolist()
