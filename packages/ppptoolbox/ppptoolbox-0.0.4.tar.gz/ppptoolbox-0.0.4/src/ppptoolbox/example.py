import pandas as pd

def greet(name: str) -> str:
    """Return a greeting message."""
    return f"Hello, {name}!"

def greet_test(name: str) -> str:
    """Return a greeting message."""
    return f"Hello, {name}!"

def get_column_mean(df: pd.DataFrame, column: str) -> float:
    """
    Calculate the mean of a given column in a DataFrame.
    Raises ValueError if the column does not exist or contains non-numeric values.
    """
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame.")
    if not pd.api.types.is_numeric_dtype(df[column]):
        raise ValueError(f"Column '{column}' must be numeric.")
    return df[column].mean()