"""
formatting.py

Utility functions for formatting and displaying pandas DataFrames.

Includes:
- Numeric formatting to specified decimal places
- Truncation of large DataFrames for previewing

Part of the glazzbocks.utils module.
"""


def format_number(x, decimals=2):
    """
    Format a number to a fixed number of decimal places.

    Parameters:
    - x (float or int): The number to format.
    - decimals (int): Number of decimal places (default is 2).

    Returns:
    - str: Formatted number as a string.
    """
    return f"{x:.{decimals}f}"


def truncate_dataframe(df, max_rows=20, max_cols=20):
    """
    Truncate a DataFrame to a maximum number of rows and columns.

    Useful for quickly previewing large DataFrames.

    Parameters:
    - df (pd.DataFrame): Input DataFrame.
    - max_rows (int): Max number of rows to retain (default is 20).
    - max_cols (int): Max number of columns to retain (default is 20).

    Returns:
    - pd.DataFrame: Truncated DataFrame.
    """
    return df.iloc[:max_rows, :max_cols]
