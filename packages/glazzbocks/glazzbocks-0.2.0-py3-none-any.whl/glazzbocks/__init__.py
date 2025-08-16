"""
glazzbocks: Glassbox Machine Learning for Interpretable AI

Modules:
- DataExplorer: EDA, summaries, and professional PDF reports.
- MLPipeline: Modeling pipeline with transparent preprocessing.
- ModelDiagnostics: Visual diagnostics for regression/classification.
- ModelInterpreter: Post-hoc model explainability (e.g. SHAP).
"""

# glazzbocks/__init__.py

from .diagnostics.feature_diagnostics import (
    compute_vif,
    correlation_matrix,
    low_variance_features,
)
from .diagnostics.model_diagnostics import ModelDiagnostics
from .eda.data_explorer import DataExplorer
from .interpreters.modelinterpreter import ModelInterpreter
from .pipeline.ML_pipeline import MLPipeline

__all__ = [
    "MLPipeline",
    "ModelDiagnostics",
    "ModelInterpreter",
    "compute_vif",
    "low_variance_features",
    "correlation_matrix",
    "DataExplorer",
]
