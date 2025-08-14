from abc import ABC, abstractmethod
from typing import Literal, Optional, Union

import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.model_selection import BaseCrossValidator

from classifier_toolkit.feature_selection.utils.scoring import get_scorer


class BaseModel(BaseEstimator, TransformerMixin, ABC):
    """
    Base class for model fitting for the hyperparameter tuning.

    This abstract class provides the basic structure and interface for all machine learning algorithms that
    will be used for the hyperparameter tuning. It implements common functionality while requiring specific
    methods to be implemented by subclasses.

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
        self.scoring = scoring

        self.scorer = get_scorer(scoring)
        self.cv = cv
        self.verbose = verbose

    @abstractmethod
    def fit(self, X: pd.DataFrame, y: pd.Series) -> "BaseModel":
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

    @abstractmethod
    def evaluate(self, X: pd.DataFrame, y: pd.Series) -> float:
        """
        Evaluate the model based on the defined metric.

        Parameters
        ----------
        X : pd.DataFrame
            The feature matrix.
        y : pd.Series
            The target variable.

        Returns
        -------
        float
            The score.
        """
