# glazzbocks/runtime/loaders.py
import pathlib
import pandas as pd
import joblib

def load_model(path: str):
    p = pathlib.Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Model file not found: {p}")
    try:
        return joblib.load(p)
    except Exception as e:
        raise RuntimeError(f"Failed to load model {p}: {e}")

def load_table(path: str) -> pd.DataFrame:
    p = str(path)
    if p.endswith(".csv"):
        return pd.read_csv(p)
    if p.endswith(".parquet"):
        return pd.read_parquet(p)
    raise ValueError("Only .csv and .parquet supported for now")

def infer_task(y: pd.Series) -> str:
    # <=10 unique → classification; else regression
    return "classification" if y.nunique(dropna=False) <= 10 else "regression"
