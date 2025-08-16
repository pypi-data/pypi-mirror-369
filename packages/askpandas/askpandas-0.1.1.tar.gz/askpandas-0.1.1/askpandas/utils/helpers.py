import pandas as pd
import numpy as np
from typing import Any, Dict, List, Union


def validate_dataframe(df: Any) -> pd.DataFrame:
    """Validate and convert input to pandas DataFrame."""
    if isinstance(df, pd.DataFrame):
        return df
    elif isinstance(df, dict):
        return pd.DataFrame(df)
    elif isinstance(df, list):
        return pd.DataFrame(df)
    elif isinstance(df, str):
        if df.endswith('.csv'):
            return pd.read_csv(df, encoding='utf-8', low_memory=False)
        elif df.endswith('.json'):
            return pd.read_json(df, encoding='utf-8')
        else:
            raise ValueError("Unsupported file format. Use .csv or .json")
    else:
        try:
            return pd.DataFrame(df)
        except Exception as e:
            raise ValueError(f"Failed to create DataFrame: {e}")


def get_dataframe_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Get comprehensive summary of a DataFrame."""
    return {
        'shape': df.shape,
        'columns': list(df.columns),
        'dtypes': dict(df.dtypes),
        'memory_usage': df.memory_usage(deep=True).sum(),
        'null_counts': df.isnull().sum().to_dict(),
        'unique_counts': {col: df[col].nunique() for col in df.columns},
        'sample_data': df.head(3).to_dict('records')
    }


def format_number(value: Union[int, float]) -> str:
    """Format numbers for better readability."""
    if isinstance(value, (int, float)):
        if abs(value) >= 1e6:
            return f"{value/1e6:.2f}M"
        elif abs(value) >= 1e3:
            return f"{value/1e3:.2f}K"
        else:
            return f"{value:.2f}"
    return str(value)


def detect_data_types(df: pd.DataFrame) -> Dict[str, str]:
    """Detect and suggest optimal data types for DataFrame columns."""
    suggestions = {}
    
    for col in df.columns:
        if df[col].dtype == 'object':
            # Check if it's actually numeric
            try:
                pd.to_numeric(df[col], errors='raise')
                suggestions[col] = 'numeric'
            except (ValueError, TypeError):
                # Check if it's datetime
                try:
                    pd.to_datetime(df[col], errors='raise')
                    suggestions[col] = 'datetime'
                except (ValueError, TypeError):
                    suggestions[col] = 'categorical'
        elif df[col].dtype == 'int64':
            suggestions[col] = 'int'
        elif df[col].dtype == 'float64':
            suggestions[col] = 'float'
        else:
            suggestions[col] = str(df[col].dtype)
    
    return suggestions


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Clean column names by removing special characters and standardizing format."""
    df_clean = df.copy()
    df_clean.columns = (
        df_clean.columns
        .str.lower()
        .str.replace(r'[^\w\s]', '', regex=True)
        .str.replace(r'\s+', '_', regex=True)
        .str.strip('_')
    )
    return df_clean


def get_memory_usage_mb(df: pd.DataFrame) -> float:
    """Get memory usage of DataFrame in MB."""
    return df.memory_usage(deep=True).sum() / 1024 / 1024
