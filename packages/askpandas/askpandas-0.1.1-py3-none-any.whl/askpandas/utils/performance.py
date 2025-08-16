"""
Performance benchmarking and optimization utilities for AskPandas.
Provides tools to measure and improve performance of data operations.
"""

import time
import psutil
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Callable, Tuple
from functools import wraps
import gc
import warnings


class PerformanceBenchmark:
    """Performance benchmarking for data operations."""

    def __init__(self):
        """Initialize the benchmarker."""
        self.benchmarks = {}
        self.memory_tracker = MemoryTracker()

    def benchmark_operation(
        self, name: str, operation: Callable, *args, **kwargs
    ) -> Dict[str, Any]:
        """Benchmark a single operation."""
        # Clear memory before operation
        gc.collect()

        # Get initial memory state
        initial_memory = self.memory_tracker.get_memory_usage()

        # Time the operation
        start_time = time.perf_counter()
        start_cpu = time.process_time()

        try:
            result = operation(*args, **kwargs)
            success = True
        except Exception as e:
            result = None
            success = False
            error = str(e)

        end_time = time.perf_counter()
        end_cpu = time.process_time()

        # Get final memory state
        final_memory = self.memory_tracker.get_memory_usage()

        # Calculate metrics
        wall_time = end_time - start_time
        cpu_time = end_cpu - start_cpu
        memory_delta = final_memory["rss"] - initial_memory["rss"]

        benchmark_result = {
            "name": name,
            "wall_time": wall_time,
            "cpu_time": cpu_time,
            "memory_delta_mb": memory_delta / 1024 / 1024,
            "initial_memory_mb": initial_memory["rss"] / 1024 / 1024,
            "final_memory_mb": final_memory["rss"] / 1024 / 1024,
            "success": success,
            "timestamp": time.time(),
        }

        if not success:
            benchmark_result["error"] = error

        self.benchmarks[name] = benchmark_result
        return benchmark_result

    def benchmark_dataframe_operations(
        self, df: pd.DataFrame, operations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Benchmark multiple dataframe operations."""
        results = {}

        for op_config in operations:
            op_name = op_config["name"]
            op_func = op_config["function"]
            op_args = op_config.get("args", [])
            op_kwargs = op_config.get("kwargs", {})

            # Create a copy of the dataframe for each operation
            df_copy = df.copy()

            # Wrap the operation to include the dataframe
            def wrapped_operation():
                return op_func(df_copy, *op_args, **op_kwargs)

            result = self.benchmark_operation(op_name, wrapped_operation)
            results[op_name] = result

            # Clean up
            del df_copy
            gc.collect()

        return results

    def compare_operations(
        self, operation_sets: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compare performance of different operation sets."""
        comparison = {
            "operation_sets": [],
            "performance_ranking": [],
            "recommendations": [],
        }

        for i, op_set in enumerate(operation_sets):
            set_name = op_set["name"]
            operations = op_set["operations"]

            # Benchmark this operation set
            total_time = 0
            total_memory = 0
            success_count = 0

            for op in operations:
                result = self.benchmark_operation(
                    f"{set_name}_{op['name']}", op["function"]
                )
                total_time += result["wall_time"]
                total_memory += result["memory_delta_mb"]
                if result["success"]:
                    success_count += 1

            set_result = {
                "name": set_name,
                "total_time": total_time,
                "total_memory_mb": total_memory,
                "operation_count": len(operations),
                "success_rate": success_count / len(operations),
                "average_time_per_op": total_time / len(operations),
                "average_memory_per_op": total_memory / len(operations),
            }

            comparison["operation_sets"].append(set_result)

        # Rank by performance
        comparison["performance_ranking"] = sorted(
            comparison["operation_sets"], key=lambda x: x["total_time"]
        )

        # Generate recommendations
        comparison["recommendations"] = self._generate_performance_recommendations(
            comparison
        )

        return comparison

    def _generate_performance_recommendations(
        self, comparison: Dict[str, Any]
    ) -> List[str]:
        """Generate performance improvement recommendations."""
        recommendations = []

        if not comparison["operation_sets"]:
            return recommendations

        # Find the fastest and slowest sets
        fastest = comparison["performance_ranking"][0]
        slowest = comparison["performance_ranking"][-1]

        if fastest["total_time"] > 0:
            speedup_factor = slowest["total_time"] / fastest["total_time"]
            if speedup_factor > 2:
                recommendations.append(
                    f"Operation set '{fastest['name']}' is {speedup_factor:.1f}x faster than '{slowest['name']}'. "
                    f"Consider using the faster approach."
                )

        # Memory efficiency recommendations
        memory_efficient = min(
            comparison["operation_sets"], key=lambda x: x["total_memory_mb"]
        )
        memory_inefficient = max(
            comparison["operation_sets"], key=lambda x: x["total_memory_mb"]
        )

        if memory_efficient["total_memory_mb"] > 0:
            memory_factor = (
                memory_inefficient["total_memory_mb"]
                / memory_efficient["total_memory_mb"]
            )
            if memory_factor > 1.5:
                recommendations.append(
                    f"Operation set '{memory_efficient['name']}' uses {memory_factor:.1f}x less memory. "
                    f"Consider for large datasets."
                )

        # General recommendations
        for op_set in comparison["operation_sets"]:
            if op_set["success_rate"] < 1.0:
                recommendations.append(
                    f"Operation set '{op_set['name']}' has {op_set['success_rate']:.1%} success rate. "
                    f"Check for errors or edge cases."
                )

        return recommendations

    def get_benchmark_summary(self) -> Dict[str, Any]:
        """Get a summary of all benchmarks."""
        if not self.benchmarks:
            return {"message": "No benchmarks have been run yet"}

        total_operations = len(self.benchmarks)
        successful_operations = sum(1 for b in self.benchmarks.values() if b["success"])

        total_time = sum(b["wall_time"] for b in self.benchmarks.values())
        total_memory = sum(b["memory_delta_mb"] for b in self.benchmarks.values())

        return {
            "total_operations": total_operations,
            "successful_operations": successful_operations,
            "success_rate": (
                successful_operations / total_operations if total_operations > 0 else 0
            ),
            "total_time": total_time,
            "total_memory_mb": total_memory,
            "average_time_per_op": (
                total_time / total_operations if total_operations > 0 else 0
            ),
            "average_memory_per_op": (
                total_memory / total_operations if total_operations > 0 else 0
            ),
            "benchmarks": self.benchmarks,
        }

    def clear_benchmarks(self):
        """Clear all benchmark results."""
        self.benchmarks.clear()


class MemoryTracker:
    """Track memory usage during operations."""

    def __init__(self):
        """Initialize the memory tracker."""
        self.process = psutil.Process()

    def get_memory_usage(self) -> Dict[str, int]:
        """Get current memory usage."""
        try:
            memory_info = self.process.memory_info()
            return {
                "rss": memory_info.rss,  # Resident Set Size
                "vms": memory_info.vms,  # Virtual Memory Size
                "percent": self.process.memory_percent(),
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return {"rss": 0, "vms": 0, "percent": 0}

    def get_memory_trend(
        self, duration: float = 1.0, interval: float = 0.1
    ) -> List[Dict[str, Any]]:
        """Track memory usage over time."""
        trend = []
        start_time = time.time()

        while time.time() - start_time < duration:
            memory_usage = self.get_memory_usage()
            trend.append(
                {
                    "timestamp": time.time(),
                    "memory_mb": memory_usage["rss"] / 1024 / 1024,
                    "percent": memory_usage["percent"],
                }
            )
            time.sleep(interval)

        return trend


class PerformanceOptimizer:
    """Optimize dataframe operations for better performance."""

    def __init__(self):
        """Initialize the optimizer."""
        self.optimization_suggestions = []

    def analyze_dataframe_performance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze dataframe for performance optimization opportunities."""
        analysis = {
            "size_analysis": self._analyze_size_optimization(df),
            "type_optimization": self._analyze_type_optimization(df),
            "memory_usage": self._analyze_memory_usage(df),
            "operation_optimization": self._analyze_operation_optimization(df),
            "recommendations": [],
        }

        # Generate recommendations
        analysis["recommendations"] = self._generate_optimization_recommendations(
            analysis
        )

        return analysis

    def _analyze_size_optimization(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze opportunities for size optimization."""
        size_analysis = {
            "current_size_mb": df.memory_usage(deep=True).sum() / 1024 / 1024,
            "optimized_size_mb": 0,
            "potential_savings_mb": 0,
            "optimization_opportunities": [],
        }

        # Analyze each column for optimization
        for col in df.columns:
            col_analysis = self._analyze_column_optimization(df[col])
            if col_analysis["can_optimize"]:
                size_analysis["optimization_opportunities"].append(col_analysis)
                size_analysis["potential_savings_mb"] += col_analysis[
                    "potential_savings_mb"
                ]

        size_analysis["optimized_size_mb"] = (
            size_analysis["current_size_mb"] - size_analysis["potential_savings_mb"]
        )

        return size_analysis

    def _analyze_column_optimization(self, series: pd.Series) -> Dict[str, Any]:
        """Analyze a single column for optimization opportunities."""
        analysis = {
            "column": series.name,
            "current_type": str(series.dtype),
            "current_size_mb": series.memory_usage(deep=True) / 1024 / 1024,
            "can_optimize": False,
            "suggested_type": None,
            "potential_savings_mb": 0,
            "reason": None,
        }

        # Integer optimization
        if str(series.dtype).startswith("int"):
            min_val = series.min()
            max_val = series.max()

            if min_val >= 0:
                if max_val <= 255:
                    analysis["suggested_type"] = "uint8"
                    analysis["can_optimize"] = True
                    analysis["reason"] = (
                        f"Values range from {min_val} to {max_val}, can use uint8"
                    )
                elif max_val <= 65535:
                    analysis["suggested_type"] = "uint16"
                    analysis["can_optimize"] = True
                    analysis["reason"] = (
                        f"Values range from {min_val} to {max_val}, can use uint16"
                    )
            else:
                if min_val >= -128 and max_val <= 127:
                    analysis["suggested_type"] = "int8"
                    analysis["can_optimize"] = True
                    analysis["reason"] = (
                        f"Values range from {min_val} to {max_val}, can use int8"
                    )

        # Float optimization
        elif str(series.dtype).startswith("float"):
            # Check if float32 precision is sufficient
            try:
                float32_series = series.astype("float32")
                precision_loss = np.abs(series - float32_series).max()

                if precision_loss < 1e-6:
                    analysis["suggested_type"] = "float32"
                    analysis["can_optimize"] = True
                    analysis["reason"] = (
                        f"Precision loss is {precision_loss:.2e}, can use float32"
                    )
            except:
                pass

        # Object to category optimization
        elif series.dtype == "object":
            unique_ratio = series.nunique() / len(series)
            if unique_ratio < 0.5:  # Less than 50% unique values
                analysis["suggested_type"] = "category"
                analysis["can_optimize"] = True
                analysis["reason"] = (
                    f"Only {unique_ratio:.1%} unique values, can use category"
                )

        # Calculate potential savings
        if analysis["can_optimize"]:
            try:
                optimized_series = series.astype(analysis["suggested_type"])
                optimized_size_mb = (
                    optimized_series.memory_usage(deep=True) / 1024 / 1024
                )
                analysis["potential_savings_mb"] = (
                    analysis["current_size_mb"] - optimized_size_mb
                )
            except:
                analysis["can_optimize"] = False

        return analysis

    def _analyze_type_optimization(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze data type optimization opportunities."""
        return {
            "current_types": df.dtypes.to_dict(),
            "optimization_opportunities": len(
                [
                    col
                    for col in df.columns
                    if self._analyze_column_optimization(df[col])["can_optimize"]
                ]
            ),
        }

    def _analyze_memory_usage(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze memory usage patterns."""
        memory_info = df.memory_usage(deep=True)

        return {
            "total_memory_mb": memory_info.sum() / 1024 / 1024,
            "memory_by_column": (memory_info / 1024 / 1024).to_dict(),
            "memory_by_type": self._get_memory_by_type(df),
            "peak_memory_mb": self._get_peak_memory(),
        }

    def _get_memory_by_type(self, df: pd.DataFrame) -> Dict[str, float]:
        """Get memory usage grouped by data type."""
        memory_by_type = {}
        for dtype in df.dtypes.unique():
            cols = df.select_dtypes(include=[dtype]).columns
            memory_by_type[str(dtype)] = (
                df[cols].memory_usage(deep=True).sum() / 1024 / 1024
            )

        return memory_by_type

    def _get_peak_memory(self) -> float:
        """Get peak memory usage."""
        try:
            process = psutil.Process()
            return process.memory_info().peak_wset / 1024 / 1024
        except:
            return 0.0

    def _analyze_operation_optimization(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze operation optimization opportunities."""
        return {
            "vectorization_opportunities": self._identify_vectorization_opportunities(
                df
            ),
            "chunking_recommendations": self._get_chunking_recommendations(df),
            "parallel_processing_opportunities": self._identify_parallel_processing_opportunities(
                df
            ),
        }

    def _identify_vectorization_opportunities(self, df: pd.DataFrame) -> List[str]:
        """Identify operations that could benefit from vectorization."""
        opportunities = []

        # Check for potential loops that could be vectorized
        # This is a simplified analysis - in practice, you'd need more sophisticated code analysis

        if len(df) > 10000:
            opportunities.append(
                "Large dataset detected - ensure vectorized operations"
            )

        if df.select_dtypes(include=["object"]).shape[1] > 0:
            opportunities.append(
                "String operations detected - consider vectorized string methods"
            )

        return opportunities

    def _get_chunking_recommendations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get recommendations for chunked processing."""
        total_memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024

        if total_memory_mb > 1000:  # More than 1GB
            return {
                "recommended": True,
                "chunk_size": max(1000, int(1000 / total_memory_mb * len(df))),
                "reason": f"Dataset size ({total_memory_mb:.1f}MB) suggests chunked processing",
            }
        else:
            return {
                "recommended": False,
                "reason": "Dataset size is manageable for in-memory processing",
            }

    def _identify_parallel_processing_opportunities(
        self, df: pd.DataFrame
    ) -> List[str]:
        """Identify operations that could benefit from parallel processing."""
        opportunities = []

        if len(df) > 50000:
            opportunities.append(
                "Large dataset - consider parallel processing for heavy computations"
            )

        if df.select_dtypes(include=[np.number]).shape[1] > 5:
            opportunities.append(
                "Multiple numeric columns - parallel correlation analysis possible"
            )

        return opportunities

    def _generate_optimization_recommendations(
        self, analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []

        # Size optimization recommendations
        size_analysis = analysis["size_analysis"]
        if size_analysis["potential_savings_mb"] > 10:
            recommendations.append(
                f"Memory optimization: Potential savings of {size_analysis['potential_savings_mb']:.1f}MB "
                f"({size_analysis['potential_savings_mb']/size_analysis['current_size_mb']*100:.1f}%)"
            )

        # Chunking recommendations
        chunking = analysis["operation_optimization"]["chunking_recommendations"]
        if chunking["recommended"]:
            recommendations.append(
                f"Processing optimization: Use chunked processing with chunk size {chunking['chunk_size']}"
            )

        # Vectorization recommendations
        vectorization = analysis["operation_optimization"][
            "vectorization_opportunities"
        ]
        if vectorization:
            recommendations.extend(vectorization)

        # Parallel processing recommendations
        parallel = analysis["operation_optimization"][
            "parallel_processing_opportunities"
        ]
        if parallel:
            recommendations.extend(parallel)

        return recommendations


def benchmark_function(name: str = None):
    """Decorator to benchmark a function."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            benchmarker = PerformanceBenchmark()
            op_name = name or func.__name__

            result = benchmarker.benchmark_operation(op_name, func, *args, **kwargs)

            # Print benchmark results
            print(f"Benchmark: {op_name}")
            print(f"  Time: {result['wall_time']:.4f}s")
            print(f"  Memory: {result['memory_delta_mb']:.2f}MB")
            print(f"  Success: {result['success']}")

            return result["result"] if result["success"] else None

        return wrapper

    return decorator


def optimize_dataframe(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """Quick dataframe optimization."""
    optimizer = PerformanceOptimizer()
    analysis = optimizer.analyze_dataframe_performance(df)

    # Apply optimizations
    optimized_df = df.copy()
    optimizations_applied = []

    for col_analysis in analysis["size_analysis"]["optimization_opportunities"]:
        if col_analysis["can_optimize"]:
            try:
                optimized_df[col_analysis["column"]] = optimized_df[
                    col_analysis["column"]
                ].astype(col_analysis["suggested_type"])
                optimizations_applied.append(
                    f"Optimized {col_analysis['column']}: {col_analysis['current_type']} → {col_analysis['suggested_type']}"
                )
            except:
                pass

    return optimized_df, optimizations_applied


def get_performance_summary() -> Dict[str, Any]:
    """Get system performance summary."""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        return {
            "cpu_usage_percent": cpu_percent,
            "memory_usage_percent": memory.percent,
            "memory_available_gb": memory.available / 1024 / 1024 / 1024,
            "disk_usage_percent": (disk.used / disk.total) * 100,
            "disk_free_gb": disk.free / 1024 / 1024 / 1024,
        }
    except:
        return {"error": "Unable to get system performance information"}
