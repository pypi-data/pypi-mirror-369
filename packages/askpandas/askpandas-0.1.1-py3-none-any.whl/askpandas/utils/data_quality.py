"""
Advanced data quality assessment and cleaning utilities for AskPandas.
Provides comprehensive data quality analysis and automated cleaning capabilities.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union, Any
import re
from datetime import datetime
import warnings
from scipy import stats


class DataQualityAnalyzer:
    """Comprehensive data quality analysis and assessment."""

    def __init__(self, df: pd.DataFrame):
        """Initialize with a dataframe."""
        self.df = df
        self.original_shape = df.shape
        self.quality_report = {}

    def comprehensive_quality_assessment(self) -> Dict[str, Any]:
        """Perform comprehensive data quality assessment."""
        self.quality_report = {
            "basic_info": self._get_basic_info(),
            "missing_data": self._analyze_missing_data(),
            "duplicates": self._analyze_duplicates(),
            "data_types": self._analyze_data_types(),
            "value_ranges": self._analyze_value_ranges(),
            "consistency": self._analyze_consistency(),
            "outliers": self._detect_outliers(),
            "data_quality_score": 0.0,
            "recommendations": [],
        }

        # Calculate overall quality score
        self.quality_report["data_quality_score"] = self._calculate_quality_score()

        # Generate recommendations
        self.quality_report["recommendations"] = self._generate_recommendations()

        return self.quality_report

    def _get_basic_info(self) -> Dict[str, Any]:
        """Get basic information about the dataset."""
        return {
            "shape": self.df.shape,
            "total_cells": self.df.size,
            "memory_usage_mb": self.df.memory_usage(deep=True).sum() / 1024 / 1024,
            "column_count": len(self.df.columns),
            "row_count": len(self.df),
            "numeric_columns": len(self.df.select_dtypes(include=[np.number]).columns),
            "categorical_columns": len(
                self.df.select_dtypes(include=["object", "category"]).columns
            ),
            "datetime_columns": len(
                self.df.select_dtypes(include=["datetime"]).columns
            ),
            "boolean_columns": len(self.df.select_dtypes(include=["bool"]).columns),
        }

    def _analyze_missing_data(self) -> Dict[str, Any]:
        """Analyze missing data patterns."""
        missing_info = {}

        # Overall missing data
        total_missing = self.df.isnull().sum().sum()
        missing_info["total_missing"] = total_missing
        missing_info["total_missing_percentage"] = (total_missing / self.df.size) * 100

        # Missing data by column
        missing_by_column = self.df.isnull().sum()
        missing_info["missing_by_column"] = missing_by_column.to_dict()
        missing_info["missing_percentage_by_column"] = (
            missing_by_column / len(self.df) * 100
        ).to_dict()

        # Missing data patterns
        missing_patterns = self._identify_missing_patterns()
        missing_info["missing_patterns"] = missing_patterns

        # Columns with high missing data
        high_missing_threshold = 0.5  # 50%
        high_missing_cols = missing_by_column[
            missing_by_column / len(self.df) > high_missing_threshold
        ]
        missing_info["high_missing_columns"] = high_missing_cols.to_dict()

        return missing_info

    def _identify_missing_patterns(self) -> List[Dict[str, Any]]:
        """Identify patterns in missing data."""
        patterns = []

        # Check for completely empty columns
        empty_cols = self.df.columns[self.df.isnull().all()].tolist()
        if empty_cols:
            patterns.append(
                {
                    "type": "completely_empty_columns",
                    "columns": empty_cols,
                    "severity": "high",
                }
            )

        # Check for columns with same missing pattern
        missing_matrix = self.df.isnull()
        for i, col1 in enumerate(self.df.columns):
            for j, col2 in enumerate(self.df.columns[i + 1 :], i + 1):
                if missing_matrix[col1].equals(missing_matrix[col2]):
                    patterns.append(
                        {
                            "type": "same_missing_pattern",
                            "columns": [col1, col2],
                            "severity": "medium",
                        }
                    )

        # Check for systematic missing patterns
        for col in self.df.columns:
            if self.df[col].isnull().sum() > 0:
                # Check if missing data follows a pattern (e.g., every nth row)
                missing_indices = self.df[self.df[col].isnull()].index
                if len(missing_indices) > 1:
                    diffs = np.diff(missing_indices)
                    if len(set(diffs)) <= 2:  # If differences are consistent
                        patterns.append(
                            {
                                "type": "systematic_missing",
                                "column": col,
                                "pattern": f"Missing every {diffs[0]} rows approximately",
                                "severity": "medium",
                            }
                        )

        return patterns

    def _analyze_duplicates(self) -> Dict[str, Any]:
        """Analyze duplicate data."""
        duplicate_info = {}

        # Overall duplicates
        total_duplicates = self.df.duplicated().sum()
        duplicate_info["total_duplicates"] = total_duplicates
        duplicate_info["duplicate_percentage"] = (total_duplicates / len(self.df)) * 100

        # Duplicates by column
        duplicate_by_column = {}
        for col in self.df.columns:
            duplicate_by_column[col] = self.df[col].duplicated().sum()
        duplicate_info["duplicates_by_column"] = duplicate_by_column

        # Duplicate patterns
        duplicate_patterns = []

        # Check for exact duplicates
        if total_duplicates > 0:
            duplicate_patterns.append(
                {
                    "type": "exact_duplicates",
                    "count": total_duplicates,
                    "severity": (
                        "high" if total_duplicates > len(self.df) * 0.1 else "medium"
                    ),
                }
            )

        # Check for potential duplicates (similar but not exact)
        potential_duplicates = self._find_potential_duplicates()
        if potential_duplicates:
            duplicate_patterns.append(
                {
                    "type": "potential_duplicates",
                    "count": len(potential_duplicates),
                    "examples": potential_duplicates[:5],  # Show first 5 examples
                    "severity": "medium",
                }
            )

        duplicate_info["duplicate_patterns"] = duplicate_patterns

        return duplicate_info

    def _find_potential_duplicates(self) -> List[Tuple[int, int]]:
        """Find potential duplicates based on similarity."""
        potential_dups = []

        # For numeric columns, find rows with very similar values
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns

        if len(numeric_cols) > 0:
            # Use a simple similarity measure
            for i in range(len(self.df)):
                for j in range(
                    i + 1, min(i + 100, len(self.df))
                ):  # Check next 100 rows
                    similarity = self._calculate_row_similarity(i, j, numeric_cols)
                    if similarity > 0.95:  # 95% similarity threshold
                        potential_dups.append((i, j))

        return potential_dups

    def _calculate_row_similarity(
        self, row1_idx: int, row2_idx: int, numeric_cols: List[str]
    ) -> float:
        """Calculate similarity between two rows."""
        if len(numeric_cols) == 0:
            return 0.0

        row1 = self.df.loc[row1_idx, numeric_cols].fillna(0)
        row2 = self.df.loc[row2_idx, numeric_cols].fillna(0)

        # Calculate cosine similarity
        dot_product = np.dot(row1, row2)
        norm1 = np.linalg.norm(row1)
        norm2 = np.linalg.norm(row2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def _analyze_data_types(self) -> Dict[str, Any]:
        """Analyze data types and suggest optimizations."""
        type_info = {}

        # Current data types
        type_info["current_types"] = self.df.dtypes.to_dict()

        # Memory usage by type
        memory_by_type = {}
        for dtype in self.df.dtypes.unique():
            cols = self.df.select_dtypes(include=[dtype]).columns
            memory_by_type[str(dtype)] = (
                self.df[cols].memory_usage(deep=True).sum() / 1024 / 1024
            )
        type_info["memory_by_type"] = memory_by_type

        # Type optimization suggestions
        optimization_suggestions = []

        for col in self.df.columns:
            current_type = str(self.df[col].dtype)
            suggestion = self._suggest_type_optimization(col, current_type)
            if suggestion:
                optimization_suggestions.append(
                    {
                        "column": col,
                        "current_type": current_type,
                        "suggested_type": suggestion["new_type"],
                        "memory_saving_mb": suggestion["memory_saving"],
                        "reason": suggestion["reason"],
                    }
                )

        type_info["optimization_suggestions"] = optimization_suggestions

        return type_info

    def _suggest_type_optimization(
        self, col: str, current_type: str
    ) -> Optional[Dict[str, Any]]:
        """Suggest type optimization for a column."""
        if current_type.startswith("int"):
            # Check if we can use smaller int types
            col_data = self.df[col].dropna()
            if len(col_data) > 0:
                min_val = col_data.min()
                max_val = col_data.max()

                if min_val >= 0:
                    if max_val <= 255:
                        new_type = "uint8"
                        memory_saving = (
                            (
                                self.df[col].memory_usage(deep=True)
                                - self.df[col].astype(new_type).memory_usage(deep=True)
                            )
                            / 1024
                            / 1024
                        )
                        return {
                            "new_type": new_type,
                            "memory_saving": memory_saving,
                            "reason": f"Values range from {min_val} to {max_val}, can use uint8",
                        }
                    elif max_val <= 65535:
                        new_type = "uint16"
                        memory_saving = (
                            (
                                self.df[col].memory_usage(deep=True)
                                - self.df[col].astype(new_type).memory_usage(deep=True)
                            )
                            / 1024
                            / 1024
                        )
                        return {
                            "new_type": new_type,
                            "memory_saving": memory_saving,
                            "reason": f"Values range from {min_val} to {max_val}, can use uint16",
                        }
                else:
                    if min_val >= -128 and max_val <= 127:
                        new_type = "int8"
                        memory_saving = (
                            (
                                self.df[col].memory_usage(deep=True)
                                - self.df[col].astype(new_type).memory_usage(deep=True)
                            )
                            / 1024
                            / 1024
                        )
                        return {
                            "new_type": new_type,
                            "memory_saving": memory_saving,
                            "reason": f"Values range from {min_val} to {max_val}, can use int8",
                        }

        elif current_type.startswith("float"):
            # Check if we can use float32 instead of float64
            col_data = self.df[col].dropna()
            if len(col_data) > 0:
                # Check if precision loss is acceptable
                col_float32 = col_data.astype("float32")
                precision_loss = np.abs(col_data - col_float32).max()

                if precision_loss < 1e-6:  # Very small precision loss
                    memory_saving = (
                        (
                            self.df[col].memory_usage(deep=True)
                            - self.df[col].astype("float32").memory_usage(deep=True)
                        )
                        / 1024
                        / 1024
                    )
                    return {
                        "new_type": "float32",
                        "memory_saving": memory_saving,
                        "reason": f"Precision loss is {precision_loss:.2e}, can use float32",
                    }

        elif current_type == "object":
            # Check if we can convert to category
            unique_ratio = self.df[col].nunique() / len(self.df)
            if unique_ratio < 0.5:  # Less than 50% unique values
                memory_saving = (
                    (
                        self.df[col].memory_usage(deep=True)
                        - self.df[col].astype("category").memory_usage(deep=True)
                    )
                    / 1024
                    / 1024
                )
                return {
                    "new_type": "category",
                    "memory_saving": memory_saving,
                    "reason": f"Only {unique_ratio:.1%} unique values, can use category",
                }

        return None

    def _analyze_value_ranges(self) -> Dict[str, Any]:
        """Analyze value ranges and identify potential issues."""
        range_info = {}

        # Numeric column ranges
        numeric_ranges = {}
        for col in self.df.select_dtypes(include=[np.number]).columns:
            col_data = self.df[col].dropna()
            if len(col_data) > 0:
                numeric_ranges[col] = {
                    "min": col_data.min(),
                    "max": col_data.max(),
                    "range": col_data.max() - col_data.min(),
                    "mean": col_data.mean(),
                    "median": col_data.median(),
                    "std": col_data.std(),
                }
        range_info["numeric_ranges"] = numeric_ranges

        # Categorical column value counts
        categorical_counts = {}
        for col in self.df.select_dtypes(include=["object", "category"]).columns:
            value_counts = self.df[col].value_counts()
            categorical_counts[col] = {
                "unique_values": len(value_counts),
                "most_common": value_counts.index[0] if len(value_counts) > 0 else None,
                "most_common_count": (
                    value_counts.iloc[0] if len(value_counts) > 0 else 0
                ),
                "least_common": (
                    value_counts.index[-1] if len(value_counts) > 0 else None
                ),
                "least_common_count": (
                    value_counts.iloc[-1] if len(value_counts) > 0 else 0
                ),
            }
        range_info["categorical_counts"] = categorical_counts

        # Identify potential data quality issues
        data_issues = []

        # Check for suspicious patterns
        for col in self.df.columns:
            if self.df[col].dtype in ["int64", "float64"]:
                col_data = self.df[col].dropna()
                if len(col_data) > 0:
                    # Check for all zeros or all same values
                    if col_data.nunique() == 1:
                        data_issues.append(
                            {
                                "column": col,
                                "issue": "all_values_same",
                                "value": col_data.iloc[0],
                                "severity": "medium",
                            }
                        )

                    # Check for suspicious ranges
                    if col_data.max() == 0 and col_data.min() == 0:
                        data_issues.append(
                            {"column": col, "issue": "all_zeros", "severity": "high"}
                        )

        range_info["data_issues"] = data_issues

        return range_info

    def _analyze_consistency(self) -> Dict[str, Any]:
        """Analyze data consistency across columns."""
        consistency_info = {}

        # Check for logical inconsistencies
        logical_inconsistencies = []

        # Example: age should be positive
        for col in self.df.columns:
            if "age" in col.lower() and self.df[col].dtype in ["int64", "float64"]:
                negative_ages = self.df[self.df[col] < 0][col]
                if len(negative_ages) > 0:
                    logical_inconsistencies.append(
                        {
                            "type": "negative_age",
                            "column": col,
                            "count": len(negative_ages),
                            "severity": "high",
                        }
                    )

        # Example: dates should be in reasonable range
        for col in self.df.columns:
            if self.df[col].dtype == "object":
                # Try to detect date columns
                try:
                    pd.to_datetime(self.df[col].head(100))
                    # Check for unreasonable dates
                    dates = pd.to_datetime(self.df[col], errors="coerce")
                    if dates.notna().sum() > 0:
                        min_date = dates.min()
                        max_date = dates.max()
                        current_year = datetime.now().year

                        if min_date.year < 1900 or max_date.year > current_year + 10:
                            logical_inconsistencies.append(
                                {
                                    "type": "unreasonable_dates",
                                    "column": col,
                                    "min_date": min_date,
                                    "max_date": max_date,
                                    "severity": "medium",
                                }
                            )
                except:
                    pass

        consistency_info["logical_inconsistencies"] = logical_inconsistencies

        # Check for format consistency
        format_inconsistencies = []

        for col in self.df.select_dtypes(include=["object"]).columns:
            # Check for mixed formats
            sample_values = self.df[col].dropna().head(100)
            if len(sample_values) > 0:
                # Check for mixed case
                case_variations = sample_values.str.isupper().sum()
                if 0 < case_variations < len(sample_values):
                    format_inconsistencies.append(
                        {"column": col, "issue": "mixed_case", "severity": "low"}
                    )

                # Check for leading/trailing whitespace
                whitespace_count = sample_values.str.strip().ne(sample_values).sum()
                if whitespace_count > 0:
                    format_inconsistencies.append(
                        {
                            "column": col,
                            "issue": "leading_trailing_whitespace",
                            "count": whitespace_count,
                            "severity": "low",
                        }
                    )

        consistency_info["format_inconsistencies"] = format_inconsistencies

        return consistency_info

    def _detect_outliers(self) -> Dict[str, Any]:
        """Detect outliers using multiple methods."""
        outlier_info = {}

        for col in self.df.select_dtypes(include=[np.number]).columns:
            col_data = self.df[col].dropna()
            if len(col_data) < 4:  # Need at least 4 points for outlier detection
                continue

            col_outliers = {}

            # IQR method
            Q1 = col_data.quantile(0.25)
            Q3 = col_data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            iqr_outliers = col_data[(col_data < lower_bound) | (col_data > upper_bound)]
            col_outliers["iqr"] = {
                "count": len(iqr_outliers),
                "percentage": (len(iqr_outliers) / len(col_data)) * 100,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
            }

            # Z-score method
            z_scores = np.abs(stats.zscore(col_data))
            zscore_outliers = col_data[z_scores > 3]
            col_outliers["zscore"] = {
                "count": len(zscore_outliers),
                "percentage": (len(zscore_outliers) / len(col_data)) * 100,
            }

            outlier_info[col] = col_outliers

        return outlier_info

    def _calculate_quality_score(self) -> float:
        """Calculate overall data quality score (0-100)."""
        score = 100.0

        # Deduct points for missing data
        missing_percentage = self.quality_report["missing_data"][
            "total_missing_percentage"
        ]
        score -= min(missing_percentage * 2, 30)  # Max 30 points deduction

        # Deduct points for duplicates
        duplicate_percentage = self.quality_report["duplicates"]["duplicate_percentage"]
        score -= min(duplicate_percentage * 3, 20)  # Max 20 points deduction

        # Deduct points for data type issues
        type_issues = len(self.quality_report["data_types"]["optimization_suggestions"])
        score -= min(type_issues * 2, 15)  # Max 15 points deduction

        # Deduct points for consistency issues
        consistency_issues = len(
            self.quality_report["consistency"]["logical_inconsistencies"]
        ) + len(self.quality_report["consistency"]["format_inconsistencies"])
        score -= min(consistency_issues * 3, 20)  # Max 20 points deduction

        # Deduct points for outliers (if excessive)
        outlier_penalty = 0
        for col, outliers in self.quality_report["outliers"].items():
            if (
                "iqr" in outliers and outliers["iqr"]["percentage"] > 10
            ):  # More than 10% outliers
                outlier_penalty += 5
        score -= min(outlier_penalty, 15)  # Max 15 points deduction

        return max(score, 0.0)  # Ensure score doesn't go below 0

    def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate actionable recommendations for data quality improvement."""
        recommendations = []

        # Missing data recommendations
        missing_data = self.quality_report["missing_data"]
        if missing_data["total_missing_percentage"] > 20:
            recommendations.append(
                {
                    "priority": "high",
                    "category": "missing_data",
                    "action": "Investigate missing data patterns and consider data collection improvements",
                    "impact": "High impact on analysis reliability",
                }
            )

        # Duplicate recommendations
        duplicates = self.quality_report["duplicates"]
        if duplicates["duplicate_percentage"] > 5:
            recommendations.append(
                {
                    "priority": "high",
                    "category": "duplicates",
                    "action": "Remove or investigate duplicate records",
                    "impact": "Data integrity and analysis accuracy",
                }
            )

        # Data type optimization recommendations
        data_types = self.quality_report["data_types"]
        if data_types["optimization_suggestions"]:
            total_savings = sum(
                s["memory_saving_mb"] for s in data_types["optimization_suggestions"]
            )
            if total_savings > 10:  # More than 10MB savings
                recommendations.append(
                    {
                        "priority": "medium",
                        "category": "data_types",
                        "action": f"Optimize data types to save {total_savings:.1f}MB memory",
                        "impact": "Memory efficiency and performance",
                    }
                )

        # Consistency recommendations
        consistency = self.quality_report["consistency"]
        if consistency["logical_inconsistencies"]:
            recommendations.append(
                {
                    "priority": "high",
                    "category": "consistency",
                    "action": "Fix logical inconsistencies in data",
                    "impact": "Data validity and business logic",
                }
            )

        # Outlier recommendations
        outliers = self.quality_report["outliers"]
        outlier_issues = []
        for col, col_outliers in outliers.items():
            if "iqr" in col_outliers and col_outliers["iqr"]["percentage"] > 15:
                outlier_issues.append(col)

        if outlier_issues:
            recommendations.append(
                {
                    "priority": "medium",
                    "category": "outliers",
                    "action": f'Investigate outliers in columns: {", ".join(outlier_issues[:3])}',
                    "impact": "Data quality and analysis robustness",
                }
            )

        return recommendations

    def generate_quality_report(self) -> str:
        """Generate a human-readable quality report."""
        if not self.quality_report:
            self.comprehensive_quality_assessment()

        report_parts = []

        # Header
        report_parts.append("DATA QUALITY ASSESSMENT REPORT")
        report_parts.append("=" * 50)
        report_parts.append(
            f"Dataset: {self.original_shape[0]} rows × {self.original_shape[1]} columns"
        )
        report_parts.append(
            f"Overall Quality Score: {self.quality_report['data_quality_score']:.1f}/100"
        )
        report_parts.append("")

        # Missing data summary
        missing = self.quality_report["missing_data"]
        report_parts.append("MISSING DATA ANALYSIS")
        report_parts.append("-" * 30)
        report_parts.append(
            f"Total missing cells: {missing['total_missing']:,} ({missing['total_missing_percentage']:.1f}%)"
        )

        if missing["high_missing_columns"]:
            report_parts.append("Columns with >50% missing data:")
            for col, count in missing["high_missing_columns"].items():
                percentage = (count / len(self.df)) * 100
                report_parts.append(f"  {col}: {count:,} ({percentage:.1f}%)")

        # Duplicate analysis
        duplicates = self.quality_report["duplicates"]
        report_parts.append(f"\nDUPLICATE ANALYSIS")
        report_parts.append("-" * 30)
        report_parts.append(
            f"Total duplicate rows: {duplicates['total_duplicates']:,} ({duplicates['duplicate_percentage']:.1f}%)"
        )

        # Data type analysis
        data_types = self.quality_report["data_types"]
        if data_types["optimization_suggestions"]:
            report_parts.append(f"\nDATA TYPE OPTIMIZATION")
            report_parts.append("-" * 30)
            total_savings = sum(
                s["memory_saving_mb"] for s in data_types["optimization_suggestions"]
            )
            report_parts.append(f"Potential memory savings: {total_savings:.1f}MB")

            for suggestion in data_types["optimization_suggestions"][:5]:  # Show top 5
                if 'new_type' in suggestion and 'current_type' in suggestion:
                    report_parts.append(
                        f"  {suggestion['column']}: {suggestion['current_type']} → {suggestion['new_type']} "
                        f"(save {suggestion['memory_saving_mb']:.1f}MB)"
                    )

        # Consistency issues
        consistency = self.quality_report["consistency"]
        if (
            consistency["logical_inconsistencies"]
            or consistency["format_inconsistencies"]
        ):
            report_parts.append(f"\nCONSISTENCY ISSUES")
            report_parts.append("-" * 30)

            for issue in consistency["logical_inconsistencies"]:
                report_parts.append(
                    f"  {issue['type']} in {issue['column']}: {issue['count']} instances"
                )

            for issue in consistency["format_inconsistencies"]:
                report_parts.append(f"  {issue['issue']} in {issue['column']}")

        # Recommendations
        recommendations = self.quality_report["recommendations"]
        if recommendations:
            report_parts.append(f"\nRECOMMENDATIONS")
            report_parts.append("-" * 30)
            for i, rec in enumerate(recommendations, 1):
                report_parts.append(f"{i}. [{rec['priority'].upper()}] {rec['action']}")
                report_parts.append(f"   Impact: {rec['impact']}")

        return "\n".join(report_parts)


