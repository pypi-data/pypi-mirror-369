from .llm.ollama_client import OllamaLLM
from .llm.huggingface_client import HuggingFaceLLM
from .core.dataframe import AskDataFrame
from .core.engine import AskPandasEngine
from .core.query_processor import QueryProcessor
from .utils.helpers import (
    validate_dataframe,
    get_dataframe_summary,
    format_number,
    detect_data_types,
    clean_column_names,
    get_memory_usage_mb,
)
from .visualization.charts import (
    save_plot,
    create_bar_chart,
    create_line_chart,
    create_scatter_plot,
    create_histogram,
    create_correlation_heatmap,
    create_box_plot,
    set_plot_style,
    get_plot_colors,
)

__version__ = "0.1.1"
__author__ = "Md Irfan Ali"
__email__ = "irfanali29@hotmail.com"

__all__ = [
    # Core classes
    "AskDataFrame",
    "AskPandasEngine",
    "QueryProcessor",
    # LLM clients
    "OllamaLLM",
    "HuggingFaceLLM",
    # Utility functions
    "validate_dataframe",
    "get_dataframe_summary",
    "format_number",
    "detect_data_types",
    "clean_column_names",
    "get_memory_usage_mb",
    # Visualization functions
    "save_plot",
    "create_bar_chart",
    "create_line_chart",
    "create_scatter_plot",
    "create_histogram",
    "create_correlation_heatmap",
    "create_box_plot",
    "set_plot_style",
    "get_plot_colors",
    # Convenience functions
    "DataFrame",
    "set_llm",
    "chat",
    "get_config",
    "set_config",
]


class Config:
    """Configuration class for AskPandas."""

    def __init__(self):
        self.llm = None
        self.model_name = "mistral"
        self.temperature = 0.1
        self.max_tokens = 1000
        self.enable_plotting = True
        self.safe_mode = True
        self.output_dir = "askpandas_plots"
        self.plot_style = "seaborn"
        self.max_execution_time = 30  # seconds
        self.enable_history = True
        self.verbose = False

    def to_dict(self):
        """Convert config to dictionary."""
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "enable_plotting": self.enable_plotting,
            "safe_mode": self.safe_mode,
            "output_dir": self.output_dir,
            "plot_style": self.plot_style,
            "max_execution_time": self.max_execution_time,
            "enable_history": self.enable_history,
            "verbose": self.verbose,
        }

    def update(self, **kwargs):
        """Update configuration with new values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Unknown configuration key: {key}")


# Global configuration instance
config = Config()


def set_llm(llm):
    """Set the LLM to use globally."""
    if not hasattr(llm, "generate") or not hasattr(llm, "is_available"):
        raise ValueError("LLM must implement 'generate' and 'is_available' methods")

    config.llm = llm
    if config.verbose:
        print(f"LLM set to: {type(llm).__name__}")


def get_llm():
    """Get the currently configured LLM."""
    return config.llm


def get_config():
    """Get current configuration."""
    return config.to_dict()


def set_config(**kwargs):
    """Update configuration."""
    config.update(**kwargs)
    if config.verbose:
        print("Configuration updated:", kwargs)


def chat(query, *dataframes):
    """Chat with multiple dataframes using configured LLM."""
    if not config.llm:
        raise ValueError("No LLM configured. Use askpandas.set_llm() to set one.")

    if not dataframes:
        raise ValueError("At least one dataframe must be provided.")

    # Validate dataframes
    validated_dfs = []
    for df in dataframes:
        if isinstance(df, AskDataFrame):
            validated_dfs.append(df)
        else:
            validated_dfs.append(AskDataFrame(df))

    engine = AskPandasEngine(config.llm)
    return engine.process_query(query, validated_dfs)


def DataFrame(data):
    """Create an AskPandas DataFrame."""
    return AskDataFrame(data)


def get_available_models():
    """Get list of available models for different LLM providers."""
    return {
        "ollama": [
            "mistral",
            "llama2",
            "llama2:13b",
            "llama2:70b",
            "codellama",
            "gemma",
            "neural-chat",
            "vicuna",
        ],
        "huggingface": [
            "HuggingFaceH4/zephyr-7b-beta",
            "microsoft/DialoGPT-medium",
            "gpt2",
            "distilgpt2",
        ],
    }


def get_query_examples(category=None):
    """Get example queries for different categories."""
    processor = QueryProcessor()
    return processor.get_query_examples(category)


def analyze_query(query):
    """Analyze a query and provide insights."""
    processor = QueryProcessor()
    return processor.categorize_query(query)


def validate_query(query, columns):
    """Validate if a query can be executed with given columns."""
    processor = QueryProcessor()
    return processor.validate_query(query, columns)


# Set default plotting style
set_plot_style(config.plot_style)
