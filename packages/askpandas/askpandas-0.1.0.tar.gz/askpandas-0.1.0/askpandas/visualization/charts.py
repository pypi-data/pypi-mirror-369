import matplotlib.pyplot as plt
import seaborn as sns
import os
import pandas as pd
from typing import Optional, Tuple, List
import numpy as np


def save_plot(fig, filename: str = "plot.png", dpi: int = 150, 
              output_dir: str = "askpandas_plots") -> str:
    """Save a matplotlib or seaborn plot to a file."""
    try:
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        
        # Set figure size if not already set
        if fig.get_size_inches().sum() == 0:
            fig.set_size_inches(10, 6)
        
        fig.savefig(filepath, bbox_inches="tight", dpi=dpi, 
                   facecolor='white', edgecolor='none')
        plt.close(fig)
        return f"Plot saved to {filepath}"
    except Exception as e:
        return f"Failed to save plot: {e}"


def create_bar_chart(data: pd.DataFrame, x_col: str, y_col: str, 
                    title: str = None, figsize: Tuple[int, int] = (10, 6)) -> plt.Figure:
    """Create a bar chart."""
    fig, ax = plt.subplots(figsize=figsize)
    
    # Sort data by y_col for better visualization
    data_sorted = data.sort_values(y_col, ascending=False)
    
    bars = ax.bar(data_sorted[x_col], data_sorted[y_col])
    ax.set_xlabel(x_col.title())
    ax.set_ylabel(y_col.title())
    
    if title:
        ax.set_title(title)
    
    # Rotate x-axis labels if they're long
    if len(data_sorted[x_col].iloc[0]) > 10:
        plt.xticks(rotation=45, ha='right')
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:,.0f}', ha='center', va='bottom')
    
    plt.tight_layout()
    return fig


def create_line_chart(data: pd.DataFrame, x_col: str, y_col: str,
                     title: str = None, figsize: Tuple[int, int] = (10, 6)) -> plt.Figure:
    """Create a line chart."""
    fig, ax = plt.subplots(figsize=figsize)
    
    # Sort by x_col for proper line plotting
    data_sorted = data.sort_values(x_col)
    
    ax.plot(data_sorted[x_col], data_sorted[y_col], marker='o', linewidth=2, markersize=6)
    ax.set_xlabel(x_col.title())
    ax.set_ylabel(y_col.title())
    
    if title:
        ax.set_title(title)
    
    # Rotate x-axis labels if they're long
    if len(str(data_sorted[x_col].iloc[0])) > 10:
        plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    return fig


def create_scatter_plot(data: pd.DataFrame, x_col: str, y_col: str,
                       title: str = None, color_col: Optional[str] = None, 
                       size_col: Optional[str] = None,
                       figsize: Tuple[int, int] = (10, 6)) -> plt.Figure:
    """Create a scatter plot."""
    fig, ax = plt.subplots(figsize=figsize)
    
    if color_col and size_col:
        scatter = ax.scatter(data[x_col], data[y_col], 
                           c=data[color_col], s=data[size_col], alpha=0.6)
        plt.colorbar(scatter, ax=ax, label=color_col.title())
    elif color_col:
        scatter = ax.scatter(data[x_col], data[y_col], c=data[color_col], alpha=0.6)
        plt.colorbar(scatter, ax=ax, label=color_col.title())
    elif size_col:
        ax.scatter(data[x_col], data[y_col], s=data[size_col], alpha=0.6)
    else:
        ax.scatter(data[x_col], data[y_col], alpha=0.6)
    
    ax.set_xlabel(x_col.title())
    ax.set_ylabel(y_col.title())
    
    if title:
        ax.set_title(title)
    
    plt.tight_layout()
    return fig


def create_histogram(data: pd.DataFrame, column: str, bins: int = 30,
                    title: str = None, figsize: Tuple[int, int] = (10, 6)) -> plt.Figure:
    """Create a histogram."""
    fig, ax = plt.subplots(figsize=figsize)
    
    ax.hist(data[column].dropna(), bins=bins, alpha=0.7, edgecolor='black')
    ax.set_xlabel(column.title())
    ax.set_ylabel('Frequency')
    
    if title:
        ax.set_title(title)
    
    plt.tight_layout()
    return fig


def create_correlation_heatmap(data: pd.DataFrame, title: str = None,
                              figsize: Tuple[int, int] = (8, 6)) -> plt.Figure:
    """Create a correlation heatmap."""
    # Select only numeric columns
    numeric_data = data.select_dtypes(include=[np.number])
    
    if numeric_data.empty:
        raise ValueError("No numeric columns found for correlation analysis")
    
    fig, ax = plt.subplots(figsize=figsize)
    
    correlation_matrix = numeric_data.corr()
    
    # Create heatmap
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                square=True, ax=ax, cbar_kws={"shrink": .8})
    
    if title:
        ax.set_title(title)
    else:
        ax.set_title('Correlation Matrix')
    
    plt.tight_layout()
    return fig


def create_box_plot(data: pd.DataFrame, x_col: str, y_col: str,
                   title: str = None, figsize: Tuple[int, int] = (10, 6)) -> plt.Figure:
    """Create a box plot."""
    fig, ax = plt.subplots(figsize=figsize)
    
    data.boxplot(column=y_col, by=x_col, ax=ax)
    ax.set_xlabel(x_col.title())
    ax.set_ylabel(y_col.title())
    
    if title:
        ax.set_title(title)
    
    plt.tight_layout()
    return fig


def set_plot_style(style: str = "default") -> None:
    """Set the plotting style."""
    if style == "seaborn":
        sns.set_style("whitegrid")
        sns.set_palette("husl")
    elif style == "minimal":
        plt.style.use('default')
        plt.rcParams['figure.facecolor'] = 'white'
        plt.rcParams['axes.facecolor'] = 'white'
    elif style == "dark":
        plt.style.use('dark_background')
    else:
        plt.style.use('default')


def get_plot_colors(n_colors: int = 10) -> List[str]:
    """Get a list of distinct colors for plotting."""
    return plt.cm.Set3(np.linspace(0, 1, n_colors))
