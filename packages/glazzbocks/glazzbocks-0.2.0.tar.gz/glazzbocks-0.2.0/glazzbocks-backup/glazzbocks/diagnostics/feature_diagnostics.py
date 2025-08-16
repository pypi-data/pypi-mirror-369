"""
feature_diagnostics.py

Provides utilities for analyzing features prior to modeling.
This includes checks for multicollinearity (VIF), low variance,
redundant features, and basic statistical diagnostics.

Designed for use within the Glazzbocks framework.

Author: Joshua Thompson
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tools.tools import add_constant

from ..utils.preprocessing import impute_numeric


def compute_vif(
    X,
    include_constant=False,
    impute_strategy="median",
    threshold=10.0,
    verbose=True,
):
    """
    Computes Variance Inflation Factor (VIF) for numeric features.

    Automatically imputes missing values using the given strategy.

    Args:
        X (pd.DataFrame): Numeric DataFrame with possible missing values.
        include_constant (bool): Whether to include intercept in VIF.
        impute_strategy (str): Strategy for imputing missing values.
                               Options: "mean", "median", "most_frequent", etc.
        threshold (float): Threshold above which to flag VIF as high.
        verbose (bool): Whether to print warnings for high-VIF features.

    Returns:
        pd.DataFrame: Features and their VIF scores.
    """
    X_imputed = impute_numeric(X, strategy=impute_strategy)

    if include_constant:
        X_imputed = add_constant(X_imputed)

    vif_data = pd.DataFrame()
    vif_data["Feature"] = X_imputed.columns
    vif_data["VIF"] = [
        variance_inflation_factor(X_imputed.values, i)
        for i in range(X_imputed.shape[1])
    ]

    if not include_constant:
        vif_data = vif_data[vif_data["Feature"] != "const"]

    if verbose:
        high_vif = vif_data[vif_data["VIF"] > threshold].sort_values(
            "VIF", ascending=False
        )
        if not high_vif.empty:
            print(
                "\nHigh multicollinearity detected (VIF > {}):".format(
                    threshold
                )
            )
            print(high_vif.head(5).to_string(index=False))

    return vif_data


def low_variance_features(X, threshold=0.01):
    """
    Identifies features with variance below a given threshold.

    Args:
        X (pd.DataFrame): Input features.
        threshold (float): Variance threshold.

    Returns:
        List[str]: Features with low variance.
    """
    X_numeric = X.select_dtypes(include="number")
    variances = X_numeric.var()
    low_var_cols = variances[variances <= threshold].index.tolist()
    return low_var_cols


def correlation_matrix(X, threshold=0.9, plot=True):
    """
    Computes a correlation matrix and returns highly correlated feature pairs.

    Args:
        X (pd.DataFrame): Input DataFrame (numeric features automatically selected).
        threshold (float): Absolute correlation threshold to flag.
        plot (bool): If True, displays a heatmap of the correlation matrix.

    Returns:
        pd.DataFrame: Highly correlated feature pairs with correlation values.
    """
    # Ensure only numeric data
    X_numeric = X.select_dtypes(include="number")
    corr_matrix = X_numeric.corr().abs()

    # Plot if requested
    if plot:
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f")
        plt.title("Feature Correlation Matrix")
        plt.tight_layout()
        plt.show()

    # Extract upper triangle of correlation matrix
    upper = corr_matrix.where(
        np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
    )

    # Identify high correlations
    high_corrs = [
        {"Feature 1": col1, "Feature 2": col2, "Correlation": corr}
        for col1 in upper.columns
        for col2, corr in upper[col1].items()
        if pd.notnull(corr) and corr > threshold
    ]

    high_corrs_df = pd.DataFrame(high_corrs)

    # Ensure correct column structure even if empty
    if high_corrs_df.empty:
        high_corrs_df = pd.DataFrame(
            columns=["Feature 1", "Feature 2", "Correlation"]
        )

    return high_corrs_df.sort_values(by="Correlation", ascending=False)