class DataCleaner:
    """Advanced data cleaning and preprocessing."""

    def __init__(self, df: pd.DataFrame):
        """Initialize with a dataframe."""
        self.df = df.copy()
        self.cleaning_log = []

    def auto_clean(self, aggressive: bool = False) -> pd.DataFrame:
        """Automatically clean the dataframe based on common issues."""
        self.cleaning_log = []

        # Basic cleaning
        self._remove_leading_trailing_whitespace()
        self._standardize_case()
        self._fix_data_types()

        if aggressive:
            self._remove_duplicates()
            self._handle_missing_values()
            self._remove_outliers()

        return self.df

    def _remove_leading_trailing_whitespace(self):
        """Remove leading and trailing whitespace from string columns."""
        for col in self.df.select_dtypes(include=["object"]).columns:
            if self.df[col].dtype == "object":
                original_nulls = self.df[col].isnull().sum()
                self.df[col] = self.df[col].str.strip()
                new_nulls = self.df[col].isnull().sum()

                if new_nulls > original_nulls:
                    self.cleaning_log.append(
                        f"Warning: Converting empty strings to NaN in {col}"
                    )

    def _standardize_case(self):
        """Standardize case for categorical columns."""
        for col in self.df.select_dtypes(include=["object"]).columns:
            # Check if column contains mixed case
            sample_values = self.df[col].dropna().head(100)
            if len(sample_values) > 0:
                case_variations = sample_values.str.isupper().sum()
                if 0 < case_variations < len(sample_values):
                    # Convert to title case for consistency
                    self.df[col] = self.df[col].str.title()
                    self.cleaning_log.append(
                        f"Standardized case to title case in {col}"
                    )

    def _fix_data_types(self):
        """Automatically fix data types where possible."""
        for col in self.df.columns:
            if self.df[col].dtype == "object":
                # Try to convert to numeric
                try:
                    numeric_col = pd.to_numeric(self.df[col], errors="coerce")
                    if (
                        numeric_col.notna().sum() > len(self.df) * 0.8
                    ):  # 80% conversion success
                        self.df[col] = numeric_col
                        self.cleaning_log.append(f"Converted {col} to numeric type")
                        continue
                except:
                    pass

                # Try to convert to datetime
                try:
                    datetime_col = pd.to_datetime(self.df[col], errors="coerce")
                    if (
                        datetime_col.notna().sum() > len(self.df) * 0.8
                    ):  # 80% conversion success
                        self.df[col] = datetime_col
                        self.cleaning_log.append(f"Converted {col} to datetime type")
                        continue
                except:
                    pass

                # Try to convert to category if low cardinality
                unique_ratio = self.df[col].nunique() / len(self.df)
                if unique_ratio < 0.5:  # Less than 50% unique values
                    self.df[col] = self.df[col].astype("category")
                    self.cleaning_log.append(f"Converted {col} to category type")

    def _remove_duplicates(self):
        """Remove duplicate rows."""
        original_count = len(self.df)
        self.df = self.df.drop_duplicates()
        removed_count = original_count - len(self.df)

        if removed_count > 0:
            self.cleaning_log.append(f"Removed {removed_count} duplicate rows")

    def _handle_missing_values(self):
        """Handle missing values intelligently."""
        for col in self.df.columns:
            missing_count = self.df[col].isnull().sum()
            if missing_count > 0:
                missing_percentage = (missing_count / len(self.df)) * 100

                if missing_percentage > 50:
                    # Remove column if more than 50% missing
                    self.df = self.df.drop(columns=[col])
                    self.cleaning_log.append(
                        f"Dropped column {col} (>{missing_percentage:.1f}% missing)"
                    )
                elif missing_percentage > 20:
                    # Remove rows with missing values if 20-50% missing
                    self.df = self.df.dropna(subset=[col])
                    self.cleaning_log.append(
                        f"Removed rows with missing values in {col}"
                    )
                else:
                    # Fill missing values based on data type
                    if self.df[col].dtype in ["int64", "float64"]:
                        fill_value = self.df[col].median()
                        self.df[col] = self.df[col].fillna(fill_value)
                        self.cleaning_log.append(
                            f"Filled missing values in {col} with median: {fill_value}"
                        )
                    elif self.df[col].dtype == "object":
                        fill_value = (
                            self.df[col].mode().iloc[0]
                            if not self.df[col].mode().empty
                            else "Unknown"
                        )
                        self.df[col] = self.df[col].fillna(fill_value)
                        self.cleaning_log.append(
                            f"Filled missing values in {col} with mode: {fill_value}"
                        )

    def _remove_outliers(self):
        """Remove outliers using IQR method."""
        for col in self.df.select_dtypes(include=[np.number]).columns:
            col_data = self.df[col].dropna()
            if len(col_data) < 4:
                continue

            Q1 = col_data.quantile(0.25)
            Q3 = col_data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outliers_mask = (self.df[col] < lower_bound) | (self.df[col] > upper_bound)
            outlier_count = outliers_mask.sum()

            if outlier_count > 0:
                self.df = self.df[~outliers_mask]
                self.cleaning_log.append(f"Removed {outlier_count} outliers from {col}")

    def get_cleaning_log(self) -> List[str]:
        """Get the cleaning operations log."""
        return self.cleaning_log

    def get_cleaning_summary(self) -> Dict[str, Any]:
        """Get a summary of cleaning operations."""
        return {
            "original_shape": self.df.shape,
            "cleaning_operations": len(self.cleaning_log),
            "cleaning_log": self.cleaning_log,
        }


# Convenience functions
def assess_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """Quick data quality assessment."""
    analyzer = DataQualityAnalyzer(df)
    return analyzer.comprehensive_quality_assessment()


def clean_dataframe(
    df: pd.DataFrame, aggressive: bool = False
) -> Tuple[pd.DataFrame, List[str]]:
    """Quick data cleaning."""
    cleaner = DataCleaner(df)
    cleaned_df = cleaner.auto_clean(aggressive)
    return cleaned_df, cleaner.get_cleaning_log()


def generate_quality_report(df: pd.DataFrame) -> str:
    """Generate a comprehensive quality report."""
    analyzer = DataQualityAnalyzer(df)
    return analyzer.generate_quality_report()
