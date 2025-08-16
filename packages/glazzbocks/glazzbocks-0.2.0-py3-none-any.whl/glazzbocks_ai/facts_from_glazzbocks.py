"""
facts_from_glazzbocks.py

Builds a compact, model-agnostic "facts" JSON that can be fed to an LLM
for narrative generation. Unlike earlier versions, this file DOES NOT
assume a `.pipeline` attribute. It works with:

- A fitted bare estimator (e.g., RandomForestClassifier)
- A fitted sklearn Pipeline (has .predict/.predict_proba and .get_params())

It also tolerates the absence of preprocessing steps and any optional
attributes like `feature_importances_` or `coef_`.
"""

from __future__ import annotations
import json

from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    roc_auc_score,
    confusion_matrix,
    classification_report,
    r2_score,
    mean_absolute_error,
    mean_squared_error,
)


def _infer_task(y: pd.Series) -> str:
    """Classify as 'classification' if small cardinality, else 'regression'."""
    try:
        n_unique = y.nunique(dropna=True)
        if n_unique <= 10 and pd.api.types.is_integer_dtype(y) or pd.api.types.is_bool_dtype(y):
            return "classification"
        # also allow small unique but non-integer labels
        if n_unique <= 10:
            return "classification"
    except Exception:
        pass
    return "regression"


def _safe_predict(estimator, X: pd.DataFrame) -> np.ndarray:
    return estimator.predict(X)


def _safe_predict_proba(estimator, X: pd.DataFrame) -> Optional[np.ndarray]:
    if hasattr(estimator, "predict_proba"):
        try:
            proba = estimator.predict_proba(X)
            return np.asarray(proba)
        except Exception:
            return None
    return None


def _model_name_and_params(estimator) -> Tuple[str, Dict[str, Any]]:
    """Return a readable model name and (trimmed) params dict."""
    try:
        name = type(estimator).__name__
    except Exception:
        name = str(estimator)
    try:
        params = estimator.get_params(deep=False)
    except Exception:
        params = {}
    # Trim very large values for readability
    trimmed = {}
    for k, v in params.items():
        s = repr(v)
        if len(s) > 200:
            s = s[:200] + "..."
        trimmed[k] = s
    return name, trimmed


def _eda_summary(df: pd.DataFrame) -> Dict[str, Any]:
    d = {
        "shape": list(df.shape),
        "dtypes": {c: str(df[c].dtype) for c in df.columns},
        "missing_pct": {c: float(df[c].isna().mean() * 100) for c in df.columns},
        "numeric_cols": [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])],
        "categorical_cols": [c for c in df.columns if df[c].dtype == "object" or pd.api.types.is_categorical_dtype(df[c])],
    }
    return d


def _classification_metrics(y_true, y_pred, y_prob) -> Dict[str, Any]:
    acc = accuracy_score(y_true, y_pred)
    prec, rec, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="binary" if len(np.unique(y_true))==2 else "macro", zero_division=0)
    cm = confusion_matrix(y_true, y_pred).tolist()

    metrics = {
        "accuracy": float(acc),
        "precision": float(prec),
        "recall": float(rec),
        "f1": float(f1),
        "confusion_matrix": cm,
        "classification_report": classification_report(y_true, y_pred, output_dict=True),
    }
    if y_prob is not None and len(np.unique(y_true)) == 2:
        try:
            # For binary, use positive-class column (assume [:,1])
            auc = roc_auc_score(y_true, y_prob[:,1] if y_prob.ndim==2 and y_prob.shape[1] > 1 else y_prob.ravel())
            metrics["roc_auc"] = float(auc)
        except Exception:
            pass
    return metrics


def _regression_metrics(y_true, y_pred) -> Dict[str, Any]:
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_true, y_pred)
    r2  = r2_score(y_true, y_pred)
    return {"mse": float(mse), "rmse": float(rmse), "mae": float(mae), "r2": float(r2)}


def _feature_importance_like(estimator) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    if hasattr(estimator, "feature_importances_"):
        try:
            out["feature_importances_"] = list(map(float, np.asarray(estimator.feature_importances_).ravel()))
        except Exception:
            pass
    if hasattr(estimator, "coef_"):
        try:
            coefs = np.asarray(estimator.coef_)
            if coefs.ndim > 1:
                coefs = coefs.mean(axis=0)  # multiclass => mean abs is also common, but keep simple
            out["coef_"] = list(map(float, coefs.ravel()))
        except Exception:
            pass
    return out


def build_facts_from_glazzbocks(
    ml_pipeline,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    target_col: str,
    dataset_name: str,
    out_path: str = "outputs_llm/model_facts.json",
) -> Dict[str, Any]:
    """
    Create a compact facts dict from a fitted estimator or Pipeline + datasets.

    Parameters
    ----------
    ml_pipeline : estimator or Pipeline
        A fitted sklearn estimator *or* Pipeline. Must support `.predict`.
    X_train, y_train, X_test, y_test : DataFrames/Series
        Datasets used for computing metrics.
    target_col : str
        Name of the target column.
    dataset_name : str
        A label used only for context in the report.
    out_path : str
        Where to write the JSON.

    Returns
    -------
    Dict[str, Any]
    """
    estimator = ml_pipeline  # accept bare estimator or Pipeline
    if not hasattr(estimator, "predict"):
        raise ValueError("Provided ml_pipeline/estimator must be fitted and support .predict")

    task = _infer_task(y_train)

    # Predict
    y_pred_train = _safe_predict(estimator, X_train)
    y_pred_test  = _safe_predict(estimator, X_test)
    y_prob_train = _safe_predict_proba(estimator, X_train)
    y_prob_test  = _safe_predict_proba(estimator, X_test)

    # Metrics
    if task == "classification":
        metrics_train = _classification_metrics(y_train, y_pred_train, y_prob_train)
        metrics_test  = _classification_metrics(y_test,  y_pred_test,  y_prob_test)
        class_balance = y_train.value_counts(normalize=True).to_dict()
    else:
        metrics_train = _regression_metrics(y_train, y_pred_train)
        metrics_test  = _regression_metrics(y_test,  y_pred_test)
        class_balance = None

    # Model info
    model_name, model_params = _model_name_and_params(estimator)
    fi_like = _feature_importance_like(estimator)

    # EDA summaries (feature-only; target excluded)
    eda_train = _eda_summary(X_train)
    eda_test  = _eda_summary(X_test)

    facts: Dict[str, Any] = {
        "version": "0.1.0-ai",
        "dataset_name": dataset_name,
        "target": target_col,
        "task": task,
        "model": {
            "name": model_name,
            "params": model_params,
            "has_predict_proba": bool(y_prob_test is not None),
            **fi_like,
        },
        "eda": {
            "train": eda_train,
            "test": eda_test,
        },
        "metrics": {
            "train": metrics_train,
            "test": metrics_test,
        },
        "class_balance_train": class_balance,
        "columns": list(X_train.columns),
    }

    # Write JSON
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(facts, f, indent=2, default=lambda o: float(o) if isinstance(o, np.floating) else str(o))

    return facts
