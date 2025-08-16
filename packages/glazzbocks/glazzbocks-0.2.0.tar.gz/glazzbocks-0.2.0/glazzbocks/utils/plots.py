"""
plot_utils.py

Helper utilities for handling matplotlib figures and plot formatting.

Includes:
- Conversion of matplotlib figures to base64-encoded PNGs
- Standardized axis formatting for visual consistency

Part of the glazzbocks.utils module.
"""

import base64
from io import BytesIO


def save_plot_to_base64(fig):
    """
    Convert a matplotlib figure to a base64-encoded PNG string.

    Useful for embedding plots in HTML reports or web UIs.

    Parameters:
    - fig (matplotlib.figure.Figure): The matplotlib figure to convert.

    Returns:
    - str: Base64-encoded PNG representation of the figure.
    """
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def format_axes(ax):
    """
    Apply standard formatting to matplotlib axes.

    Sets font size, grid style, and improves readability.

    Parameters:
    - ax (matplotlib.axes.Axes): The axes object to format.

    Returns:
    - None
    """
    ax.tick_params(axis="both", which="major", labelsize=10)
    ax.grid(True, linestyle="--", alpha=0.6)
