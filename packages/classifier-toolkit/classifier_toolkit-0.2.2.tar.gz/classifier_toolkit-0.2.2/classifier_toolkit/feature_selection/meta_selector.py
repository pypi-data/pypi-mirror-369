from typing import Dict, List, Literal, Optional, Tuple

import numpy as np
import pandas as pd

# Optional progress bar dependency. Fall back to a no-op if tqdm is unavailable.
try:
    from tqdm import tqdm  # type: ignore
except Exception:  # pragma: no cover - fallback only used in limited envs

    class tqdm:  # type: ignore
        def __init__(self, total=None, desc=None):
            """No-op progress bar placeholder."""
            self.total = total
            self.desc = desc

        def update(self, _):
            """No-op update."""
            return None

        def set_description(self, *_args, **_kwargs) -> None:
            """No-op description setter."""
            return None

        def close(self):
            """No-op close."""
            return None


from classifier_toolkit.feature_selection.base import (
    BaseFeatureSelector,
    FeatureSelectionError,
)
from classifier_toolkit.feature_selection.embedded_methods.elastic_net import (
    ElasticNetLogisticSelector,
)
from classifier_toolkit.feature_selection.wrapper_methods.rfe import (
    RFESelector,
)
from classifier_toolkit.feature_selection.wrapper_methods.rfe_catboost import (
    RFECatBoostSelector,
)
from classifier_toolkit.feature_selection.wrapper_methods.sequential_selection import (
    SequentialSelector,
)


