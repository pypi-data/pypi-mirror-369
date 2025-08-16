# glazzbocks/runtime/schema.py
import pandas as pd

def infer_schema(df: pd.DataFrame) -> dict:
    dtypes = df.dtypes
    numerical   = dtypes[dtypes.apply(pd.api.types.is_numeric_dtype)].index.tolist()
    datetime    = dtypes[dtypes.apply(pd.api.types.is_datetime64_any_dtype)].index.tolist()
    categorical = [c for c in df.columns if c not in numerical + datetime]
    # crude text heuristic: long average string length
    text = [c for c in categorical if df[c].astype(str).str.len().median() > 50]
    return {"numerical": numerical, "categorical": categorical, "datetime": datetime, "text": text}
