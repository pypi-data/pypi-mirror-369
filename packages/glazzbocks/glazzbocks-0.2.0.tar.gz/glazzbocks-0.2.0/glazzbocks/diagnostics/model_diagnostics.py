"""
model_diagnostics.py

Provides a comprehensive visual diagnostics toolkit for scikit-learn models.

Supports both classification and regression pipelines via intuitive plotting functions,
including:

- ROC and precision-recall curves (binary/multiclass)
- Confusion matrices and F1-threshold visualizations
- Lift and cumulative gain charts
- Residual analysis and QQ plots for regression models
- Automated plotting suite via `auto_plot()`

The module is designed for use with fitted sklearn `Pipeline` objects and
automatically detects model type and plot applicability.

Author: Joshua Thompson
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from scipy.stats import normaltest
from sklearn.base import is_classifier
from sklearn.linear_model import ElasticNet, Lasso, LinearRegression, Ridge
from sklearn.manifold import TSNE
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    RocCurveDisplay,
    brier_score_loss,
    confusion_matrix,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import label_binarize


class ModelDiagnostics:
    """
    A visualization-based diagnostic toolkit for evaluating fitted scikit-learn pipelines.
    """

    def __init__(self, pipeline):
        self.pipeline = pipeline
        self.model = self.pipeline.steps[-1][1]

    def _check_fitted(self, X=None, y=None):
        """
        Confirm that the pipeline is fitted and warn if running diagnostics on training data.
        """
        if not hasattr(self.pipeline, "predict"):
            raise ValueError("Pipeline is not fitted.")

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

    def plot_roc_curve(self, X_test, y_test):
        self._check_fitted(X_test, y_test)
        if not is_classifier(self.model):
            raise ValueError("Only valid for classification models.")
        y_proba = self.pipeline.predict_proba(X_test)
        classes = np.unique(y_test)
        plt.figure(figsize=(8, 6))
        if y_proba.shape[1] == 2:
            y_score = y_proba[:, 1]
            auc_score = roc_auc_score(y_test, y_score)
            RocCurveDisplay.from_predictions(y_test, y_score)
            plt.title(f"ROC Curve - Binary (AUC = {auc_score:.2f})")
        else:
            y_test_bin = label_binarize(y_test, classes=classes)
            for i, cls in enumerate(classes):
                fpr, tpr, _ = roc_curve(y_test_bin[:, i], y_proba[:, i])
                auc_score = roc_auc_score(y_test_bin[:, i], y_proba[:, i])
                plt.plot(fpr, tpr, label=f"Class {cls} (AUC={auc_score:.2f})")
            plt.plot([0, 1], [0, 1], "k--")
            plt.title("ROC Curve - Multiclass OvR")
            plt.legend()
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.grid(True)
        plt.show()

    def plot_precision_recall_curve(self, X_test, y_test):
        self._check_fitted(X_test, y_test)
        if not is_classifier(self.model):
            raise ValueError("Only valid for classification models.")
        y_proba = self.pipeline.predict_proba(X_test)
        if y_proba.shape[1] != 2:
            print("Precision-recall curve not supported for multiclass.")
            return
        precision, recall, _ = precision_recall_curve(y_test, y_proba[:, 1])
        plt.figure(figsize=(8, 6))
        plt.plot(recall, precision, label="PR Curve")
        plt.xlabel("Recall")
        plt.ylabel("Precision")
        plt.title("Precision-Recall Curve - Test Set")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def plot_f1_threshold(self, X_test, y_test):
        self._check_fitted(X_test, y_test)
        if not is_classifier(self.model):
            raise ValueError("Only valid for classification models.")
        y_proba = self.pipeline.predict_proba(X_test)
        if y_proba.shape[1] != 2:
            print("F1 vs Threshold not supported for multiclass.")
            return
        y_score = y_proba[:, 1]
        precision, recall, thresholds = precision_recall_curve(y_test, y_score)
        f1_scores = 2 * (precision * recall) / (precision + recall + 1e-10)
        idx = np.argmax(f1_scores)
        plt.figure(figsize=(8, 6))
        plt.plot(thresholds, f1_scores[:-1], label="F1 Score")
        plt.plot(
            thresholds[idx],
            f1_scores[idx],
            "ro",
            label=f"Best = {thresholds[idx]:.2f}",
        )
        plt.xlabel("Threshold")
        plt.ylabel("F1 Score")
        plt.title("F1 Score vs Threshold - Test Set")
        plt.legend()
        plt.grid(True)
        plt.show()

    def plot_confusion_matrix(self, X_test, y_test, normalize="true", threshold=None):
        self._check_fitted(X_test, y_test)
        if not is_classifier(self.model):
            raise ValueError("Only valid for classification models.")

        if threshold is not None:
            y_pred_proba = self.pipeline.predict_proba(X_test)[:, 1]
            y_pred = (y_pred_proba >= threshold).astype(int)
        else:
            y_pred = self.pipeline.predict(X_test)

        cm = confusion_matrix(y_test, y_pred, normalize=normalize)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm)
        disp.plot(cmap="Blues", values_format=".2f" if normalize else "d")
        plt.title(
            f"Confusion Matrix - Test Set (Threshold = {threshold:.2f})"
            if threshold else "Confusion Matrix - Test Set"
        )
        plt.grid(False)
        plt.show()

    def plot_lift_chart(self, X_test, y_test, bins=10):
        self._check_fitted(X_test, y_test)
        if not is_classifier(self.model):
            raise ValueError("Only valid for classification models.")
        y_proba = self.pipeline.predict_proba(X_test)
        if y_proba.shape[1] != 2:
            print("Lift chart only supported for binary classification.")
            return
        df = pd.DataFrame({"y": y_test, "proba": y_proba[:, 1]})
        if not pd.api.types.is_numeric_dtype(df["y"]):
            df["y"] = df["y"].astype("category").cat.codes
        df["bin"] = pd.qcut(df["proba"], q=bins, duplicates="drop")
        lift = df.groupby("bin", observed=False)["y"].mean() / df["y"].mean()
        lift.plot(kind="bar", figsize=(8, 6))
        plt.title("Lift Chart")
        plt.ylabel("Lift")
        plt.xlabel("Probability Decile")
        plt.grid(False)
        plt.show()

    def plot_cumulative_gain_chart(self, X_test, y_test):
        self._check_fitted(X_test, y_test)
        if not is_classifier(self.model):
            raise ValueError("Only valid for classification models.")
        y_proba = self.pipeline.predict_proba(X_test)
        if y_proba.shape[1] != 2:
            print(
                "Cumulative gain chart only supported for binary classification."
            )
            return
        y_numeric = pd.Series(y_test)
        if not pd.api.types.is_numeric_dtype(y_numeric):
            y_numeric = y_numeric.astype("category").cat.codes
        data = pd.DataFrame({"y_true": y_numeric, "y_score": y_proba[:, 1]})
        data.sort_values(by="y_score", ascending=False, inplace=True)
        data["cum_positive"] = data["y_true"].cumsum()
        data["percent_samples"] = np.arange(1, len(data) + 1) / len(data)
        data["percent_positive"] = data["cum_positive"] / data["y_true"].sum()
        plt.figure(figsize=(8, 6))
        plt.plot(
            data["percent_samples"], data["percent_positive"], label="Model"
        )
        plt.plot([0, 1], [0, 1], "k--", label="Baseline")
        plt.title("Cumulative Gain Chart")
        plt.xlabel("Proportion of Samples")
        plt.ylabel("Cumulative Positives")
        plt.legend()
        plt.grid(False)
        plt.show()

    def plot_predicted_vs_actual(self, X_test, y_test):
        self._check_fitted(X_test, y_test)
        if is_classifier(self.model):
            raise ValueError("Only valid for regression models.")
        y_pred = self.pipeline.predict(X_test)
        plt.figure(figsize=(8, 6))
        plt.scatter(y_test, y_pred, alpha=0.5)
        plt.plot(
            [y_test.min(), y_test.max()],
            [y_test.min(), y_test.max()],
            "r--",
            lw=2,
        )
        plt.title("Predicted vs Actual - Test Set")
        plt.xlabel("Actual")
        plt.ylabel("Predicted")
        plt.grid(False)
        plt.show()

    def plot_residuals(self, X_test, y_test, check_normality=True):
        self._check_fitted(X_test, y_test)
        if is_classifier(self.model):
            raise ValueError("Only valid for regression models.")
        y_pred = self.pipeline.predict(X_test)
        residuals = y_test - y_pred
        is_linear = isinstance(
            self.model, (LinearRegression, Ridge, Lasso, ElasticNet)
        )
        if is_linear and check_normality:
            stat, p = normaltest(residuals)
            print(
                f"Normality Test: stat={stat:.2f}, p={p:.3f} → {'Normal' if p >= 0.05 else 'Not Normal'}"
            )
        plt.figure(figsize=(8, 6))
        plt.scatter(y_pred, residuals, alpha=0.5)
        plt.axhline(0, color="red", linestyle="--")
        plt.title("Residuals vs Predicted")
        plt.xlabel("Predicted")
        plt.ylabel("Residuals")
        plt.grid(False)
        plt.show()

    def plot_error_distribution(self, X_test, y_test):
        self._check_fitted(X_test, y_test)
        if is_classifier(self.model):
            raise ValueError("Only valid for regression models.")
        residuals = y_test - self.pipeline.predict(X_test)
        plt.figure(figsize=(8, 6))
        plt.hist(residuals, bins=30, alpha=0.7)
        plt.title("Residuals Histogram")
        plt.xlabel("Residuals")
        plt.grid(False)
        plt.show()

    def plot_qq(self, X_test, y_test):
        self._check_fitted(X_test, y_test)
        if is_classifier(self.model):
            raise ValueError("Only valid for regression models.")
        residuals = y_test - self.pipeline.predict(X_test)
        plt.figure(figsize=(8, 6))
        stats.probplot(residuals, dist="norm", plot=plt)
        plt.title("QQ Plot of Residuals")
        plt.grid(False)
        plt.show()

    def calibration_reliability_table(self, X_test, y_test, n_bins=10):
        self._check_fitted(X_test, y_test)
        if not is_classifier(self.model):
            raise ValueError(
                "Calibration diagnostics are only valid for classification models."
            )
        y_proba = self.pipeline.predict_proba(X_test)
        if y_proba.shape[1] != 2:
            raise ValueError(
                "Calibration plot currently supports binary classification only."
            )
        y = pd.Series(y_test)
        if not pd.api.types.is_numeric_dtype(y):
            y = y.astype("category").cat.codes
        y_true = y.to_numpy().astype(int)
        y_prob = y_proba[:, 1].astype(float)
        bins = np.linspace(0.0, 1.0, n_bins + 1)
        idx = np.digitize(y_prob, bins) - 1
        rows = []
        for b in range(n_bins):
            mask = idx == b
            if not np.any(mask):
                continue
            pred_mean = float(y_prob[mask].mean())
            obs_rate = float(y_true[mask].mean())
            rows.append(
                {
                    "bin": int(b + 1),
                    "pred_mean": pred_mean,
                    "obs_rate": obs_rate,
                    "count": int(mask.sum()),
                    "bin_left": float(bins[b]),
                    "bin_right": float(bins[b + 1]),
                }
            )
        return pd.DataFrame(rows)

    def calibration_summary(self, X_test, y_test, n_bins=10, return_df=True):
        self._check_fitted(X_test, y_test)
        if not is_classifier(self.model):
            raise ValueError(
                "Calibration diagnostics are only valid for classification models."
            )
        y_proba = self.pipeline.predict_proba(X_test)
        if y_proba.shape[1] != 2:
            raise ValueError(
                "Calibration summary currently supports binary classification only."
            )
        y = pd.Series(y_test)
        if not pd.api.types.is_numeric_dtype(y):
            y = y.astype("category").cat.codes
        y_true = y.to_numpy().astype(int)
        y_prob = y_proba[:, 1].astype(float)
        metrics = {
            "Brier Score": brier_score_loss(y_true, y_prob),
            "ECE (Expected Calibration Error)": self._expected_calibration_error(
                y_true, y_prob, n_bins=n_bins
            ),
            "Avg Predicted Probability": np.mean(y_prob),
            "Avg Observed Frequency": np.mean(y_true),
            "Number of Bins Used": n_bins,
        }
        if return_df:
            df = pd.DataFrame(metrics, index=["Calibration Summary"]).T
            df.columns = ["Value"]
            return df.round(4)
        return {k: float(v) for k, v in metrics.items()}

    @staticmethod
    def _expected_calibration_error(
        y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10
        ) -> float:
            bins = np.linspace(0.0, 1.0, n_bins + 1)
            idx = np.digitize(y_prob, bins) - 1
            ece = 0.0
            n = len(y_true)
            for b in range(n_bins):
                mask = idx == b
                if not np.any(mask):
                    continue
                p_hat = y_prob[mask].mean()
                p_obs = y_true[mask].mean()
                w = mask.sum() / n
                ece += w * abs(p_hat - p_obs)
            return float(ece)

    def plot_class_separation(self, X, y, method="tsne", perplexity=30):
        """
        Projects feature space into 2D and colors by class for visual separability.
        """
        try:
            if isinstance(self.pipeline, Pipeline):
                X_transformed = self.pipeline.named_steps[
                    "preprocessing"
                ].transform(X)
            else:
                X_transformed = X

            if method == "tsne":
                reducer = TSNE(
                    n_components=2, perplexity=perplexity, random_state=42
                )
            elif method == "umap":
                import umap

                reducer = umap.UMAP(n_components=2, random_state=42)
            else:
                raise ValueError("Method must be 'tsne' or 'umap'.")

            embedding = reducer.fit_transform(X_transformed)
            df_plot = pd.DataFrame(embedding, columns=["Dim1", "Dim2"])
            df_plot["Class"] = y

            plt.figure(figsize=(8, 6))
            sns.scatterplot(
                data=df_plot,
                x="Dim1",
                y="Dim2",
                hue="Class",
                alpha=0.7,
                palette="tab10",
            )
            plt.title(f"{method.upper()} Class Separation")
            plt.tight_layout()
            plt.show()

        except Exception as e:
            print(f"Class separation plot failed: {e}")

    def plot_calibration(
        self, X_test, y_test, n_bins=10, show_points=True, ax=None
        ):
            self._check_fitted(X_test, y_test)
            tbl = self.calibration_reliability_table(X_test, y_test, n_bins=n_bins)
            if ax is None:
                _, ax = plt.subplots(figsize=(7.5, 6))
            ax.plot([0, 1], [0, 1], "k--", linewidth=1, label="Perfect")
            tbl_sorted = tbl.sort_values("pred_mean")
            ax.plot(
                tbl_sorted["pred_mean"],
                tbl_sorted["obs_rate"],
                linewidth=2,
                label="Observed",
            )
            if show_points:
                ax.scatter(
                    tbl_sorted["pred_mean"],
                    tbl_sorted["obs_rate"],
                    s=np.clip(tbl_sorted["count"], 20, 120),
                    alpha=0.7,
                )
            ax.set_title("Reliability Curve (Calibration)")
            ax.set_xlabel("Predicted probability (bin mean)")
            ax.set_ylabel("Observed event rate")
            ax.grid(True, linestyle=":", alpha=0.6)
            ax.legend()
            plt.tight_layout()
            return ax

    def auto_plot(self, X_test, y_test):
        """
        Run all applicable plots based on model type.

        Args:
            X_test (np.ndarray | pd.DataFrame): Test set features.
            y_test (np.ndarray | pd.Series): True labels or values.
        """
        # Warn if running on training data
        self._check_fitted(X_test, y_test)

        if is_classifier(self.model):
            n_classes = len(np.unique(y_test))

            # Always show these for classification
            try:
                self.plot_confusion_matrix(X_test, y_test)
            except Exception as e:
                print(f"[auto_plot] Skipped confusion matrix: {e}")

            try:
                self.plot_roc_curve(X_test, y_test)
            except Exception as e:
                print(f"[auto_plot] Skipped ROC curve: {e}")

            # Binary-only extras
            if n_classes == 2:
                try:
                    self.plot_precision_recall_curve(X_test, y_test)
                except Exception as e:
                    print(f"[auto_plot] Skipped Precision-Recall curve: {e}")

                try:
                    self.plot_calibration(X_test, y_test)
                except Exception as e:
                    print(
                        f"[auto_plot] Skipped Calibration (reliability) plot: {e}"
                    )

                try:
                    self.plot_f1_threshold(X_test, y_test)
                except Exception as e:
                    print(f"[auto_plot] Skipped F1 vs Threshold: {e}")

                try:
                    self.plot_lift_chart(X_test, y_test)
                except Exception as e:
                    print(f"[auto_plot] Skipped Lift chart: {e}")

                try:
                    self.plot_cumulative_gain_chart(X_test, y_test)
                except Exception as e:
                    print(f"[auto_plot] Skipped Cumulative Gain chart: {e}")

        else:
            # Regression suite
            try:
                self.plot_predicted_vs_actual(X_test, y_test)
            except Exception as e:
                print(f"[auto_plot] Skipped Predicted vs Actual: {e}")

            try:
                self.plot_residuals(X_test, y_test)
            except Exception as e:
                print(f"[auto_plot] Skipped Residuals plot: {e}")

            try:
                self.plot_error_distribution(X_test, y_test)
            except Exception as e:
                print(f"[auto_plot] Skipped Error Distribution: {e}")

            try:
                self.plot_qq(X_test, y_test)
            except Exception as e:
                print(f"[auto_plot] Skipped QQ plot: {e}")
