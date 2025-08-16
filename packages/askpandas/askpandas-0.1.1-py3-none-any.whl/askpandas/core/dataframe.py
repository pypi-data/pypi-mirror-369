import pandas as pd
from typing import Any, Dict, List, Optional, Union
from ..utils.helpers import (
    validate_dataframe,
    get_dataframe_summary,
    clean_column_names,
)
import numpy as np


class AskDataFrame:
    """Enhanced DataFrame with AI-powered capabilities."""

    def __init__(self, data: Any):
        """Initialize an AskDataFrame from various input types."""
        try:
            self.df = validate_dataframe(data)
        except Exception as e:
            raise ValueError(f"Failed to create DataFrame: {e}")

        # Store original data source for reference
        self._source = data if isinstance(data, str) else "data"

        # Initialize engine (will be set later)
        self._engine = None

    def _get_engine(self):
        """Get or create the engine instance."""
        if self._engine is None:
            # Import here to avoid circular imports
            from .. import get_llm
            from ..core.engine import AskPandasEngine

            llm = get_llm()
            if llm:
                self._engine = AskPandasEngine(llm)
        return self._engine

    def chat(self, query: str) -> Any:
        """Query the dataframe using natural language."""
        engine = self._get_engine()
        if engine is None:
            raise ValueError("No LLM configured. Use askpandas.set_llm() to set one.")

        return engine.process_query(query, [self])

    def info(self) -> str:
        """Return a string with dataframe metadata and sample data."""
        summary = get_dataframe_summary(self.df)

        info_str = f"""
DataFrame Info:
- Shape: {summary['shape']}
- Columns: {summary['columns']}
- Data types: {summary['dtypes']}
- Memory usage: {summary['memory_usage'] / 1024 / 1024:.2f} MB
- Null counts: {summary['null_counts']}
- Unique counts: {summary['unique_counts']}
- Sample data (first 3 rows):
{self.df.head(3).to_string()}
"""
        return info_str

    def describe(self) -> pd.DataFrame:
        """Get statistical description of the DataFrame."""
        return self.df.describe(include="all")

    def head(self, n: int = 5) -> pd.DataFrame:
        """Get first n rows of the DataFrame."""
        return self.df.head(n)

    def tail(self, n: int = 5) -> pd.DataFrame:
        """Get last n rows of the DataFrame."""
        return self.df.tail(n)

    def shape(self) -> tuple:
        """Get the shape of the DataFrame."""
        return self.df.shape

    def columns(self) -> List[str]:
        """Get the column names."""
        return list(self.df.columns)

    def dtypes(self) -> Dict[str, str]:
        """Get the data types of columns."""
        return dict(self.df.dtypes)

    def isnull(self) -> pd.DataFrame:
        """Get boolean mask of null values."""
        return self.df.isnull()

    def notnull(self) -> pd.DataFrame:
        """Get boolean mask of non-null values."""
        return self.df.notnull()

    def dropna(self, **kwargs) -> "AskDataFrame":
        """Drop rows with null values."""
        return AskDataFrame(self.df.dropna(**kwargs))

    def fillna(self, value, **kwargs) -> "AskDataFrame":
        """Fill null values."""
        return AskDataFrame(self.df.fillna(value, **kwargs))

    def sort_values(self, by: Union[str, List[str]], **kwargs) -> "AskDataFrame":
        """Sort DataFrame by values."""
        return AskDataFrame(self.df.sort_values(by, **kwargs))

    def groupby(
        self, by: Union[str, List[str]], **kwargs
    ) -> pd.core.groupby.DataFrameGroupBy:
        """Group DataFrame by columns."""
        return self.df.groupby(by, **kwargs)

    def query(self, expr: str) -> "AskDataFrame":
        """Query DataFrame using string expression."""
        return AskDataFrame(self.df.query(expr))

    def select_dtypes(self, include=None, exclude=None) -> "AskDataFrame":
        """Select columns based on data types."""
        return AskDataFrame(self.df.select_dtypes(include=include, exclude=exclude))

    def clean_columns(self) -> "AskDataFrame":
        """Clean column names by removing special characters and standardizing format."""
        return AskDataFrame(clean_column_names(self.df))

    def to_csv(self, path: str, **kwargs) -> str:
        """Save DataFrame to CSV file."""
        try:
            self.df.to_csv(path, **kwargs)
            return f"DataFrame saved to {path}"
        except Exception as e:
            return f"Failed to save DataFrame: {e}"

    def to_json(self, path: str, **kwargs) -> str:
        """Save DataFrame to JSON file."""
        try:
            self.df.to_json(path, **kwargs)
            return f"DataFrame saved to {path}"
        except Exception as e:
            return f"Failed to save DataFrame: {e}"

    def get_summary_stats(self) -> Dict[str, Any]:
        """Get comprehensive summary statistics."""
        summary = get_dataframe_summary(self.df)

        # Add additional statistics
        summary.update(
            {
                "numeric_columns": list(
                    self.df.select_dtypes(include=[np.number]).columns
                ),
                "categorical_columns": list(
                    self.df.select_dtypes(include=["object"]).columns
                ),
                "datetime_columns": list(
                    self.df.select_dtypes(include=["datetime"]).columns
                ),
                "total_memory_mb": summary["memory_usage"] / 1024 / 1024,
                "duplicate_rows": self.df.duplicated().sum(),
                "unique_rows": self.df.drop_duplicates().shape[0],
            }
        )

        return summary

    def get_column_info(self, column: str) -> Dict[str, Any]:
        """Get detailed information about a specific column."""
        if column not in self.df.columns:
            raise ValueError(f"Column '{column}' not found in DataFrame")

        col_data = self.df[column]
        col_type = str(col_data.dtype)

        info = {
            "name": column,
            "dtype": col_type,
            "count": col_data.count(),
            "null_count": col_data.isnull().sum(),
            "unique_count": col_data.nunique(),
            "memory_usage": col_data.memory_usage(deep=True),
        }

        if col_type in ["int64", "float64"]:
            info.update(
                {
                    "min": col_data.min(),
                    "max": col_data.max(),
                    "mean": col_data.mean(),
                    "median": col_data.median(),
                    "std": col_data.std(),
                }
            )
        elif col_type == "object":
            info.update(
                {
                    "top_values": col_data.value_counts().head(5).to_dict(),
                    "most_common": (
                        col_data.mode().iloc[0] if not col_data.mode().empty else None
                    ),
                }
            )

        return info

    def __getattr__(self, name):
        """Delegate unknown attributes to the underlying pandas DataFrame."""
        return getattr(self.df, name)

    def __getitem__(self, key):
        """Allow indexing operations."""
        result = self.df[key]
        if isinstance(result, pd.DataFrame):
            return AskDataFrame(result)
        return result

    def __len__(self):
        """Return the length of the DataFrame."""
        return len(self.df)

    def __repr__(self):
        """String representation of the DataFrame."""
        return f"AskDataFrame(shape={self.df.shape}, columns={list(self.df.columns)})"

    def __str__(self):
        """String representation of the DataFrame."""
        return self.__repr__()
