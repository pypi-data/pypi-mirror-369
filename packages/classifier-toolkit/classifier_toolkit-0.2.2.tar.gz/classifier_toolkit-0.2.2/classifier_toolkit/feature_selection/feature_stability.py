import math
import random
from typing import Literal

import pandas as pd
from tqdm import tqdm

from classifier_toolkit.feature_selection.utils.data_handling import (
    prepare_data_for_modeling,
)
from classifier_toolkit.feature_selection.wrapper_methods.rfe import RFESelector


class FeatureStability:
    """
    A class for assessing feature stability through various resampling methods.

    This class implements feature stability assessment using different resampling techniques
    like jackknife, and evaluates feature importance across different subsets of data.

    Parameters
    ----------
    X : pd.DataFrame
        The feature matrix.
    y : pd.Series
        The target variable.
    target_col : str
        Name of the target column.
    model_params : dict
        Parameters for the model to be used.
    method_params : dict
        Parameters for the resampling method.
    model : {'xgboost', 'lightgbm', 'catboost', 'random_forest'}, optional
        The model to use for feature selection, by default 'xgboost'.
    method : str, optional
        The resampling method to use, by default 'jackknife'.
    seed : int, optional
        Random seed for reproducibility, by default 42.
    scoring : {'accuracy', 'f1', 'precision', 'recall', 'roc_auc', 'average_precision'}, optional
        Scoring metric to use, by default 'average_precision'.
    cutoff_ratio : float, optional
        Ratio of features to select in each iteration, by default 0.33.

    Attributes
    ----------
    importances : list
        List of feature importance DataFrames from each iteration.
    models : list
        List of fitted RFE models from each iteration.
    """

    def __init__(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        target_col: str,
        model_params: dict,
        method_params: dict,
        model: Literal["xgboost", "lightgbm", "catboost", "random_forest"] = "xgboost",
        method: str = "jackknife",
        seed: int = 42,
        scoring: Literal[
            "accuracy", "f1", "precision", "recall", "roc_auc", "average_precision"
        ] = "average_precision",
        cutoff_ratio: float = 0.33,
    ):
        self.X = X
        self.y = y
        self.model = model
        self.target_col = target_col
        self.model_params = model_params
        self.method = method
        self.method_params = method_params
        self.seed = seed
        self.scoring = scoring
        self.cutoff_ratio = cutoff_ratio

    def jackknife(self, **kwargs):
        """
        Implementation of the Delete-d Jackknife method for feature selection.

        This method creates n_sets from the original dataset by removing d random samples.
        Theoretically, it can create d chooses n_sets different datasets.

        Parameters
        ----------
        **kwargs : dict
            Must include:
                d : int
                    Number of samples to be removed
                n_sets : int
                    Number of sets to be created

        Returns
        -------
        dict
            Dictionary of boolean masks for each jackknife sample

        Raises
        ------
        ValueError
            If d or n_sets are not provided
            If d is larger than the number of samples
            If n_sets is larger than possible combinations
        """

        d = kwargs.get("d")
        n_sets = kwargs.get("n_sets")

        if d is None or n_sets is None:
            raise ValueError("d and n_sets should be provided.")

        indices = {}

        if d > len(self.X):
            raise ValueError(
                "d should be smaller than number of samples in the dataframe."
            )
        elif n_sets > math.comb(len(self.X), d):
            raise ValueError(
                "n_sets should be smaller than d chooses n_sets, which is math.comb(len(X), d)."
            )
        else:
            random.seed(self.seed)
            theta = len(self.X) - d
            # Use range(len(X)) instead of X.index
            positions = list(range(len(self.X) - 1))

            for i in range(n_sets):
                # Sample positions instead of index values
                sampled_positions = random.sample(positions, theta)
                # Convert positions to boolean mask
                mask = pd.Series(False, index=range(len(self.X)))
                mask[sampled_positions] = True
                indices[i] = mask

            return indices

    def fit(self):
        """
        Fit the feature stability model using the specified resampling method.

        This method performs feature selection on multiple subsets of the data
        to assess feature stability. For each subset:

        1. Creates a mask using the specified resampling method
        2. Selects data using the mask
        3. Prepares the data for modeling
        4. Fits an RFE selector
        5. Stores feature importances and the fitted model

        Returns
        -------
        FeatureStability
            The fitted FeatureStability instance

        Raises
        ------
        ValueError
            If the specified resampling method is not implemented
        """
        self.importances = []
        self.models = []

        if self.method == "jackknife":
            indices = self.jackknife(**self.method_params)
        else:
            raise ValueError("Method not implemented.")

        for i in tqdm(range(len(indices)), desc="Processing indices", unit="index"):
            rfe_selector = RFESelector(
                estimator_name=self.model,  # type: ignore
                n_features_to_select=-1,
                scoring=self.scoring,  # type: ignore
                cv=5,
                verbose=1,
                model_params=self.model_params,
                random_state=self.seed,
                cross_validate_prauc=True,
            )

            print("Preparing the data for modeling...")

            # Use boolean mask to select rows
            mask = indices[i]
            current_X = self.X[mask]
            current_y = self.y[mask]

            current_X = current_X.reset_index(drop=True)
            current_y = current_y.reset_index(drop=True)

            X_encoded, y_encoded, cv_folds = prepare_data_for_modeling(
                current_X,
                current_y,
                y_name=self.target_col,
                n_splits=5,
                test_size=0.2,
                random_state=self.seed,
                encoding_method="distribution",
                verbose=False,
            )

            print("Fitting the model...")
            rfe_selector.fit(X_encoded, y_encoded, cv_folds)

            feature_importances = rfe_selector.get_feature_importances()

            self.importances.append(feature_importances)

            self.models.append(rfe_selector)

    def calculate_stability(self):
        """
        Calculate the stability scores for features across all iterations.

        This method analyzes how consistently features are selected across different
        subsets of the data. It:

        1. Determines the cutoff point based on cutoff_ratio
        2. Identifies selected features in each iteration
        3. Calculates how many times each feature was selected

        Returns
        -------
        pd.DataFrame
            DataFrame containing feature names and their selection frequency,
            sorted by frequency in descending order
        """
        cutoff = int(len(self.importances[0]) * self.cutoff_ratio)

        selected = {}

        for i in range(len(self.importances)):
            selected[i] = list(self.importances[i][:cutoff].index)

        selected_frequency = dict.fromkeys(list(self.X.columns), 0)

        for i in range(len(selected)):
            for col in selected[i]:
                selected_frequency[col] += 1

        df = pd.DataFrame(
            selected_frequency.items(), columns=["Feature Name", "Times Selected"]
        )
        df = df.sort_values(by="Times Selected", ascending=False)
        return df
