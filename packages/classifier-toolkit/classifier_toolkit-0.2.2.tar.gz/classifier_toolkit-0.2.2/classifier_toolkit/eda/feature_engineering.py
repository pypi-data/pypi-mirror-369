import math
from typing import List, Literal, NamedTuple, Optional, Union

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
import pandas as pd
from category_encoders import CatBoostEncoder
from scipy.stats import anderson, probplot
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.impute import KNNImputer, SimpleImputer
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import (
    OneHotEncoder,
    OrdinalEncoder,
    PowerTransformer,
    StandardScaler,
)


class AndersonResult(NamedTuple):
    statistic: float
    critical_values: npt.NDArray
    significance_level: npt.NDArray


class FeatureEngineering:
    def __init__(
        self,
        dataframe: pd.DataFrame,
        target_column: str,
        numerical_columns: List[str],
        categorical_columns: List[str],
        to_be_encoded: Optional[List[str]] = None,
        transformations: Optional[List[dict]] = None,
    ):
        """
        Initialize the FeatureEngineering class with data and configuration.

        Parameters
        ----------
        dataframe : pd.DataFrame
            The data to be processed.
        target_column : str
            The target column for analysis.
        numerical_columns : List[str]
            List of numerical columns in the data.
        categorical_columns : List[str]
            List of categorical columns in the data.
        to_be_encoded : Optional[List[str]], optional
            Columns to be encoded, by default None.
        transformations : Optional[List[dict]], optional
            List of transformations to be applied, by default None.
        """
        self.data = dataframe.copy()
        self.target_column = target_column
        self.numerical_columns = numerical_columns
        self.categorical_columns = categorical_columns
        self.encode_list = to_be_encoded if to_be_encoded else categorical_columns
        self.transformations = (
            transformations if isinstance(transformations, list) else []
        )
        self.transformed_data: Optional[pd.DataFrame] = None

    def _log_transformation(self, method_name: str, params: dict):
        """
        Log the transformation applied to the data.

        Parameters
        ----------
        method_name : str
            The name of the transformation method.
        params : dict
            Parameters used in the transformation.
        """
        self.transformations.append({"method": method_name, "params": params})

    def apply_stored_transformations(self, new_data: pd.DataFrame) -> pd.DataFrame:
        """
        Apply stored transformations to new data.

        Parameters
        ----------
        new_data : pd.DataFrame
            The new data to apply transformations to.

        Returns
        -------
        pd.DataFrame
            The transformed data.
        """
        backup = self.data.copy()
        self.data = new_data

        for transformation in self.transformations:
            method = transformation["method"]
            params = transformation["params"]

            if method == "handle_missing_values":
                new_data = self.handle_missing_values(**params)
            elif method == "normality_transform":
                new_data = self.apply_normality_transformations(**params)
            elif method == "winsorization":
                new_data = self.apply_winsorization(**params)
            elif method == "encoding_categorical":
                new_data = self.encoding_categorical(**params)
            else:
                print(f"Transformation method '{method}' not found.")

        self.data = backup
        return new_data

    def handle_missing_values(
        self,
        method: Literal["knn", "mean", "median", "most_frequent", "quantile"] = "knn",
        n_neighbors: Optional[int] = 5,
    ) -> pd.DataFrame:
        """
        Handle missing values in the DataFrame using the specified method.

        Parameters
        ----------
        method : {'knn', 'mean', 'median', 'most_frequent', 'quantile'}, optional
            The imputation method to use, by default 'knn'.
        n_neighbors : Optional[int], optional
            Number of neighbors to use for KNN imputation, by default 5.

        Returns
        -------
        pd.DataFrame
            DataFrame with imputed values.
        """
        # Get all columns except the target
        features = self.data.drop(columns=[self.target_column])
        numeric_columns = self.numerical_columns.copy()
        if self.target_column in numeric_columns:
            numeric_columns.remove(self.target_column)

        # Validate numerical columns
        missing_numerical_columns = [
            col for col in numeric_columns if col not in features.columns
        ]
        if missing_numerical_columns:
            raise KeyError(
                f"Numerical columns not found in DataFrame: {missing_numerical_columns}"
            )

        numerical_features = features[numeric_columns]

        # Validate categorical columns
        missing_categorical_columns = [
            col for col in self.categorical_columns if col not in features.columns
        ]
        if missing_categorical_columns:
            raise KeyError(
                f"Categorical columns not found in DataFrame: {missing_categorical_columns}"
            )

        categorical_features = features[self.categorical_columns].copy()
        encoders = {}
        for column in self.categorical_columns:
            encoder = OrdinalEncoder(
                handle_unknown="use_encoded_value", unknown_value=-1
            )
            categorical_features[column] = encoder.fit_transform(
                categorical_features[[column]]
            ).ravel()
            encoders[column] = encoder

        # Combine numeric and encoded categorical features
        combined_features = pd.concat(
            [numerical_features, categorical_features], axis=1
        )

        # Check if the method is one of the SimpleImputer strategies
        simple_imputer_methods = ["mean", "median", "most_frequent", "quantile"]

        if method.lower() == "knn":
            # Initialize the KNN imputer
            if n_neighbors is None:
                raise ValueError("n_neighbors must be specified for KNN imputation.")
            imputer = KNNImputer(n_neighbors=n_neighbors)
        elif method.lower() in simple_imputer_methods:
            # Initialize the SimpleImputer based on the method
            if method.lower() == "quantile":
                imputer = SimpleImputer(strategy="constant", fill_value=0.5)
            else:
                imputer = SimpleImputer(strategy=method.lower())
        else:
            raise ValueError(
                f"Method '{method}' is not supported. Choose from 'knn', 'mean', 'median', 'most_frequent', or 'quantile'."
            )

        # Fit and transform the combined features
        imputed_features = imputer.fit_transform(combined_features)

        # Convert the imputed array back to a DataFrame
        imputed_df = pd.DataFrame(
            imputed_features, columns=combined_features.columns, index=self.data.index
        )

        # Decode categorical columns
        for column in self.categorical_columns:
            imputed_df[column] = (
                encoders[column].inverse_transform(imputed_df[[column]]).ravel()
            )

        # Add the target column back
        imputed_df[self.target_column] = self.data[self.target_column]

        # Update the current DataFrame with the imputed values
        self.data[imputed_df.columns] = imputed_df

        print(f"\nMissing values have been imputed using {method} imputation.")
        print("Note: The target column was excluded from imputation.")
        print("Categorical columns were encoded before imputation and then decoded.")

        # Log the transformation
        self._log_transformation(
            "handle_missing", {"method": method, "n_neighbors": n_neighbors}
        )
        return self.data

    def diagnose_normality_transform(
        self,
        method: Literal["power", "standard"] = "power",
        alpha: float = 0.05,
        test_mode: bool = False,
    ) -> tuple[dict, Union[PowerTransformer, StandardScaler]]:
        transformed_data = self.data.copy()
        results = {}
        for column in self.numerical_columns:
            if column == self.target_column:
                print(
                    f"{column} is the target column. Skipping normality check and transformation."
                )
                continue
            # Perform Anderson-Darling test before transformation
            ad_result: AndersonResult = anderson(self.data[column].dropna())  # type: ignore
            ad_statistic = ad_result.statistic
            ad_critical_values = ad_result.critical_values
            ad_significance_level = ad_result.significance_level
            is_normal_ad = (
                ad_statistic
                < ad_critical_values[np.searchsorted(ad_significance_level, alpha)]
            )

            results[column] = {
                "ad_statistic": ad_statistic,
                "ad_critical_values": ad_critical_values,
                "is_normal_ad": is_normal_ad,
                "transformation": "None",
                "lambda": None,
            }

            # Create Q-Q plot before transformation
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            probplot(self.data[column], dist="norm", plot=ax1)
            ax1.set_title(f"{column} Before Transformation")

            # If not normal, apply selected transformation
            if not is_normal_ad:
                if method.lower() == "power":
                    transformer = PowerTransformer(method="yeo-johnson")
                elif method.lower() == "standard":
                    transformer = StandardScaler()

                # Mask for non-missing values
                non_missing_mask = ~self.data[column].isna()

                # Fit and transform only non-missing values
                transformed_data_col = transformer.fit_transform(
                    self.data.loc[non_missing_mask, [column]]
                )
                transformed_data_col = transformed_data_col.flatten()

                # Perform Anderson-Darling test after transformation
                ad_result_after: AndersonResult = anderson(transformed_data_col)  # type: ignore
                ad_statistic_after = ad_result_after.statistic
                ad_critical_values_after = ad_result_after.critical_values
                is_normal_ad_after = (
                    ad_statistic_after
                    < ad_critical_values_after[
                        np.searchsorted(ad_significance_level, alpha)
                    ]
                )

                # Create Q-Q plot after transformation
                probplot(transformed_data_col, dist="norm", plot=ax2)
                ax2.set_title(f"{column} After Transformation")

                # Update the column with transformed data in the transformed DataFrame
                transformed_data[column] = self.data[column].astype(float)
                transformed_data.loc[non_missing_mask, column] = transformed_data_col
                results[column]["transformation"] = method.capitalize() + "Transformer"
                if method == "power":
                    results[column]["lambda"] = transformer.lambdas_[0]  # type: ignore
                results[column]["ad_statistic_after"] = ad_statistic_after
                results[column]["ad_critical_values_after"] = ad_critical_values_after
                results[column]["is_normal_ad_after"] = is_normal_ad_after
            else:
                ax2.axis("off")

            plt.tight_layout()
            if not test_mode:
                plt.show()

        # Store the transformed data
        self.transformed_data = transformed_data

        # Print results
        print("\nNormality Test Results and Transformations:")
        for column, result in results.items():
            print(f"\n{column}:")
            print(f"  Anderson-Darling statistic: {result['ad_statistic']:.4f}")
            print(f"  Initially normal (Anderson-Darling): {result['is_normal_ad']}")
            if result["transformation"] != "None":
                print(f"  Transformation applied: {result['transformation']}")
                if result["transformation"] == "PowerTransformer":
                    print(f"  Lambda value: {result['lambda']:.4f}")
                print(
                    f"  Anderson-Darling statistic after transformation: {result['ad_statistic_after']:.4f}"
                )
                print(
                    f"  Normal after transformation (Anderson-Darling): {result['is_normal_ad_after']}"
                )
            else:
                print("  No transformation applied")

        self._log_transformation(
            "normality_transform", {"method": method, "alpha": alpha}
        )
        return results, transformer

    def apply_normality_transformations(
        self, columns_to_keep: List[str]
    ) -> pd.DataFrame:
        """
        Apply the transformations to the specified columns and keep them in the DataFrame.

        Parameters
        ----------
        columns_to_keep : List[str]
            List of columns to keep after applying transformations.

        Returns
        -------
        pd.DataFrame
            DataFrame with applied transformations.
        """
        if self.transformed_data is None:
            raise ValueError(
                "No transformations have been applied yet. Please run normality_transform first."
            )

        # Create a new DataFrame with the selected columns
        updated_data = self.data.copy()
        for column in columns_to_keep:
            if column in self.transformed_data.columns:
                updated_data[column] = self.transformed_data[column]
            else:
                raise ValueError(f"Column {column} not found in transformed data")

        self.data = updated_data

        for transform in self.transformations:
            if transform["method"] == "normality_transform":
                transform["selected_columns"] = columns_to_keep

        return self.data

    def handle_high_cardinality(
        self,
        high_cardinality_columns: List[str],
        method: Literal["gathering", "woe", "perlich"] = "gathering",
    ) -> None:
        """
        Handle high cardinality in categorical columns using the specified method.

        Parameters
        ----------
        high_cardinality_columns : List[str]
            List of columns with high cardinality.
        method : {'gathering', 'woe', 'perlich'}, optional
            The method to use for handling high cardinality, by default 'gathering'.
        """
        self.high_cardinality_columns = high_cardinality_columns
        self.method = method.lower()

        for column in high_cardinality_columns:
            if self.method == "gathering":
                self._gathering_method(column)
            elif self.method == "woe":
                self._woe_method(column)
            elif self.method == "perlich":
                pass  # To be implemented later
            else:
                print("Please choose the correct method: gathering | woe | perlich")
                return None

    def _gathering_method(self, column: str, threshold: float = 0.01) -> None:
        """
        Gather all categories representing less than a specified percentage of the population into 'other'.

        Parameters
        ----------
        column : str
            The column to apply the method to.
        threshold : float, optional
            The threshold for the percentage of the population, by default 0.01.
        """
        value_counts = self.data[column].value_counts(normalize=True)
        small_categories = value_counts[value_counts < threshold].index  # type: ignore
        self.data[column] = self.data[column].apply(
            lambda x: "other" if x in small_categories else x
        )

    def _woe_method(self, column: str) -> None:
        """
        Calculate the Weight of Evidence (WOE) for high-cardinality columns.

        Parameters
        ----------
        column : str
            The column to apply the method to.
        """
        if self.data[self.target_column].dtype.name == "category":
            self.data[self.target_column] = self.data[self.target_column].cat.codes
        elif not np.issubdtype(self.data[self.target_column].dtype, np.number):  # type: ignore
            self.data[self.target_column] = self.data[self.target_column].astype(float)

        target = self.data[self.target_column]
        df = pd.DataFrame({column: self.data[column], "target": target})

        total_good = df["target"].sum()
        total_bad = df["target"].count() - total_good

        grouped = df.groupby(column)["target"].agg(["sum", "count"])
        grouped["good"] = grouped["sum"]
        grouped["bad"] = grouped["count"] - grouped["sum"]

        epsilon = 1e-10
        grouped["good_pct"] = (grouped["good"] + epsilon) / (total_good + epsilon)
        grouped["bad_pct"] = (grouped["bad"] + epsilon) / (total_bad + epsilon)

        grouped["woe"] = np.log(grouped["good_pct"] / grouped["bad_pct"])

        woe_dict = grouped["woe"].to_dict()
        self.data[column] = (
            self.data[column].map(woe_dict).fillna(0)
        )  # Fill missing values with 0

    def transform_and_plot_high_cardinality_histograms(
        self,
        high_cardinality_columns: List[str],
        method: Literal["gathering", "woe", "perlich"] = "gathering",
    ) -> Optional[pd.DataFrame]:
        """
        Transform high cardinality columns and plot histograms before and after transformation.

        Parameters
        ----------
        high_cardinality_columns : List[str]
            List of columns with high cardinality.
        method : {'gathering', 'woe', 'perlich'}, optional
            The method to use for handling high cardinality, by default 'gathering'.

        Returns
        -------
        pd.DataFrame
            DataFrame with transformed columns.
        """
        self.high_cardinality_columns = high_cardinality_columns
        self.method = method.lower()
        for column in high_cardinality_columns:
            if column not in self.data.columns:
                print(f"Column '{column}' does not exist in the DataFrame.")
                continue

            original_data = self.data[column].copy()

            plt.figure(figsize=(12, 6))
            plt.subplot(1, 2, 1)
            original_data.value_counts().plot(kind="bar")
            plt.title(f"{column} - Before Transformation")
            plt.xlabel(column)
            plt.ylabel("Frequency")

            if self.method == "gathering":
                self._gathering_method(column)
            elif self.method == "woe":
                self._woe_method(column)
            elif self.method == "perlich":
                pass  # To be implemented later
            else:
                print("Please choose the correct method: gathering | woe | perlich")
                return None

            plt.subplot(1, 2, 2)
            if self.method == "woe":
                transformed_data = self.data[column]
                transformed_data.plot(kind="kde", color="#1e78b5")
                plt.title(f"{column} - After Transformation ({method.capitalize()})")
                plt.xlabel(f"{column} (WOE)")
                plt.ylabel("Density")
            else:
                transformed_data = self.data[column].value_counts()
                colors = [
                    "#23eb1c" if x == "other" else "#1e78b5"
                    for x in transformed_data.index
                ]
                transformed_data.plot(kind="bar", color=colors)
                plt.title(f"{column} - After Transformation ({method.capitalize()})")
                plt.xlabel(column)
                plt.ylabel("Frequency")

            plt.tight_layout()
            plt.show()

        return self.data

    def perform_low_cardinality_checks_numerical(
        self, threshold: int = 10
    ) -> List[str]:
        """
        Check for low cardinality numerical columns.

        Parameters
        ----------
        threshold : int, optional
            The threshold for low cardinality, by default 10.

        Returns
        -------
        List[str]
            List of low cardinality numerical columns.
        """
        low_cardinality_numeric = [
            col
            for col in self.numerical_columns
            if self.data[col].nunique() < threshold
        ]
        return low_cardinality_numeric

    def _kmeans_binning(self, column: str, n_bins: int) -> pd.Series:
        """
        Apply k-means binning to the specified column.

        Parameters
        ----------
        column : str
            The column to bin.
        n_bins : int
            The number of bins to create.

        Returns
        -------
        pd.Series
            Series with binned data.
        """
        kmeans = KMeans(n_clusters=n_bins)
        self.data[column + "_binned"] = kmeans.fit_predict(self.data[[column]])
        print(f"KMeans Bins for {column}: {self.data[column + '_binned'].unique()}")
        print(
            f"KMeans Cluster Centers for {column}: {kmeans.cluster_centers_.flatten()}"
        )
        return self.data[column + "_binned"]

    def _fixed_width_binning(self, column: str, n_bins: int) -> pd.Series:
        """
        Apply fixed-width binning to the specified column.

        Parameters
        ----------
        column : str
            The column to bin.
        n_bins : int
            The number of bins to create.

        Returns
        -------
        pd.Series
            Series with binned data.
        """
        min_val = self.data[column].min()
        max_val = self.data[column].max()

        bin_edges = np.linspace(min_val, max_val, n_bins + 1)
        bin_edges = np.ceil(bin_edges).astype(int)

        print(f"Fixed Width Bins for {column}: {bin_edges}")

        self.data[column + "_binned"] = np.digitize(
            self.data[column], bin_edges, right=False
        )

        print(
            f"Bin counts for {column} with fixed_width binning: {self.data[column + '_binned'].value_counts()}"
        )

        return self.data[column + "_binned"]

    def _exponential_binning(self, column: str, n_bins: int) -> pd.Series:
        """
        Apply exponential binning to the specified column.

        Parameters
        ----------
        column : str
            The column to bin.
        n_bins : int
            The number of bins to create.

        Returns
        -------
        pd.Series
            Series with binned data.
        """
        min_val = self.data[column].min()
        max_val = self.data[column].max()
        bins = [min_val]
        for i in range(1, n_bins):
            bins.append(
                min_val
                + (math.exp(i) - 1) * (max_val - min_val) / (math.exp(n_bins) - 1)
            )
        bins.append(max_val)
        self.data[column + "_binned"] = (
            np.digitize(self.data[column], bins, right=True) - 1
        )
        print(f"Exponential Bins for {column}: {bins}")
        return self.data[column + "_binned"]

    def _quantile_binning(self, column: str, n_bins: int) -> pd.Series:
        """
        Apply quantile binning to the specified column.

        Parameters
        ----------
        column : str
            The column to bin.
        n_bins : int
            The number of bins to create.

        Returns
        -------
        pd.Series
            Series with binned data.
        """
        try:
            self.data[column + "_binned"] = pd.qcut(
                self.data[column], q=n_bins, labels=False, duplicates="drop"
            )
            print(
                f"Quantile Bins for {column}: {pd.qcut(self.data[column], q=n_bins, duplicates='drop').unique()}"
            )
        except ValueError:
            self.data[column + "_binned"] = pd.qcut(
                self.data[column].rank(method="first"),
                q=n_bins,
                labels=False,
                duplicates="drop",
            )
            print(
                f"Quantile Bins (with ranking) for {column}: {pd.qcut(self.data[column].rank(method='first'), q=n_bins, duplicates='drop').unique()}"
            )
        return self.data[column + "_binned"]

    def _equal_frequency_binning(self, column: str, n_bins: int) -> pd.Series:
        """
        Apply equal frequency binning to the specified column.

        Parameters
        ----------
        column : str
            The column to bin.
        n_bins : int
            The number of bins to create.

        Returns
        -------
        pd.Series
            Series with binned data.
        """
        try:
            self.data[column + "_binned"] = pd.qcut(
                self.data[column], q=n_bins, labels=False, duplicates="drop"
            )
            print(
                f"Equal Frequency Bins for {column}: {pd.qcut(self.data[column], q=n_bins, duplicates='drop').unique()}"
            )
        except ValueError:
            self.data[column + "_binned"] = pd.qcut(
                self.data[column].rank(method="first"),
                q=n_bins,
                labels=False,
                duplicates="drop",
            )
            print(
                f"Equal Frequency Bins (with ranking) for {column}: {pd.qcut(self.data[column].rank(method='first'), q=n_bins, duplicates='drop').unique()}"
            )
        return self.data[column + "_binned"]

    def binnings(
        self,
        methods: Literal[
            "kmeans", "fixed_width", "exponential", "quantile", "equal_frequency"
        ] = "equal_frequency",
        n_bins: int = 5,
        state: Literal["prod", "dev"] = "prod",
    ) -> pd.DataFrame:
        """
        Apply binning to low cardinality numerical columns using the specified methods.

        Parameters
        ----------
        methods : {'kmeans', 'fixed_width', 'exponential', 'quantile', 'equal_frequency'}, optional
            The binning methods to use, by default 'equal_frequency'.
        n_bins : int, optional
            The number of bins to create, by default 5.
        state : {'prod', 'dev'}, optional
            The state is to indicate whether we test the function or not, if testing, plots are not shown.
        Returns
        -------
        pd.DataFrame
            DataFrame with binned columns.
        """
        low_cardinality_numeric = self.perform_low_cardinality_checks_numerical()
        print(f"Low cardinality numerical features: {low_cardinality_numeric}")

        for col in low_cardinality_numeric:
            if state == "prod":
                self.plot_distribution(col, "before transform", binned=False)

            print(f"\nApplying {methods} binning for column: {col}")

            if methods == "kmeans":
                self.data[col + "_binned"] = self._kmeans_binning(col, n_bins)
            elif methods == "fixed_width":
                self.data[col + "_binned"] = self._fixed_width_binning(col, n_bins)
            elif methods == "exponential":
                self.data[col + "_binned"] = self._exponential_binning(col, n_bins)
            elif methods == "quantile":
                self.data[col + "_binned"] = self._quantile_binning(col, n_bins)
            elif methods == "equal_frequency":
                self.data[col + "_binned"] = self._equal_frequency_binning(col, n_bins)
            else:
                raise ValueError("Please check the name of the method")

            print(
                f"Bin counts for {col} with {methods} binning: {self.data[col + '_binned'].value_counts()}"
            )

            if state == "prod":
                self.plot_distribution(col, method_name=methods, binned=True)

        return self.data

    def plot_distribution(
        self,
        column: str,
        method_name: str,
        binned: bool = False,
        log_scale: bool = False,
    ) -> None:
        """
        Plot the distribution of the specified column.

        Parameters
        ----------
        column : str
            The column to plot.
        method_name : str
            The name of the method used for binning.
        binned : bool, optional
            Whether the data has been binned, by default False.
        log_scale : bool, optional
            Whether to use a log scale for the y-axis, by default False.
        """
        plt.figure(figsize=(10, 6))
        if binned:
            binned_data = self.data[column + "_binned"]
            bin_counts = binned_data.value_counts().sort_index()

            bars = plt.bar(
                bin_counts.index,
                list(bin_counts.values),
                color="blue",
                alpha=0.7,
                label="Binned",
            )

            plt.xticks(bin_counts.index, bin_counts.index.to_list(), rotation=45)

            plt.title(
                f"Distribution of {column} (Binned) with {method_name.capitalize()} Method"
            )
            plt.xlabel(f"{column}")

            for bar, count in zip(bars, bin_counts.values):
                plt.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() / 2,
                    f"{count}",
                    ha="center",
                    va="center",
                    color="white",
                    fontsize=10,
                    weight="bold",
                )

        else:
            plt.hist(
                self.data[column], bins="auto", alpha=0.7, color="red", label="Original"
            )
            plt.title(f"Distribution of {column}")
            plt.xlabel(column)

        plt.ylabel("Frequency")
        if log_scale:
            plt.yscale("log")
        plt.legend()
        plt.tight_layout()
        plt.show()

    def _encoding_categorical_one_hot(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Perform one-hot encoding for the specified categorical columns.

        Parameters
        ----------
        data : pd.DataFrame
            The data containing the categorical columns to encode.

        Returns
        -------
        pd.DataFrame
            DataFrame with one-hot encoded columns.
        """
        encoder = OneHotEncoder(
            sparse_output=False, drop="first", handle_unknown="ignore"
        )
        encoded_array = encoder.fit_transform(data[self.encode_list])

        encoded_df = pd.DataFrame(
            encoded_array,
            columns=encoder.get_feature_names_out(self.encode_list),
            index=data.index,
        )

        data = data.drop(columns=self.encode_list)
        data = pd.concat([data, encoded_df], axis=1)

        return data

    def _encoding_categorical_distribution(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Perform distribution encoding for the specified categorical columns.

        Parameters
        ----------
        data : pd.DataFrame
            The data containing the categorical columns to encode.

        Returns
        -------
        pd.DataFrame
            DataFrame with distribution encoded columns.
        """
        for column in self.encode_list:
            counts = data[column].value_counts(normalize=True)
            data[column] = data[column].map(counts)
        return data

    def _encoding_categorical_woe(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Perform Weight of Evidence (WOE) encoding for the specified categorical columns.

        Parameters
        ----------
        data : pd.DataFrame
            The data containing the categorical columns to encode.

        Returns
        -------
        pd.DataFrame
            DataFrame with WOE encoded columns.
        """
        for column in self.encode_list:
            target = data[self.target_column]
            df = pd.DataFrame({column: data[column], "target": target})

            total_good = df["target"].sum()
            total_bad = df["target"].count() - total_good

            grouped = df.groupby(column, observed=False)["target"].agg(["sum", "count"])
            grouped["good"] = grouped["sum"]
            grouped["bad"] = grouped["count"] - grouped["sum"]

            epsilon = 1e-10
            grouped["good_pct"] = (grouped["good"] + epsilon) / (total_good + epsilon)
            grouped["bad_pct"] = (grouped["bad"] + epsilon) / (total_bad + epsilon)

            grouped["woe"] = np.log(grouped["good_pct"] / grouped["bad_pct"])

            woe_dict = grouped["woe"].to_dict()

            data[column] = data[column].astype(str).map(woe_dict).fillna(0)
        return data

    def _encoding_categorical_catboost(
        self, data: pd.DataFrame, sigma_value: float = 0.05
    ) -> pd.DataFrame:
        """
        Perform CatBoost encoding for the specified categorical columns.

        Parameters
        ----------
        data : pd.DataFrame
            The DataFrame containing the data to encode.
        sigma_value : float, optional
            The regularization parameter for the encoding, by default 0.05.

        Returns
        -------
        pd.DataFrame
            DataFrame with CatBoost encoded columns.
        """
        encoder = CatBoostEncoder(cols=self.encode_list, sigma=sigma_value)
        data[self.encode_list] = encoder.fit_transform(
            data[self.encode_list], data[self.target_column]
        )
        return data

    def encoding_categorical(
        self,
        method: Literal["one_hot", "distribution", "woe", "catboost"] = "one_hot",
        fit: bool = True,
        data: Optional[pd.DataFrame] = None,
        verbose: bool = False,
    ) -> pd.DataFrame:
        """
        Perform encoding for the specified categorical columns using the chosen method.

        Parameters
        ----------
        method : {'one_hot', 'distribution', 'woe', 'catboost'}, optional
            The encoding method to use, by default 'one_hot'.
        fit : bool, optional
            Whether to fit the encoder (True) or just transform (False), by default True.
        data : Optional[pd.DataFrame], optional
            The data to encode. If None, uses self.data, by default None.

        Returns
        -------
        pd.DataFrame
            DataFrame with encoded columns.
        """
        if self.encode_list is None:
            print("No columns specified for encoding.")
            return self.data if data is None else data

        data = self.data.copy() if data is None else data.copy()

        missing_columns = [col for col in self.encode_list if col not in data.columns]
        if missing_columns:
            raise ValueError(
                f"The following columns are not in the DataFrame: {missing_columns}"
            )

        if method == "one_hot":
            if fit:
                print("Fitting OneHotEncoder...") if verbose else None
                self.encoder = OneHotEncoder(
                    sparse_output=False, drop="first", handle_unknown="ignore"
                )
                encoded_array = self.encoder.fit_transform(data[self.encode_list])
            else:
                print(
                    "Transforming data with OneHotEncoder fit before..."
                ) if verbose else None
                encoded_array = self.encoder.transform(data[self.encode_list])

            encoded_df = pd.DataFrame(
                encoded_array,  # type: ignore
                columns=self.encoder.get_feature_names_out(self.encode_list),
                index=data.index,
            )  # type: ignore

            data = data.drop(columns=self.encode_list)
            data = pd.concat([data, encoded_df], axis=1)

        elif method == "distribution":
            if fit:
                print("Fitting distribution maps...") if verbose else None
                self.distribution_maps = {
                    col: data[col].value_counts(normalize=True)
                    for col in self.encode_list
                }
                for column in self.encode_list:
                    data[column] = (
                        data[column].map(self.distribution_maps[column]).fillna(0)
                    )
            else:
                print(
                    "Transforming data with distribution maps fit before..."
                ) if verbose else None
                if self.distribution_maps:
                    for column in self.encode_list:
                        data[column] = (
                            data[column].map(self.distribution_maps[column]).fillna(0)
                        )
                else:
                    raise ValueError(
                        "Distribution maps not found. Please fit the encoder first."
                    )

        elif method == "woe":
            if fit:
                print("Fitting WOE maps...") if verbose else None
                self.woe_maps = {}
                for column in self.encode_list:
                    target = data[self.target_column]
                    df = pd.DataFrame({column: data[column], "target": target})
                    total_good = df["target"].sum()
                    total_bad = df["target"].count() - total_good
                    grouped = df.groupby(column, observed=False)["target"].agg(
                        ["sum", "count"]
                    )
                    grouped["good"] = grouped["sum"]
                    grouped["bad"] = grouped["count"] - grouped["sum"]
                    epsilon = 1e-10
                    grouped["good_pct"] = (grouped["good"] + epsilon) / (
                        total_good + epsilon
                    )
                    grouped["bad_pct"] = (grouped["bad"] + epsilon) / (
                        total_bad + epsilon
                    )
                    grouped["woe"] = np.log(grouped["good_pct"] / grouped["bad_pct"])
                    self.woe_maps[column] = grouped["woe"].to_dict()

                for column in self.encode_list:
                    data[column] = (
                        data[column].astype(str).map(self.woe_maps[column]).fillna(0)
                    )
            else:
                print(
                    "Transforming data with WOE maps fit before..."
                ) if verbose else None
                if self.woe_maps:
                    for column in self.encode_list:
                        data[column] = (
                            data[column]
                            .astype(str)
                            .map(self.woe_maps[column])
                            .fillna(0)
                        )
                else:
                    raise ValueError(
                        "WOE maps not found. Please fit the encoder first."
                    )

        elif method == "catboost":
            if fit:
                print("Fitting CatBoostEncoder...") if verbose else None
                self.encoder = CatBoostEncoder(cols=self.encode_list)
                data[self.encode_list] = self.encoder.fit_transform(
                    data[self.encode_list], data[self.target_column]
                )
            else:
                print(
                    "Transforming data with CatBoostEncoder fit before..."
                ) if verbose else None
                data[self.encode_list] = self.encoder.transform(data[self.encode_list])

        else:
            raise ValueError(
                f"Encoding method '{method}' is not supported. Choose from 'one_hot', 'distribution', 'woe', or 'catboost'."
            )

        if fit:
            self._log_transformation(
                "encoding_categorical",
                {"method": method, "selected_columns": self.encode_list},
            )

        return data

    ####### FEATURE ENGINEERING: OPTIONAL FUNCTIONS #######
    def search_pca_components(self):
        """
        Search for the optimal number of principal components to retain.
        """
        numerical_data = self.data[self.numerical_columns]

        pca = PCA()
        pca.fit(numerical_data)

        explained_variance = pca.explained_variance_ratio_
        cumulative_variance = explained_variance.cumsum()

        plt.figure(figsize=(10, 6))
        plt.plot(
            range(1, len(explained_variance) + 1),
            explained_variance,
            marker="o",
            label="Explained Variance",
        )
        plt.plot(
            range(1, len(cumulative_variance) + 1),
            cumulative_variance,
            marker="o",
            label="Cumulative Variance",
        )
        plt.title("Explained Variance by Principal Components")
        plt.xlabel("Number of Principal Components")
        plt.ylabel("Variance Explained")
        plt.legend()
        plt.grid(True)
        plt.show()

        for i, (ev, cv) in enumerate(zip(explained_variance, cumulative_variance), 1):
            print(
                f"Principal Component {i}: Explained Variance = {ev:.4f}, Cumulative Variance = {cv:.4f}"
            )

        print(
            "Use the cumulative variance to decide the number of components to retain and then call implement_pca with the desired number of components."
        )

    def implement_pca(self, n_components: int):
        """
        Implement PCA with the specified number of components.

        Parameters
        ----------
        n_components : int
            The number of principal components to retain.
        """
        numerical_data = self.data[self.numerical_columns]

        pca = PCA(n_components=n_components)
        principal_components = pca.fit_transform(numerical_data)

        pca_columns = [f"PC{i+1}" for i in range(n_components)]
        pca_df = pd.DataFrame(
            principal_components, columns=pca_columns, index=self.data.index
        )

        self.data.drop(columns=self.numerical_columns, inplace=True)
        self.data[pca_columns] = pca_df

        print(
            f"PCA has been applied, reducing the data to {n_components} principal components."
        )

    def search_svd_components(self, max_components: int):
        """
        Search for the optimal number of singular value components to retain.

        Parameters
        ----------
        max_components : int
            The maximum number of components to evaluate.
        """
        numerical_data = self.data[self.numerical_columns]

        if max_components <= 0:
            max_components = min(numerical_data.shape[1], numerical_data.shape[0])

        explained_variances = []
        cumulative_variances = []

        for n in range(1, max_components + 1):
            svd = TruncatedSVD(n_components=n)
            svd.fit(numerical_data)
            explained_variance = svd.explained_variance_ratio_
            cumulative_variance = explained_variance.sum()
            explained_variances.append(explained_variance[-1])
            cumulative_variances.append(cumulative_variance)
            print(
                f"Number of components: {n}, Explained Variance: {explained_variance[-1]:.4f}, Cumulative Variance: {cumulative_variance:.4f}"
            )

        plt.figure(figsize=(10, 6))
        plt.plot(
            range(1, max_components + 1),
            explained_variances,
            marker="o",
            label="Explained Variance",
        )
        plt.plot(
            range(1, max_components + 1),
            cumulative_variances,
            marker="o",
            label="Cumulative Variance",
        )
        plt.title("Explained Variance by SVD Components")
        plt.xlabel("Number of SVD Components")
        plt.ylabel("Variance Explained")
        plt.legend()
        plt.grid(True)
        plt.show()

        print(
            "Use the explained and cumulative variance to decide the number of components to retain, then call implement_svd with the desired number of components."
        )

    def implement_svd(self, n_components: int):
        """
        Implement Singular Value Decomposition (SVD) with the specified number of components.

        Parameters
        ----------
        n_components : int
            The number of singular value components to retain.
        """
        numerical_data = self.data[self.numerical_columns]

        svd = TruncatedSVD(n_components=n_components)
        svd_components = svd.fit_transform(numerical_data)

        svd_columns = [f"SVD{i+1}" for i in range(n_components)]
        svd_df = pd.DataFrame(
            svd_components, columns=svd_columns, index=self.data.index
        )

        self.data.drop(columns=self.numerical_columns, inplace=True)
        self.data[svd_columns] = svd_df

        print(
            f"SVD has been applied, reducing the data to {n_components} singular value components."
        )

    def evaluate_lda_components(self):
        """
        Evaluate the performance of Linear Discriminant Analysis (LDA) with different numbers of components.
        """
        numerical_data = self.data[self.numerical_columns]
        target_data = self.data[self.target_column]

        num_classes = len(target_data.unique())
        num_features = numerical_data.shape[1]
        max_components = min(num_classes - 1, num_features)

        scores = []
        for n in range(1, max_components + 1):
            lda = LDA(n_components=n)
            score = cross_val_score(lda, numerical_data, target_data, cv=5).mean()
            scores.append(score)
            print(f"Number of components: {n}, Cross-validation score: {score:.4f}")

        plt.figure(figsize=(10, 6))
        plt.plot(range(1, max_components + 1), scores, marker="o")
        plt.title("LDA Components vs. Cross-Validation Score")
        plt.xlabel("Number of LDA Components")
        plt.ylabel("Cross-Validation Score")
        plt.grid(True)
        plt.show()

        print(
            "Use the plot to decide the optimal number of components and then call implement_lda with the desired number of components."
        )

    def implement_lda(self, n_components: int):
        """
        Implement Linear Discriminant Analysis (LDA) with the specified number of components.

        Parameters
        ----------
        n_components : int
            The number of LDA components to retain.
        """
        numerical_data = self.data[self.numerical_columns]
        target_data = self.data[self.target_column]

        lda = LDA(n_components=n_components)
        lda_components = lda.fit_transform(numerical_data, target_data)

        lda_columns = [f"LD{i+1}" for i in range(n_components)]
        lda_df = pd.DataFrame(
            lda_components, columns=lda_columns, index=self.data.index
        )

        self.data.drop(columns=self.numerical_columns, inplace=True)
        self.data[lda_columns] = lda_df

        print(
            f"LDA has been applied, reducing the data to {n_components} linear discriminants."
        )

    def apply_winsorization(
        self, selected_columns: List[str], percentile: float = 0.05
    ) -> pd.DataFrame:
        """
        Apply winsorization to numerical columns to limit extreme values.

        Parameters
        ----------
        selected_columns : List[str]
            List of columns to apply winsorization to.
        percentile : float, optional
            The percentage of data to be considered as extreme values on each side, by default 0.05.

        Returns
        -------
        pd.DataFrame
            DataFrame with winsorized columns.
        """
        if len(selected_columns) == 0:
            selected_columns = self.numerical_columns

        for column in selected_columns:
            if column == self.target_column:
                print(f"{column} is the target column. Skipping winsorization.")
                continue

            lower_bound = np.percentile(self.data[column], percentile * 100)
            upper_bound = np.percentile(self.data[column], (1 - percentile) * 100)
            self.data[column] = np.clip(self.data[column], lower_bound, upper_bound)

        print(f"\n{' WINSORIZATION RESULTS '.center(100, '=')}")
        print(
            f"Winsorization applied with {percentile * 100:.1f}% capping on each side."
        )
        print("=" * 100)

        # Prepare the summary statistics
        summary = self.data[selected_columns].describe()

        # Determine the width for each column based on the longest column name
        col_width = max(max(len(col) for col in selected_columns), 15) + 2

        # Print column names
        print(
            f"{'Statistic':<15}"
            + "".join(f"{col:^{col_width}}" for col in selected_columns)
        )
        print("-" * (15 + col_width * len(selected_columns)))

        # Print the summary statistics
        for stat in summary.index:
            print(
                f"{stat:<15}"
                + "".join(
                    f"{summary.loc[stat, col]:^{col_width}.6f}"
                    for col in selected_columns
                )
            )

        print("=" * (15 + col_width * len(selected_columns)))

        self._log_transformation(
            "winsorization",
            {"selected_columns": selected_columns, "percentile": percentile},
        )
        return self.data

    percentile_capping = apply_winsorization


'''
    def encoding_categorical(
        self,
        method: Literal["one_hot", "distribution", "woe", "catboost"] = "one_hot",
    ) -> pd.DataFrame:
        """
        Perform encoding for the specified categorical columns using the chosen method.

        The columns to be encoded are specified during the initialization of the FeatureEngineering class.

        Parameters
        ----------
        method : {'one_hot', 'distribution', 'woe', 'catboost'}, optional
            The encoding method to use, by default 'one_hot'.
        """
        if self.encode_list is None:
            print("No columns specified for encoding.")

        missing_columns = [
            col for col in self.encode_list if col not in self.data.columns
        ]
        if missing_columns:
            raise ValueError(
                f"The following columns are not in the DataFrame: {missing_columns}"
            )

        data = self.data.copy()

        if method == "one_hot":
            data = self._encoding_categorical_one_hot(data)
            print(f"One-hot encoding performed on columns: {self.encode_list}")
            # Get the names of the new encoded columns
            new_columns = [
                col for col in data.columns if col.startswith(tuple(self.encode_list))
            ]
            print("\nHead of encoded columns:")
            print(data[new_columns].head())
        elif method == "distribution":
            data = self._encoding_categorical_distribution(data)
            print(f"Distribution encoding performed on columns: {self.encode_list}")
            print("\nHead of encoded columns:")
            print(data[self.encode_list].head())
        elif method == "woe":
            data = self._encoding_categorical_woe(data)
            print(f"WOE encoding performed on columns: {self.encode_list}")
            print("\nHead of encoded columns:")
            print(data[self.encode_list].head())
        elif method == "catboost":
            data = self._encoding_categorical_catboost(data)
            print(f"CatBoost encoding performed on columns: {self.encode_list}")
            print("\nHead of encoded columns:")
            print(data[self.encode_list].head())
        else:
            raise ValueError(
                f"Encoding method '{method}' is not supported. Choose from 'one_hot', 'distribution', 'woe', or 'catboost'."
            )

        self.data = data
        self.data.info()
        self._log_transformation(
            "encoding_categorical",
            {"method": method, "selected_columns": self.encode_list},
        )
        return self.data
'''
