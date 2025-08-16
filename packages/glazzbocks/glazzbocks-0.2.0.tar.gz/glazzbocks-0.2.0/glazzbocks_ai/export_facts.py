# glazzbocks_ai/export_facts.py
from __future__ import annotations
from pathlib import Path
from typing import Dict, Any

import pandas as pd

from .facts_from_glazzbocks import build_facts_from_glazzbocks

def export_facts_json(
    ml_pipeline,               # <- your MLPipeline instance
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    target_col: str,
    dataset_name: str,
    out_path: str = "outputs_llm/model_facts.json",
) -> Dict[str, Any]:
    """
    Collects metrics/EDA/interpretability using *your* Glazzbocks modules and
    writes a single JSON file the LLM can read later.
    """
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    facts = build_facts_from_glazzbocks(
        ml_pipeline=ml_pipeline,
        X_train=X_train, y_train=y_train,
        X_test=X_test,   y_test=y_test,
        target_col=target_col,
        dataset_name=dataset_name,
        out_path=out_path,
    )
    return facts
