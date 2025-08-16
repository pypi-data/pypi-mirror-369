"""
Advanced statistical analysis utilities for AskPandas.
Provides comprehensive statistical functions for data analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from scipy import stats
from scipy.stats import chi2_contingency, f_oneway, kruskal
import warnings


class StatisticalAnalyzer:
    """Advanced statistical analysis for dataframes."""

    def __init__(self, df: pd.DataFrame):
        """Initialize with a dataframe."""
        self.df = df
        self.numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = df.select_dtypes(
            include=["object", "category"]
        ).columns.tolist()

    def descriptive_statistics(self, columns: Optional[List[str]] = None) -> Dict:
        """Generate comprehensive descriptive statistics."""
        if columns is None:
            columns = self.numeric_cols

        stats_dict = {}
        for col in columns:
            if col in self.df.columns and self.df[col].dtype in ["int64", "float64"]:
                col_data = self.df[col].dropna()
                if len(col_data) > 0:
                    stats_dict[col] = {
                        "count": len(col_data),
                        "mean": col_data.mean(),
                        "median": col_data.median(),
                        "std": col_data.std(),
                        "min": col_data.min(),
                        "max": col_data.max(),
                        "q1": col_data.quantile(0.25),
                        "q3": col_data.quantile(0.75),
                        "iqr": col_data.quantile(0.75) - col_data.quantile(0.25),
                        "skewness": col_data.skew(),
                        "kurtosis": col_data.kurtosis(),
                        "missing_count": self.df[col].isnull().sum(),
                        "missing_percentage": (
                            self.df[col].isnull().sum() / len(self.df)
                        )
                        * 100,
                    }

        return stats_dict

    def correlation_analysis(
        self, method: str = "pearson", significance_level: float = 0.05
    ) -> Dict:
        """Perform comprehensive correlation analysis."""
        if len(self.numeric_cols) < 2:
            return {"error": "Need at least 2 numeric columns for correlation analysis"}

        # Calculate correlation matrix
        corr_matrix = self.df[self.numeric_cols].corr(method=method)

        # Calculate p-values for significance testing
        p_values = pd.DataFrame(index=self.numeric_cols, columns=self.numeric_cols)

        for i, col1 in enumerate(self.numeric_cols):
            for j, col2 in enumerate(self.numeric_cols):
                if i != j:
                    try:
                        if method == "pearson":
                            corr, p_val = stats.pearsonr(
                                self.df[col1].dropna(), self.df[col2].dropna()
                            )
                        elif method == "spearman":
                            corr, p_val = stats.spearmanr(
                                self.df[col1].dropna(), self.df[col2].dropna()
                            )
                        else:
                            corr, p_val = stats.kendalltau(
                                self.df[col1].dropna(), self.df[col2].dropna()
                            )
                        p_values.loc[col1, col2] = p_val
                    except:
                        p_values.loc[col1, col2] = np.nan

        # Identify significant correlations
        significant_correlations = []
        for i, col1 in enumerate(self.numeric_cols):
            for j, col2 in enumerate(self.numeric_cols):
                if i < j:  # Avoid duplicates
                    corr_val = corr_matrix.loc[col1, col2]
                    p_val = p_values.loc[col1, col2]

                    if not pd.isna(p_val) and p_val < significance_level:
                        significance = (
                            "high"
                            if abs(corr_val) > 0.7
                            else "medium" if abs(corr_val) > 0.5 else "low"
                        )
                        significant_correlations.append(
                            {
                                "variables": (col1, col2),
                                "correlation": corr_val,
                                "p_value": p_val,
                                "significance": significance,
                                "interpretation": self._interpret_correlation(corr_val),
                            }
                        )

        return {
            "correlation_matrix": corr_matrix,
            "p_values": p_values,
            "significant_correlations": significant_correlations,
            "method": method,
            "significance_level": significance_level,
        }

    def _interpret_correlation(self, corr_val: float) -> str:
        """Interpret correlation coefficient."""
        abs_corr = abs(corr_val)
        if abs_corr >= 0.9:
            return "Very strong correlation"
        elif abs_corr >= 0.7:
            return "Strong correlation"
        elif abs_corr >= 0.5:
            return "Moderate correlation"
        elif abs_corr >= 0.3:
            return "Weak correlation"
        else:
            return "Very weak or no correlation"

    def outlier_detection(
        self, columns: Optional[List[str]] = None, method: str = "iqr"
    ) -> Dict:
        """Detect outliers using multiple methods."""
        if columns is None:
            columns = self.numeric_cols

        outliers = {}

        for col in columns:
            if col in self.df.columns and self.df[col].dtype in ["int64", "float64"]:
                col_data = self.df[col].dropna()
                if len(col_data) == 0:
                    continue

                col_outliers = {}

                if method == "iqr":
                    Q1 = col_data.quantile(0.25)
                    Q3 = col_data.quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR

                    outliers_mask = (col_data < lower_bound) | (col_data > upper_bound)
                    col_outliers["iqr"] = {
                        "count": outliers_mask.sum(),
                        "percentage": (outliers_mask.sum() / len(col_data)) * 100,
                        "indices": col_data[outliers_mask].index.tolist(),
                        "values": col_data[outliers_mask].tolist(),
                        "bounds": (lower_bound, upper_bound),
                    }

                elif method == "zscore":
                    z_scores = np.abs(stats.zscore(col_data))
                    outliers_mask = z_scores > 3

                    col_outliers["zscore"] = {
                        "count": outliers_mask.sum(),
                        "percentage": (outliers_mask.sum() / len(col_data)) * 100,
                        "indices": col_data[outliers_mask].index.tolist(),
                        "values": col_data[outliers_mask].tolist(),
                        "z_scores": z_scores[outliers_mask].tolist(),
                    }

                elif method == "both":
                    # IQR method
                    Q1 = col_data.quantile(0.25)
                    Q3 = col_data.quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR

                    outliers_mask_iqr = (col_data < lower_bound) | (
                        col_data > upper_bound
                    )

                    # Z-score method
                    z_scores = np.abs(stats.zscore(col_data))
                    outliers_mask_zscore = z_scores > 3

                    # Combined outliers
                    combined_mask = outliers_mask_iqr | outliers_mask_zscore

                    col_outliers["combined"] = {
                        "count": combined_mask.sum(),
                        "percentage": (combined_mask.sum() / len(col_data)) * 100,
                        "indices": col_data[combined_mask].index.tolist(),
                        "values": col_data[combined_mask].tolist(),
                        "iqr_outliers": outliers_mask_iqr.sum(),
                        "zscore_outliers": outliers_mask_zscore.sum(),
                    }

                outliers[col] = col_outliers

        return outliers

    def normality_tests(self, columns: Optional[List[str]] = None) -> Dict:
        """Perform normality tests on numeric columns."""
        if columns is None:
            columns = self.numeric_cols

        normality_results = {}

        for col in columns:
            if col in self.df.columns and self.df[col].dtype in ["int64", "float64"]:
                col_data = self.df[col].dropna()
                if len(col_data) < 3:
                    continue

                try:
                    # Shapiro-Wilk test (good for small samples)
                    shapiro_stat, shapiro_p = stats.shapiro(col_data)

                    # Anderson-Darling test
                    anderson_result = stats.anderson(col_data)

                    # Kolmogorov-Smirnov test
                    ks_stat, ks_p = stats.kstest(
                        col_data, "norm", args=(col_data.mean(), col_data.std())
                    )

                    normality_results[col] = {
                        "shapiro_wilk": {
                            "statistic": shapiro_stat,
                            "p_value": shapiro_p,
                            "is_normal": shapiro_p > 0.05,
                        },
                        "anderson_darling": {
                            "statistic": anderson_result.statistic,
                            "critical_values": anderson_result.critical_values,
                            "significance_levels": anderson_result.significance_level,
                        },
                        "kolmogorov_smirnov": {
                            "statistic": ks_stat,
                            "p_value": ks_p,
                            "is_normal": ks_p > 0.05,
                        },
                        "sample_size": len(col_data),
                        "overall_assessment": self._assess_normality(shapiro_p, ks_p),
                    }
                except Exception as e:
                    normality_results[col] = {"error": str(e)}

        return normality_results

    def _assess_normality(self, shapiro_p: float, ks_p: float) -> str:
        """Assess normality based on test results."""
        if shapiro_p > 0.05 and ks_p > 0.05:
            return "Likely normal"
        elif shapiro_p > 0.01 and ks_p > 0.01:
            return "Possibly normal"
        else:
            return "Likely not normal"

    def hypothesis_testing(self, test_type: str, **kwargs) -> Dict:
        """Perform various hypothesis tests."""
        if test_type == "t_test_independent":
            return self._independent_t_test(**kwargs)
        elif test_type == "t_test_paired":
            return self._paired_t_test(**kwargs)
        elif test_type == "anova":
            return self._anova_test(**kwargs)
        elif test_type == "chi_square":
            return self._chi_square_test(**kwargs)
        elif test_type == "mann_whitney":
            return self._mann_whitney_test(**kwargs)
        elif test_type == "kruskal_wallis":
            return self._kruskal_wallis_test(**kwargs)
        else:
            return {"error": f"Unknown test type: {test_type}"}

    def _independent_t_test(
        self, group_col: str, value_col: str, group1: str, group2: str
    ) -> Dict:
        """Perform independent t-test."""
        try:
            group1_data = self.df[self.df[group_col] == group1][value_col].dropna()
            group2_data = self.df[self.df[group_col] == group2][value_col].dropna()

            if len(group1_data) < 2 or len(group2_data) < 2:
                return {"error": "Insufficient data for t-test"}

            # Perform t-test
            t_stat, p_val = stats.ttest_ind(group1_data, group2_data)

            # Calculate effect size (Cohen's d)
            pooled_std = np.sqrt(
                (
                    (len(group1_data) - 1) * group1_data.var()
                    + (len(group2_data) - 1) * group2_data.var()
                )
                / (len(group1_data) + len(group2_data) - 2)
            )
            cohens_d = (group1_data.mean() - group2_data.mean()) / pooled_std

            return {
                "test_type": "Independent t-test",
                "groups": (group1, group2),
                "t_statistic": t_stat,
                "p_value": p_val,
                "significant": p_val < 0.05,
                "effect_size": cohens_d,
                "effect_interpretation": self._interpret_cohens_d(cohens_d),
                "group1_stats": {
                    "n": len(group1_data),
                    "mean": group1_data.mean(),
                    "std": group1_data.std(),
                },
                "group2_stats": {
                    "n": len(group2_data),
                    "mean": group2_data.mean(),
                    "std": group2_data.std(),
                },
            }
        except Exception as e:
            return {"error": str(e)}

    def _interpret_cohens_d(self, d: float) -> str:
        """Interpret Cohen's d effect size."""
        abs_d = abs(d)
        if abs_d < 0.2:
            return "Small effect"
        elif abs_d < 0.5:
            return "Small to medium effect"
        elif abs_d < 0.8:
            return "Medium effect"
        else:
            return "Large effect"

    def _anova_test(self, group_col: str, value_col: str) -> Dict:
        """Perform one-way ANOVA test."""
        try:
            groups = self.df[group_col].unique()
            group_data = [
                self.df[self.df[group_col] == group][value_col].dropna()
                for group in groups
            ]

            # Check if all groups have sufficient data
            if any(len(data) < 2 for data in group_data):
                return {"error": "Insufficient data for ANOVA"}

            # Perform ANOVA
            f_stat, p_val = f_oneway(*group_data)

            # Calculate effect size (eta-squared)
            total_ss = sum((data - data.mean()) ** 2 for data in group_data)
            between_ss = sum(
                len(data) * (data.mean() - self.df[value_col].mean()) ** 2
                for data in group_data
            )
            eta_squared = between_ss / total_ss if total_ss > 0 else 0

            return {
                "test_type": "One-way ANOVA",
                "groups": groups.tolist(),
                "f_statistic": f_stat,
                "p_value": p_val,
                "significant": p_val < 0.05,
                "effect_size": eta_squared,
                "effect_interpretation": self._interpret_eta_squared(eta_squared),
                "group_stats": {
                    group: {"n": len(data), "mean": data.mean(), "std": data.std()}
                    for group, data in zip(groups, group_data)
                },
            }
        except Exception as e:
            return {"error": str(e)}

    def _interpret_eta_squared(self, eta_squared: float) -> str:
        """Interpret eta-squared effect size."""
        if eta_squared < 0.01:
            return "Small effect"
        elif eta_squared < 0.06:
            return "Medium effect"
        else:
            return "Large effect"

    def _chi_square_test(self, var1: str, var2: str) -> Dict:
        """Perform chi-square test of independence."""
        try:
            if var1 not in self.categorical_cols or var2 not in self.categorical_cols:
                return {"error": "Both variables must be categorical"}

            # Create contingency table
            contingency_table = pd.crosstab(self.df[var1], self.df[var2])

            # Perform chi-square test
            chi2_stat, p_val, dof, expected = chi2_contingency(contingency_table)

            # Calculate Cramer's V (effect size)
            n = len(self.df)
            min_dim = min(contingency_table.shape) - 1
            cramers_v = np.sqrt(chi2_stat / (n * min_dim)) if min_dim > 0 else 0

            return {
                "test_type": "Chi-square test of independence",
                "variables": (var1, var2),
                "chi2_statistic": chi2_stat,
                "p_value": p_val,
                "degrees_of_freedom": dof,
                "significant": p_val < 0.05,
                "effect_size": cramers_v,
                "effect_interpretation": self._interpret_cramers_v(cramers_v),
                "contingency_table": contingency_table.to_dict(),
                "expected_frequencies": expected.tolist(),
            }
        except Exception as e:
            return {"error": str(e)}

    def _interpret_cramers_v(self, v: float) -> str:
        """Interpret Cramer's V effect size."""
        if v < 0.1:
            return "Small effect"
        elif v < 0.3:
            return "Medium effect"
        else:
            return "Large effect"

    def distribution_analysis(self, columns: Optional[List[str]] = None) -> Dict:
        """Analyze distribution characteristics of numeric columns."""
        if columns is None:
            columns = self.numeric_cols

        distribution_results = {}

        for col in columns:
            if col in self.df.columns and self.df[col].dtype in ["int64", "float64"]:
                col_data = self.df[col].dropna()
                if len(col_data) == 0:
                    continue

                try:
                    # Basic distribution stats
                    mean = col_data.mean()
                    median = col_data.median()
                    mode = (
                        col_data.mode().iloc[0] if not col_data.mode().empty else None
                    )

                    # Skewness and kurtosis
                    skewness = col_data.skew()
                    kurtosis = col_data.kurtosis()

                    # Percentiles
                    percentiles = col_data.quantile(
                        [0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95]
                    )

                    # Distribution shape assessment
                    shape_assessment = self._assess_distribution_shape(
                        skewness, kurtosis
                    )

                    distribution_results[col] = {
                        "central_tendency": {
                            "mean": mean,
                            "median": median,
                            "mode": mode,
                            "mean_median_diff": abs(mean - median),
                        },
                        "variability": {
                            "std": col_data.std(),
                            "variance": col_data.var(),
                            "range": col_data.max() - col_data.min(),
                            "iqr": col_data.quantile(0.75) - col_data.quantile(0.25),
                        },
                        "shape": {
                            "skewness": skewness,
                            "kurtosis": kurtosis,
                            "assessment": shape_assessment,
                        },
                        "percentiles": percentiles.to_dict(),
                        "sample_size": len(col_data),
                    }
                except Exception as e:
                    distribution_results[col] = {"error": str(e)}

        return distribution_results

    def _assess_distribution_shape(self, skewness: float, kurtosis: float) -> str:
        """Assess the shape of a distribution."""
        skew_assessment = (
            "symmetric"
            if abs(skewness) < 0.5
            else "right-skewed" if skewness > 0.5 else "left-skewed"
        )
        kurt_assessment = (
            "normal"
            if abs(kurtosis) < 2
            else "heavy-tailed" if kurtosis > 2 else "light-tailed"
        )

        return f"{skew_assessment}, {kurt_assessment}"

    def generate_statistical_report(self) -> str:
        """Generate a comprehensive statistical report."""
        report_parts = []

        # Basic info
        report_parts.append(f"STATISTICAL ANALYSIS REPORT")
        report_parts.append("=" * 50)
        report_parts.append(
            f"Dataset: {len(self.df)} rows × {len(self.df.columns)} columns"
        )
        report_parts.append(f"Numeric columns: {len(self.numeric_cols)}")
        report_parts.append(f"Categorical columns: {len(self.categorical_cols)}")
        report_parts.append("")

        # Descriptive statistics
        desc_stats = self.descriptive_statistics()
        if desc_stats:
            report_parts.append("DESCRIPTIVE STATISTICS")
            report_parts.append("-" * 30)
            for col, stats in desc_stats.items():
                report_parts.append(f"\n{col}:")
                report_parts.append(f"  Count: {stats['count']}")
                report_parts.append(f"  Mean: {stats['mean']:.4f}")
                report_parts.append(f"  Std: {stats['std']:.4f}")
                report_parts.append(
                    f"  Missing: {stats['missing_count']} ({stats['missing_percentage']:.1f}%)"
                )

        # Correlation analysis
        if len(self.numeric_cols) >= 2:
            report_parts.append("\nCORRELATION ANALYSIS")
            report_parts.append("-" * 30)
            corr_results = self.correlation_analysis()
            if "significant_correlations" in corr_results:
                for corr in corr_results["significant_correlations"][:5]:  # Top 5
                    var1, var2 = corr["variables"]
                    report_parts.append(
                        f"{var1} ↔ {var2}: r={corr['correlation']:.3f} (p={corr['p_value']:.4f})"
                    )

        # Outlier analysis
        report_parts.append("\nOUTLIER ANALYSIS")
        report_parts.append("-" * 30)
        outliers = self.outlier_detection(method="iqr")
        for col, col_outliers in outliers.items():
            if "iqr" in col_outliers:
                report_parts.append(
                    f"{col}: {col_outliers['iqr']['count']} outliers ({col_outliers['iqr']['percentage']:.1f}%)"
                )

        # Normality tests
        if len(self.numeric_cols) > 0:
            report_parts.append("\nNORMALITY TESTS")
            report_parts.append("-" * 30)
            normality = self.normality_tests()
            for col, results in normality.items():
                if "overall_assessment" in results:
                    report_parts.append(f"{col}: {results['overall_assessment']}")

        return "\n".join(report_parts)


