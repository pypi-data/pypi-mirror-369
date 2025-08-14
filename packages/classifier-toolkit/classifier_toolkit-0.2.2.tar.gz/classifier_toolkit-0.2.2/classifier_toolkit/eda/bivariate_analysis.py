import re
from typing import List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm
from pandas.core.indexes.base import Index as PandasIndex
from sklearn.preprocessing import StandardScaler
from statsmodels.formula.api import ols
from tqdm import tqdm

from .univariate_analysis import UnivariateAnalysis


class BivariateAnalysis:
    def __init__(
        self, data: pd.DataFrame, numerical_columns: Optional[List[str]] = None
    ) -> None:
        """
        Initialize the BivariateAnalysis class with data and optional numerical columns.

        Parameters
        ----------
        data : pd.DataFrame
            The data to be analyzed.
        numerical_columns : Optional[List[str]], optional
            List of numerical columns to consider. If None, all numerical columns in the data will be used.
        """
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Data should be a pandas DataFrame")
        self.data = data.copy()
        if numerical_columns is None:
            self.numerical_columns = self.data.select_dtypes(
                include=[np.number]
            ).columns.tolist()
        else:
            self.numerical_columns = numerical_columns

    def generate_correlation_heatmap(self, columns: List[str]) -> go.Figure:
        """
        Generate an interactive correlation heatmap for the specified columns using Plotly.

        Parameters
        ----------
        columns : list of str
            List of column names to include in the correlation analysis.

        Returns
        -------
        go.Figure
            The Plotly figure object of the plot.
        """
        if len(columns) == 0:
            columns = self.numerical_columns

        # Calculate the correlation matrix
        corr_matrix = self.data[columns].corr(method="pearson")

        # Create a mask for the upper triangle
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        corr_matrix_masked = corr_matrix.mask(mask)

        # Calculate dynamic figure size and font size
        n_features = len(columns)
        base_size = 500  # Base size for the heatmap
        fig_size = min(
            1000, max(500, base_size + 20 * n_features)
        )  # Adjust figure size based on number of features
        font_size = max(
            8, min(12, 20 - n_features // 10)
        )  # Adjust font size based on number of features

        # Create a Plotly heatmap
        fig = go.Figure(
            data=go.Heatmap(
                z=corr_matrix_masked.values[
                    ::-1
                ],  # Reverse the order of rows to flip the triangle
                x=corr_matrix_masked.columns,
                y=corr_matrix_masked.index[
                    ::-1
                ],  # Reverse the order of labels to match the flipped triangle
                colorscale="plasma",
                zmin=-1,
                zmax=1,
                colorbar={"title": "Correlation"},
                hovertemplate="x: %{x}<br>y: %{y}<br>Correlation: %{z:.2f}<extra></extra>",
            )
        )

        # Update layout
        fig.update_layout(
            title=f"Correlation Heatmap ({'Pearson'.capitalize()} method)",
            xaxis={
                "title": "Features",
                "side": "bottom",
                "tickangle": 45,  # Always set to 45 degrees
                "tickfont": {"size": font_size},
                "constrain": "domain",
            },
            yaxis={
                "title": "Features",
                "tickfont": {"size": font_size},
                "scaleanchor": "x",
                "scaleratio": 1,
                "constrain": "domain",
            },
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_showgrid=False,
            yaxis_showgrid=False,
            xaxis_zeroline=False,
            yaxis_zeroline=False,
            width=fig_size,
            height=fig_size,
            margin={"l": 100, "r": 100, "t": 100, "b": 100},
        )

        # Adjust the size of the heatmap to leave space for labels
        heatmap_size = 0.8  # 80% of the figure size
        fig.update_layout(
            xaxis={"domain": [0, heatmap_size]}, yaxis={"domain": [0, heatmap_size]}
        )

        fig.show()

        return fig

    def _clean_column_name(self, name: str) -> str:
        """
        Clean column names to be compatible with formula notation.

        Parameters
        ----------
        name : str
            The column name to be cleaned.

        Returns
        -------
        str
            The cleaned column name.
        """
        return re.sub(r"\W+", "_", name)

    def perform_anova_numeric_categorical(
        self, cat_cols: Union[str, List[str]]
    ) -> Tuple[go.Figure, pd.DataFrame]:
        """
        Perform ANOVA between numerical and categorical variables using Fisher's F-statistic.

        Parameters
        ----------
        cat_cols : Union[str, List[str]]
            List of categorical column names to include in the ANOVA analysis.

        Returns
        -------
        Tuple[go.Figure, pd.DataFrame]
            The Plotly figure object of the ANOVA heatmap and the DataFrame containing ANOVA results.
        """
        if isinstance(cat_cols, str):
            cat_cols = [cat_cols]

        # Check if the columns exist in the DataFrame
        missing_columns = [col for col in cat_cols if col not in self.data.columns]
        if missing_columns:
            raise ValueError(
                f"The following columns are not in the DataFrame: {missing_columns}"
            )

        # Create a copy of the data to avoid modifying the original
        data_copy = self.data.copy()

        # Clean column names
        data_copy.columns = PandasIndex(
            [self._clean_column_name(col) for col in data_copy.columns]
        )
        cat_cols = [self._clean_column_name(col) for col in cat_cols]
        numerical_columns = [
            self._clean_column_name(col) for col in self.numerical_columns
        ]

        # Standardize numerical data
        std_scaler = StandardScaler()
        numerical_feature_list_std = []
        for num in numerical_columns:
            data_copy[num + "_std"] = std_scaler.fit_transform(
                data_copy[num].to_numpy().reshape(-1, 1)
            )
            numerical_feature_list_std.append(num + "_std")

        # Perform ANOVA for each combination of numerical and categorical variables
        rows = []
        total_combinations = len(cat_cols) * len(numerical_feature_list_std)

        with tqdm(total=total_combinations, desc="Performing ANOVA") as pbar:
            for cat in cat_cols:
                col = []
                for num in numerical_feature_list_std:
                    try:
                        equation = f"{num} ~ C({cat})"
                        model = ols(equation, data=data_copy).fit()
                        anova_table = sm.stats.anova_lm(model, typ=1)
                        col.append(anova_table.loc[f"C({cat})"]["F"])
                    except Exception as e:
                        print(f"Error in ANOVA for {num} ~ {cat}: {e!s}")
                        col.append(np.nan)
                    pbar.update(1)
                rows.append(col)

        # Store the results in a DataFrame
        anova_result = np.array(rows)
        anova_result_df = pd.DataFrame(
            anova_result, columns=self.numerical_columns, index=cat_cols
        )

        # Create a Plotly heatmap
        fig = go.Figure(
            data=go.Heatmap(
                z=anova_result_df.values,
                x=anova_result_df.columns,
                y=anova_result_df.index,
                colorscale="plasma",
                zmin=anova_result_df.values.min(),
                zmax=anova_result_df.values.max(),
                colorbar={"title": "Fisher's F-statistic"},
            )
        )

        # Update layout
        fig.update_layout(
            title="Fisher's Statistic Heatmap",
            xaxis={"title": "Numerical Features"},
            yaxis={"title": "Categorical Features"},
            plot_bgcolor="rgba(0,0,0,0)",  # Remove background grid
            xaxis_showgrid=False,
            yaxis_showgrid=False,
            xaxis_zeroline=False,
            yaxis_zeroline=False,
            width=800,
            height=800,
            margin={
                "l": 100,
                "r": 100,
                "t": 100,
                "b": 100,
            },  # Adjust margins to center the plot
        )

        return fig, anova_result_df

    def compute_pairwise_cramers_v(
        self, categorical_features: List[str]
    ) -> pd.DataFrame:
        """
        Compute pairwise Cramer's V for categorical features.

        Parameters
        ----------
        categorical_features : List[str]
            List of categorical feature names.

        Returns
        -------
        pd.DataFrame
            DataFrame with pairwise Cramer's V values.
        """

        n = len(categorical_features)
        cramers_matrix = np.zeros((n, n))

        for i in range(n):
            for j in range(n):  # Changed to calculate for all pairs
                if i == j:
                    cramers_matrix[i, j] = 1.0  # Cramer's V with itself is 1
                else:
                    cramers_v = UnivariateAnalysis._get_cramers_v(  # noqa: SLF001
                        self.data, categorical_features[i], categorical_features[j]
                    )
                    cramers_matrix[i, j] = cramers_v
                    cramers_matrix[j, i] = cramers_v  # Mirror the value

        return pd.DataFrame(
            cramers_matrix, index=categorical_features, columns=categorical_features
        )

    def plot_pairwise_cramers_v(
        self,
        categorical_features: List[str],
        fig_width: int = 800,
        fig_height: int = 800,
    ) -> None:
        """
        Plot pairwise Cramer's V for categorical variables using Plotly Express.

        Parameters
        ----------
        categorical_features : List[str]
            List of categorical feature names. If None, all object and category columns will be used.
        fig_width : int, optional
            Width of the figure in pixels.
        fig_height : int, optional
            Height of the figure in pixels.
        """
        # Compute pairwise Cramer's V
        cramers_df = self.compute_pairwise_cramers_v(categorical_features)

        # Mask the upper triangle
        mask = np.triu(np.ones_like(cramers_df, dtype=bool))

        # Create the heatmap using Plotly Express
        fig = px.imshow(
            cramers_df.where(~mask, np.nan),  # Mask the upper triangle
            labels={
                "x": "Categorical Features",
                "y": "Categorical Features",
                "color": "Cramer's V",
            },
            x=cramers_df.columns,
            y=cramers_df.index,
            color_continuous_scale="Plasma",
            text_auto=True,
            aspect="auto",
            width=fig_width,
            height=fig_height,
        )

        # Update layout to remove gridlines
        fig.update_layout(
            title="Pairwise Cramer's V for Categorical Variables (Lower Triangle)",
            xaxis={"showgrid": False},  # Remove x-axis gridlines
            yaxis={"showgrid": False},  # Remove y-axis gridlines
        )

        # Display the figure
        fig.show()


'''
    def generate_correlation_heatmap(self, columns: List[str]) -> go.Figure:
        """
        Generate an interactive correlation heatmap for the specified columns using Plotly.

        Parameters
        ----------
        columns : list of str
            List of column names to include in the correlation analysis.

        Returns
        -------
        go.Figure
            The Plotly figure object of the plot.
        """
        if len(columns) == 0:
            columns = self.numerical_columns

        # Calculate the correlation matrix
        corr_matrix = self.data[columns].corr(method="pearson")

        # Create a mask for the upper triangle
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        corr_matrix_masked = corr_matrix.mask(mask)

        # Create a Plotly heatmap
        fig = go.Figure(
            data=go.Heatmap(
                z=corr_matrix_masked.values[
                    ::-1
                ],  # Reverse the order of rows to flip the triangle
                x=corr_matrix_masked.columns,
                y=corr_matrix_masked.index[
                    ::-1
                ],  # Reverse the order of labels to match the flipped triangle
                colorscale="plasma",
                zmin=0,
                zmax=1,
                colorbar={"title": "Correlation"},
            )
        )

        # Update layout with square aspect ratio and remove excess margins
        fig.update_layout(
            title=f"Correlation Heatmap ({'Pearson'.capitalize()} method)",
            xaxis={
                "title": "Features",
                "side": "bottom",
                "tickangle": 45,
                "constrain": "domain",
            },  # Ensure square cells
            yaxis={
                "title": "Features",
                "scaleanchor": "x",
                "scaleratio": 1,
                "constrain": "domain",
            },  # Ensure square cells
            plot_bgcolor="rgba(0,0,0,0)",  # Remove background grid
            xaxis_showgrid=False,
            yaxis_showgrid=False,
            xaxis_zeroline=False,
            yaxis_zeroline=False,
            margin={
                "l": 40,
                "r": 40,
                "t": 40,
                "b": 40,
            },  # Adjust margins to center the plot
        )

        fig.show()

        return fig
'''
