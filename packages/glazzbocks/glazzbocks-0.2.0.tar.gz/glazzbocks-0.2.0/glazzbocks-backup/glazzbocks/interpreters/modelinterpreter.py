"""
model_interpreter.py - Glazzbocks Core

Provides a unified interpretation interface for scikit-learn models and pipelines.

Supports:
- Feature importance and coefficients
- SHAP summary plots (compatible models only)
- Partial dependence plots (PDP)
- Permutation importance
- Pipeline-aware feature name tracking and transformation handling

Works for both regression and classification tasks.

Author: Joshua Thompson
"""

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
from sklearn.inspection import PartialDependenceDisplay, permutation_importance
from sklearn.pipeline import Pipeline


class ModelInterpreter:
    """
    A model interpretability utility for sklearn models and pipelines.

    Supports visual and numeric interpretation techniques including:
    - Feature importances
    - Coefficients
    - SHAP values
    - Partial dependence plots
    - Permutation importance

    Attributes:
        model (BaseEstimator): Underlying model (last step of pipeline if applicable).
        pipeline (Pipeline or None): Sklearn pipeline (if provided).
        X_train (pd.DataFrame): Training data (before transformation).
        task (str): 'regression' or 'classification'.
        logger (logging.Logger, optional): Logger for warnings and messages.
        feature_names (List[str]): Names of input features after preprocessing.
    """

    def __init__(self, model, X_train, task="regression", logger=None):
        """
        Initialize the ModelInterpreter.

        Args:
            model (Pipeline or estimator): Sklearn model or pipeline.
            X_train (pd.DataFrame): Original training data.
            task (str): Task type - 'regression' or 'classification'.
            logger (logging.Logger, optional): Logger to use instead of print.
        """
        self.X_train = X_train
        self.task = task
        self.logger = logger

        if isinstance(model, Pipeline):
            self.pipeline = model
            self.model = model.steps[-1][1]
            self.feature_names = self._extract_feature_names(model, X_train)
        else:
            self.pipeline = None
            self.model = model
            self.feature_names = list(X_train.columns)

    def _log(self, message):
        """Logs a message using the logger or prints it."""
        if self.logger:
            self.logger.warning(message)
        else:
            print(message)

    def _extract_feature_names(self, pipeline, X):
        """
        Extracts feature names from pipeline preprocessing step.

        Returns:
            List[str]: Transformed feature names or original if unavailable.
        """
        try:
            preprocessor = pipeline.named_steps.get("preprocessing")
            if preprocessor and hasattr(preprocessor, "get_feature_names_out"):
                return preprocessor.get_feature_names_out()
        except Exception as e:
            self._log(f"Feature name extraction failed: {e}")
        return list(X.columns)

    def _save_and_remove_plot(self, fig_name):
        """Saves the current figure and deletes the image from disk after use (if needed)."""
        plt.savefig(fig_name, bbox_inches="tight")
        os.remove(fig_name)

    def summary(self):
        """
        Prints summary info about the model, feature space, and supported interpretability options.
        """
        print("Model Interpreter Summary")
        print(f"Model type: {type(self.model).__name__}")
        print(f"Task: {self.task}")
        if self.task == "classification":
            try:
                classes = np.unique(self.pipeline.predict(self.X_train))
                print(
                    f"Detected classes: {classes.tolist()} (n={len(classes)})"
                )
            except Exception:
                pass
        print(f"Feature count: {len(self.feature_names)}")
        print("Supports:")
        print(f" - Coefficients: {hasattr(self.model, 'coef_')}")
        print(
            f" - Feature Importances: {hasattr(self.model, 'feature_importances_')}"
        )
        print(" - SHAP: (if model is compatible)")

    def feature_importance(self, return_fig=False):
        """
        Plots or returns model-based feature importances (for tree-based models).

        Args:
            return_fig (bool): If True, returns figure and axis.

        Returns:
            pd.Series or tuple: Importances (and figure/axis if return_fig is True), or None.
        """
        if hasattr(self.model, "feature_importances_"):
            names = self.feature_names
            importances = pd.Series(
                self.model.feature_importances_, index=names
            ).sort_values()

            fig, ax = plt.subplots(figsize=(8, 6))
            importances.plot(kind="barh", ax=ax)
            ax.set_title("Feature Importance")
            plt.tight_layout()
            self._save_and_remove_plot("feature_importance.png")
            if not return_fig:
                plt.show()
            return importances if not return_fig else (importances, fig, ax)
        else:
            self._log("Feature importances not available.")
            return None

    def coefficients(self, plot=True, return_fig=False):
        """
        Plots or returns model coefficients (for linear models only).

        Args:
            plot (bool): Whether to plot the coefficients.
            return_fig (bool): Whether to return fig/axis.

        Returns:
            pd.Series or tuple: Coefficients (and fig/axis if requested), or None.
        """
        if not hasattr(self.model, "coef_"):
            self._log(
                "Coefficients not available. Please ensure you're using a linear model "
                "(e.g., LogisticRegression, LinearRegression, Ridge, Lasso) before calling this method."
            )
            return None

        coefs = self.model.coef_
        if self.task == "classification" and coefs.ndim > 1:
            # Handle multi-class: use mean absolute coefficient across classes
            coefs = np.mean(np.abs(coefs), axis=0)

        names = self.feature_names
        coefs_series = pd.Series(coefs, index=names).sort_values()

        if plot:
            fig, ax = plt.subplots(figsize=(8, 6))
            coefs_series.plot(kind="barh", ax=ax)
            ax.set_title("Model Coefficients")
            plt.tight_layout()
            self._save_and_remove_plot("coefficients.png")
            if return_fig:
                return coefs_series, fig, ax
            else:
                plt.show()

        return coefs_series

    def odds_ratios(self, as_percent_change=True):
        """
        Computes odds ratios from log-odds coefficients.

        Args:
            as_percent_change (bool): If True, expresses odds ratios as % change.

        Returns:
            pd.DataFrame: Feature name, odds ratio, and optional % change in odds.
        """
        if not hasattr(self.model, "coef_"):
            self._log("Model does not support coefficients.")
            return None

        odds = np.exp(self.model.coef_).flatten()
        names = self.feature_names
        odds_ratios = pd.Series(odds, index=names).sort_values(ascending=False)

        if as_percent_change:
            percent_change = (odds_ratios - 1) * 100
            return pd.DataFrame(
                {
                    "odds_ratio": odds_ratios,
                    "%_change_in_odds": percent_change.map("{:+.1f}%".format),
                }
            ).sort_values("odds_ratio", ascending=False)
        else:
            return odds_ratios

    def shap_summary(self, X_test, sample_size=100, sparse_threshold=0.0):
        """
        Computes and plots SHAP summary for the model.

        Args:
            X_test (pd.DataFrame): Test features.
            sample_size (int): Number of rows to use for SHAP (default: 100).
            sparse_threshold (float): Threshold for converting sparse to dense (default: 0.0).
        """
        try:
            # Sample if needed
            if sample_size and len(X_test) > sample_size:
                X_test = X_test.sample(n=sample_size, random_state=42)

            # Get preprocessor and override sparse threshold
            preprocessor = self.pipeline.named_steps["preprocessing"]
            preprocessor.sparse_threshold = sparse_threshold

            # Transform data
            X_transformed = preprocessor.transform(X_test)

            # Convert to dense if needed
            if hasattr(X_transformed, "toarray"):
                X_transformed = X_transformed.toarray()

            # Get feature names
            if hasattr(preprocessor, "get_feature_names_out"):
                feature_names = preprocessor.get_feature_names_out()
            else:
                feature_names = [
                    f"feature_{i}" for i in range(X_transformed.shape[1])
                ]

            # SHAP explanation
            explainer = shap.Explainer(self.model, X_transformed)
            shap_values = explainer(X_transformed)

            # Plot SHAP summary
            shap.summary_plot(
                shap_values,
                features=X_transformed,
                feature_names=feature_names,
            )

        except Exception as e:
            print(f"SHAP interpretation failed: {e}")

    def partial_dependence(self, features, grid_resolution=50):
        """
        Generates partial dependence plots (PDP) for selected features.

        Args:
            features (list): List of feature names or indices to plot.
            grid_resolution (int): Number of grid points to evaluate.

        Note:
            For multiclass classification, plots are shown per class.
        """
        estimator = self.pipeline if self.pipeline is not None else self.model
        X = self.X_train

        try:
            # Multiclass classification
            if (
                self.task == "classification"
                and hasattr(self.model, "classes_")
                and len(self.model.classes_) > 2
            ):
                for cls_idx, cls in enumerate(self.model.classes_):
                    print(f"\nPartial Dependence for class {cls}:")
                    PartialDependenceDisplay.from_estimator(
                        estimator,
                        X,
                        features=features,
                        target=cls_idx,
                        grid_resolution=grid_resolution,
                    )
                    plt.tight_layout()
                    self._save_and_remove_plot(
                        f"partial_dependence_class_{cls}.png"
                    )
                    plt.show()
            else:
                # Binary or regression
                PartialDependenceDisplay.from_estimator(
                    estimator,
                    X,
                    features=features,
                    grid_resolution=grid_resolution,
                )
                plt.tight_layout()
                self._save_and_remove_plot("partial_dependence.png")
                plt.show()

        except Exception as e:
            self._log(f"PDP failed: {e}")

    def individual_conditional_expectation(self, features, grid_resolution=50):
        """
        Plots ICE (Individual Conditional Expectation) curves for selected features.

        Args:
            features (list): Feature names or indices.
            grid_resolution (int): Number of points to evaluate per feature.
        """
        estimator = self.pipeline if self.pipeline else self.model
        X = self.X_train

        try:
            PartialDependenceDisplay.from_estimator(
                estimator,
                X,
                features=features,
                kind="individual",
                grid_resolution=grid_resolution,
            )
            plt.tight_layout()
            self._save_and_remove_plot("ice_plot.png")
            plt.show()

        except Exception as e:
            self._log(f"ICE plot failed: {e}")

    def permutation_importance(
        self, scoring=None, n_repeats=10, random_state=42, plot=True
    ):
        """
        Calculates and optionally plots permutation importance scores.

        Args:
            scoring (str or callable, optional): Scoring function (e.g., 'r2', 'accuracy').
            n_repeats (int): Number of permutations.
            random_state (int): Random seed.
            plot (bool): Whether to display the plot.

        Returns:
            pd.Series or None: Importances ranked by mean score drop, or None on failure.
        """
        estimator = self.pipeline if self.pipeline is not None else self.model
        X = self.X_train

        try:
            y_true = estimator.predict(X)
            result = permutation_importance(
                estimator,
                X,
                y_true,
                scoring=scoring,
                n_repeats=n_repeats,
                random_state=random_state,
            )
            importances = pd.Series(
                result.importances_mean, index=self.feature_names
            ).sort_values(ascending=False)

            if plot:
                importances.plot(kind="barh", figsize=(8, 6))
                plt.gca().invert_yaxis()
                plt.title("Permutation Feature Importance")
                self._save_and_remove_plot("permutation_importance.png")
                plt.show()

            return importances

        except Exception as e:
            self._log(f"Permutation importance failed: {e}")
            return None
