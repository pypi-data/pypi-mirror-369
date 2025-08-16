"""
data_explorer.py

Provides a comprehensive exploratory data analysis (EDA) toolkit for both
classification and regression problems. Includes tools for:

- Summary statistics (numeric & categorical)
- Visualizations (target distribution, correlation, missing data)
- Class balance and entropy (for classification)
- Normality tests
- Automatic report generation as a styled PDF (via xhtml2pdf)

Handles datetime features and preprocessing considerations for modeling readiness.

Author: Joshua Thompson
"""

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from jinja2 import Template
from scipy.stats import entropy, normaltest
from xhtml2pdf import pisa

from ..utils.preprocessing import impute_numeric


class DataExplorer:
    """
    An advanced exploratory data analysis (EDA) toolkit for classification and regression problems.

    Detects task type automatically, extracts datetime components, supports summary statistics,
    visualizations, diagnostic checks (e.g., normality, multicollinearity), and can generate
    a styled PDF report.

    Attributes:
        df (pd.DataFrame): Cleaned copy of the input DataFrame.
        target_col (str): Name of the target variable.
        task_type (str): 'classification' if target has ≤10 unique values, else 'regression'.
        datetime_cols (List[str]): Original datetime column names prior to decomposition.
    """

    def __init__(self, df, target_col):
        """
        Initialize the DataExplorer with a DataFrame and a target column.

        Automatically detects task type (classification or regression) based on
        target column cardinality.

        Args:
            df (pd.DataFrame): Dataset to analyze.
            target_col (str): Column to treat as the target.
        """
        self.df = df.copy()
        self.target_col = target_col
        self.task_type = (
            "classification"
            if self.df[target_col].nunique() <= 10
            else "regression"
        )
        self.datetime_cols = df.select_dtypes(
            include="datetime"
        ).columns.tolist()
        self.extract_datetime_features()

    def extract_datetime_features(self):
        """
        Extracts basic time-based components from datetime columns: year, month, day, weekday.

        Removes original datetime columns after extraction.
        """
        for col in self.datetime_cols:
            self.df[f"{col}_year"] = self.df[col].dt.year
            self.df[f"{col}_month"] = self.df[col].dt.month
            self.df[f"{col}_day"] = self.df[col].dt.day
            self.df[f"{col}_weekday"] = self.df[col].dt.weekday
        self.df.drop(columns=self.datetime_cols, inplace=True)

    def get_imputed_numeric_df(self):
        """
        Returns a numeric-only DataFrame with missing values imputed using utility function.

        Returns:
            pd.DataFrame: Imputed numeric features (excluding target column).
        """
        X = self.df.drop(columns=[self.target_col], errors="ignore")
        return impute_numeric(X)

    def numeric_summary(self, return_df=False):
        """
        Summarizes numeric columns with statistics (mean, median, skewness, etc.) and missing values.

        Args:
            return_df (bool): If True, returns summary as DataFrame. If False, prints to console.

        Returns:
            Optional[pd.DataFrame]: Numeric summary DataFrame if return_df is True.
        """
        df = self.df.copy()
        shape_info = f"{df.shape[0]:,} rows × {df.shape[1]:,} columns"

        numeric_df = df.select_dtypes(include="number")
        numeric_cols = numeric_df.columns

        dtypes = df.dtypes[numeric_cols].astype(str)
        missing_pct = df[numeric_cols].isnull().mean() * 100

        stats = pd.DataFrame(
            {
                "Mean": numeric_df.mean(),
                "Median": numeric_df.median(),
                "Min": numeric_df.min(),
                "25th %ile": numeric_df.quantile(0.25),
                "75th %ile": numeric_df.quantile(0.75),
                "Max": numeric_df.max(),
                "Skewness": numeric_df.skew(),
            }
        )

        summary_df = pd.concat([dtypes, missing_pct, stats], axis=1)
        summary_df.columns = [
            "Data Type",
            "Missing (%)",
            "Mean",
            "Median",
            "Min",
            "25th %ile",
            "75th %ile",
            "Max",
            "Skewness",
        ]
        summary_df["Missing (%)"] = summary_df["Missing (%)"].map(
            "{:.2f}".format
        )
        summary_df = summary_df.round(2)

        if return_df:
            return summary_df

        print(f"Dataset Summary: {shape_info}")
        from IPython.display import HTML, display

        display(HTML(summary_df.to_html(classes="table table-sm", border=0)))

    def categorical_summary(self, return_df=False):
        """
        Summarizes categorical (object or category) columns with frequency, uniqueness, and missing rates.

        Args:
            return_df (bool): If True, returns summary as DataFrame.

        Returns:
            Optional[pd.DataFrame]: Summary table if return_df is True.
        """
        df = self.df.copy()
        cat_df = df.select_dtypes(include=["object", "category"])

        if cat_df.empty:
            print("No categorical features found.")
            return pd.DataFrame() if return_df else None

        dtypes = cat_df.dtypes.astype(str)
        missing_pct = cat_df.isnull().mean() * 100
        unique_counts = cat_df.nunique()

        # Safely get most frequent values and their percentages
        most_frequent = cat_df.apply(
            lambda x: x.mode().iloc[0] if not x.mode().empty else np.nan
        )
        most_freq_pct = cat_df.apply(
            lambda x: (
                x.value_counts(normalize=True).iloc[0] * 100
                if not x.value_counts().empty
                else 0
            )
        )

        summary = pd.DataFrame(
            {
                "Data Type": dtypes,
                "Missing (%)": missing_pct,
                "# Unique": unique_counts,
                "Most Frequent": most_frequent,
                "Freq (%)": most_freq_pct,
            }
        )

        summary["Missing (%)"] = summary["Missing (%)"].round(2)
        summary["Freq (%)"] = summary["Freq (%)"].round(2)

        if return_df:
            return summary

        print(f"Categorical Feature Summary: {summary.shape[0]} columns")
        from IPython.display import HTML, display

        display(HTML(summary.to_html(classes="table table-sm", border=0)))

    def plot_target_distribution(self, ax=None):
        """
        Plots the distribution of the target variable.

        Args:
            ax (matplotlib.axes._subplots.AxesSubplot, optional): Axis to draw on. Creates one if not provided.
        """
        ax = ax or plt.gca()
        if self.task_type == "regression":
            sns.histplot(self.df[self.target_col], kde=True, ax=ax)
            ax.set_title(f"Target Distribution: {self.target_col}")
        else:
            class_counts = self.df[self.target_col].value_counts()
            class_counts.plot(kind="bar", ax=ax)
            ax.set_title(
                f"Class Distribution ({class_counts.shape[0]} classes)"
            )

        if ax is plt.gca():
            plt.tight_layout()
            plt.show()

    def correlation_heatmap(self, ax=None, exclude_cols=None):
        """
        Displays a correlation heatmap for numeric features.

        Args:
            ax (matplotlib.axes._subplots.AxesSubplot, optional): Axis to draw on.
            exclude_cols (List[str], optional): Columns to exclude from heatmap.
        """
        ax = ax or plt.gca()
        data = (
            self.df.drop(columns=exclude_cols, errors="ignore")
            if exclude_cols
            else self.df
        )
        corr = data.select_dtypes(include="number").corr()
        sns.heatmap(
            corr,
            annot=True,
            fmt=".3f",
            cmap="coolwarm",
            annot_kws={"size": 8},
            ax=ax,
        )
        ax.set_title("Correlation Heatmap")
        if ax is plt.gca():
            plt.tight_layout()
            plt.show()

    def test_feature_normality(
        self, alpha=0.05, unique_threshold=30, verbose=True
    ):
        """
        Performs D’Agostino and Pearson’s normality test for continuous numeric features only.

        Skips binary/discrete features with low unique values.

        Args:
            alpha (float): Significance level to determine normality.
            unique_threshold (int): Minimum unique values to be considered continuous.
            verbose (bool): Print summary of skipped features.

        Returns:
            pd.DataFrame: Test statistics, p-values, and normality flags.
        """
        X = self.get_imputed_numeric_df()

        # Filter out low-cardinality features
        filtered_cols = [
            col for col in X.columns if X[col].nunique() > unique_threshold
        ]
        skipped_cols = [col for col in X.columns if col not in filtered_cols]

        results = {}
        for col in filtered_cols:
            try:
                stat, p = normaltest(X[col])
                results[col] = {
                    "statistic": stat,
                    "p_value": p,
                    "normal": p >= alpha,
                }
            except Exception:
                results[col] = {
                    "statistic": None,
                    "p_value": None,
                    "normal": None,
                }

        if verbose and skipped_cols:
            print(
                f"Skipped {len(skipped_cols)} low-cardinality or binary feature(s): {', '.join(skipped_cols)}"
            )

        return pd.DataFrame(results).T.sort_values(
            "p_value", na_position="last"
        )

    def class_balance_summary(self):
        """
        Shows the distribution of target classes (for classification tasks only).

        Returns:
            pd.DataFrame or None: Class proportion table if classification; None otherwise.
        """
        if self.task_type != "classification":
            print("Only valid for classification tasks.")
            return
        return (
            self.df[self.target_col]
            .value_counts(normalize=True)
            .to_frame("Proportion")
        )

    def class_entropy(self):
        """
        Calculates Shannon entropy of the target class distribution.

        Returns:
            float or None: Entropy score, or None if not classification.
        """
        if self.task_type != "classification":
            print("Only applicable to classification tasks.")
            return
        probs = self.df[self.target_col].value_counts(normalize=True)
        return entropy(probs)

    def generate_report(
        self, output_path="eda_report.pdf", sample_size=10000, max_features=40
    ):
        """
        Generates a full EDA report as a styled PDF file, with plots and summaries.

        Args:
            output_path (str): File path for saving the PDF.
            sample_size (int): Max number of rows to include (for speed).
            max_features (int): Max number of numeric features (by variance).
        """
        # === Setup directory for plot files ===
        plot_dir = os.path.abspath("glazzbocks_report_images")
        os.makedirs(plot_dir, exist_ok=True)

        # === Subset if too large ===
        df = self.df.copy()
        reduction_note = ""

        if df.shape[0] > sample_size:
            df = df.sample(n=sample_size, random_state=42)
            reduction_note += f"Sampled to {sample_size} rows. "

        if df.select_dtypes(include="number").shape[1] > max_features:
            top_vars = (
                df.select_dtypes(include="number")
                .var()
                .sort_values(ascending=False)
                .head(max_features)
                .index
            )
            df = df[top_vars.to_list() + [self.target_col]]
            reduction_note += (
                f"Top {max_features} numeric features retained by variance. "
            )

        # === Tables ===
        numeric_tbl = self.numeric_summary(return_df=True).to_html(
            classes="table table-sm", border=0
        )
        cat_summary_df = self.categorical_summary(return_df=True)
        cat_tbl = (
            cat_summary_df.to_html(classes="table table-sm", border=0)
            if not cat_summary_df.empty
            else None
        )

        # === Missing Summary Table ===
        missing_tbl = df.isnull().mean().reset_index()
        missing_tbl.columns = ["column", "missing_percent"]
        missing_tbl = missing_tbl[missing_tbl["missing_percent"] > 0]
        if not missing_tbl.empty:
            missing_tbl["missing_percent"] = (
                missing_tbl["missing_percent"] * 100
            ).map("{:.2f}%".format)
            missing_html = missing_tbl.to_html(index=False)
        else:
            missing_html = None

        # === Classification-Specific Info ===
        if self.task_type == "classification":
            entropy_val = f"{self.class_entropy():.4f}"
            imbalance = self.class_balance_summary().to_html(classes="table")
        else:
            entropy_val = None
            imbalance = None

        # === Helper to Save Plots ===
        def save_plot(func, filename):
            path = os.path.join(plot_dir, filename)
            try:
                plt.figure()
                func()
                plt.tight_layout()
                plt.savefig(path, format="png", dpi=150)
                plt.close()
                return path.replace("\\", "/")
            except Exception:
                return None

        # === Create Plots ===
        target_path = save_plot(self.plot_target_distribution, "target.png")
        corr_path = save_plot(self.correlation_heatmap, "correlation.png")

        # === Template & Export ===
        html_template = """<html>
        <head><style>body { font-family: Arial; }</style></head>
        <body>
            <h1>EDA Report</h1>
            <p>{{ note }}</p>
            <p><b>Shape:</b> {{ rows }} rows × {{ cols }} columns</p>
            <p><b>Task:</b> {{ task }}</p>
            <p><b>Target Column:</b> {{ target }}</p>

            {% if entropy %}
                <p><b>Entropy:</b> {{ entropy }}</p>
            {% endif %}

            {% if imbalance %}
                <h3>Class Balance</h3>
                {{ imbalance | safe }}
            {% endif %}

            <h3>Numeric Summary</h3>
            {{ numeric | safe }}

            {% if categorical %}
                <h3>Categorical Summary</h3>
                {{ categorical | safe }}
            {% endif %}

            {% if missing %}
                <h3>Missing Values</h3>
                {{ missing | safe }}
            {% endif %}

            <h3>Target Distribution</h3>
            {% if target_img %}<img src="{{ target_img }}"><br>{% endif %}

            <h3>Correlation Heatmap</h3>
            {% if correlation_img %}<img src="{{ correlation_img }}"><br>{% endif %}
        </body></html>
        """

        template = Template(html_template)
        html_content = template.render(
            note=reduction_note,
            rows=df.shape[0],
            cols=df.shape[1],
            task=self.task_type,
            target=self.target_col,
            numeric=numeric_tbl,
            categorical=cat_tbl,
            missing=missing_html,
            entropy=entropy_val,
            imbalance=imbalance,
            target_img=target_path,
            correlation_img=corr_path,
        )

        with open(output_path, "w+b") as result_file:
            pisa.CreatePDF(src=html_content, dest=result_file)

        print(f"PDF exported to: {output_path}")
