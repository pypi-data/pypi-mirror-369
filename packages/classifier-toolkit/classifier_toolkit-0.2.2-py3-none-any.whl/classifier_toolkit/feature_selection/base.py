from abc import ABC, abstractmethod
from typing import List, Literal, Optional, Union

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_selection import RFECV
from sklearn.model_selection import BaseCrossValidator, cross_val_score
from sklearn.utils import check_X_y


class BaseFeatureSelector(BaseEstimator, TransformerMixin, ABC):
    """
    Base class for feature selection methods.

    This abstract class provides the basic structure and interface for all feature selection methods.
    It implements common functionality while requiring specific methods to be implemented by subclasses.

    Parameters
    ----------
    estimator : Optional[BaseEstimator]
        The estimator to use for feature selection. Must be a scikit-learn compatible estimator.
    n_features_to_select : int, optional
        The number of features to select, by default 1.
    scoring : {'accuracy', 'f1', 'precision', 'recall', 'roc_auc', 'average_precision'}, optional
        The scoring metric to use for evaluating features, by default 'accuracy'.
    cv : Union[int, BaseCrossValidator], optional
        Cross-validation strategy. Can be an integer for k-fold cross-validation
        or a scikit-learn cross-validator object, by default 5.
    verbose : int, optional
        Controls the verbosity of the feature selection process, by default 0.

    Attributes
    ----------
    estimator : Optional[BaseEstimator]
        The fitted estimator used for feature selection.
    selected_features_ : Optional[List[str]]
        The names of the selected features after fitting.
    feature_importances_ : Optional[pd.Series]
        The importance scores for each feature after fitting.
    rfecv : Optional[RFECV]
        The RFECV object if recursive feature elimination with cross-validation is used.
    rfecv_step : int
        The step size for recursive feature elimination.
    """

    @abstractmethod
    def __init__(
        self,
        estimator: Optional[BaseEstimator],
        n_features_to_select: int = 1,
        scoring: Literal[
            "accuracy", "f1", "precision", "recall", "roc_auc", "average_precision"
        ] = "accuracy",
        cv: Union[int, BaseCrossValidator] = 5,
        verbose: int = 0,
    ) -> None:
        """
        Initialize the feature selector.

        Parameters
        ----------
        estimator : Optional[BaseEstimator]
            The estimator to use for feature selection.
        n_features_to_select : int, optional
            The number of features to select, by default 1.
        scoring : Literal["accuracy", "f1", "precision", "recall", "roc_auc"], optional
            The scoring metric to use, by default "accuracy".
        cv : Union[int, BaseCrossValidator], optional
            Number of folds to use in cross-validation, by default 5.
        """
        self.estimator: Optional[BaseEstimator] = estimator
        self.n_features_to_select = n_features_to_select
        self.scoring = scoring
        from .utils.scoring import get_scorer

        self.scorer = get_scorer(scoring)
        self.cv = cv
        self.verbose = verbose
        self.selected_features_: Optional[List[str]] = None
        self.feature_importances_: Optional[pd.Series] = None
        self.rfecv: Optional[RFECV] = None
        self.rfecv_step: int = 1

    @abstractmethod
    def fit(self, X: pd.DataFrame, y: pd.Series) -> "BaseFeatureSelector":
        """
        Fit the feature selector to the data.

        Parameters
        ----------
        X : pd.DataFrame
            The feature matrix.
        y : pd.Series
            The target variable.

        Returns
        -------
        BaseFeatureSelector
            The fitted feature selector.
        """

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Transform the data to include only selected features.

        Parameters
        ----------
        X : pd.DataFrame
            The feature matrix.

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
        if isinstance(self.selected_features_[0], str):
            return X[self.selected_features_]
        else:
            return X.loc[:, self.selected_features_]

    def fit_transform(self, X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
        """
        Fit the selector and transform the data.

        Parameters
        ----------
        X : pd.DataFrame
            The feature matrix.
        y : pd.Series
            The target variable.

        Returns
        -------
        pd.DataFrame
            The transformed data containing only the selected features.
        """
        return self.fit(X, y).transform(X)

    @abstractmethod
    def _get_score(self, X: pd.DataFrame, y: pd.Series, features: List[int]) -> float:
        """
        Evaluate the score for a subset of features.

        Parameters
        ----------
        X : pd.DataFrame
            The feature matrix.
        y : pd.Series
            The target variable.
        features : List[int]
            The indices of features to evaluate.

        Returns
        -------
        float
            The score for the given features.
        """

    @abstractmethod
    def get_feature_importances(self) -> pd.Series:
        """
        Get the importance scores for each feature.

        Returns
        -------
        pd.Series
            A series containing the importance scores for each feature.

        Raises
        ------
        FeatureSelectionError
            If the selector has not been fitted yet.
        """

    def get_support(self, indices: bool = False) -> Union[List[bool], List[int]]:
        """
        Get a mask, or integer index, of the features selected.

        Parameters
        ----------
        indices : bool, optional
            If True, returns integer indices of selected features.
            If False, returns a boolean mask, by default False.

        Returns
        -------
        Union[List[bool], List[int]]
            Either a boolean mask or integer indices indicating selected features.

        Raises
        ------
        FeatureSelectionError
            If the selector has not been fitted yet.
        ValueError
            If feature importances are not available.
        """
        if self.selected_features_ is None:
            raise FeatureSelectionError(
                "Selector has not been fitted yet. Call 'fit' first."
            )
        assert self.feature_importances_ is not None, ValueError(
            'Feature importances are not available. Call "fit" first.'
        )
        mask = [
            feature in self.selected_features_
            for feature in self.feature_importances_.index
        ]
        if indices:
            return [i for i, m in enumerate(mask) if m]
        return mask

    def _evaluate_features(
        self, X: Union[pd.DataFrame, np.ndarray], y: pd.Series
    ) -> pd.Series:
        """
        Evaluate the features using cross-validation.

        Args:
            X (Union[pd.DataFrame, np.ndarray]): The input features.
            y (pd.Series): The target variable.

        Returns:
            pd.Series: A series containing the mean cross-validation score for each feature.
        """
        if self.estimator is None:
            raise ValueError("Estimator is not set. Please provide an estimator.")

        X, y = check_X_y(X, y, ensure_min_features=0, force_all_finite=False)

        if isinstance(X, np.ndarray):
            X = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(X.shape[1])])

        scores = []
        feature_names = X.columns

        for feature in feature_names:
            X_feature = X[[feature]]
            try:
                feature_scores = cross_val_score(
                    self.estimator,
                    X_feature,
                    y,
                    scoring=self.scorer,
                    cv=self.cv,
                    n_jobs=-1,
                    error_score="raise",
                )
                mean_score = np.mean(feature_scores)
            except Exception as e:
                if self.verbose > 0:
                    print(f"Error evaluating feature {feature}: {e!s}")
                mean_score = np.nan

            scores.append(mean_score)

        return pd.Series(scores, index=feature_names, name="Feature Scores")

    def fit_rfecv(
        self, X: pd.DataFrame, y: pd.Series, **rfecv_params
    ) -> "BaseFeatureSelector":
        """
        Fit the selector using RFECV.

        Parameters
        ----------
        X : pd.DataFrame
            The input features.
        y : pd.Series
            The target variable.
        rfecv_params : dict, optional
            Additional parameters to pass to RFECV.
            See :class:`sklearn.feature_selection.RFECV` for details.

        Returns
        -------
        self : BaseFeatureSelector
            The fitted selector.
        """
        if self.estimator is None:
            raise ValueError("Estimator is not set. Please provide an estimator.")

        self.rfecv = RFECV(
            estimator=self.estimator,
            step=self.rfecv_step,
            cv=self.cv,
            scoring=self.scoring,
            n_jobs=-1,
            verbose=self.verbose,
            **rfecv_params,
        )

        self.rfecv.fit(X, y)
        self.selected_features_ = X.columns[self.rfecv.support_].tolist()
        self.feature_importances_ = pd.Series(self.rfecv.ranking_, index=X.columns)

        return self


class FeatureSelectionError(Exception):
    """Base exception for feature selection errors."""
