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

    def feature_importance(self, return_fig=False, top_n=20, plot_top_only=True):
        """
        Plots or returns model-based feature importances (for tree-based models).

        Args:
            return_fig (bool): If True, returns (importances, fig, ax).
            top_n (int): Number of top features to show in the plot.
            plot_top_only (bool): If True, plot only the top_n features.
            figsize (tuple): Matplotlib figure size.

        Returns:
            pd.Series or tuple:
                - If return_fig is False: full importances as a pd.Series (all features).
                - If return_fig is True: (full_importances, fig, ax)
        """
        if not hasattr(self.model, "feature_importances_"):
            self._log("Feature importances not available.")
            return None

        # Full importances (all features), sorted ascending for nicer horizontal bars
        names = list(self.feature_names)
        importances_full = pd.Series(self.model.feature_importances_, index=names).sort_values()

        # Slice for plotting
        if plot_top_only and top_n is not None and top_n > 0:
            # take the largest top_n, keep ascending order for barh
            to_plot = importances_full.tail(top_n)
        else:
            to_plot = importances_full

        fig, ax = plt.subplots(figsize=(8, 6))
        to_plot.plot(kind="barh", ax=ax)

        shown = len(to_plot)
        ax.set_title(f"Feature Importance (top {shown} of {len(importances_full)})")
        ax.set_xlabel("Importance")
        ax.set_ylabel("Feature")
        plt.tight_layout()

        # If you actually want to keep the image on disk, comment out the next line
        self._save_and_remove_plot("feature_importance.png")

        if return_fig:
            return importances_full, fig, ax
        else:
            plt.show()
            return importances_full


    def coefficients(self, plot=True, return_fig=False, top_n=20, plot_top_only=True):
        """
        Plots or returns model coefficients (for linear models only).

        Args:
            plot (bool): Whether to plot the coefficients.
            return_fig (bool): Whether to return (series, fig, ax).
            top_n (int): Number of top (absolute) coefficients to display in the plot.
            plot_top_only (bool): If True, plot only the top_n coefficients.

        Returns:
            pd.Series or (pd.Series, fig, ax): Full coefficient series (all features).
        """
        if not hasattr(self.model, "coef_"):
            self._log(
                "Coefficients not available. Use a linear model (e.g., LogisticRegression, Ridge, Lasso)."
            )
            return None

        coefs = self.model.coef_
        if self.task == "classification" and getattr(coefs, "ndim", 1) > 1:
            coefs = np.mean(np.abs(coefs), axis=0)

        names = list(self.feature_names)
        coefs_series = pd.Series(coefs, index=names)

        ranked = coefs_series.reindex(coefs_series.abs().sort_values(ascending=False).index)

        if plot:
            to_plot = ranked.head(top_n) if (plot_top_only and top_n and top_n > 0) else ranked
            to_plot_plot = to_plot.sort_values(ascending=True)

            fig, ax = plt.subplots(figsize=(8, 6))
            to_plot_plot.plot(kind="barh", ax=ax)
            shown = len(to_plot_plot)
            ax.set_title(f"Model Coefficients (top {shown} of {len(coefs_series)})")
            ax.set_xlabel("Coefficient")
            ax.set_ylabel("Feature")
            plt.tight_layout()
            self._save_and_remove_plot("coefficients.png")

            if return_fig:
                return coefs_series, fig, ax

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

    def shap_summary(self, X_test, sample_size=100, sparse_threshold=0.0, max_display=20):
        """
        Computes and plots SHAP summary for the model.

        Args:
            X_test (pd.DataFrame): Test features.
            sample_size (int): Rows to use for SHAP.
            sparse_threshold (float): Override pipeline sparse threshold.
            max_display (int): Max number of features to display in the SHAP plot.
        """
        try:
            if sample_size and len(X_test) > sample_size:
                X_test = X_test.sample(n=sample_size, random_state=42)

            preprocessor = self.pipeline.named_steps["preprocessing"]
            preprocessor.sparse_threshold = sparse_threshold

            X_transformed = preprocessor.transform(X_test)
            if hasattr(X_transformed, "toarray"):
                X_transformed = X_transformed.toarray()

            if hasattr(preprocessor, "get_feature_names_out"):
                feature_names = preprocessor.get_feature_names_out()
            else:
                feature_names = [f"feature_{i}" for i in range(X_transformed.shape[1])]

            explainer = shap.Explainer(self.model, X_transformed)
            shap_values = explainer(X_transformed)

            shap.summary_plot(
                shap_values,
                features=X_transformed,
                feature_names=feature_names,
                max_display=max_display,
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

    def permutation_importance(self, scoring=None, n_repeats=10, random_state=42,
                           plot=True, top_n=20, plot_top_only=True):
        """
        Calculates and optionally plots permutation importance scores.

        Args:
            scoring (str|callable): e.g., 'r2', 'accuracy'.
            n_repeats (int): Number of permutations.
            random_state (int): RNG seed.
            plot (bool): Whether to plot.
            top_n (int): How many top features to display in the plot.
            plot_top_only (bool): Plot only top_n if True.

        Returns:
            pd.Series or None: Full importance series (all features), or None on failure.
        """
        estimator = self.pipeline if self.pipeline is not None else self.model
        X = self.X_train

        try:
            y_pred = estimator.predict(X)
            result = permutation_importance(
                estimator,
                X,
                y_pred,
                scoring=scoring,
                n_repeats=n_repeats,
                random_state=random_state,
            )

            importances_full = pd.Series(result.importances_mean, index=self.feature_names)
            ranked = importances_full.reindex(importances_full.abs().sort_values(ascending=False).index)

            if plot:
                to_plot = ranked.head(top_n) if (plot_top_only and top_n and top_n > 0) else ranked
                to_plot_plot = to_plot.sort_values(ascending=True)

                fig, ax = plt.subplots(figsize=(8, 6))
                to_plot_plot.plot(kind="barh", ax=ax)
                shown = len(to_plot_plot)
                ax.set_title(f"Permutation Feature Importance (top {shown} of {len(importances_full)})")
                ax.set_xlabel("Mean score drop")
                ax.set_ylabel("Feature")
                plt.tight_layout()
                self._save_and_remove_plot("permutation_importance.png")
                plt.show()

            return ranked

        except Exception as e:
            self._log(f"Permutation importance failed: {e}")
            return None

