from typing import Dict, List, Literal

import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.metrics import average_precision_score

from classifier_toolkit.feature_selection.base import BaseFeatureSelector
from classifier_toolkit.feature_selection.utils.data_handling import (
    create_catboost_pools,
)


class RFECatBoostSelector(BaseFeatureSelector):
    """
    Recursive Feature Elimination selector using CatBoost.

    This class implements feature selection using CatBoost's feature importance
    for recursive feature elimination.

    Parameters
    ----------
    model_params : Dict
        Parameters for the CatBoost model.
    cat_features : List[str]
        List of categorical feature names.
    n_features_to_select : int, optional
        Number of features to select, by default -1 (auto-select based on performance).
    scoring : {'accuracy', 'f1', 'precision', 'recall', 'roc_auc', 'average_precision'}, optional
        Scoring metric to use, by default 'average_precision'.
    cv : int, optional
        Number of cross-validation folds, by default 5.
    verbose : int, optional
        Verbosity level, by default 1.
    random_state : int, optional
        Random state for reproducibility, by default 42.

    Attributes
    ----------
    rankings : pd.DataFrame
        Feature rankings after fitting.
    prauc_scores_ : List[float]
        PRAUC scores during feature elimination.
    selected_features_ : List[str]
        Selected feature names after fitting.
    feature_importances_ : pd.Series
        Feature importance scores after fitting.
    """

    def __init__(
        self,
        model_params: Dict,
        cat_features: List[str],
        n_features_to_select: int = -1,
        scoring: Literal[
            "accuracy", "f1", "precision", "recall", "roc_auc", "average_precision"
        ] = "average_precision",
        cv: int = 5,
        verbose: int = 1,
        random_state: int = 42,
    ):
        super().__init__(
            estimator=None,
            n_features_to_select=n_features_to_select,
            scoring=scoring,
            cv=cv,
            verbose=verbose,
        )
        self.model_params = model_params
        self.random_state = random_state
        self.cat_features = cat_features
        self.rankings = None
        self.prauc_scores_ = []

    def fit(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        cv_folds: Dict,
    ) -> "RFECatBoostSelector":
        """
        Fit the RFE selector using CatBoost's select_features method.
        The process follows these steps:
        1. Rank all features using CatBoost's select_features across all folds
        2. Use this ranking to perform RFE, eliminating features in order of importance
        3. Select the optimal number of features based on PRAUC scores
        """
        if self.verbose:
            self.validate_datasets(y, cv_folds)

        # First, get feature rankings across all folds
        self.rankings = self.rank_features(X, y, cv_folds)
        self.feature_importances_ = self.rankings["mean_rank"]

        # Get ranked features list (sorted by mean rank)
        ranked_features = self.rankings.sort_values("mean_rank").index.tolist()

        # Perform RFE loop using the pre-computed ranking
        self.prauc_scores_ = self.rfe_loop(X, y, cv_folds, ranked_features)

        # Select optimal number of features
        if self.n_features_to_select == -1:
            # Find the number of features that gives the best PRAUC
            optimal_feature_count = len(ranked_features) - np.argmax(self.prauc_scores_)
            self.n_features_to_select = optimal_feature_count

        self.selected_features_ = ranked_features[: self.n_features_to_select]

        if self.verbose:
            print(f"Selected {len(self.selected_features_)} features")
            print("Selected features:", self.selected_features_)

        return self

    def rank_features(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        cv_folds: Dict,
    ) -> pd.DataFrame:
        """
        Rank features using CatBoost's feature importance.

        Parameters
        ----------
        X : pd.DataFrame
            The feature matrix.
        y : pd.Series
            The target variable.
        cv_folds : Dict
            Cross-validation fold indices.

        Returns
        -------
        pd.DataFrame
            DataFrame containing feature rankings and importance scores.
        """
        rankings = pd.DataFrame()
        feature_names = X.columns.tolist()

        # Modified to match the procedural approach
        for fold, _ in cv_folds.items():
            pools = create_catboost_pools(X, y, cv_folds, self.cat_features, fold)
            model = CatBoostClassifier(**self.model_params)

            results = model.select_features(
                X=pools["train_pool"],
                eval_set=pools["eval_pool"],
                features_for_select=feature_names,
                num_features_to_select=1,
                train_final_model=False,
                logging_level="Silent" if not self.verbose else "Info",
            )

            # Create ranking for this fold (matching your procedural approach)
            fold_ranking = pd.DataFrame(
                {
                    "feature": list(
                        reversed(
                            results["eliminated_features_names"]
                            + results["selected_features_names"]
                        )
                    ),
                    "fold": f"fold_{fold+1}",  # Changed to match your fold numbering
                }
            ).set_index("feature")

            fold_ranking[f"rank_fold_{fold+1}"] = range(1, len(feature_names) + 1)

            if rankings.empty:
                rankings = fold_ranking[[f"rank_fold_{fold+1}"]]
            else:
                rankings = rankings.join(fold_ranking[[f"rank_fold_{fold+1}"]])

        # Calculate summary statistics
        rankings["mean_rank"] = rankings[
            [col for col in rankings.columns if "fold" in col]
        ].mean(axis=1)
        rankings["min_rank"] = rankings[
            [col for col in rankings.columns if "fold" in col]
        ].min(axis=1)
        rankings["max_rank"] = rankings[
            [col for col in rankings.columns if "fold" in col]
        ].max(axis=1)
        rankings["std"] = (
            rankings[[col for col in rankings.columns if "fold" in col]]
            .std(axis=1)
            .round(2)
        )

        return rankings.sort_values("mean_rank")

    def rfe_loop(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        cv_folds: Dict,
        ranked_features: List[str],
    ) -> List[float]:
        """
        Perform RFE loop to evaluate different feature subsets.

        Parameters
        ----------
        X : pd.DataFrame
            The feature matrix.
        y : pd.Series
            The target variable.
        cv_folds : Dict
            Cross-validation fold indices.
        ranked_features : List[str]
            List of features ranked by importance.

        Returns
        -------
        List[float]
            List of performance scores for each feature subset.
        """
        feature_count = len(ranked_features)
        prauc_scores = []

        # Use a consistent fold for evaluation (fold 3 as in procedural code)
        evaluation_fold = 3

        # Iterate through feature counts in descending order
        for i in range(feature_count - 1):
            # Take top N features based on ranking
            features_to_use = ranked_features[: feature_count - i]

            if self.verbose > 0:
                print(f"Features removed: {i}")
                print(f"Features kept: {len(features_to_use)}")

            # Evaluate using only fold 3, matching procedural approach
            prauc = self.rfe_evaluate(
                X[features_to_use],
                y,
                cv_folds,
                features_to_use,
                fold_index=evaluation_fold,
            )
            prauc_scores.append(prauc)

        return prauc_scores

    def rfe_evaluate(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        cv_folds: Dict,
        features_to_use: List[str],
        fold_index: int = 3,  # Default to fold 3 to match procedural code
    ) -> float:
        """Evaluate features using RFE with CatBoost."""
        # Filter X to only include features_to_use
        X_subset = X[features_to_use]

        # Create pools for evaluation
        pools = create_catboost_pools(
            X_subset,
            y,
            cv_folds,
            self.cat_features,  # Pass all categorical features
            fold_index,
        )

        # Train model
        model = CatBoostClassifier(**self.model_params)
        model.fit(
            pools["train_pool"], eval_set=pools["eval_pool"], verbose=self.verbose > 0
        )

        # Get predictions and calculate scores
        y_pred_test = model.predict_proba(pools["test_pool"])[:, 1]
        y_pred_train = model.predict_proba(pools["train_pool"])[:, 1]

        prauc_test = average_precision_score(
            pools["test_pool"].get_label(), y_pred_test
        )
        prauc_train = average_precision_score(
            pools["train_pool"].get_label(), y_pred_train
        )

        if self.verbose > 0:
            print(f"Features kept: {features_to_use}")
            print(f"PRAUC on train set: {prauc_train:.4f}")
            print(f"PRAUC on test set: {prauc_test:.4f}\n")

        return prauc_test

    def validate_datasets(self, y: pd.Series, cv_folds: Dict):
        """
        Validate datasets for both final and fold splits.

        Parameters
        ----------
        y : pd.Series
            The target variable.
        cv_folds : Dict
            Cross-validation fold indices.
        """
        for fold_idx, fold in cv_folds.items():
            train_indices = fold["X_train"]
            val_indices = fold["X_validation"]
            test_indices = fold["X_test"]

            # Calculate statistics for each split
            splits = {
                "train": train_indices,
                "validation": val_indices,
                "test": test_indices,
            }

            if self.verbose:
                print(f"\nFold {fold_idx + 1} validation")
                print("=" * 20)

                for split_name, indices in splits.items():
                    split_y = y.iloc[indices]

                    total_count = len(split_y)
                    positive_count = split_y.sum()
                    positive_freq = (positive_count / total_count) * 100

                    print(f"\n{split_name.capitalize()} split:")
                    print(f"Total count: {total_count}")
                    print(f"Positive count: {positive_count}")
                    print(f"Positive frequency: {positive_freq:.2f}%")

    def get_feature_importances(self) -> pd.DataFrame:
        """Get the importance scores for each feature."""
        if self.rankings is None:
            raise ValueError("Feature rankings are not available. Call 'fit' first.")
        return self.rankings

    def _get_score(self) -> None:
        pass
