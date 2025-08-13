"""
Module for data analysis in Excel and CSV files.
"""

from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd
from scipy import stats


def calculate_basic_stats(
    df: pd.DataFrame, columns: Optional[List[str]] = None
) -> Dict[str, Dict[str, float]]:
    """
    Calculates basic statistics for numeric columns in the DataFrame.

    Args:
        df: pandas DataFrame
        columns: Optional list of columns for analysis. If None, uses all numeric columns.  # noqa: E501

    Returns:
        Dictionary with statistics for each column
    """
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns.tolist()

    stats_dict = {}
    for col in columns:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            mode_value = df[col].mode()
            stats_dict[col] = {
                "mean": df[col].mean(),
                "median": df[col].median(),
                "mode": mode_value.iloc[0] if not mode_value.empty else None,
                "std": df[col].std(),
                "min": df[col].min(),
                "max": df[col].max(),
                "q1": df[col].quantile(0.25),
                "q3": df[col].quantile(0.75),
            }

    return stats_dict


def detect_outliers(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None,
    method: str = "zscore",
    threshold: float = 3.0,
) -> Dict[str, List[int]]:
    """
    Detects outliers in numeric columns using different methods.

    Args:
        df: pandas DataFrame
        columns: Optional list of columns for analysis
        method: Detection method ('zscore' or 'iqr')
        threshold: Threshold for outlier detection

    Returns:
        Dictionary with outlier indices for each column
    """
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns.tolist()

    outliers = {}
    for col in columns:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            if method == "zscore":
                z_scores = np.abs(stats.zscore(df[col].dropna()))
                outliers[col] = df[col].index[z_scores > threshold].tolist()
            elif method == "iqr":
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                outliers[col] = (
                    df[col]
                    .index[(df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))]
                    .tolist()
                )

    return outliers


def calculate_correlations(
    df: pd.DataFrame, columns: Optional[List[str]] = None, method: str = "pearson"
) -> pd.DataFrame:
    """
    Calculates correlations between numeric columns.

    Args:
        df: pandas DataFrame
        columns: Optional list of columns for analysis
        method: Correlation method ('pearson', 'spearman' or 'kendall')

    Returns:
        DataFrame with correlation matrix
    """
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns.tolist()

    return df[columns].corr(method=method)


def create_pivot_table(
    df: pd.DataFrame,
    index: Union[str, List[str]],
    columns: Optional[Union[str, List[str]]] = None,
    values: Optional[Union[str, List[str]]] = None,
    aggfunc: str = "mean",
) -> pd.DataFrame:
    """
    Creates a pivot table from the DataFrame.

    Args:
        df: pandas DataFrame
        index: Column(s) to use as index
        columns: Column(s) to use as columns
        values: Column(s) to use as values
        aggfunc: Aggregation function ('mean', 'sum', 'count', etc.)

    Returns:
        DataFrame with the pivot table
    """
    return pd.pivot_table(
        df, index=index, columns=columns, values=values, aggfunc=aggfunc
    )
