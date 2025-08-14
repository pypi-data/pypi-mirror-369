import warnings
from typing import Dict, Literal, Optional, Tuple, Union

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import BaseCrossValidator, cross_val_score
from tqdm import tqdm

from classifier_toolkit.feature_selection.base import BaseFeatureSelector


class ElasticNetLogisticSelector(BaseFeatureSelector):
    """
    Feature selector using Elastic Net regularization with Logistic Regression.

    This class implements feature selection using Elastic Net regularization, combining
    L1 and L2 penalties. It performs a grid search over different l1_ratio values to find
    the optimal feature combination.

    Parameters
    ----------
    l1_ratios : Tuple[float, ...], optional
        The l1_ratio values to try for Elastic Net, by default (0.1, 0.5, 0.7, 0.9).
    C : float, optional
        Inverse of regularization strength, by default 1.0.
    n_features_to_select : int, optional
        Number of features to select, by default 1.
    scoring : {'accuracy', 'f1', 'precision', 'recall', 'roc_auc', 'average_precision'}, optional
        Scoring metric to use, by default 'accuracy'.
    cv : Union[int, BaseCrossValidator], optional
        Cross-validation strategy, by default 5.
    verbose : int, optional
        Verbosity level, by default 0.
    max_iter : int, optional
        Maximum number of iterations for the solver, by default 500.

    Attributes
    ----------
    best_l1_ratio : Optional[float]
        The best l1_ratio found after fitting.
    best_model : Optional[LogisticRegression]
        The best model found after fitting.
    l1_ratio_scores : Dict[float, float]
        Scores for each l1_ratio tried.
    feature_importances_ : pd.Series
        Feature importance scores after fitting.
    selected_features_ : List[str]
        Selected feature names after fitting.
    """

    def __init__(
        self,
        l1_ratios: Tuple[float, ...] = (0.1, 0.5, 0.7, 0.9),
        C: float = 1.0,
        n_features_to_select: int = 1,
        scoring: Literal[
            "accuracy", "f1", "precision", "recall", "roc_auc", "average_precision"
        ] = "accuracy",
        cv: Union[int, BaseCrossValidator] = 5,
        verbose: int = 0,
        max_iter: int = 500,
    ) -> None:
        super().__init__(
            estimator=None,
            n_features_to_select=n_features_to_select,
            scoring=scoring,
            cv=cv,
            verbose=verbose,
        )

        self.l1_ratios = list(l1_ratios)
        self.C = C
        self.max_iter = max_iter
        self.best_l1_ratio: Optional[float] = None
        self.best_model: Optional[LogisticRegression] = None
        self.l1_ratio_scores: Dict[float, float] = {}

    def _get_score(self, X: pd.DataFrame, y: pd.Series, l1_ratio: float) -> float:
        """
        Calculate the cross-validation score for a given l1_ratio.

        Parameters
        ----------
        X : pd.DataFrame
            The feature matrix.
        y : pd.Series
            The target variable.
        l1_ratio : float
            The l1_ratio to use for Elastic Net.

        Returns
        -------
        float
            The mean cross-validation score.
        """
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=ConvergenceWarning)
            model = LogisticRegression(
                penalty="elasticnet",
                solver="saga",
                l1_ratio=l1_ratio,
                C=self.C,
                max_iter=self.max_iter,
                random_state=42,
            )
            scores = cross_val_score(model, X, y, cv=self.cv, scoring=self.scoring)
        return np.mean(scores)  # type: ignore

    def fit(self, X: pd.DataFrame, y: pd.Series) -> "ElasticNetLogisticSelector":
        """
        Fit the ElasticNetLogisticSelector to the data.

        This method performs a grid search over the specified l1_ratios to find
        the best combination of features.

        Parameters
        ----------
        X : pd.DataFrame
            The feature matrix.
        y : pd.Series
            The target variable.

        Returns
        -------
        ElasticNetLogisticSelector
            The fitted selector.
        """
        best_score = -np.inf
        best_features = []
        best_importances = None
        self.l1_ratio_scores = {}

        # Create a progress bar
        pbar = tqdm(self.l1_ratios, desc="Trying l1_ratios", unit="ratio")

        for l1_ratio in pbar:
            mean_score = self._get_score(X, y, l1_ratio)
            self.l1_ratio_scores[l1_ratio] = mean_score

            # Update progress bar description
            pbar.set_description(
                f"Trying l1_ratio: {l1_ratio:.3f}, Score: {mean_score:.3f}"
            )

            if mean_score > best_score:
                best_score = mean_score
                self.best_l1_ratio = l1_ratio
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=ConvergenceWarning)
                    self.best_model = LogisticRegression(
                        penalty="elasticnet",
                        solver="saga",
                        l1_ratio=l1_ratio,
                        C=self.C,
                        max_iter=self.max_iter,
                        random_state=42,
                    ).fit(X, y)

                feature_importances = np.abs(self.best_model.coef_[0])
                feature_importances_series = pd.Series(
                    feature_importances, index=X.columns
                )
                sorted_features = feature_importances_series.sort_values(
                    ascending=False
                )

                best_features = sorted_features.index[
                    : self.n_features_to_select
                ].tolist()
                best_importances = sorted_features

        pbar.close()

        self.selected_features_ = best_features
        self.feature_importances_ = best_importances

        return self

    def get_feature_importances(self) -> pd.Series:
        """
        Get the feature importances from the best model.

        Returns
        -------
        pd.Series
            A series containing the feature importances.

        Raises
        ------
        ValueError
            If the model hasn't been fitted yet.
        """
        if self.feature_importances_ is None:
            raise ValueError("Feature importances are not available. Call 'fit' first.")
        return self.feature_importances_

    def get_best_l1_ratio(self) -> Optional[float]:
        """
        Get the best l1_ratio found during fitting.

        Returns
        -------
        Optional[float]
            The best l1_ratio value.

        Raises
        ------
        ValueError
            If the model hasn't been fitted yet.
        """
        if self.best_l1_ratio is None:
            raise ValueError("Model has not been fitted yet. Call 'fit' first.")
        return self.best_l1_ratio

    def get_l1_ratio_scores(self) -> Dict[float, float]:
        """
        Get the scores for each l1_ratio tried during fitting.

        Returns
        -------
        Dict[float, float]
            A dictionary mapping l1_ratio values to their corresponding scores.

        Raises
        ------
        ValueError
            If the model hasn't been fitted yet.
        """
        if not self.l1_ratio_scores:
            raise ValueError("Model has not been fitted yet. Call 'fit' first.")
        return self.l1_ratio_scores

    def plot_l1_ratio_scores(self):
        """
        Plot the scores for each l1_ratio tried during fitting.

        Creates an interactive plot using Plotly to visualize how model performance
        changes with different l1_ratio values.

        Raises
        ------
        ValueError
            If the model hasn't been fitted yet.
        """
        l1_ratio_scores = self.get_l1_ratio_scores()
        fig = make_subplots(rows=1, cols=1)

        fig.add_trace(
            go.Scatter(
                x=list(l1_ratio_scores.keys()),
                y=list(l1_ratio_scores.values()),
                mode="lines+markers",
                name="Score",
                line={"color": "royalblue"},
                marker={"size": 8},
            )
        )

        fig.update_layout(
            title="Performance across different l1_ratios",
            xaxis_title="l1_ratio",
            yaxis_title="Score",
            height=600,
            width=1000,
            showlegend=False,
            hovermode="x",
        )

        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="LightGrey")
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="LightGrey")

        fig.show()

    def summarize_performance(self):
        """
        Print a summary of the feature selection performance.

        Displays the selected features, best l1_ratio, best score achieved,
        and feature importances.

        Raises
        ------
        ValueError
            If the model hasn't been fitted yet.
        """
        print(f"Selected features: {self.selected_features_}")
        best_l1_ratio = self.get_best_l1_ratio()
        best_score = max(self.get_l1_ratio_scores().values())

        print(f"Best l1_ratio: {best_l1_ratio}")
        print(f"Best {self.scoring} score: {best_score}")
        print("Feature importances:")
        print(self.get_feature_importances())
