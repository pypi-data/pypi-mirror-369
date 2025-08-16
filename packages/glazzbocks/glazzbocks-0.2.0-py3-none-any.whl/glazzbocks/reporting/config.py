# glazzbocks/reporting/config.py
DEFAULT_CONFIG = {
  "sections": {
    "eda": True,
    "metrics": True,
    "interpretation": True,
    "calibration": True,
    "bias_checks": False
  },
  "limits": {
    "top_n_features": 20,
    "max_corr_pairs": 30,
    "shap_sample": 500
  },
  "output": {"html": True, "pdf": True, "markdown": True, "pptx": False},
  "audience": "exec"
}