def quick_stats(df: pd.DataFrame, columns: Optional[List[str]] = None) -> Dict:
    """Quick statistical summary for a dataframe."""
    analyzer = StatisticalAnalyzer(df)
    return analyzer.descriptive_statistics(columns)


def correlation_matrix(df: pd.DataFrame, method: str = "pearson") -> pd.DataFrame:
    """Quick correlation matrix calculation."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    return df[numeric_cols].corr(method=method)


def detect_outliers(
    df: pd.DataFrame, columns: Optional[List[str]] = None, method: str = "iqr"
) -> Dict:
    """Quick outlier detection."""
    analyzer = StatisticalAnalyzer(df)
    return analyzer.outlier_detection(columns, method)

    def _paired_t_test(
        self, group_col: str, value_col: str, group1: str, group2: str
    ) -> Dict:
        """Perform paired t-test."""
        try:
            # This would require paired data - for now return error
            return {"error": "Paired t-test not yet implemented"}
        except Exception as e:
            return {"error": str(e)}

    def _mann_whitney_test(
        self, group_col: str, value_col: str, group1: str, group2: str
    ) -> Dict:
        """Perform Mann-Whitney U test."""
        try:
            group1_data = self.df[self.df[group_col] == group1][value_col].dropna()
            group2_data = self.df[self.df[group_col] == group2][value_col].dropna()

            if len(group1_data) < 2 or len(group2_data) < 2:
                return {"error": "Insufficient data for Mann-Whitney test"}

            # Perform Mann-Whitney U test
            u_stat, p_val = stats.mannwhitneyu(
                group1_data, group2_data, alternative="two-sided"
            )

            return {
                "test_type": "Mann-Whitney U test",
                "groups": (group1, group2),
                "u_statistic": u_stat,
                "p_value": p_val,
                "significant": p_val < 0.05,
                "group1_stats": {"n": len(group1_data), "median": group1_data.median()},
                "group2_stats": {"n": len(group2_data), "median": group2_data.median()},
            }
        except Exception as e:
            return {"error": str(e)}

    def _kruskal_wallis_test(self, group_col: str, value_col: str) -> Dict:
        """Perform Kruskal-Wallis H test."""
        try:
            groups = self.df[group_col].unique()
            group_data = [
                self.df[self.df[group_col] == group][value_col].dropna()
                for group in groups
            ]

            # Check if all groups have sufficient data
            if any(len(data) < 2 for data in group_data):
                return {"error": "Insufficient data for Kruskal-Wallis test"}

            # Perform Kruskal-Wallis test
            h_stat, p_val = kruskal(*group_data)

            return {
                "test_type": "Kruskal-Wallis H test",
                "groups": groups.tolist(),
                "h_statistic": h_stat,
                "p_value": p_val,
                "significant": p_val < 0.05,
                "group_stats": {
                    group: {"n": len(data), "median": data.median()}
                    for group, data in zip(groups, group_data)
                },
            }
        except Exception as e:
            return {"error": str(e)}