class MetaSelector(BaseFeatureSelector):
    """
    Meta-selector combining multiple feature selection methods.

    This class implements ensemble feature selection by combining multiple methods
    using weighted voting.

    Parameters
    ----------
    model_params : List[Dict]
        Parameters for each base model.
    rfe_params : Dict
        Parameters for RFE selector.
    rfe_catboost_params : Dict
        Parameters for RFECatBoost selector.
    sequential_params : Dict
        Parameters for Sequential selector.
    elastic_net_params : Dict
        Parameters for ElasticNet selector.
    n_features_to_select : int
        Number of features to select.
    methods : Optional[List[BaseFeatureSelector]], optional
        List of feature selection methods to use, by default None.
    method_weights : Optional[Tuple[float, ...]], optional
        Weights for each method, by default None.
    voting : {'majority', 'union', 'intersection'}, optional
        Voting strategy to use, by default 'majority'.
    feature_multiplier : float, optional
        Multiplier for number of features in union/intersection voting, by default 1.5.
    scoring : {'accuracy', 'f1', 'precision', 'recall', 'roc_auc', 'average_precision'}, optional
        Scoring metric to use, by default 'accuracy'.
    cv : int, optional
        Number of cross-validation folds, by default 5.
    verbose : int, optional
        Verbosity level, by default 1.

    Attributes
    ----------
    methods : List[BaseFeatureSelector]
        List of feature selection methods.
    method_weights : np.ndarray
        Weights for each method.
    feature_importances_ : pd.Series
        Combined feature importance scores.
    selected_features_ : List[str]
        Selected feature names after voting.
    """

    def __init__(
        self,
        model_params: List[Dict],
        rfe_params: Dict,
        rfe_catboost_params: Dict,
        sequential_params: Dict,
        elastic_net_params: Dict,
        n_features_to_select: int,
        methods: Optional[List[BaseFeatureSelector]] = None,
        method_weights: Optional[Tuple[float, ...]] = None,
        voting: Literal["majority", "union", "intersection"] = "majority",
        feature_multiplier: float = 1.5,
        scoring: Literal[
            "accuracy", "f1", "precision", "recall", "roc_auc", "average_precision"
        ] = "accuracy",
        cv: int = 5,
        verbose: int = 1,
    ):
        super().__init__(
            estimator=None,
            n_features_to_select=n_features_to_select,
            scoring=scoring,
            cv=cv,
            verbose=verbose,
        )

        # Set these attributes first
        self.voting = voting
        self.feature_multiplier = feature_multiplier

        # Store parameters
        self.model_params = model_params
        self.rfe_params = rfe_params
        self.rfe_catboost_params = rfe_catboost_params
        self.sequential_params = sequential_params
        self.elastic_net_params = elastic_net_params

        # Initialize default methods if none provided
        self.methods = methods or [
            RFESelector(
                **self.rfe_params,
                n_features_to_select=self._get_adjusted_n_features(),
                model_params=self.model_params[0],
            ),
            RFECatBoostSelector(
                **self.rfe_catboost_params,
                model_params=self.model_params[1],
                n_features_to_select=self._get_adjusted_n_features(),
            ),
            SequentialSelector(
                **self.sequential_params,
                estimator_params=self.model_params[2],
                n_features_to_select=self._get_adjusted_n_features(),
            ),
            ElasticNetLogisticSelector(
                **self.elastic_net_params,
                n_features_to_select=self._get_adjusted_n_features(),
            ),
        ]

        # Validate methods
        if not all(isinstance(method, BaseFeatureSelector) for method in self.methods):
            raise ValueError("All methods must be instances of BaseFeatureSelector")

        # Initialize and validate weights
        self.method_weights = self._validate_weights(method_weights)

    def _validate_weights(self, weights: Optional[Tuple[float, ...]]) -> np.ndarray:
        """Validate and normalize method weights."""
        if weights is None:
            # Equal weights if none provided
            weights = tuple([1.0 / len(self.methods)] * len(self.methods))

        if len(weights) != len(self.methods):
            raise ValueError("Number of weights must match number of methods")

        if not np.isclose(sum(weights), 1.0):
            raise ValueError("Weights must sum to 1")

        return np.array(weights)

    def _get_adjusted_n_features(self) -> int:
        """Calculate adjusted number of features based on voting strategy."""
        if self.voting in ["intersection", "union"]:
            return int(self.n_features_to_select * self.feature_multiplier)
        return self.n_features_to_select

    def fit(
        self, X: pd.DataFrame, y: pd.Series, cv_folds: Optional[Dict] = None
    ) -> "MetaSelector":
        """
        Fit the MetaSelector to the data.

        Parameters
        ----------
        X : pd.DataFrame
            The feature matrix
        y : pd.Series
            The target variable
        cv_folds : Optional[Dict]
            Cross-validation folds dictionary required for RFECatBoostSelector and RFESelector.
            If not provided, will be created automatically.
        """
        # Create cv_folds if not provided and required selectors are present
        if cv_folds is None and any(
            isinstance(m, (RFECatBoostSelector, RFESelector)) for m in self.methods
        ):
            from classifier_toolkit.feature_selection.utils.data_handling import (
                create_cross_validation_folds,
            )

            cv_folds = create_cross_validation_folds(X, y, n_splits=self.cv)

        # Create progress bar
        pbar = tqdm(total=len(self.methods), desc="Fitting methods")

        # Fit each method
        for _, method in enumerate(self.methods):
            if self.verbose:
                print(f"\nFitting {type(method).__name__}")

            # Adjust n_features_to_select for the method
            method.n_features_to_select = self._get_adjusted_n_features()

            # Handle different fitting requirements
            if isinstance(method, (RFECatBoostSelector, RFESelector)):
                if cv_folds is None:
                    raise ValueError(
                        "cv_folds is required for RFECatBoostSelector and RFESelector"
                    )
                method.fit(X, y, cv_folds)
            else:
                method.fit(X, y)

            pbar.update(1)
            pbar.set_description(f"Fitted {type(method).__name__}")

        pbar.close()

        # Combine results using weighted voting
        self._combine_results(X.columns)
        return self

    def _combine_results(self, feature_names: List[str]) -> None:
        """Combine results from all methods using weighted voting."""
        all_selected = []
        self.feature_importances_ = pd.Series(0.0, index=feature_names)

        # Collect selected features from each method
        for method, weight in zip(self.methods, self.method_weights):
            selected_features = set(method.selected_features_)
            all_selected.append(selected_features)

            # Get feature importances and ensure they're for all features
            importances = method.get_feature_importances()
            if isinstance(importances, pd.Series):
                importances = importances.values
            if len(importances.shape) > 1:
                # Take mean across dimensions if multi-dimensional
                importances = np.mean(importances, axis=1)

            # If importances are only for selected features, expand to all features
            if len(importances) != len(feature_names):
                full_importances = np.zeros(len(feature_names))
                for i, feat in enumerate(feature_names):
                    if feat in selected_features:
                        idx = list(selected_features).index(feat)
                        full_importances[i] = importances[idx]
                importances = full_importances

            # Normalize importances to [0,1] range
            if importances.max() != importances.min():
                normalized_importances = pd.Series(
                    (importances - importances.min())
                    / (importances.max() - importances.min()),
                    index=feature_names,
                )
            else:
                normalized_importances = pd.Series(importances, index=feature_names)

            # Apply method weight
            weighted_importances = normalized_importances * weight
            self.feature_importances_ += weighted_importances

        # Apply voting strategy
        if self.voting == "majority":
            self._majority_voting(all_selected)
        elif self.voting == "union":
            self._union_voting(all_selected)
        else:  # intersection
            self._intersection_voting(all_selected)

    def _majority_voting(self, all_selected: List[set]) -> None:
        """Implement majority voting with weights."""
        feature_votes = pd.Series(0.0, index=self.feature_importances_.index)

        for selected, weight in zip(all_selected, self.method_weights):
            feature_votes[list(selected)] += weight

        # Select top features based on weighted votes
        self.selected_features_ = (
            feature_votes.sort_values(ascending=False)
            .head(self.n_features_to_select)
            .index.tolist()
        )

    def _union_voting(self, all_selected: List[set]) -> None:
        """Implement union voting."""
        union_features = set().union(*all_selected)

        # Select top features based on importance scores
        self.selected_features_ = (
            self.feature_importances_[list(union_features)]
            .sort_values(ascending=False)
            .head(self.n_features_to_select)
            .index.tolist()
        )

    def _intersection_voting(self, all_selected: List[set]) -> None:
        """Implement intersection voting."""
        intersection_features = set.intersection(*all_selected)

        if len(intersection_features) < self.n_features_to_select and self.verbose:
            print(
                f"Warning: Intersection yielded only {len(intersection_features)} features, "
                f"less than the requested {self.n_features_to_select}"
            )

        self.selected_features_ = list(intersection_features)

    def get_feature_importances(self) -> pd.Series:
        """Get the combined feature importances."""
        if self.feature_importances_ is None:
            raise FeatureSelectionError("Call fit first")
        return self.feature_importances_

    def _get_score(self, X: pd.DataFrame, y: pd.Series, features: List[int]) -> float:
        raise NotImplementedError

    def get_method_specific_results(self) -> Dict[str, List[str]]:
        """
        Get selected features from each individual method.

        Returns
        -------
        Dict[str, List[str]]
            Dictionary mapping method names to their selected features.
        """
        return {
            type(method).__name__: method.selected_features_ for method in self.methods
        }  # type: ignore
