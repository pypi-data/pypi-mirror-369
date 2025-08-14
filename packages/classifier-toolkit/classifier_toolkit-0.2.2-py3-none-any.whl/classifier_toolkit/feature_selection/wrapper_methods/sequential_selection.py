from typing import Dict, List, Literal, Optional, Set, Tuple, Union

import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import get_scorer as sklearn_get_scorer
from sklearn.model_selection import cross_val_score, train_test_split
from xgboost import XGBClassifier

from classifier_toolkit.feature_selection.base import (
    BaseFeatureSelector,
    FeatureSelectionError,
)
from classifier_toolkit.feature_selection.utils.plottings import (
    plot_exhaustive_search_results,
)
from classifier_toolkit.feature_selection.utils.scoring import get_scorer  # Add this


class SequentialSelector(BaseFeatureSelector):
    """
    Sequential feature selector using various estimators.

    This class implements forward, backward, and bidirectional feature selection
    using different estimators. Features are selected sequentially based on their
    performance with the chosen estimator.

    Parameters
    ----------
    estimator_params : Optional[Dict[str, float]]
        Parameters for the estimator. If None, default parameters will be used.
    estimator_name : {'random_forest', 'lightgbm', 'xgboost', 'logistic_regression'}, optional
        The name of the estimator to use, by default 'random_forest'.
    n_features_to_select : int, optional
        The number of features to select, by default 1.
    scoring : {'accuracy', 'f1', 'precision', 'recall', 'roc_auc', 'average_precision'}, optional
        The scoring metric to use, by default 'roc_auc'.
    cv : int, optional
        The number of cross-validation folds, by default 5.
    method : {'forward', 'backward', 'bidirectional'}, optional
        The selection method to use, by default 'forward'.
    verbose : int, optional
        Verbosity level, by default 0.
    tolerance : float, optional
        Tolerance for early stopping, by default 1e-4.
    n_jobs : int, optional
        The number of jobs to run in parallel, by default -1.
    early_stopping_rounds : int, optional
        The number of rounds for early stopping, by default 5.
    random_state : int, optional
        Random state for reproducibility, by default 42.

    Attributes
    ----------
    estimator : object
        The fitted estimator used for feature selection.
    feature_scores_ : Dict[str, float]
        Scores for each feature after fitting.
    selected_features_ : List[str]
        The names of selected features after fitting.
    feature_importances_ : pd.Series
        The importance scores for each feature after fitting.
    """

    def __init__(
        self,
        estimator_params: Optional[Dict[str, Union[int, float, str]]],
        estimator_name: Literal[
            "random_forest", "lightgbm", "xgboost", "logistic_regression"
        ] = "random_forest",
        n_features_to_select: int = 1,
        scoring: Literal[
            "accuracy", "f1", "precision", "recall", "roc_auc", "average_precision"
        ] = "roc_auc",
        cv: int = 5,
        method: Literal["forward", "backward", "bidirectional"] = "forward",
        verbose: int = 0,
        tolerance: float = 1e-4,
        n_jobs: int = -1,
        early_stopping_rounds: int = 5,
        random_state: int = 42,
    ) -> None:
        super().__init__(
            estimator=None,
            n_features_to_select=n_features_to_select,
            scoring=scoring,
            cv=cv,
            verbose=verbose,
        )
        self.estimator_params = estimator_params or {}
        self.method = method
        self.feature_scores_: Dict[str, float] = {}
        self.tolerance = tolerance
        self.n_jobs = n_jobs
        self.early_stopping_rounds = early_stopping_rounds
        self.estimator_name = estimator_name
        self.random_state = random_state
        self.estimator = self.initialize_estimator()  # type: ignore

        # Update the scoring handling
        try:
            self.scorer = get_scorer(scoring)
        except ValueError:
            # Fallback to sklearn's get_scorer for backward compatibility
            self.scorer = sklearn_get_scorer(scoring)

    def initialize_estimator(self):
        """
        Initialize the estimator based on the provided name and parameters.

        Returns
        -------
        object
            The initialized estimator.

        Raises
        ------
        ValueError
            If the estimator name is not recognized.
        """
        if self.estimator_name == "random_forest":
            return RandomForestClassifier(**self.estimator_params)  # type: ignore
        elif self.estimator_name == "lightgbm":
            return LGBMClassifier(**self.estimator_params)  # type: ignore
        elif self.estimator_name == "xgboost":
            return XGBClassifier(**self.estimator_params)
        elif self.estimator_name == "logistic_regression":
            return LogisticRegression(**self.estimator_params)  # type: ignore
        else:
            raise ValueError(
                "Estimator must be 'random_forest', 'lightgbm', 'xgboost', or 'logistic_regression'"
            )

    def fit(self, X: pd.DataFrame, y: pd.Series) -> "SequentialSelector":
        """
        Fit the SequentialSelector to the data.

        Parameters
        ----------
        X : pd.DataFrame
            The input features.
        y : pd.Series
            The target variable.

        Returns
        -------
        SequentialSelector
            The fitted SequentialSelector instance.

        Raises
        ------
        ValueError
            If the selection method is not recognized.
        """
        self.feature_names_ = X.columns.tolist()

        if self.method == "forward":
            self._forward_selection(X, y)
        elif self.method == "backward":
            self._backward_selection(X, y)
        elif self.method == "bidirectional":
            self._bidirectional_selection(X, y)
        else:
            raise ValueError("Method must be 'forward', 'backward', or 'bidirectional'")

        # Ensure feature_importances_ is set
        if self.feature_importances_ is None:
            self.feature_importances_ = pd.Series(0, index=self.feature_names_)
            for feature in self.selected_features_:  # type: ignore
                self.feature_importances_[feature] = (
                    1  # Set a default importance for selected features
                )

        return self

    def _get_score(self, X: pd.DataFrame, y: pd.Series, features: List[int]) -> float:
        """
        Calculate the cross-validation score for a subset of features.

        Parameters
        ----------
        X : pd.DataFrame
            The input features.
        y : pd.Series
            The target variable.
        features : List[int]
            The indices of features to use.

        Returns
        -------
        float
            The mean cross-validation score.

        Raises
        ------
        ValueError
            If the estimator is not set.
        """
        X_subset = X.iloc[:, features]

        if self.estimator is not None:
            scores = cross_val_score(
                self.estimator, X_subset, y, scoring=self.scorer, cv=self.cv, n_jobs=-1
            )
            return float(np.mean(scores))
        else:
            raise ValueError("Estimator is not set.")

    def _get_score_fast(self, X_train, X_val, y_train, y_val, features: List[int]):
        """
        Calculate the score for a subset of features using a fast method.

        This method fits the model on training data and evaluates on validation data,
        which is faster than cross-validation but may be less robust.

        Parameters
        ----------
        X_train : pd.DataFrame
            The training input features.
        X_val : pd.DataFrame
            The validation input features.
        y_train : pd.Series
            The training target variable.
        y_val : pd.Series
            The validation target variable.
        features : List[int]
            The indices of features to evaluate.

        Returns
        -------
        float
            The score for the given features.

        Raises
        ------
        ValueError
            If the estimator is not set.
        """
        X_train_subset = X_train.iloc[:, features]
        X_val_subset = X_val.iloc[:, features]

        if self.estimator is not None:
            self.estimator.fit(X_train_subset, y_train)  # type: ignore
            return self.scorer(self.estimator, X_val_subset, y_val)
        else:
            raise ValueError("Estimator is not set.")

    def _forward_selection(self, X: pd.DataFrame, y: pd.Series) -> None:
        """
        Perform forward feature selection.

        Features are added one at a time, selecting the feature that gives the best
        performance when added to the current set of features.

        Parameters
        ----------
        X : pd.DataFrame
            The input features.
        y : pd.Series
            The target variable.
        """
        selected: List[int] = []
        remaining = list(range(X.shape[1]))
        feature_scores: Dict[int, float] = {}

        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=self.random_state
        )

        max_features = (
            self.n_features_to_select
            if self.n_features_to_select is not None
            else X.shape[1]
        )

        while len(selected) < max_features:
            scores = []
            for feature in remaining:
                temp_selected = [*selected, feature]
                score = self._get_score_fast(
                    X_train, X_val, y_train, y_val, temp_selected
                )
                scores.append((score, feature))

            best_score, best_feature = max(scores)
            selected.append(best_feature)
            remaining.remove(best_feature)
            feature_scores[best_feature] = best_score

            print(
                f"Selected feature: {X.columns[best_feature]}, Score: {best_score:.6f}"
            )

            if self.n_features_to_select is None and len(selected) == X.shape[1]:
                break

        self.selected_features_ = [X.columns[i] for i in selected]
        self.feature_scores_ = {X.columns[k]: v for k, v in feature_scores.items()}

        # At the end of the method, update feature_importances_
        self.feature_importances_ = pd.Series(self.feature_scores_)

    def _backward_selection(self, X: pd.DataFrame, y: pd.Series) -> None:
        """
        Perform backward feature selection.

        Features are removed one at a time, removing the feature that results in
        the smallest decrease in performance.

        Parameters
        ----------
        X : pd.DataFrame
            The input features.
        y : pd.Series
            The target variable.
        """
        selected = list(range(X.shape[1]))
        feature_scores: Dict[str, float] = {
            X.columns[i]: 0.0 for i in range(X.shape[1])
        }

        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=self.random_state
        )

        min_features = (
            self.n_features_to_select if self.n_features_to_select is not None else 1
        )

        while len(selected) > min_features:
            scores = []
            for feature in selected:
                temp_selected = [f for f in selected if f != feature]
                score = self._get_score_fast(
                    X_train, X_val, y_train, y_val, temp_selected
                )
                scores.append((score, feature))

            best_score, worst_feature = max(scores)
            selected.remove(worst_feature)
            feature_scores[X.columns[worst_feature]] = best_score

            print(
                f"Removed feature: {X.columns[worst_feature]}, Score: {best_score:.6f}"
            )

            if self.n_features_to_select is None and len(selected) == 1:
                break

        # Calculate importance for selected features
        final_score = self._get_score_fast(X_train, X_val, y_train, y_val, selected)
        for feature in selected:
            feature_scores[X.columns[feature]] = final_score

        self.selected_features_ = [X.columns[i] for i in selected]
        self.feature_importances_ = pd.Series(feature_scores)

    def _bidirectional_selection(self, X: pd.DataFrame, y: pd.Series) -> None:
        """
        Perform bidirectional feature selection.

        Features can be either added or removed at each step, choosing the action
        that results in the best performance.

        Parameters
        ----------
        X : pd.DataFrame
            The input features.
        y : pd.Series
            The target variable.
        """
        selected: List[int] = []
        remaining: List[int] = list(range(X.shape[1]))
        feature_scores: Dict[int, List[float]] = {
            feature: [] for feature in range(X.shape[1])
        }
        recently_added: Set[int] = set()
        recently_removed: Set[int] = set()

        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=self.random_state
        )

        # Start with the best single feature
        initial_scores = [
            (self._get_score_fast(X_train, X_val, y_train, y_val, [f]), f)
            for f in remaining
        ]
        best_score, best_feature = max(initial_scores)
        selected.append(best_feature)
        remaining.remove(best_feature)
        feature_scores[best_feature].append(best_score)
        recently_added.add(best_feature)

        print(f"Initial feature: {X.columns[best_feature]}, Score: {best_score:.6f}")

        max_iterations = (
            X.shape[1] * 2
            if self.n_features_to_select is None
            else self.n_features_to_select * 2
        )
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            # Forward step
            forward_scores = [
                (
                    self._get_score_fast(
                        X_train,
                        X_val,
                        y_train,
                        y_val,
                        [*selected, f],
                    ),
                    f,
                )
                for f in remaining
                if f not in recently_removed
            ]
            best_forward_score, best_forward_feature = (
                max(forward_scores) if forward_scores else (-np.inf, None)
            )

            # Backward step (if there's more than one feature)
            backward_scores = []
            if len(selected) > 1:
                backward_scores = [
                    (
                        self._get_score_fast(
                            X_train,
                            X_val,
                            y_train,
                            y_val,
                            [f for f in selected if f != feat],
                        ),
                        feat,
                    )
                    for feat in selected
                    if feat not in recently_added
                ]
            best_backward_score, best_backward_feature = (
                max(backward_scores) if backward_scores else (-np.inf, None)
            )

            # Update feature scores
            for score, feature in forward_scores:
                feature_scores[feature].append(score)
            for score, feature in backward_scores:
                feature_scores[feature].append(score)

            # Decide whether to add or remove a feature
            if (
                best_forward_score > best_backward_score
                and best_forward_feature is not None
            ):
                selected.append(best_forward_feature)
                remaining.remove(best_forward_feature)
                recently_added.add(best_forward_feature)
                recently_removed.clear()
                print(
                    f"Added feature: {X.columns[best_forward_feature]}, Score: {best_forward_score:.6f}"
                )
            elif best_backward_feature is not None:
                selected.remove(best_backward_feature)
                remaining.append(best_backward_feature)
                recently_removed.add(best_backward_feature)
                recently_added.clear()
                print(
                    f"Removed feature: {X.columns[best_backward_feature]}, Score: {best_backward_score:.6f}"
                )
            else:
                print("No improvement possible. Stopping.")
                break

            # Clear recent sets after a few iterations to allow reconsideration
            if len(selected) % 5 == 0:
                recently_added.clear()
                recently_removed.clear()

            print(f"Iteration {iteration}, Selected features: {len(selected)}")

            # Check if we've reached the desired number of features
            if (
                self.n_features_to_select is not None
                and len(selected) == self.n_features_to_select
            ):
                print(
                    f"Reached desired number of features ({self.n_features_to_select}). Stopping."
                )
                break

            # Check if we've reached the maximum number of iterations
            if iteration >= max_iterations:
                print(
                    f"Reached maximum number of iterations ({max_iterations}). Stopping."
                )
                break

        self.selected_features_ = [
            X.columns[i] for i in selected[: self.n_features_to_select]
        ]

        # Calculate average scores for all features
        self.feature_scores_ = {}
        for feature_idx, scores in feature_scores.items():
            feature_name = X.columns[feature_idx]
            self.feature_scores_[feature_name] = (
                float(np.mean(scores)) if scores else 0.0
            )

        print("\nFeature selection completed.")
        print(f"Total iterations: {iteration}")
        print(f"Selected features: {len(self.selected_features_)}")
        print("Feature importances (average scores):")
        for feature, score in sorted(
            self.feature_scores_.items(), key=lambda x: x[1], reverse=True
        ):
            print(f"{feature}: {score:.6f}")

        # Update feature_importances_
        self.feature_importances_ = pd.Series(self.feature_scores_)

    def get_feature_importances(self) -> pd.Series:
        """
        Get the feature importances (scores) from the fitted model.

        Returns
        -------
        pd.Series
            The feature importances.

        Raises
        ------
        FeatureSelectionError
            If the selector has not been fitted yet.
        """
        if self.feature_importances_ is None:
            raise FeatureSelectionError(
                "Selector has not been fitted yet. Call 'fit' first."
            )

        return self.feature_importances_

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Transform the input data by selecting the chosen features.

        Parameters
        ----------
        X : pd.DataFrame
            The input features.

        Returns
        -------
        pd.DataFrame
            The transformed data containing only the selected features.

        Raises
        ------
        FeatureSelectionError
            If the selector has not been fitted yet.
        """
        if self.selected_features_ is None:
            raise FeatureSelectionError(
                "Selector has not been fitted yet. Call 'fit' first."
            )
        return X[self.selected_features_]

    def print_feature_importances(self):
        """
        Print the feature importances (scores) in descending order.

        Raises
        ------
        FeatureSelectionError
            If feature importances are not available (i.e., fit hasn't been called).
        """
        if self.feature_importances_ is None:
            raise FeatureSelectionError(
                "Feature importances are not available. Call 'fit' first."
            )

        sorted_importances = sorted(
            zip(self.feature_importances_.index, self.feature_importances_),
            key=lambda x: x[1],
            reverse=True,
        )

        print("Feature importances (in descending order):")
        for feature, importance in sorted_importances:
            print(f"('{feature}', {importance:.6f})")

    def exhaustive_search(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        max_features: Optional[int] = None,
        static: bool = False,
    ) -> Tuple[List[str], float]:
        """
        Perform an exhaustive search for the best number of features using the specified method.

        Parameters
        ----------
        X : pd.DataFrame
            The input features.
        y : pd.Series
            The target variable.
        max_features : Optional[int], default None
            The maximum number of features to consider. If None, all features will be considered.
        static : bool, default False
            If True, there will also be a static (not interactive) plot, default is False.

        Returns
        -------
        Tuple[List[str], float]
            A tuple containing the list of best features and the best score.
        """
        if max_features is None:
            max_features = X.shape[1]
        else:
            max_features = min(max_features, X.shape[1])

        best_features_list = []
        scores = []

        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=self.random_state
        )

        original_method = self.method
        original_n_features = self.n_features_to_select

        try:
            if self.method == "backward":
                # For backward selection, start with all features and remove one by one
                current_features = list(X.columns)
                for n_features in range(
                    X.shape[1], max(1, X.shape[1] - max_features), -1
                ):
                    self.n_features_to_select = n_features - 1
                    self.fit(X_train[current_features], y_train)

                    selected_features = self.selected_features_
                    score = self._get_score_fast(
                        X_train[selected_features],
                        X_val[selected_features],
                        y_train,
                        y_val,
                        list(range(len(selected_features))),  # type: ignore
                    )

                    best_features_list.append(selected_features)
                    scores.append(score)
                    current_features = selected_features

                    print(
                        f"Number of features: {len(selected_features)}, Test Score: {score:.6f}"  # type: ignore
                    )
            else:
                # Forward and bidirectional selection
                for n_features in range(1, max_features + 1):
                    self.n_features_to_select = n_features
                    self.fit(X_train, y_train)

                    selected_features = self.selected_features_
                    score = self._get_score_fast(
                        X_train[selected_features],
                        X_val[selected_features],
                        y_train,
                        y_val,
                        list(range(len(selected_features))),  # type: ignore
                    )

                    best_features_list.append(selected_features)
                    scores.append(score)

                    print(f"Number of features: {n_features}, Test Score: {score:.6f}")

            best_index = np.argmax(scores)
            best_features = best_features_list[best_index]
            best_score = scores[best_index]

            # Plot the results
            plot_exhaustive_search_results(best_features_list, scores, static=static)

            return best_features, best_score
        finally:
            # Restore original method and n_features_to_select
            self.method = original_method
            self.n_features_to_select = original_n_features
