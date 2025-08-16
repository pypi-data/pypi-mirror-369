"""
ML_pipeline.py - Glazzbocks Core
Author: Joshua Thompson
"""

import time

import numpy as np
import pandas as pd
from sklearn.base import clone, is_classifier, is_regressor
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.metrics import (
    classification_report,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    accuracy_score, 
    precision_score, 
    recall_score, 
    f1_score,
    
)
from sklearn.model_selection import cross_validate, train_test_split
from sklearn.pipeline import Pipeline

from ..diagnostics import ModelDiagnostics
from ..utils.preprocessing import (
    create_categorical_pipeline,
    create_numeric_pipeline,
)


class MLPipeline:
    def __init__(self, model=None):
        self.model = model
        self.pipeline = None
        self.numeric_cols = []
        self.categorical_cols = []

    def set_model(self, model):
        """Set a new model and clear the pipeline."""
        self.model = model
        self.pipeline = None
        print(f"Model set to: {self.model}")

    def split_data(self, df, target_col, test_size=0.2, random_state=42):
        """Split into train/test sets."""
        X = df.drop(columns=[target_col])
        y = df[target_col]
        return train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )

    def _build_transformers(self, X_train):
        self.numeric_cols = X_train.select_dtypes(
            include="number"
        ).columns.tolist()
        self.categorical_cols = X_train.select_dtypes(
            include=["object", "category"]
        ).columns.tolist()
        transformers = []
        if self.numeric_cols:
            transformers.append(
                ("num", create_numeric_pipeline(), self.numeric_cols)
            )
        if self.categorical_cols:
            transformers.append(
                ("cat", create_categorical_pipeline(), self.categorical_cols)
            )
        return transformers

    def build_pipeline(self, X_train):
        transformers = self._build_transformers(X_train)
        preprocessor = ColumnTransformer(transformers, remainder="passthrough")
        self.pipeline = Pipeline(
            [
                ("preprocessing", preprocessor),
                ("model", self.model),
            ]
        )

    def fit(self, X_train, y_train):
        if self.pipeline is None:
            raise ValueError("Pipeline has not been built.")
        self.pipeline.fit(X_train, y_train)

        # Save training data for diagnostics warnings
        self.last_X_train = X_train.copy()
        self.last_y_train = y_train.copy()

    def _check_fitted(self, X=None, y=None):
        """
        Confirm that the pipeline has been fitted.
        Optionally warn if the provided X and y match the training data.

        Args:
            X (pd.DataFrame or np.ndarray): Feature matrix to check.
            y (pd.Series or np.ndarray): Labels to check.
        """
        if not hasattr(self.pipeline, "predict"):
            raise ValueError("Pipeline is not fitted.")

        # Warn if running diagnostics on the same data used for training
        try:
            if hasattr(self.pipeline, "last_X_train") and hasattr(
                self.pipeline, "last_y_train"
            ):
                if X is not None and y is not None:
                    if isinstance(X, pd.DataFrame) and isinstance(
                        self.pipeline.last_X_train, pd.DataFrame
                    ):
                        if X.equals(self.pipeline.last_X_train) and y.equals(
                            self.pipeline.last_y_train
                        ):
                            print(
                                "⚠️ Warning: You're running diagnostics on your training data. "
                                "This may overestimate performance."
                            )
        except Exception:
            pass

    @staticmethod
    def evaluate_models(model_dict, X_train, y_train, n_splits=5):
        results = {}
        pipelines = {}

        for name, model in model_dict.items():
            print(f"\n🔁 Cross-validating model: {name}")

            # Detect task type
            if is_classifier(model):
                scoring = ["accuracy", "precision_macro", "recall_macro", "f1_macro"]
            elif is_regressor(model):
                scoring = {
                    "rmse": "neg_root_mean_squared_error",
                    "mae": "neg_mean_absolute_error",
                    "r2": "r2"
                }
            else:
                raise ValueError(f"Unknown model type for: {name}")

            temp_pipe = MLPipeline(model)
            transformers = temp_pipe._build_transformers(X_train)
            preprocessor = ColumnTransformer(transformers, remainder="passthrough")

            pipeline_with_preproc = Pipeline(
                [("preprocessing", preprocessor), ("model", clone(model))]
            )

            cv_results = cross_validate(
                pipeline_with_preproc,
                X_train,
                y_train,
                cv=n_splits,
                scoring=scoring,
                return_train_score=False,
            )

            # Print raw CV scores
            for metric in scoring:
                scores = cv_results[f"test_{metric}"]
                print(f"  {metric}: {scores}")

            # Store summary
            summary = {
                metric: (scores.mean(), scores.std())
                for metric, scores in (
                    (m, cv_results[f"test_{m}"]) for m in scoring
                )
            }
            results[name] = summary

            # Fit final pipeline for this model
            temp_pipe.build_pipeline(X_train)
            temp_pipe.fit(X_train, y_train)

            # Inference time
            try:
                sample = X_train.sample(min(100, len(X_train)), random_state=42)
                t0 = time.time()
                _ = temp_pipe.pipeline.predict(sample)
                latency_ms = (time.time() - t0) / len(sample) * 1000
            except Exception:
                latency_ms = None

            summary["inference_time_ms"] = latency_ms
            pipelines[name] = temp_pipe

        # Convert results to DataFrame
        rows = []
        for model_name, metrics in results.items():
            row = {"model": model_name}
            for metric, value in metrics.items():
                if isinstance(value, tuple):
                    row[f"{metric}_mean"] = value[0]
                    row[f"{metric}_std"] = value[1]
                else:
                    row[metric] = value
            rows.append(row)

        summary_df = pd.DataFrame(rows)
        summary_df.set_index("model", inplace=True)
        return summary_df, pipelines

    def evaluate_on_test(self, X_test, y_test, return_df=True):
        """Evaluate on a test set."""
        if self.pipeline is None:
            raise ValueError("Pipeline has not been built.")
        is_classification = is_classifier(self.pipeline.named_steps["model"])
        y_pred = self.pipeline.predict(X_test)

        if is_classification:
            report = classification_report(y_test, y_pred, output_dict=True)
            if return_df:
                df = pd.DataFrame(report).T.round(3)
                df.index.name = "Label"
                return df.replace({np.nan: ""})
            return report
        else:
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            rmse = np.sqrt(mse)
            return pd.Series(
                {
                    "test_mse": mse,
                    "test_mae": mae,
                    "test_rmse": rmse,
                    "test_r2": r2,
                }
            ).round(3)

    def calibrate_model(self, method="sigmoid", cv=5, inplace=True):
        """
        Wrap the current model in a CalibratedClassifierCV for probability calibration.

        Args:
            method (str): Calibration method ('sigmoid' or 'isotonic').
            cv (int): Number of cross-validation folds for calibration.
            inplace (bool): If True, replaces the model inside the pipeline.
                            If False, returns a new calibrated pipeline.
        """
        if self.pipeline is None:
            raise ValueError("Pipeline has not been built yet.")

        model = self.pipeline.named_steps["model"]

        if not is_classifier(model):
            raise ValueError(
                "Calibration is only applicable for classification models."
            )

        calibrated_model = CalibratedClassifierCV(model, method=method, cv=cv)

        if inplace:
            # Replace the model in the existing pipeline
            self.pipeline.steps[-1] = ("model", calibrated_model)
            print(
                f"Model calibrated in-place using '{method}' method with cv={cv}."
            )
        else:
            # Return a new pipeline with the calibrated model
            from sklearn.pipeline import Pipeline

            new_pipeline = Pipeline(
                [
                    (
                        "preprocessing",
                        self.pipeline.named_steps["preprocessing"],
                    ),
                    ("model", calibrated_model),
                ]
            )
            print(
                f"Returning new calibrated pipeline using '{method}' method with cv={cv}."
            )
            return new_pipeline

    def get_diagnostics(self):
        if self.pipeline is None:
            raise ValueError("Pipeline has not been built or fitted.")
        return ModelDiagnostics(self.pipeline)
