# glazzbocks/runtime/evaluate.py
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    mean_squared_error, mean_absolute_error, r2_score
)

def _safe_proba(model, X):
    # best-effort proba for classifiers
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)
        return proba[:, 1] if proba.ndim == 2 and proba.shape[1] == 2 else None
    if hasattr(model, "decision_function"):
        df = model.decision_function(X)
        if getattr(df, "ndim", 1) == 1:
            m, M = float(np.min(df)), float(np.max(df))
            return (df - m) / (M - m + 1e-9)
    return None

def evaluate_model(model, X_test: pd.DataFrame, y_test: pd.Series, task: str) -> dict:
    y_pred = model.predict(X_test)
    out = {"n": int(len(y_test))}
    if task == "classification":
        avg = "binary" if y_test.nunique() == 2 else "macro"
        out["accuracy"]  = float(accuracy_score(y_test, y_pred))
        out["precision"] = float(precision_score(y_test, y_pred, average=avg, zero_division=0))
        out["recall"]    = float(recall_score(y_test, y_pred, average=avg, zero_division=0))
        out["f1"]        = float(f1_score(y_test, y_pred, average=avg, zero_division=0))
        proba = _safe_proba(model, X_test)
        if proba is not None and y_test.nunique() == 2:
            try:
                out["roc_auc"] = float(roc_auc_score(y_test, proba))
            except Exception:
                pass
    else:
        mse  = mean_squared_error(y_test, y_pred)
        out["rmse"] = float(np.sqrt(mse))
        out["mae"]  = float(mean_absolute_error(y_test, y_pred))
        out["r2"]   = float(r2_score(y_test, y_pred))
    return out
