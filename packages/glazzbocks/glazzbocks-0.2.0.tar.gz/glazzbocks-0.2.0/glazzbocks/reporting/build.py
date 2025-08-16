# glazzbocks/reporting/build.py (adaptive)
from pathlib import Path
import json
import pandas as pd
from glazzbocks.runtime.loaders import infer_task
from glazzbocks.runtime.evaluate import evaluate_model
from glazzbocks_ai.export_facts import export_facts_json
from glazzbocks_ai.explain_with_gpt import explain_with_gpt

def _call_export_facts(export_fn, model_obj, X_train, y_train, X_test, y_test, target_col, out_dir):
    """Call export_facts_json with whichever first-arg name it supports."""
    import inspect
    sig = inspect.signature(export_fn)
    params = list(sig.parameters.keys())

    common_kwargs = dict(
        X_train=X_train, y_train=y_train,
        X_test=X_test,   y_test=y_test,
        target_col=target_col,
        dataset_name="uploaded",
        out_path=f"{out_dir}/model_facts.json",
    )

    # Try recognized names in order
    for first_name in ("model", "pipeline", "estimator"):
        if first_name in params:
            kwargs = {first_name: model_obj, **common_kwargs}
            return export_fn(**kwargs)

    # If it takes *args or a single positional, try positional call
    try:
        return export_fn(model_obj, **common_kwargs)
    except TypeError:
        pass

    # Last resort: try without the model (if exporter derives from context)
    try:
        return export_fn(**common_kwargs)
    except TypeError as e:
        raise TypeError(f"export_facts_json signature not compatible. Expected one of first params "
                        f"[model|pipeline|estimator], got: {params}") from e

def build_report_run(model, df_train: pd.DataFrame, df_test: pd.DataFrame, target_col: str,
                     out_dir: str = "outputs_llm", config: dict | None = None) -> dict:
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    task = infer_task(df_train[target_col])

    X_train, y_train = df_train.drop(columns=[target_col]), df_train[target_col]
    X_test,  y_test  = df_test.drop(columns=[target_col]),  df_test[target_col]

    facts = _call_export_facts(
        export_facts_json, model, X_train, y_train, X_test, y_test, target_col, out_dir
    )

    # quick metrics (even if exporter already added something)
    try:
        facts.setdefault("metrics_quick", evaluate_model(model, X_test, y_test, task))
    except Exception:
        pass

    # Optional LLM step (will just return a short stub if no API key)
    md = explain_with_gpt(facts)
    (Path(out_dir)/"report.md").write_text(md, encoding="utf-8")

    (Path(out_dir)/"model_facts.slim.json").write_text(
        json.dumps(facts, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return {"facts": facts, "markdown_path": f"{out_dir}/report.md"}
