import math
from typing import List, Literal, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import chi2_contingency


class UnivariateAnalysis:
    def __init__(
        self, df: pd.DataFrame, target_column: str, numerical_features: List[str]
    ) -> None:
        """
        Initialize the UnivariateAnalysis class with data and configuration.

        Parameters
        ----------
        df : pd.DataFrame
            The data to be analyzed.
        target_column : str
            The target column for analysis.
        numerical_features : List[str]
            List of numerical features.
        """
        self.data = df.copy()
        self.target_column = target_column
        self.numerical_features = numerical_features or []

    @staticmethod
    def _get_cramers_v(df: pd.DataFrame, var1: str, var2: str) -> float:
        """
        Calculate Cramer's V statistic for two variables.

        Parameters
        ----------
        df : pd.DataFrame
            The data containing the variables.
        var1 : str
            The first variable.
        var2 : str
            The second variable.

        Returns
        -------
        float
            Cramer's V statistic.
        """
        confusion_matrix = pd.crosstab(df[var1], df[var2])
        chi2 = chi2_contingency(confusion_matrix)[0]
        n = confusion_matrix.sum().sum()
        min_dim = min(confusion_matrix.shape) - 1

        return np.sqrt(chi2 / (n * min_dim))

    def _prepare_cramers_v_features(
        self, numerical_features: List[str], num_bins: int = 5
    ) -> List[str]:
        """
        Prepare features for Cramer's V calculation by binning numerical features.

        Parameters
        ----------
        numerical_features : List[str]
            List of numerical feature names.
        num_bins : int, optional
            Number of bins for continuous variables, by default 5.

        Returns
        -------
        List[str]
            List of features prepared for Cramer's V calculation.
        """
        cramers_v_var_list = self.data.select_dtypes(
            include=["object", "category"]
        ).columns.tolist()

        # Exclude the target column
        cramers_v_var_list = [
            var for var in cramers_v_var_list if var != self.target_column
        ]

        for num in numerical_features:
            unique_values = self.data[num].nunique()

            if (
                unique_values > 1
            ):  # Ensure there are at least two unique values for binning
                try:
                    self.data[f"{num}_bin"] = pd.qcut(
                        self.data[num], q=num_bins, duplicates="drop"
                    )
                    # Check if the resulting bins are more than 1
                    if self.data[f"{num}_bin"].nunique() <= 1:
                        raise ValueError(
                            f"Only 1 bin created for {num} with q={num_bins}."
                        )

                except ValueError as e:
                    print(
                        f"Equal frequency binning not possible for {num}, attempting 2 bins: {e}"
                    )
                    if pd.api.types.is_integer_dtype(self.data[num]):
                        # For integer type, ensure bins are whole numbers
                        self.data[f"{num}_bin"] = pd.cut(
                            self.data[num], bins=2, include_lowest=True, right=False
                        )
                    else:
                        # For non-integer type, fallback to 2 equal frequency bins
                        self.data[f"{num}_bin"] = pd.qcut(
                            self.data[num], q=2, duplicates="drop"
                        )
                cramers_v_var_list.append(f"{num}_bin")
            else:
                # Handle the case where there is only one unique value
                print(f"Skipping {num} as it has only {unique_values} unique value(s).")

        return cramers_v_var_list

    def plot_cramers_v(
        self,
        numerical_features: List[str],
        excluded_columns: List[str],
        filter_threshold: float,
        num_bins: int = 5,
        fig_width: int = 800,
        fig_height: int = 800,
    ) -> Tuple[pd.DataFrame, List[str]]:
        """
        Calculate and plot Cramer's V for multiple features using Plotly Express.

        Parameters
        ----------
        numerical_features : List[str]
            List of numerical feature names.
        excluded_columns : List[str]
            List of variables to exclude from the analysis.
        num_bins : int, optional
            Number of bins for continuous variables, by default 5.
        fig_width : int, optional
            Width of the figure in pixels, by default 800.
        fig_height : int, optional
            Height of the figure in pixels, by default 800.

        Returns
        -------
        pd.DataFrame
            DataFrame containing Cramer's V values.
        """
        cramers_v_var_list = self._prepare_cramers_v_features(
            numerical_features, num_bins
        )

        # Exclude any specified variables
        cramers_v_var_list = [
            var for var in cramers_v_var_list if var not in excluded_columns
        ]

        rows = []
        for cat in cramers_v_var_list:
            cramers = UnivariateAnalysis._get_cramers_v(
                self.data, cat, self.target_column
            )
            rows.append(round(cramers, 2))

        cramers_results = pd.DataFrame(
            rows, columns=[self.target_column], index=cramers_v_var_list
        )

        cramers_results.sort_values(
            by=self.target_column, ascending=False, inplace=True
        )

        # Create a Plotly heatmap
        fig = px.imshow(
            cramers_results,
            labels={"x": self.target_column, "y": "Features", "color": "Cramer's V"},
            color_continuous_scale="Plasma",
            text_auto=True,
            aspect="auto",
            width=fig_width,
            height=fig_height,
        )

        fig.update_layout(
            title="Cramer's V with Target Variable",
            xaxis_title=self.target_column,
            yaxis_title="Features",
        )

        fig.show()

        filtered_vars = cramers_results[
            cramers_results[self.target_column] > filter_threshold
        ].index.tolist()

        return cramers_results, filtered_vars

    def _calculate_information_value(
        self,
        feature_column: str,
        target_column: str,
        num_bins: int = 10,
        show_woe: bool = False,
    ) -> Union[Tuple[float, pd.DataFrame], float]:
        """
        Calculate Information Value for a single feature.

        Parameters
        ----------
        feature_column : str
            Name of the feature column.
        target_column : str
            Name of the target column.
        num_bins : int, optional
            Number of bins for continuous variables, by default 10.
        show_woe : bool, optional
            Boolean to show WOE values, by default False.

        Returns
        -------
        Tuple[float, pd.DataFrame] or float
            Information Value and optionally the WOE DataFrame.
        """
        df = pd.DataFrame(
            {
                feature_column: self.data[feature_column],
                target_column: self.data[target_column].astype(float),
            }
        )

        if df[feature_column].dtype in ["int64", "float64"]:
            df["bins"] = pd.qcut(df[feature_column], q=num_bins, duplicates="drop")
        else:
            df["bins"] = df[feature_column]

        total_good = df[target_column].sum()
        total_bad = df[target_column].count() - total_good

        # Explicitly setting observed=False to retain current behavior
        grouped = df.groupby("bins", observed=False)[target_column].agg(
            ["sum", "count"]
        )
        grouped["good"] = grouped["sum"]
        grouped["bad"] = grouped["count"] - grouped["sum"]

        # Add a small value to prevent division by zero
        epsilon = 1e-10
        grouped["good_pct"] = (grouped["good"] + epsilon) / (total_good + epsilon)
        grouped["bad_pct"] = (grouped["bad"] + epsilon) / (total_bad + epsilon)

        grouped["woe"] = np.log(grouped["good_pct"] / grouped["bad_pct"])
        grouped["iv"] = (grouped["good_pct"] - grouped["bad_pct"]) * grouped["woe"]

        iv = grouped["iv"].sum()

        if show_woe:
            return iv, grouped[["good", "bad", "good_pct", "bad_pct", "woe", "iv"]]
        else:
            return iv

    def plot_information_value(
        self,
        numerical_features: List[str],
        filter_threshold: float,
        target_column: str,
        num_bins: int = 10,
        fig_width: int = 800,
        fig_height: int = 800,
    ) -> Tuple[pd.DataFrame, List[str]]:
        """
        Calculate and plot Information Value for multiple features using Plotly Express.

        Parameters
        ----------
        numerical_features : List[str]
            List of numerical feature names.
        target_column : str
            Name of the target column.
        num_bins : int, optional
            Number of bins for continuous variables, by default 10.
        fig_width : int, optional
            Width of the figure in pixels, by default 800.
        fig_height : int, optional
            Height of the figure in pixels, by default 800.

        Returns
        -------
        pd.DataFrame
            DataFrame containing Information Values.
        """
        iv_values = []
        for feature in numerical_features:
            iv = self._calculate_information_value(feature, target_column, num_bins)
            iv_values.append(iv)

        iv_df = pd.DataFrame(
            iv_values, columns=[target_column], index=numerical_features
        )

        iv_df.sort_values(by=target_column, ascending=False, inplace=True)

        # Create the heatmap using Plotly Express
        fig = px.imshow(
            iv_df,
            labels={"x": "Features", "y": target_column, "color": "Information Value"},
            color_continuous_scale="Plasma",
            text_auto=True,
            aspect="auto",
            width=fig_width,
            height=fig_height,
        )

        # Update layout
        fig.update_layout(
            title="Information Value with Target Variable",
            xaxis_title="Features",
            yaxis_title=target_column,
        )

        # Display the figure
        fig.show()

        filtered_vars = iv_df[filter_threshold < iv_df[target_column]].index.tolist()

        return iv_df, filtered_vars

    def plot_distributions(
        self,
        numerical_columns: Optional[List[str]] = None,
        grouped: bool = False,
        fig_width: int = 1100,
        fig_height: int = 600,
    ) -> None:
        """
        Plot the distribution of numerical columns using Plotly Express.

        Parameters
        ----------
        numerical_columns : Optional[List[str]], optional
            List of numerical columns to plot. If None, all numerical features will be available for selection.
        grouped : bool, optional
            If True, plot distributions grouped by the target variable, by default False.
        fig_width : int, optional
            Width of the figure in pixels, by default 800.
        fig_height : int, optional
            Height of the figure in pixels, by default 500.
        """
        if numerical_columns is None:
            numerical_columns = self.numerical_features

        # Create the initial figure
        fig = go.Figure()

        # Add traces for each numerical column (initially hidden)
        for col in numerical_columns:
            if grouped:
                for target_value in self.data[self.target_column].unique():
                    data = self.data[self.data[self.target_column] == target_value]
                    fig.add_trace(
                        go.Histogram(
                            x=data[col],
                            name=f"{col} ({self.target_column}={target_value})",
                            visible=False,
                        )
                    )
            else:
                fig.add_trace(go.Histogram(x=self.data[col], name=col, visible=False))

        # Create buttons for dropdown
        buttons = []
        for i, col in enumerate(numerical_columns):
            button = {
                "method": "update",
                "label": col,
                "args": [
                    {"visible": [False] * len(fig.data)},  # type: ignore
                    {"title": f"Distribution of {col}"},
                ],
            }
            if grouped:
                for j in range(len(self.data[self.target_column].unique())):
                    button["args"][0]["visible"][
                        i * len(self.data[self.target_column].unique()) + j
                    ] = True
            else:
                button["args"][0]["visible"][i] = True
            buttons.append(button)

        # Update layout
        fig.update_layout(
            updatemenus=[
                {
                    "active": 0,
                    "buttons": buttons,
                    "direction": "down",
                    "pad": {"r": 10, "t": 10},
                    "showactive": True,
                    "x": 0.1,
                    "xanchor": "left",
                    "y": 1.15,
                    "yanchor": "top",
                },
            ],
            annotations=[
                {
                    "text": "Select Feature:",
                    "showarrow": False,
                    "x": 0,
                    "y": 1.085,
                    "yref": "paper",
                    "align": "left",
                }
            ],
            barmode="overlay" if grouped else "stack",
            width=fig_width,
            height=fig_height,
        )

        # Make the first trace visible
        if len(fig.data) > 0:  # type: ignore
            fig.data[0].visible = True  # type: ignore

        fig.show()

    def _make_partitions(self, num_partitions: int) -> pd.DataFrame:
        """
        Partition the numerical features into 4 bins.

        Returns
        -------
        pd.DataFrame
            DataFrame with partitioned numerical features.
        """
        partitioned = self.data.copy()
        for num in self.numerical_features:
            partitioned[num + "_bin"] = pd.qcut(
                x=partitioned[num],
                q=num_partitions,
                labels=False,
                duplicates="drop",
            ).astype("category")
        return partitioned

    def get_num_feature_repartition(
        self, time_column: str, num_partitions: int = 4, freq: str = "1ME"
    ) -> Optional[pd.DataFrame]:
        """
        Plot the risk class repartition through time and return a table of the risk class repartition through time.

        Parameters
        ----------
        time_column : str
            Name of the column that contains the observation date.
        freq : str, optional
            The frequency at which the risk class is aggregated ('D', 'M', or 'Y'), by default '1ME'.

        Returns
        -------
        Optional[pd.DataFrame]
            DataFrame containing the risk class repartition through time.
        """
        partitioned = self._make_partitions(num_partitions)

        # Drop rows where the time column is NaT
        if partitioned[time_column].isnull().any():
            print(
                f"There are missing entries in the {time_column} column, dropping them for the functionality; however, try to mitigate the problem."
            )
            partitioned = partitioned.dropna(subset=[time_column])

        row_nb = math.ceil(len(self.numerical_features) / 2)
        fig, ax = plt.subplots(row_nb, 2, figsize=(20, num_partitions * row_nb))
        i, j = 0, 0

        for num in self.numerical_features:
            axes = ax[j] if row_nb == 1 else ax[i, j]

            # Group by and count
            draw = (
                partitioned.groupby(
                    [num + "_bin", pd.Grouper(key=time_column, freq=freq)],
                    observed=False,
                )[self.target_column]
                .count()
                .reset_index()
            )

            # Create 'freq' column with aligned indices
            draw["freq"] = draw.groupby([time_column])[self.target_column].transform(
                lambda x: x / x.sum()
            )

            # Ensure that the indices align
            draw_pivot = pd.pivot_table(
                draw,
                values="freq",
                index=time_column,
                columns=num + "_bin",
                observed=False,
            )

            draw_pivot.plot.bar(stacked=True, ax=axes)

            if j == 0:
                j += 1
            else:
                i += 1
                j = 0

        plt.show()
        return None

    def _create_buckets(
        self, series: pd.Series, bins: list[float] | dict[str, int]
    ) -> pd.Series:
        """Create buckets for continuous and categorical variables."""
        if isinstance(bins, list):  # Continuous variable
            return pd.cut(
                series, bins=bins, labels=range(len(bins) - 1), include_lowest=True
            )
        elif isinstance(bins, dict):  # Categorical variable
            # Map categories to consistent buckets across train and test datasets
            return series.map(bins)
        else:
            raise ValueError("Invalid bins argument type.")

    def _create_bins(
        self,
        series: pd.Series,
        buckets: int = 10,
        bucket_type: Literal["quantile", "fixed_width"] = "quantile",
    ) -> list[float] | dict[str, int]:
        """Create bins for continuous variables; create mapping for categorical."""
        if series.dtype.kind in "iufc":  # Continuous variable
            if bucket_type == "quantile":
                bins = np.quantile(series.dropna(), np.linspace(0, 1, buckets + 1))
            elif bucket_type == "fixed_width":
                min_val, max_val = series.min(), series.max()
                bins = np.linspace(min_val, max_val, buckets + 1)
            else:
                raise ValueError(
                    "bucket_type must be either 'quantile' or 'fixed_width'"
                )
            return list(np.unique(bins))
        else:  # Categorical variable
            # Create a consistent mapping for categories across train and test datasets
            unique_values = series.unique()
            return {v: i for i, v in enumerate(unique_values)}

    def calculate_psi(
        self,
        train: pd.DataFrame,
        test: pd.DataFrame,
        feature_col: str,
        buckets: int = 10,
        bucket_type: Literal["quantile", "fixed_width"] = "quantile",
        epsilon: float = 1e-5,
    ) -> float:
        """
        Calculate the Population Stability Index (PSI), handling both continuous and categorical features.
        """
        combined = pd.concat([train[[feature_col]], test[[feature_col]]])
        bins = self._create_bins(combined[feature_col], buckets, bucket_type)

        train["bucket"] = self._create_buckets(train[feature_col], bins)
        test["bucket"] = self._create_buckets(test[feature_col], bins)

        # Ensure all buckets are present even if there are missing categories in train/test
        all_buckets = set(train["bucket"].unique()).union(set(test["bucket"].unique()))
        all_buckets_list = sorted(all_buckets)
        train_distribution = (
            train["bucket"]
            .value_counts(normalize=True)
            .reindex(all_buckets_list, fill_value=epsilon)
        )
        test_distribution = (
            test["bucket"]
            .value_counts(normalize=True)
            .reindex(all_buckets_list, fill_value=epsilon)
        )

        psi_values = (train_distribution - test_distribution) * np.log(
            train_distribution / test_distribution
        )
        psi_value = psi_values.sum()

        return psi_value

    def calculate_psi_detailed(
        self,
        train: pd.DataFrame,
        test: pd.DataFrame,
        feature_col: str,
        buckets: int = 10,
        bucket_type: Literal["quantile", "fixed_width"] = "quantile",
        epsilon: float = 1e-5,
    ) -> tuple[float, pd.DataFrame]:
        """
        Calculate the Population Stability Index (PSI) and provide detailed distribution info for both datasets.

        Returns a tuple containing the PSI value and a DataFrame with detailed bucket distribution analysis.
        """
        combined = pd.concat([train[[feature_col]], test[[feature_col]]])
        bins = self._create_bins(combined[feature_col], buckets, bucket_type)

        train["bucket"] = self._create_buckets(train[feature_col], bins)
        test["bucket"] = self._create_buckets(test[feature_col], bins)

        all_buckets = set(train["bucket"].unique()).union(set(test["bucket"].unique()))
        all_buckets_list = sorted(all_buckets)

        train_distribution = (
            train["bucket"]
            .value_counts(normalize=True)
            .reindex(all_buckets_list, fill_value=epsilon)
        )
        test_distribution = (
            test["bucket"]
            .value_counts(normalize=True)
            .reindex(all_buckets_list, fill_value=epsilon)
        )

        psi_values = (train_distribution - test_distribution) * np.log(
            train_distribution / test_distribution
        )
        psi_value = psi_values.sum()

        detail_df = pd.DataFrame(
            {
                "Bucket": all_buckets_list,
                "Train Distribution": train_distribution.values,
                "Test Distribution": test_distribution.values,
                "PSI Contribution": psi_values.values,
            }
        ).sort_values("PSI Contribution", ascending=False)

        if isinstance(bins, dict):
            detail_df["Bucket"] = detail_df["Bucket"].map(
                {v: k for k, v in bins.items()}
            )

        return psi_value, detail_df

    def calculate_psi_for_features(
        self,
        train: pd.DataFrame,
        test: pd.DataFrame,
        feature_cols: list[str],
        buckets: int = 10,
        bucket_type: Literal["quantile", "fixed_width"] = "quantile",
        epsilon: float = 1e-5,
    ) -> dict[str, float]:
        """
        Calculate PSI for a list of features, handling both continuous and categorical.
        """
        psi_values = {}
        for feature in feature_cols:
            try:
                psi = self.calculate_psi(
                    train, test, feature, buckets, bucket_type, epsilon
                )
                psi_values[feature] = psi
            except Exception as e:
                psi_values[feature] = f"Error calculating PSI: {e!s}"
        return psi_values

    def visualize_psi_for_features(
        self,
        train: pd.DataFrame,
        test: pd.DataFrame,
        feature_cols: list[str],
        buckets: int = 10,
        bucket_type: Literal["quantile", "fixed_width"] = "quantile",
        epsilon: float = 1e-5,
    ) -> go.Figure:
        """
        Visualize the PSI for a list of features using Plotly.
        """
        psi_values = self.calculate_psi_for_features(
            train, test, feature_cols, buckets, bucket_type, epsilon
        )

        fig = go.Figure()
        """
        fig.add_hline(
            y=0.1,
            line_dash="dash",
            line_color="orange",
            annotation_text="Warning",
            annotation_position="bottom right",
            annotation_font_color="orange",
        )
        fig.add_hline(
            y=0.25,
            line_dash="dash",
            line_color="red",
            annotation_text="Critical",
            annotation_position="bottom right",
            annotation_font_color="red",
        )
        """

        for feature, psi in psi_values.items():
            # Skip plotting for features that resulted in an error
            if isinstance(psi, str):
                continue

            fig.add_trace(
                go.Bar(
                    x=[feature],
                    y=[psi],
                    name=feature,
                    text=feature,
                    textposition="auto",
                )
            )

        fig.update_layout(
            title_text="Population Stability Index (PSI) for Features",
            xaxis_title="Feature",
            yaxis_title="PSI Value",
            barmode="group",
            showlegend=False,
        )
        fig.update_xaxes(tickvals=[], ticktext=[])
        fig.show()

        return fig
