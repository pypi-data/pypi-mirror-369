import colorsys
import math
from typing import List, Literal, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm
from pandas.core.indexes.base import Index as PandasIndex
from plotly.subplots import make_subplots
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
from statsmodels.stats.outliers_influence import variance_inflation_factor
from tqdm import tqdm


class Visualizations:
    PHI = (1 + 5**0.5) / 2

    def __init__(
        self,
        df: pd.DataFrame,
        target_column: str,
        numerical_columns: List[str],
        categorical_columns: List[str],
    ) -> None:
        """
        Initialize the Visualizations class with data and configuration.

        Parameters
        ----------
        df : pd.DataFrame
            The data to be analyzed.
        target_column : str
            The target column for analysis.
        numerical_columns : List[str]
            List of numerical columns.
        categorical_columns : List[str]
            List of categorical columns.
        """
        self.data = df
        self.target_column = target_column
        self.numerical_columns = numerical_columns
        self.categorical_columns = categorical_columns

    def plot_target_dist_by_category(self, column: str) -> None:
        """
        Plot the distribution of a categorical column with respect to the target column.

        Parameters
        ----------
        column : str
            Name of the column to plot.
        """
        aggregated = self.data[column].value_counts().reset_index()
        aggregated.columns = PandasIndex([column, "total_count"])

        positive_cases = (
            self.data[self.data[self.target_column] == 1][column]
            .value_counts()
            .reset_index()
        )
        positive_cases.columns = PandasIndex([column, "positive_count"])

        merged_data = pd.merge(aggregated, positive_cases, on=column, how="left")
        merged_data["positive_count"] = merged_data["positive_count"].fillna(0)
        merged_data["positive_info"] = (
            merged_data["positive_count"].astype(int).astype(str)
            + f" {self.target_column.capitalize()} Cases"
        )

        figure = px.pie(
            merged_data,
            values="total_count",
            names=column,
            hole=0.5,
            title=f"Distribution of {column} with {self.target_column.capitalize()} Events",
            hover_data=["positive_info"],
        )

        figure.show()

    def plot_target_balance(self) -> None:
        """
        Plot the distribution of the target column.
        """
        value_counts = self.data[self.target_column].value_counts().reset_index()
        value_counts.columns = PandasIndex(["Class", "Count"])

        total = value_counts["Count"].sum()
        value_counts["Percentage"] = value_counts["Count"] / total * 100

        fig = px.pie(
            value_counts,
            values="Count",
            names="Class",
            title=f"Distribution of {self.target_column}",
            labels={"Class": self.target_column, "Count": "Number of Instances"},
            hover_data=["Percentage"],
            hole=0,
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent+label",
            insidetextorientation="radial",
        )

        fig.update_layout(
            height=500,
            legend_title=self.target_column,
            legend={
                "orientation": "h",
                "yanchor": "bottom",
                "y": 1.02,
                "xanchor": "right",
                "x": 1,
            },
        )
        fig.show()

    def plot_target_evolution(self, time_column: str, amount_column: str) -> None:
        """
        Plot the evolution of the target column over time.

        Parameters
        ----------
        time_column : str
            Name of the time column.
        amount_column : str
            Name of the amount column.
        """
        # Ensure the time_column exists in the DataFrame
        if time_column not in self.data.columns:
            raise ValueError(f"Column '{time_column}' does not exist in the DataFrame.")

        # Try to convert the time_column to datetime using the correct format
        try:
            self.data[time_column] = pd.to_datetime(
                self.data[time_column], format="%Y-%m-%d %H:%M:%S.%f%z"
            )
        except ValueError:
            # If it fails, coerce errors to NaT and drop rows with NaT
            self.data[time_column] = pd.to_datetime(
                self.data[time_column], errors="coerce"
            )
            self.data.dropna(subset=[time_column], inplace=True)

        # Ensure the target column is boolean
        self.data[self.target_column] = self.data[self.target_column].astype(bool)

        # Group by time and calculate the fraud rate and observation count
        freq = "MS"
        data = self.data.copy()

        # 1. Population Risk Rate
        risk_rate_df = data.groupby(
            [pd.Grouper(key=time_column, freq=freq), self.target_column]
        ).size()
        assert isinstance(risk_rate_df, pd.Series)
        risk_rate = risk_rate_df.reset_index(name="count")
        risk_rate["rate"] = risk_rate.groupby(time_column)["count"].transform(
            lambda x: x / x.sum()
        )
        risk_rate_fraud = risk_rate[risk_rate[self.target_column] == True]

        # 2. Population's Observation Number
        obs_count = (
            data.groupby([pd.Grouper(key=time_column, freq=freq)])[self.target_column]
            .count()
            .reset_index(name="count")
        )

        # 3. Population Risk Rate in EUR
        fraud_amount = data.groupby(
            [self.target_column, pd.Grouper(key=time_column, freq=freq)]
        )[amount_column].sum()
        fraud_amount = (
            fraud_amount / fraud_amount.groupby(level=1).sum()
        ).reset_index()
        fraud_amount_fraud = fraud_amount[fraud_amount[self.target_column] == True]

        # 4. Population's Observation in EUR
        amount_sum = (
            data.groupby([pd.Grouper(key=time_column, freq=freq)])[amount_column]
            .sum()
            .reset_index()
        )

        # Create subplots
        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=(
                "Population Risk Rate",
                "Population's Observation Number",
                "Population Risk Rate (in EUR)",
                "Population's Observation (in EUR)",
            ),
        )

        # Plot risk rate
        fig.add_trace(
            go.Scatter(
                x=risk_rate_fraud[time_column],
                y=risk_rate_fraud["rate"],
                mode="lines",
                name="Population Fraud Rate",
            ),
            row=1,
            col=1,
        )

        # Plot observation count
        fig.add_trace(
            go.Bar(
                x=obs_count[time_column],
                y=obs_count["count"],
                name="Population Observation Count",
            ),
            row=1,
            col=2,
        )

        # Plot risk rate in EUR
        fig.add_trace(
            go.Scatter(
                x=fraud_amount_fraud[time_column],
                y=fraud_amount_fraud[amount_column],
                mode="lines",
                name="Population Fraud Rate (in EUR)",
            ),
            row=2,
            col=1,
        )

        # Plot observation amount in EUR
        fig.add_trace(
            go.Bar(
                x=amount_sum[time_column],
                y=amount_sum[amount_column],
                name="Population Observation (in EUR)",
            ),
            row=2,
            col=2,
        )

        # Update layout
        fig.update_layout(
            title_text="Target Evolution Over Time", height=800, showlegend=True
        )

        fig.update_xaxes(title_text="Time", row=1, col=1)
        fig.update_yaxes(title_text="Risk Rate", row=1, col=1)
        fig.update_xaxes(title_text="Time", row=1, col=2)
        fig.update_yaxes(title_text="Nb obs", row=1, col=2)
        fig.update_xaxes(title_text="Time", row=2, col=1)
        fig.update_yaxes(title_text="Risk Rate (in EUR)", row=2, col=1)
        fig.update_xaxes(title_text="Time", row=2, col=2)
        fig.update_yaxes(title_text="Sum of EUR", row=2, col=2)

        fig.show()

    def _check_cardinality(self, threshold: int = 10) -> Tuple[List[str], List[str]]:
        """
        Check the cardinality of categorical columns.

        Parameters
        ----------
        threshold : int, optional
            Threshold to determine high and low cardinality, by default 10.

        Returns
        -------
        Tuple[List[str], List[str]]
            Lists of high and low cardinality columns.
        """
        high_car = [
            cat
            for cat in self.categorical_columns
            if len(self.data[cat].value_counts()) >= threshold
        ]
        low_car = [
            cat
            for cat in self.categorical_columns
            if len(self.data[cat].value_counts()) < threshold
        ]

        return high_car, low_car

    def visualize_high_cardinality(
        self,
        excluded_columns: List[str],
        top_n: int = 10,
        id_column: Optional[str] = None,
    ) -> None:
        """
        Visualize high cardinality features.

        Parameters
        ----------
        excluded_columns : List[str]
            List of columns to exclude.
        top_n : int, optional
            Number of top categories to display, by default 10.
        id_column : Optional[str], optional
            Name of the id column, by default None.
        """
        high_car, _ = self._check_cardinality()

        if id_column:
            excluded_columns.append(id_column)

        # Exclude specified variables from the high cardinality list
        high_car = [cat for cat in high_car if cat not in excluded_columns]

        if not high_car:
            print("No high cardinality features found.")
            return

        fig = go.Figure()
        # Create traces for each high cardinality column but initially hide them
        for _i, cat in enumerate(high_car):
            value_counts = self.data[cat].value_counts()

            # Keep top N categories and group others
            top_categories = value_counts.nlargest(top_n - 1).index
            draw = self.data[cat].apply(
                lambda x: x if x in top_categories else "Other"  # noqa: B023
            )

            draw = draw.value_counts().sort_values(ascending=True)

            fig.add_trace(
                go.Bar(
                    y=draw.index,
                    x=draw.values,
                    orientation="h",
                    name=cat,
                    text=draw.values,
                    textposition="auto",
                    marker={"color": draw.values, "colorscale": "Plasma"},
                    visible=False,  # Initially hide all traces
                )
            )

        # Add dropdown menu to toggle between traces
        buttons = []
        for i, cat in enumerate(high_car):
            buttons.append(
                {
                    "method": "update",
                    "label": cat,
                    "args": [
                        {"visible": [j == i for j in range(len(high_car))]},
                        {
                            "title": f"Distribution of {cat}",
                            "xaxis": {"title": "Count"},
                            "yaxis": {"title": "Category"},
                        },
                    ],
                }
            )

        fig.update_layout(
            updatemenus=[
                {
                    "active": 0,
                    "buttons": buttons,
                    "direction": "down",
                    "showactive": True,
                }
            ]
        )
        # if I assert, this create a bug in the example for no reason
        if len(fig.data) > 0:  # type: ignore
            fig.data[0].visible = True  # type: ignore
            fig.update_layout(title=f"Distribution of {high_car[0]}", showlegend=False)

        fig.show()

    def visualize_low_cardinality(self) -> None:
        """
        Visualize low cardinality features.
        """
        _, low_car = self._check_cardinality()

        if not low_car:
            print("No low cardinality features found.")
            return

        # Calculate number of rows and columns
        n_cols = 2
        n_rows = math.ceil(len(low_car) / n_cols)

        # Create subplots
        fig = make_subplots(
            rows=n_rows,
            cols=n_cols,
            subplot_titles=low_car,
            vertical_spacing=0.1,
            horizontal_spacing=0.05,
        )

        # Plot each low cardinality feature
        for idx, cat in enumerate(low_car):
            row = idx // n_cols + 1
            col = idx % n_cols + 1

            value_counts = self.data[cat].value_counts().sort_values(ascending=True)

            fig.add_trace(
                go.Bar(
                    x=value_counts.index,
                    y=value_counts.values,
                    name=cat,
                    text=value_counts.values,
                    textposition="auto",
                ),
                row=row,
                col=col,
            )

            fig.update_xaxes(title_text=cat, row=row, col=col)
            fig.update_yaxes(title_text="Count", row=row, col=col)

        # Update layout
        fig.update_layout(
            title_text="Distribution of Low Cardinality Categorical Features",
            showlegend=False,
            height=300 * n_rows,
            width=1000,
        )

        fig.show()

    def calculate_vif(self, threshold: int = 5, show_plot: bool = True) -> pd.DataFrame:
        """
        Calculate the Variance Inflation Factor (VIF) for numerical features.

        Parameters
        ----------
        threshold : int, optional
            Threshold value to determine multicollinearity, by default 5.
        show_plot : bool, optional
            If True, the plot will be displayed, by default True.

        Returns
        -------
        pd.DataFrame
            DataFrame containing VIF values for features.
        """
        # Select numerical data from the DataFrame, excluding the target column
        numerical_columns = [
            col for col in self.numerical_columns if col != self.target_column
        ]
        numerical_data = self.data[numerical_columns].copy()

        # Convert boolean columns to integers
        for column in numerical_data.columns:
            if numerical_data[column].dtype == "bool":
                numerical_data[column] = numerical_data[column].astype(int)

        # Check for missing values
        missing_values = numerical_data.isnull().sum()
        if missing_values.sum() > 0:
            print("\nWARNING: Missing values detected in the following columns:")
            print(missing_values[missing_values > 0])
            print("\nImputing missing values with mean for VIF calculation.")
            print(
                "It is strongly recommended to properly handle missing values in your dataset."
            )

            # Impute missing values with mean
            numerical_data = numerical_data.fillna(numerical_data.mean())

        # Add a constant to the model (intercept)
        numerical_data = sm.add_constant(numerical_data)
        assert isinstance(numerical_data, pd.DataFrame)

        # Calculate VIF for each feature
        vif_data = pd.DataFrame()
        vif_data["Feature"] = numerical_data.columns
        vif_data["VIF"] = [
            variance_inflation_factor(numerical_data.values, i)
            for i in range(numerical_data.shape[1])
        ]

        # Handle infinite VIF values
        vif_data["VIF"] = np.where(
            np.isinf(vif_data["VIF"]), np.finfo(np.float64).max, vif_data["VIF"]
        )

        # Drop the constant column from the dataframe
        vif_data = vif_data[vif_data["Feature"] != "const"]

        # Sort VIF values in descending order
        vif_data = vif_data.sort_values("VIF", ascending=False).reset_index(drop=True)

        # Assign colors based on the threshold
        vif_data["Color"] = [
            "red" if vif > threshold else "green" for vif in vif_data["VIF"]
        ]

        # Create the bar plot
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=vif_data["Feature"],
                y=vif_data["VIF"],
                marker_color=vif_data["Color"],
                text=vif_data["VIF"].round(2),
                textposition="outside",
            )
        )

        # Update layout
        fig.update_layout(
            title="Variance Inflation Factor (VIF) for Features",
            xaxis_title="Features",
            yaxis_title="VIF",
            yaxis={
                "range": [0, max(vif_data["VIF"]) * 1.1]
            },  # Set y-axis range with some padding
            showlegend=False,
        )

        # Add a horizontal line at the threshold value
        fig.add_shape(
            type="line",
            x0=-0.5,
            y0=threshold,
            x1=len(vif_data["Feature"]) - 0.5,
            y1=threshold,
            line={"color": "black", "width": 2, "dash": "dash"},
        )

        if show_plot:
            fig.show()

        return vif_data

    def _bin_and_target_freq(
        self, variable_name: str, num_bins: int = 10, scale: bool = False
    ) -> pd.DataFrame:
        """
        Bin a numerical variable and calculate target frequency.

        Parameters
        ----------
        variable_name : str
            Name of the numerical variable.
        num_bins : int, optional
            Number of bins to use, by default 10.
        scale : bool, optional
            Whether to scale the variable before binning, by default False.

        Returns
        -------
        pd.DataFrame
            DataFrame with binned data and target frequency.
        """
        df = self.data[[variable_name, self.target_column]].copy()

        # Ensure target column is numeric (0 or 1)
        df[self.target_column] = df[self.target_column].astype(int)

        # Drop missing values and inform user
        original_count = len(df)
        df.dropna(subset=[variable_name], inplace=True)
        dropped_count = original_count - len(df)
        if dropped_count > 0:
            print(
                f"Dropped {dropped_count} rows with missing values for {variable_name}"
            )

        if scale:
            # Scale the variable individually
            min_value = df[variable_name].min()
            max_value = df[variable_name].max()
            if min_value != max_value:
                df[variable_name] = (df[variable_name] - min_value) / (
                    max_value - min_value
                )
            else:
                print(
                    f"Warning: {variable_name} has constant value. Scaling not applied."
                )

        # Use 'drop' option to handle duplicate bin edges
        try:
            df["bin"] = pd.qcut(
                df[variable_name], q=num_bins, labels=False, duplicates="drop"
            )
        except ValueError as e:
            print(f"Warning: {e}")
            print(
                f"Attempting to create {num_bins} bins for {variable_name}, but some may be merged due to duplicate values."
            )
            # If qcut fails, fall back to cut with equal-width bins
            df["bin"] = pd.cut(df[variable_name], bins=num_bins, labels=False)

        grouped = df.groupby("bin").agg(
            {variable_name: "mean", self.target_column: ["count", "sum"]}
        )
        grouped.columns = PandasIndex([variable_name, "total_count", "target_sum"])
        grouped["target_freq"] = grouped["target_sum"] / grouped["total_count"]
        return grouped.reset_index()

    def plot_hexagon_target_vs_numerical(
        self, var1: str, var2: str, num_bins: int = 20, scale: bool = False
    ) -> None:
        """
        Create a hexbin plot comparing two numerical variables and their relationship to the target variable.

        Parameters
        ----------
        var1 : str
            Name of the first numerical variable.
        var2 : str
            Name of the second numerical variable.
        num_bins : int, optional
            Number of bins to use, by default 20.
        scale : bool, optional
            Whether to scale variables before binning, by default False.
        """
        data = self.data[[var1, var2, self.target_column]].copy()

        # Drop rows with missing values
        data.dropna(subset=[var1, var2], inplace=True)

        # Ensure target column is numeric (0 or 1)
        data[self.target_column] = data[self.target_column].astype(int)

        if scale:
            scaler = MinMaxScaler()
            data[[var1, var2]] = scaler.fit_transform(data[[var1, var2]])

        # Create the hexbin plot
        plt.figure(figsize=(10, 8))
        hb = plt.hexbin(
            data[var1],
            data[var2],
            C=data[self.target_column],
            gridsize=num_bins,
            cmap="YlOrRd",
            reduce_C_function=np.mean,
        )

        plt.colorbar(hb, label="Target Frequency")
        plt.xlabel(var1)
        plt.ylabel(var2)
        plt.title(f"Hexbin Plot of {var1} vs {var2} (Target Frequency)")

        # Add a text annotation for the correlation
        correlation = data[[var1, var2]].corr().iloc[0, 1]
        plt.text(
            0.05,
            0.95,
            f"Correlation: {correlation:.2f}",
            transform=plt.gca().transAxes,
            fontsize=10,
            verticalalignment="top",
        )

        plt.tight_layout()
        plt.show()

    def plot_categorical_value_counts(
        self, plot_type: Literal["bar", "pie"] = "bar"
    ) -> None:
        """
        Generate value counts for categorical features and visualize them with a dropdown menu to select columns.
        Includes a red line representing target percentages for bar plots.

        Parameters
        ----------
        plot_type : {'bar', 'pie'}, optional
            Type of plot to display, by default 'bar'.
        """
        fig = go.Figure()

        for col in self.categorical_columns:
            counts = self.data[col].value_counts().reset_index()
            counts.columns = [col, "Frequency"]
            total = counts["Frequency"].sum()
            counts["Percentage"] = counts["Frequency"] / total * 100

            # Calculate target percentage for each category
            target_percentages = self.data.groupby(col, observed=False)[
                self.target_column
            ].mean()
            counts["TargetPercentage"] = (
                counts[col].map(target_percentages).astype(float)
            )
            counts["TargetPercentage_"] = counts["TargetPercentage"] / 100

            if counts.empty:
                print(f"No data to plot for column: {col}")
                continue

            if plot_type == "bar":
                # Add bar trace
                fig.add_trace(
                    go.Bar(
                        x=counts[col],
                        y=counts["Frequency"],
                        name=col,
                        text=counts["Percentage"].apply(lambda x: f"{x:.1f}%"),
                        textposition="inside",
                        hovertemplate=(
                            f"<b>{col}</b>: %{{x}}<br>"
                            "Frequency: %{y}<br>"
                            "Percentage: %{customdata[0]:.2f}%<br>"
                            f"{self.target_column} %: %{{customdata[1]:.2%}}"
                        ),
                        customdata=counts[["Percentage", "TargetPercentage_"]],
                        visible=False,
                    )
                )

                # Add red line trace for target percentages
                fig.add_trace(
                    go.Scatter(
                        x=counts[col],
                        y=counts["TargetPercentage"],
                        mode="lines",
                        name=f"{self.target_column} %",
                        line={"color": "red", "width": 2},
                        yaxis="y2",
                        hovertemplate=f"{self.target_column} %: %{{customdata:.2%}}<extra></extra>",
                        customdata=counts["TargetPercentage_"],
                        visible=False,
                    )
                )

            elif plot_type == "pie":
                fig.add_trace(
                    go.Pie(
                        labels=counts[col],
                        values=counts["Frequency"],
                        name=col,
                        text=counts["Percentage"].apply(lambda x: f"{x:.1f}%"),
                        hovertemplate=(
                            f"<b>{col}</b>: %{{label}}<br>"
                            "Frequency: %{value}<br>"
                            "Percentage: %{customdata[0]:.2f}%<br>"
                            f"{self.target_column} %: %{{customdata[1]:.2%}}"
                        ),
                        customdata=counts[["Percentage", "TargetPercentage_"]],
                        visible=False,
                    )
                )

        # Create dropdown menu
        buttons = []
        for i, col in enumerate(self.categorical_columns):
            visible = [False] * len(fig.data)  # type: ignore
            if plot_type == "bar":
                visible[i * 2] = True  # Bar trace
                visible[i * 2 + 1] = True  # Line trace
            else:
                visible[i] = True
            buttons.append(
                {
                    "method": "update",
                    "label": col,
                    "args": [
                        {"visible": visible},
                        {
                            "title": f"Distribution of {col}",
                            "xaxis": (
                                {"title": col} if plot_type == "bar" else {}
                            ),  # Add this line
                        },
                    ],
                }
            )

        # Update layout
        fig.update_layout(
            updatemenus=[
                {
                    "active": 0,
                    "buttons": buttons,
                    "direction": "down",
                    "showactive": True,
                    "x": 1.0,
                    "xanchor": "left",
                    "y": 1.15,
                    "yanchor": "top",
                }
            ],
            title=f"Distribution of {self.categorical_columns[0]}",
            xaxis_title=(
                f"{self.categorical_columns[0]}" if plot_type == "bar" else None
            ),
            yaxis_title="Frequency" if plot_type == "bar" else None,
            showlegend=True,
            legend={
                "orientation": "h",
                "yanchor": "bottom",
                "y": 1.02,
                "xanchor": "right",
                "x": 1,
            },
        )

        if plot_type == "bar":
            max_target_percentage = max(
                self.data.groupby(col, observed=False)[self.target_column].mean().max()
                for col in self.categorical_columns
            )
            fig.update_layout(
                yaxis={"title": "Frequency", "side": "left"},
                yaxis2={
                    "title": "",
                    "overlaying": "y",
                    "side": "right",
                    "range": [0, max_target_percentage],
                    "tickformat": ".0%",
                    "showticklabels": False,  # Hide tick labels
                    "showgrid": False,  # Hide grid lines
                    "zeroline": False,  # Hide zero line
                    "showline": False,  # Hide axis line
                },
            )

        # Make the first plot visible
        if len(fig.data) > 0:  # type: ignore
            fig.data[0].visible = True  # type: ignore
            if plot_type == "bar" and len(fig.data) > 1:  # type: ignore
                fig.data[1].visible = True  # type: ignore

        fig.show()

    def _compute_categories_per_ring(self, n_categories: int) -> List[int]:
        """
        Determine the number of categories for each ring in the custom plot.

        Parameters
        ----------
        n_categories : int
            Total number of categories.

        Returns
        -------
        List[int]
            Number of categories for each ring.
        """
        power = 5
        rings: List[int] = []
        remaining = n_categories
        while remaining > 0:
            ring_size = math.ceil(Visualizations.PHI ** (power + 1)) - math.ceil(
                Visualizations.PHI**power
            )
            if remaining <= ring_size:
                # If this is the last ring or second to last ring
                if len(rings) >= 1:
                    # Distribute remaining categories: 2/3 to second last, 1/3 to last
                    second_last = math.ceil(remaining * 2 / 3)
                    last = remaining - second_last
                    rings[-1] += second_last
                    if last > 0:
                        rings.append(last)
                else:
                    rings.append(remaining)
                break
            rings.append(ring_size)
            remaining -= ring_size
            power += 1
        return rings

    def plot_stacked_donut(self, column: str) -> None:
        """
        Plot the distribution of a categorical column with respect to the target column using a custom plot.

        Parameters
        ----------
        column : str
            Name of the column to plot.
        """
        # Aggregate and prepare data
        aggregated = self.data[column].value_counts().reset_index()
        aggregated.columns = pd.Index([column, "total_count"])
        total_obs = aggregated["total_count"].sum()
        aggregated["percentage"] = aggregated["total_count"] / total_obs * 100
        positive_cases = (
            self.data[self.data[self.target_column] == 1][column]
            .value_counts()
            .reset_index()
        )
        positive_cases.columns = PandasIndex([column, "positive_count"])
        merged_data = pd.merge(aggregated, positive_cases, on=column, how="left")
        merged_data["positive_count"] = merged_data["positive_count"].fillna(0)
        merged_data["positive_rate"] = (
            merged_data["positive_count"] / merged_data["total_count"]
        )

        # Determine ring distribution
        n_categories = len(merged_data)
        ring_sizes = self._compute_categories_per_ring(n_categories)

        # Assign categories to rings
        merged_data["ring"] = 0
        start_idx = 0
        for ring, size in enumerate(ring_sizes):
            end_idx = start_idx + size
            merged_data.loc[start_idx : end_idx - 1, "ring"] = ring
            start_idx = end_idx

        # Adjust base hole size and growth rate
        base_hole_size = 0.3
        hole_growth_rate = 0.1

        # Create traces for each ring
        traces = []
        for ring in range(len(ring_sizes)):
            ring_data = merged_data[merged_data["ring"] == ring]

            if ring_data.empty:
                continue

            # Generate distinct colors for this ring
            n_colors = len(ring_data)
            hue_start = ring * 0.25  # Shift hue for each ring
            colors = [
                f"rgb({int(r*255)},{int(g*255)},{int(b*255)})"
                for r, g, b in [
                    colorsys.hsv_to_rgb((hue_start + j / n_colors) % 1, 0.7, 0.9)
                    for j in range(n_colors)
                ]
            ]

            # Adjust hole size based on ring (ensure it doesn't exceed 0.9)
            hole_size = min(0.9, base_hole_size + ring * hole_growth_rate)

            # Prepare hover text
            hover_text = [
                f"<b>{label}</b><br>"
                f"Count: {count}<br>"
                f"Percentage: {percentage:.2f}%<br>"
                f"Positive Rate: {positive_rate:.2%}"
                for label, count, percentage, positive_rate in zip(
                    ring_data[column],
                    ring_data["total_count"],
                    ring_data["percentage"],
                    ring_data["positive_rate"],
                )
            ]

            traces.append(
                go.Pie(
                    values=ring_data["total_count"],
                    labels=ring_data[column],
                    name=f"Ring {ring+1}",
                    hole=hole_size,
                    domain={"x": [0, 1], "y": [0, 1]},
                    hoverinfo="text",
                    hovertext=hover_text,
                    marker={
                        "colors": colors,
                        "line": {"color": "white", "width": 2},  # Add white borders
                    },
                    textposition="none",
                    showlegend=True,
                )
            )

        # Create the figure
        fig = go.Figure(data=traces)

        # Update layout
        layout_annotations = []
        if len(ring_sizes) > 1:
            layout_annotations = [
                {
                    "text": "Most<br>Frequent",
                    "x": 0.5,
                    "y": 0.5,
                    "font_size": 10,
                    "showarrow": False,
                },
                {
                    "text": "Least<br>Frequent",
                    "x": 0.5,
                    "y": 0.95,
                    "font_size": 10,
                    "showarrow": False,
                },
            ]

        fig.update_layout(
            title=f"Distribution of {column} with {self.target_column.capitalize()} Events",
            annotations=layout_annotations,
            legend={
                "orientation": "v",
                "yanchor": "top",
                "y": 1,
                "xanchor": "left",
                "x": 1.05,
            },
            legend_title_text="Categories",
            margin={"r": 150},  # Increase right margin to accommodate legend
        )

        fig.show()

    def plot_numerical_target_frequency_line(
        self, x_log_scale: bool = False, y_log_scale: bool = False, scale: bool = False
    ) -> None:
        """
        Plot the target frequency for all numerical columns in a single plot with different colored lines.
        All lines are initially invisible and can be toggled on/off interactively.

        Parameters
        ----------
        x_log_scale : bool, optional
            If True, the x-axis will be plotted in log scale, by default False.
        y_log_scale : bool, optional
            If True, the y-axis will be plotted in log scale, by default False.
        scale : bool, optional
            If True, scale each column's values from 0-1 before plotting, by default False.
        """
        fig = go.Figure()

        for col in self.numerical_columns:
            grouped = self._bin_and_target_freq(col, scale=scale)
            fig.add_trace(
                go.Scatter(
                    x=grouped[col],
                    y=grouped["target_freq"],
                    mode="lines",
                    name=col,
                    visible="legendonly",  # This makes the line invisible by default
                )
            )

        fig.update_layout(
            title="Target Frequency for Numerical Columns",
            xaxis_title="Value" if not scale else "Scaled Value (0-1)",
            yaxis_title="Target Frequency",
            xaxis_type="log" if x_log_scale else "linear",
            yaxis_type="log" if y_log_scale else "linear",
        )

        fig.show()

    def calc_cat_target_freq(self) -> pd.DataFrame:
        """
        Calculate the target frequency for each category of all categorical columns.

        Returns
        -------
        pd.DataFrame
            DataFrame with a multi-index structure for easy viewing and analysis.
        """
        data_list = []

        for col in self.categorical_columns:
            grouped = (
                self.data.groupby(col, observed=False)
                .agg({self.target_column: ["mean", "count"], col: "count"})
                .reset_index()
            )

            grouped.columns = PandasIndex(
                [
                    "Category",
                    "Target_Frequency",
                    "Total_Count",
                    "Category_Count",
                ]
            )
            grouped["Column"] = col
            grouped["Category_Percentage"] = (
                grouped["Category_Count"] / grouped["Total_Count"].sum() * 100
            )

            data_list.append(grouped)

        # Combine all dataframes
        result_df = pd.concat(data_list, ignore_index=True)
        # Create multi-index DataFrame
        result_df = result_df.set_index(["Column", "Category"])
        # Reorder columns
        result_df = result_df[
            ["Category_Count", "Category_Percentage", "Target_Frequency"]
        ]
        # Rename columns for clarity
        result_df.columns = PandasIndex(["Count", "Percentage", "Target_Frequency"])

        # Sort by Column and then by Count (descending)
        result_df = result_df.sort_values(["Column", "Count"], ascending=[True, False])

        return result_df

    def _calculate_vif_manual(self, X, feature_idx):
        """
        Manually calculate VIF for a single feature.
        """
        other_features = [i for i in range(X.shape[1]) if i != feature_idx]
        X_other = X[:, other_features]
        y = X[:, feature_idx]

        # Check if the feature has any variation
        if np.all(y == y[0]):
            return np.inf  # or any large number to indicate perfect multicollinearity

        # Fit linear regression
        model = LinearRegression()
        model.fit(X_other, y)

        # Calculate R-squared
        y_pred = model.predict(X_other)
        ss_total = np.sum((y - np.mean(y)) ** 2)
        ss_residual = np.sum((y - y_pred) ** 2)

        # Handle the case where ss_total is very close to zero
        if np.isclose(ss_total, 0):
            return np.inf  # or any large number to indicate perfect multicollinearity

        r_squared = 1 - (ss_residual / ss_total)

        # Calculate VIF
        vif = 1 / (1 - r_squared)

        return vif

    def plot_vif_failsafe(self, threshold: int = 5, show_plot: bool = True) -> None:
        """
        Calculate the Variance Inflation Factor (VIF) for numerical features.
        """
        # Select numerical data from the DataFrame, excluding the target column
        numerical_columns = [
            col for col in self.numerical_columns if col != self.target_column
        ]
        numerical_data = self.data[numerical_columns].copy()

        # Convert boolean columns to integers
        for column in numerical_data.columns:
            if numerical_data[column].dtype == "bool":
                numerical_data[column] = numerical_data[column].astype(int)

        # Check for missing values
        missing_values = numerical_data.isnull().sum()
        if missing_values.sum() > 0:
            print("\nWARNING: Missing values detected in the following columns:")
            print(missing_values[missing_values > 0])
            print("\nImputing missing values with mean for VIF calculation.")
            print(
                "It is strongly recommended to properly handle missing values in your dataset."
            )

            # Impute missing values with mean
            numerical_data = numerical_data.fillna(numerical_data.mean())

        # Calculate VIF for each feature
        X = numerical_data.values
        vif_data = pd.DataFrame()
        vif_data["Feature"] = numerical_data.columns

        # Use tqdm to create a progress bar
        vif_values = []
        for i in tqdm(range(X.shape[1]), desc="Calculating VIF", unit="feature"):
            vif_values.append(self._calculate_vif_manual(X, i))
        vif_data["VIF"] = vif_values

        # Sort VIF values in descending order
        vif_data = vif_data.sort_values("VIF", ascending=False).reset_index(drop=True)

        # Assign colors based on the threshold
        vif_data["Color"] = [
            "red" if vif > threshold else "green" for vif in vif_data["VIF"]
        ]

        # Create the bar plot
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=vif_data["Feature"],
                y=vif_data["VIF"],
                marker_color=vif_data["Color"],
                text=vif_data["VIF"].round(2),
                textposition="outside",
            )
        )

        # Update layout
        fig.update_layout(
            title="Variance Inflation Factor (VIF) for Features",
            xaxis_title="Features",
            yaxis_title="VIF",
            yaxis={
                "range": [0, min(max(vif_data["VIF"]), 100) * 1.1]
            },  # Set y-axis range with some padding and upper limit
            showlegend=False,
            xaxis={"tickangle": 45},
        )

        # Add a horizontal line at the threshold value
        fig.add_shape(
            type="line",
            x0=-0.5,
            y0=threshold,
            x1=len(vif_data["Feature"]) - 0.5,
            y1=threshold,
            line={"color": "black", "width": 2, "dash": "dash"},
        )

        if show_plot:
            fig.show()

    def _update_axes_and_fit(self, scale_type, fig, data):
        """
        Update the y-axis range and fit the traces to the updated y-axis range.

        Parameters
        ----------
        scale_type : str
            The type of scaling to apply to the data.
        fig : go.Figure
            The plotly figure object.
        data : dict
            A dictionary containing the original data for each trace.

        Returns
        -------
        go.Figure
            The updated plotly figure object.
        """
        min_val, max_val = float("inf"), float("-inf")
        for trace in fig.data:
            if trace.visible:
                original_data = data[trace.name]
                if scale_type == "original":
                    trace.y = original_data
                elif scale_type == "scale_0_1":
                    trace.y = (original_data - original_data.min()) / (
                        original_data.max() - original_data.min()
                    )
                elif scale_type == "log":
                    trace.y = np.log1p(original_data - original_data.min() + 1)

                min_val = min(min_val, min(trace.y))
                max_val = max(max_val, max(trace.y))

        # Add padding to the y-axis range
        padding = 0.1 * (max_val - min_val)
        y_range = [min_val - padding, max_val + padding]

        if scale_type == "scale_0_1":
            y_range = [-0.1, 1.1]  # Fixed range for 0-1 scale with padding

        fig.update_layout(yaxis_range=y_range)
        return fig

    def plot_boxplots(self):
        """
        Plot boxplots for numerical columns by target variable with one random column initially visible.
        """
        fig = make_subplots(rows=1, cols=1)

        # Randomly select one column to be initially visible
        import random

        initial_visible_column = random.choice(self.numerical_columns)

        for numeric in self.numerical_columns:
            fig.add_trace(
                go.Box(
                    y=self.data[numeric],
                    x=self.data[self.target_column],
                    name=numeric,
                    boxmean=True,
                    visible=True if numeric == initial_visible_column else "legendonly",
                )
            )

        fig.update_layout(
            title="Boxplots for Numerical Columns by Target",
            xaxis_title=self.target_column,
            yaxis_title="Value",
            boxmode="group",
            updatemenus=[
                {
                    "type": "buttons",
                    "direction": "left",
                    "buttons": [
                        {
                            "label": "Original",
                            "method": "restyle",
                            "args": [
                                {
                                    "y": [
                                        self.data[col] for col in self.numerical_columns
                                    ]
                                }
                            ],
                        },
                        {
                            "label": "Scale 0-1",
                            "method": "restyle",
                            "args": [
                                {
                                    "y": [
                                        (self.data[col] - self.data[col].min())
                                        / (self.data[col].max() - self.data[col].min())
                                        for col in self.numerical_columns
                                    ]
                                }
                            ],
                        },
                        {
                            "label": "Log Scale",
                            "method": "restyle",
                            "args": [
                                {
                                    "y": [
                                        np.log1p(
                                            self.data[col] - self.data[col].min() + 1
                                        )
                                        for col in self.numerical_columns
                                    ]
                                }
                            ],
                        },
                    ],
                    "pad": {"r": 10, "t": 10},
                    "showactive": True,
                    "x": 0.11,
                    "xanchor": "left",
                    "y": 1.1,
                    "yanchor": "top",
                },
            ],
        )

        fig.show()
