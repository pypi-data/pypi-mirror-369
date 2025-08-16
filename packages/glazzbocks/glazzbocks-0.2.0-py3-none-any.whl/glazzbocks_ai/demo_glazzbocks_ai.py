# examples/demo_glazzbocks_ai.py
from pathlib import Path
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from glazzbocks.pipeline.ML_pipeline import MLPipeline
from glazzbocks_ai.export_facts import export_facts_json
from glazzbocks_ai.explain_with_gpt import explain_with_gpt

# Replace with a small dataset of your choice
df = pd.read_csv(r"C:\Users\jthom\OneDrive\Documents\GitHub\glazzbocks\glazzbocks_ai\Telco-Customer-Churn.csv")
target = "Churn"

pipe = MLPipeline(model=LogisticRegression(random_state=42))
X_train, X_test, y_train, y_test = pipe.split_data(df, target)
pipe.build_pipeline(X_train)
pipe.fit(X_train, y_train)

# Export facts (AI layer lives in glazzbocks_ai/*)
facts = export_facts_json(
    ml_pipeline=pipe,  # <- pass the pipeline class, not raw sklearn pipeline
    X_train=X_train, y_train=y_train,
    X_test=X_test,   y_test=y_test,
    target_col=target,
    dataset_name="credit_risk",
    out_path="outputs_llm/model_facts.json",
)

# Option A: call LLM in Python
md = explain_with_gpt(facts)
Path("outputs_llm/report.md").write_text(md, encoding="utf-8")

# Option B: or do it later via CLI
# glazzbocks-ai explain --facts outputs_llm/model_facts.json --out outputs_llm/report.md
