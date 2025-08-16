"""
Utility modules for shared preprocessing, plotting, and formatting.
"""

from .formatting import format_number, truncate_dataframe
from .plots import format_axes, save_plot_to_base64
from .preprocessing import create_categorical_pipeline, create_numeric_pipeline

__all__ = [
    "create_numeric_pipeline",
    "create_categorical_pipeline",
    "save_plot_to_base64",
    "format_axes",
    "format_number",
    "truncate_dataframe",
]
