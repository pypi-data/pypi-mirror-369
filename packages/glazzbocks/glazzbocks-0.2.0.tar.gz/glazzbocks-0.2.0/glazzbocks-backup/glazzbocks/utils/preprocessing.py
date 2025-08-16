"""
preprocessing.py

Utility functions for creating preprocessing pipelines for numeric and
categorical features. Includes:

- Standard pipelines for numerical and categorical transformations
- Standalone imputation functions for numeric and categorical DataFrames

Used in glazzbocks pipeline and model preparation steps.

Author: Joshua Thompson
"""

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    FunctionTransformer,
    OneHotEncoder,
    PowerTransformer,
    QuantileTransformer,
    StandardScaler,
)
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tools.tools import add_constant


def create_numeric_pipeline(impute_strategy="median"):
    """
    Create a preprocessing pipeline for numeric features.

    The pipeline imputes missing values and scales the features.

    Parameters:
    - impute_strategy (str): Strategy for imputing missing values.
                             Options: "mean", "median", "most_frequent", etc.

    Returns:
    - sklearn.pipeline.Pipeline: A pipeline object for numeric preprocessing.
    """
    return Pipeline(
        [
            ("imputer", SimpleImputer(strategy=impute_strategy)),
            ("scaler", StandardScaler()),
        ]
    )


def create_categorical_pipeline():
    """
    Create a preprocessing pipeline for categorical features.

    The pipeline imputes missing values and encodes categories using OneHotEncoding.

    Returns:
    - sklearn.pipeline.Pipeline: A pipeline object for categorical preprocessing.
    """
    return Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )


def impute_numeric(df, strategy="median"):
    """
    Impute missing values in numeric columns of a DataFrame.

    Parameters:
    - df (pd.DataFrame): Input DataFrame with numeric features.
    - strategy (str): Imputation strategy. Defaults to "median".

    Returns:
    - pd.DataFrame: DataFrame with imputed numeric values.
    """
    numeric_df = df.select_dtypes(include="number")
    imputer = SimpleImputer(strategy=strategy)
    imputed = imputer.fit_transform(numeric_df)
    return pd.DataFrame(imputed, columns=numeric_df.columns, index=df.index)


def impute_categorical(df, strategy="most_frequent"):
    """
    Impute missing values in categorical columns of a DataFrame.

    Parameters:
    - df (pd.DataFrame): Input DataFrame with categorical features (dtype object).
    - strategy (str): Imputation strategy. Defaults to "most_frequent".

    Returns:
    - pd.DataFrame: DataFrame with imputed categorical values.
    """
    cat_df = df.select_dtypes(include="object")
    imputer = SimpleImputer(strategy=strategy)
    imputed = imputer.fit_transform(cat_df)
    return pd.DataFrame(imputed, columns=cat_df.columns, index=df.index)


def create_transformer(transform_type, columns):
    """
    Returns a named transformer tuple based on the specified transform type.

    Args:
        transform_type (str): One of ["log", "sqrt", "square", "boxcox", "yeojohnson", "quantile_uniform", "quantile_normal"]
        columns (List[str]): Columns to apply the transform to.

    Returns:
        Tuple[str, Transformer, List[str]]: Named transformer tuple for ColumnTransformer.
    """
    if transform_type == "log":
        transformer = FunctionTransformer(np.log1p, validate=False)
    elif transform_type == "sqrt":
        transformer = FunctionTransformer(np.sqrt, validate=False)
    elif transform_type == "square":
        transformer = FunctionTransformer(np.square, validate=False)
    elif transform_type == "boxcox":
        transformer = PowerTransformer(method="box-cox", standardize=True)
    elif transform_type == "yeojohnson":
        transformer = PowerTransformer(method="yeo-johnson", standardize=True)
    elif transform_type == "quantile_uniform":
        transformer = QuantileTransformer(
            output_distribution="uniform", random_state=42
        )
    elif transform_type == "quantile_normal":
        transformer = QuantileTransformer(
            output_distribution="normal", random_state=42
        )
    else:
        raise ValueError(f"Unsupported transform type: {transform_type}")

    name = f"{transform_type}_{'_'.join(columns)}"
    return (name, transformer, columns)
