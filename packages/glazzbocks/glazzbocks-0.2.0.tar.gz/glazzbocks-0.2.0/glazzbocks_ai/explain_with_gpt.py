# glazzbocks_ai/explain_with_gpt.py
from __future__ import annotations

import os
import json
import argparse
import textwrap
from pathlib import Path
from typing import Any, Dict, Optional

from openai import OpenAI

from .prompt_templates import SYSTEM_PROMPT, USER_PROMPT  # USER_PROMPT kept for compatibility


# ---------- IO ----------

def load_facts(path: str = "outputs_llm/model_facts.json") -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Facts JSON not found: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def save_text(text: str, out_path: str) -> None:
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


# ---------- Slimming helpers (keep LLM prompt small) ----------

def _top_k(mapping: Optional[Dict[str, float]], k: int = 30) -> Optional[Dict[str, float]]:
    if mapping is None:
        return None
    items = list(mapping.items())
    items.sort(key=lambda x: abs(x[1]), reverse=True)
    return dict(items[:k])


def _shrink_table_dict(table_dict: Any, max_rows: int, max_cols: int) -> Any:
    """Trim DataFrame-like dicts produced by .to_dict()."""
    if not isinstance(table_dict, dict):
        return table_dict

    cols = list(table_dict.keys())[:max_cols]
    out = {}
    for c in cols:
        v = table_dict[c]
        if isinstance(v, list):
            out[c] = v[:max_rows]
        elif isinstance(v, dict):
            out[c] = {kk: v[kk] for kk in list(v.keys())[:max_rows]}
        else:
            out[c] = v
    return out


def shrink_facts_for_llm(facts: Dict[str, Any]) -> Dict[str, Any]:
    """Produce a smaller, LLM-friendly version of the facts payload."""
    f = dict(facts)  # shallow copy

    f.setdefault("eda", {})
    f.setdefault("features", {})
    f.setdefault("metrics", {})
    f.setdefault("caveats", [])
    f.setdefault("gates", {})
    f.setdefault("dataset_name", "")
    f.setdefault("target_col", "")
    f.setdefault("task_type", "")
    f.setdefault("model_name", "")
    f.setdefault("sample_size_train", 0)
    f.setdefault("sample_size_test", 0)

    # --- Metrics (classification): keep essentials only
    m = f["metrics"]
    cls_rep = m.get("classification_report")
    if isinstance(cls_rep, dict):
        m["classification_report"] = {
            "accuracy": cls_rep.get("accuracy"),
            "macro avg": cls_rep.get("macro avg"),
            "weighted avg": cls_rep.get("weighted avg"),
        }

    # --- EDA trims
    e = f["eda"]
    e["numeric_summary"] = _shrink_table_dict(e.get("numeric_summary"), max_rows=25, max_cols=8)
    e["categorical_summary"] = _shrink_table_dict(e.get("categorical_summary"), max_rows=25, max_cols=6)

    vif = e.get("vif")
    if isinstance(vif, dict) and "VIF" in vif and "Feature" in vif:
        try:
            pairs = list(zip(vif["Feature"], vif["VIF"]))
            pairs.sort(key=lambda x: x[1], reverse=True)
            pairs = pairs[:25]
            e["vif"] = {"Feature": [p[0] for p in pairs], "VIF": [p[1] for p in pairs]}
        except Exception:
            pass

    e["high_correlations"] = _shrink_table_dict(e.get("high_correlations"), max_rows=25, max_cols=3)
    lv = e.get("low_variance")
    if isinstance(lv, list):
        e["low_variance"] = lv[:50]

    # --- Features: top-k only
    ft = f["features"]
    ft["feature_importance"] = _top_k(ft.get("feature_importance"), k=30)
    ft["coefficients"] = _top_k(ft.get("coefficients"), k=30)
    ft["odds_ratios"] = _top_k(ft.get("odds_ratios"), k=30)

    # Figures not needed for LLM text
    f["figures"] = {}

    return f


# ---------- Section chunking ----------

def _section_payloads(slim: Dict[str, Any]) -> Dict[str, Any]:
    """Split slim facts into logical sections for separate LLM calls."""
    meta = {
        "dataset_name": slim.get("dataset_name"),
        "target_col": slim.get("target_col"),
        "task_type": slim.get("task_type"),
        "model_name": slim.get("model_name"),
        "sample_size_train": slim.get("sample_size_train"),
        "sample_size_test": slim.get("sample_size_test"),
    }

    metrics = slim.get("metrics", {})
    eda = slim.get("eda", {})
    features = slim.get("features", {})
    caveats = {
        "caveats": slim.get("caveats", []),
        "gates": slim.get("gates", {}),
    }

    return {
        "meta": meta,
        "metrics": metrics,
        "eda": eda,
        "features": features,
        "risks": caveats,
    }


