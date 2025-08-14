from typing import List, Literal, Optional

import numpy as np
import pandas as pd
from bayes_opt import BayesianOptimization
from bayes_opt.event import Events
from sklearn.base import BaseEstimator
from sklearn.model_selection import cross_validate
from tqdm import tqdm

from classifier_toolkit.feature_selection.base import BaseFeatureSelector


class BayesianFeatureSelector(BaseFeatureSelector):
    """
    Feature selector using Bayesian Optimization.

    This class implements feature selection using Bayesian Optimization to find
    the optimal subset of features.

    Parameters
    ----------
    estimator : BaseEstimator
        The estimator to use for feature evaluation.
    n_features_to_select : int
        Number of features to select.
    scoring : {'accuracy', 'f1', 'precision', 'recall', 'roc_auc', 'average_precision'}, optional
        Scoring metric to use, by default 'accuracy'.
    cv : int, optional
        Number of cross-validation folds, by default 5.
    max_trials : int, optional
        Maximum number of trials for Bayesian optimization, by default 100.
    init_points_ratio : float, optional
        Ratio of initial points for Bayesian optimization, by default 0.2.
    max_init_points : int, optional
        Maximum number of initial points for Bayesian optimization, by default 10.
    verbose : int, optional
        Verbosity level, by default 0.
    random_state : int, optional
        Random state for reproducibility, by default 42.

    Attributes
    ----------
    feature_importances_ : pd.Series
        Feature importance scores after fitting.
    selected_features_ : List[str]
        Selected feature names after fitting.
    optimization_history_ : pd.DataFrame
        History of the optimization process.
    """

    def __init__(
        self,
        estimator: BaseEstimator,
        n_features_to_select: int = 20,
        scoring: Literal[
            "accuracy", "f1", "precision", "recall", "roc_auc", "average_precision"
        ] = "accuracy",
        cv: int = 5,
        max_trials: int = 100,
        init_points_ratio: float = 0.2,
        max_init_points: int = 10,
        random_state: int = 42,
        verbose: int = 0,
    ):
        super().__init__(
            estimator=estimator,
            n_features_to_select=n_features_to_select,
            scoring=scoring,
            cv=cv,
            verbose=verbose,
        )
        self.max_trials = max_trials
        self.init_points_ratio = init_points_ratio
        self.max_init_points = max_init_points
        self.random_state = random_state
        self.optimization_history_: Optional[pd.DataFrame] = None
        self._pbar = None

    def _progress_callback(
        self,
        *args,  # noqa: ARG002, We need to add this because of the library structure
    ):
        """Callback to update progress bar during optimization."""
        if self._pbar is not None:
            self._pbar.update(1)

    def _evaluate_features(
        self, X: pd.DataFrame, y: pd.Series, feature_mask: np.ndarray
    ) -> float:
        """
        Evaluate a specific feature combination using cross-validation.

        Parameters
        ----------
        X : pd.DataFrame
            The feature matrix.
        y : pd.Series
            The target variable.
        feature_mask : np.ndarray
            Boolean mask indicating selected features.

        Returns
        -------
        float
            Mean cross-validation score.
        """
        selected_columns = X.columns[feature_mask].tolist()
        X_selected = X[selected_columns]

        cv_results = cross_validate(
            self.estimator,  # type: ignore
            X_selected,
            y,
            cv=self.cv,
            scoring=self.scoring,
            n_jobs=-1,
        )

        return float(cv_results["test_score"].mean())

    def fit(self, X: pd.DataFrame, y: pd.Series) -> "BayesianFeatureSelector":
        """
        Fit the selector to the data using Bayesian optimization.

        Parameters
        ----------
        X : pd.DataFrame
            The feature matrix.
        y : pd.Series
            The target variable.

        Returns
        -------
        BayesianFeatureSelector
            The fitted selector.
        """
        experiment_log = []
        feature_names = X.columns.tolist()

        # Define the search space as probabilities for each feature
        bounds = {feat: (0, 1) for feat in feature_names}

        def opt_objective(**params):
            # Convert probabilities to binary feature mask
            probs = np.array([params[feat] for feat in feature_names])
            mask = np.zeros(len(probs), dtype=bool)
            top_indices = np.argsort(probs)[-self.n_features_to_select :]
            mask[top_indices] = True

            score = self._evaluate_features(X, y, mask)
            experiment_log.append((params, score))

            return score

        # Initialize optimizer
        optimizer = BayesianOptimization(
            f=opt_objective,
            pbounds=bounds,
            random_state=self.random_state,
            verbose=0,  # Set verbose to 0 since tqdm implemented
        )

        # Calculate initial points and iterations
        init_points = min(
            self.max_init_points, int(self.max_trials * self.init_points_ratio)
        )
        n_iter = self.max_trials - init_points

        # Set up progress bar if verbose
        if self.verbose:
            self._pbar = tqdm(
                total=self.max_trials,
                desc=f"Bayesian Optimization (Random: {init_points}, BO: {n_iter})",
            )
            # Only subscribe to optimization steps
            optimizer.subscribe(
                event=Events.OPTIMIZATION_STEP,
                subscriber=self,
                callback=self._progress_callback,
            )

        try:
            # Run optimization
            optimizer.maximize(
                init_points=init_points,
                n_iter=n_iter,
            )

            # Ensure progress bar is complete
            if self._pbar is not None:
                self._pbar.n = self.max_trials
                self._pbar.refresh()

        finally:
            # Clean up progress bar
            if self._pbar is not None:
                self._pbar.close()
                self._pbar = None

        # Get best feature set
        best_probs = np.array([optimizer.max["params"][feat] for feat in feature_names])  # type: ignore
        best_features = np.zeros(len(best_probs), dtype=bool)
        best_features[np.argsort(best_probs)[-self.n_features_to_select :]] = True

        # Store results
        self.selected_features_ = X.columns[best_features].tolist()

        # Create feature importances based on selection frequency
        importance_dict = {col: 0.0 for col in feature_names}
        for params, _ in experiment_log:
            probs = np.array([params[feat] for feat in feature_names])
            mask = np.zeros(len(probs), dtype=bool)
            top_indices = np.argsort(probs)[-self.n_features_to_select :]
            mask[top_indices] = True
            for col, selected in zip(feature_names, mask):
                if selected:
                    importance_dict[col] += 1

        self.feature_importances_ = pd.Series(importance_dict)
        self.feature_importances_ /= len(experiment_log)

        # Store optimization history
        history_data = []
        for params, score in experiment_log:
            history_entry = {
                "score": score,
                **params,
            }
            history_data.append(history_entry)

        self.optimization_history_ = pd.DataFrame(history_data)
        cols = ["score"] + [
            col for col in self.optimization_history_.columns if col != "score"
        ]
        self.optimization_history_ = self.optimization_history_[cols]

        return self

    def _get_score(self, X: pd.DataFrame, y: pd.Series, features: List[int]) -> float:
        """Implementation of abstract method."""
        mask = np.zeros(X.shape[1], dtype=bool)
        mask[features] = True
        return self._evaluate_features(X, y, mask)

    def get_feature_importances(self) -> pd.Series:
        """Get the importance scores for each feature."""
        if self.feature_importances_ is None:
            raise ValueError("Feature importances not available. Call fit first.")
        return self.feature_importances_

    def get_optimization_history(self) -> pd.DataFrame:
        """
        Get the history of the optimization process.

        Returns
        -------
        pd.DataFrame
            DataFrame containing the optimization history, including:
            - Feature probabilities for each trial
            - Score achieved
        """
        if self.optimization_history_ is None:
            raise ValueError("Optimization history not available. Call fit first.")
        return self.optimization_history_