def _summarize_section(client: OpenAI, model: str, title: str, content: Dict[str, Any], outdir: Optional[Path]) -> str:
    """Call the LLM to summarize a single section."""
    section_user_prompt = textwrap.dedent(f"""\
        You will receive ONE section of model facts as JSON.
        Summarize ONLY this section in concise Markdown bullets aimed at a product/ML audience.
        Do NOT invent values; if something is absent, skip it.

        Section: {title}
        ```json
        {json.dumps(content, ensure_ascii=False)}
        ```

        Write 4–10 bullets. Use short, direct sentences.
    """)

    resp = client.chat.completions.create(
        model=model,
        temperature=0.0,
        messages=[
            {"role": "system", "content": "You are a precise ML reviewer. Only explain the facts provided. Be concise."},
            {"role": "user", "content": section_user_prompt},
        ],
    )
    text = resp.choices[0].message.content or ""

    if outdir is not None:
        outdir.mkdir(parents=True, exist_ok=True)
        (outdir / f"{title.lower()}_summary.md").write_text(text, encoding="utf-8")

    return text


def _compose_final_report(client: OpenAI, model: str, section_summaries: Dict[str, str]) -> str:
    """Ask the LLM to stitch section summaries into the final report."""
    bundle = {
        "meta_summary": section_summaries.get("meta", ""),
        "performance_summary": section_summaries.get("metrics", ""),
        "eda_summary": section_summaries.get("eda", ""),
        "features_summary": section_summaries.get("features", ""),
        "risk_summary": section_summaries.get("risks", ""),
    }

    stitching_prompt = textwrap.dedent(f"""\
        You are given short Markdown bullet summaries for parts of a model card:
        - Meta
        - Performance
        - EDA
        - Interpretability/Features
        - Risks & Caveats

        Using ONLY these summaries (below), write a single cohesive Markdown report following this structure:

        # Executive Summary
        - 3–6 bullets on overall performance, strengths, risks

        # Performance
        Explain key metrics (e.g., AUC/PR AUC/F1 for classification, or RMSE/R2 for regression) and what they mean in practice. Mention calibration if present.

        # Interpretability
        Describe global drivers (feature importances/coefficients/odds ratios). Call out any counterintuitive effects.

        # Risk & Quality Checks
        Discuss class imbalance, leakage, calibration error, multicollinearity and high-correlation flags, and any failed gates.

        # Next Steps
        4–8 concrete actions (e.g., collect data for minority classes, calibrate probabilities, tune thresholds, add constraints, check drift).

        Summaries to use (verbatim; do not add new facts):
        ```markdown
        [META]
        {bundle["meta_summary"]}

        [PERFORMANCE]
        {bundle["performance_summary"]}

        [EDA]
        {bundle["eda_summary"]}

        [FEATURES]
        {bundle["features_summary"]}

        [RISKS]
        {bundle["risk_summary"]}
        ```
    """)

    resp = client.chat.completions.create(
        model=model,
        temperature=0.0,
        messages=[
            {"role": "system", "content": "You are a precise ML reviewer. Only explain the provided summaries. No new facts."},
            {"role": "user", "content": stitching_prompt},
        ],
    )
    return resp.choices[0].message.content or ""


# ---------- Public API ----------

def explain_with_gpt(facts: Dict[str, Any], *, write_slim_copy: bool = True, write_section_summaries: bool = True) -> str:
    """
    Turn Glazzbocks facts into a Markdown report using chunked LLM calls.
    - Reads API key from OPENAI_API_KEY
    - Model name from OPENAI_MODEL (defaults to gpt-4o-mini)
    """
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Missing OPENAI_API_KEY environment variable.")

    client = OpenAI()
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # 1) Slim overall facts (still complete but smaller)
    slim = shrink_facts_for_llm(facts)
    if write_slim_copy:
        try:
            save_text(json.dumps(slim, indent=2), "outputs_llm/model_facts.slim.json")
        except Exception:
            pass

    # 2) Split into sections and summarize each independently
    sections = _section_payloads(slim)
    outdir = Path("outputs_llm/sections") if write_section_summaries else None

    section_summaries = {}
    for title, payload in sections.items():
        section_summaries[title] = _summarize_section(client, model_name, title, payload, outdir)

    # 3) Compose the final stitched report
    final_md = _compose_final_report(client, model_name, section_summaries)
    return final_md


def explain_from_file(facts_path: str = "outputs_llm/model_facts.json",
                      out_path: str = "outputs_llm/report.md") -> str:
    facts = load_facts(facts_path)
    md = explain_with_gpt(facts)
    save_text(md, out_path)
    return out_path


# ---------- Tiny CLI ----------

def _parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Glazzbocks AI: explain model facts with chunked LLM calls.")
    ap.add_argument("--facts", default="outputs_llm/model_facts.json", help="Path to facts JSON.")
    ap.add_argument("--out",   default="outputs_llm/report.md",       help="Where to write Markdown report.")
    return ap.parse_args()


def main() -> None:
    args = _parse_args()
    path = explain_from_file(args.facts, args.out)
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
