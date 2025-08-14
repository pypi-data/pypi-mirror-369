from typing import Dict, List, Literal, Optional

import lightgbm as lgb
import numpy as np
import pandas as pd
import shap
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score

from classifier_toolkit.feature_selection.base import (
    BaseFeatureSelector,
)
from classifier_toolkit.feature_selection.utils.scoring import get_scorer


class RFESelector(BaseFeatureSelector):
    """
    Recursive Feature Elimination selector using various estimators.

    This class implements feature selection using recursive feature elimination
    with support for multiple estimators and SHAP values.

    Parameters
    ----------
    estimator_name : {'xgboost', 'random_forest', 'lightgbm'}, optional
        The estimator to use, by default 'lightgbm'.
    n_features_to_select : int, optional
        Number of features to select, by default -1 (auto-select based on performance).
    scoring : {'accuracy', 'f1', 'precision', 'recall', 'roc_auc', 'average_precision'}, optional
        Scoring metric to use, by default 'average_precision'.
    cv : int, optional
        Number of cross-validation folds, by default 5.
    verbose : int, optional
        Verbosity level, by default 0.
    n_jobs : int, optional
        Number of parallel jobs, by default -1.
    model_params : Optional[Dict], optional
        Parameters for the estimator, by default None.
    random_state : int, optional
        Random state for reproducibility, by default 42.
    cat_features : Optional[List[str]], optional
        List of categorical feature names, by default None.
    cross_validate_prauc : bool, optional
        Whether to cross-validate PRAUC scores, by default False.
    shap_combined : bool, optional
        Whether to combine SHAP values with feature importances, by default False.

    Attributes
    ----------
    rankings : pd.DataFrame
        Feature rankings after fitting.
    feature_importances_ : pd.Series
        Feature importance scores after fitting.
    selected_features_ : List[str]
        Selected feature names after fitting.
    prauc_scores_ : List[float]
        PRAUC scores during feature elimination.
    """

    @staticmethod
    def shap_importance(X, model):
        """
        Calculate SHAP importance for each feature in the dataset.
        """
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X)

        if isinstance(shap_values, list):  # Since it's a binary classification problem
            shap_values = shap_values[0]

        shap_importance = np.abs(shap_values).mean(axis=0)

        return shap_importance

    def __init__(
        self,
        estimator_name: Literal["xgboost", "random_forest", "lightgbm"] = "lightgbm",
        n_features_to_select: int = -1,
        scoring: Literal[
            "accuracy", "f1", "precision", "recall", "roc_auc", "average_precision"
        ] = "average_precision",
        cv: int = 5,
        verbose: int = 0,
        n_jobs: int = -1,
        model_params: Optional[Dict] = None,
        random_state: int = 42,
        cat_features: Optional[List[str]] = None,
        cross_validate_prauc: bool = False,
        shap_combined: bool = False,
        rerank: bool = False,
    ):
        super().__init__(
            estimator=None,
            n_features_to_select=n_features_to_select,
            scoring=scoring,
            cv=cv,
            verbose=verbose,
        )
        self.estimator_name = estimator_name
        self.n_jobs = n_jobs
        self.model_params = model_params or {}
        self.random_state = random_state
        self.cat_features = cat_features or []
        self.cross_validate_prauc = cross_validate_prauc
        self.shap_combined = shap_combined
        self.rerank = rerank

    def fit(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        cv_folds: Dict,
    ) -> "RFESelector":
        if self.estimator_name == "xgboost":
            self.rankings = self.rank_features(
                X, y, cv_folds, xgb.XGBClassifier, self.model_params
            )
        elif self.estimator_name == "lightgbm":
            self.rankings = self.rank_features(
                X, y, cv_folds, lgb.LGBMClassifier, self.model_params
            )
        elif self.estimator_name == "random_forest":
            self.rankings = self.rank_features(
                X, y, cv_folds, RandomForestClassifier, self.model_params
            )
        else:
            raise ValueError(f"Unknown estimator: {self.estimator_name}")

        self.feature_importances_ = self.rankings["mean_importance"]

        self.prauc_scores_ = self.rfe_loop(
            X,
            y,
            cv_folds,
            self.rankings.index,  # type: ignore
        )

        if self.n_features_to_select == -1:
            self.n_features_to_select = np.argmax(self.prauc_scores_) + 1

        self.selected_features_ = list(
            self.feature_importances_.index[: self.n_features_to_select]
        )
        return self

    def rank_features(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        cv_folds: Dict,
        model_name: type,
        model_params: Dict,
    ) -> pd.DataFrame:
        """
        Rank features based on their importance across folds.
        """
        feature_names = X.columns
        feature_importances = pd.DataFrame(index=feature_names)

        for fold, indices in cv_folds.items():
            X_train = X.iloc[indices["X_train"]]
            X_val = X.iloc[indices["X_validation"]]
            y_train = y.iloc[indices["y_train"]]
            y_val = y.iloc[indices["y_validation"]]

            model = model_name(**model_params)
            if isinstance(model, lgb.LGBMClassifier):
                model.fit(
                    X_train,
                    y_train,
                    eval_set=[(X_val, y_val)],
                    eval_metric="average_precision",
                    eval_names=["valid"],
                )
            elif isinstance(model, xgb.XGBClassifier):
                model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
            else:
                model.fit(X_train, y_train)

            if hasattr(model, "feature_importances_"):
                if self.shap_combined:
                    # Create Series for regular feature importances
                    fold_importances = pd.Series(
                        model.feature_importances_,
                        index=feature_names,
                        name=f"fold_{fold}",
                    )
                    # Calculate and add SHAP importances as a separate column
                    shap_importances = pd.Series(
                        self.shap_importance(X_val, model),
                        index=feature_names,
                        name=f"shap_fold_{fold}",
                    )

                    feature_importances = feature_importances.join(fold_importances)
                    feature_importances = feature_importances.join(shap_importances)

                else:
                    fold_importances = pd.Series(
                        model.feature_importances_,
                        index=feature_names,
                        name=f"fold_{fold}",
                    )

                    feature_importances = feature_importances.join(fold_importances)

            else:
                raise ValueError(
                    f"Feature importance not available for model type {type(model)}"
                )

        if self.shap_combined:
            # Calculate mean importances
            feature_importances["mean_importance"] = feature_importances.filter(
                like="fold_"
            ).mean(axis=1)
            feature_importances["mean_shap"] = feature_importances.filter(
                like="shap_fold_"
            ).mean(axis=1)

            # Calculate ranks for regular feature importances
            rank_columns = feature_importances.filter(like="fold_").rank(
                ascending=False
            )
            # Calculate ranks for SHAP importances
            shap_rank_columns = feature_importances.filter(like="shap_fold_").rank(
                ascending=False
            )

            # Calculate statistics across ranks for both
            rank_stats = rank_columns.agg(["min", "max", "std", "mean"], axis=1)
            shap_rank_stats = shap_rank_columns.agg(
                ["min", "max", "std", "mean"], axis=1
            )

            # Add the rank statistics to the original dataframe
            feature_importances["min_rank"] = rank_stats["min"]
            feature_importances["max_rank"] = rank_stats["max"]
            feature_importances["rank_std"] = rank_stats["std"]
            feature_importances["mean_rank"] = rank_stats["mean"]

            feature_importances["min_shap_rank"] = shap_rank_stats["min"]
            feature_importances["max_shap_rank"] = shap_rank_stats["max"]
            feature_importances["shap_rank_std"] = shap_rank_stats["std"]
            feature_importances["mean_shap_rank"] = shap_rank_stats["mean"]

            # Calculate final ranks for both methods
            feature_importances["importance_rank"] = feature_importances[
                "mean_importance"
            ].rank(ascending=False, method="min")
            feature_importances["shap_rank"] = feature_importances["mean_shap"].rank(
                ascending=False, method="min"
            )

            # Sort by average of both ranks
            feature_importances["combined_rank"] = feature_importances[
                ["importance_rank", "shap_rank"]
            ].mean(axis=1)
            feature_importances.sort_values("combined_rank", inplace=True)

        else:
            # Calculate mean importance
            feature_importances["mean_importance"] = feature_importances.filter(
                like="fold_"
            ).mean(axis=1)

            # Calculate ranks for all folds at once
            rank_columns = feature_importances.filter(like="fold_").rank(
                ascending=False
            )

            # Calculate statistics across ranks
            rank_stats = rank_columns.agg(["min", "max", "std", "mean"], axis=1)

            # Add the rank statistics to the original dataframe
            feature_importances["min_rank"] = rank_stats["min"]
            feature_importances["max_rank"] = rank_stats["max"]
            feature_importances["rank_std"] = rank_stats["std"]
            feature_importances["mean_rank"] = rank_stats["mean"]

            feature_importances["rank"] = feature_importances["mean_importance"].rank(
                ascending=False, method="min"
            )

            # Sort by rank to get features in order of importance
            feature_importances.sort_values("rank", inplace=True)

        return feature_importances

    def rfe_loop(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        cv_folds: Dict,
        ranking: List[str],
    ) -> List[float]:
        feature_count = len(ranking)
        prauc_scores = []

        if self.rerank:
            for i in range(feature_count - 1):
                features_to_use = ranking[: feature_count - i]
                print(f"Features kept: {features_to_use}")
                print(f"Features removed: {i}")
                prauc = self.rfe_evaluate(
                    X[features_to_use],
                    y,
                    cv_folds,
                    features_to_use,
                )
                prauc_scores.append(prauc)

                self.rankings = self.rank_features(
                    X[features_to_use],
                    y,
                    cv_folds,
                    xgb.XGBClassifier,
                    self.model_params,
                )

                print(f"Feature ranking: {self.rankings}")

            return prauc_scores

        else:
            for i in range(feature_count - 1):
                features_to_use = ranking[: feature_count - i]
                print(f"Features kept: {features_to_use}")
                print(f"Features removed: {i}")
                prauc = self.rfe_evaluate(
                    X[features_to_use],
                    y,
                    cv_folds,
                    features_to_use,
                )
                prauc_scores.append(prauc)

            return prauc_scores

    def rfe_evaluate(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        cv_folds: Dict,
        features_to_use: List[str],
        fold_index: int = 0,
    ) -> float:
        """Evaluate features using RFE with existing fold structure."""

        if self.cross_validate_prauc:
            prauc_test_scores = []
            prauc_train_scores = []
            for _, indices in cv_folds.items():
                X_train = X.iloc[indices["X_train"]]
                X_eval = X.iloc[indices["X_validation"]]
                X_test = X.iloc[indices["X_test"]]

                y_train = y.iloc[indices["y_train"]]
                y_eval = y.iloc[indices["y_validation"]]
                y_test = y.iloc[indices["y_test"]]

                if self.estimator_name == "lightgbm":
                    model = lgb.LGBMClassifier(**self.model_params)
                    model.fit(
                        X_train,
                        y_train,
                        eval_set=[(X_eval, y_eval)],
                        eval_metric="average_precision",
                        eval_names=["valid"],
                    )
                elif self.estimator_name == "xgboost":
                    model = xgb.XGBClassifier(**self.model_params)
                    model.fit(
                        X_train, y_train, eval_set=[(X_eval, y_eval)], verbose=False
                    )
                else:
                    model = RandomForestClassifier(**self.model_params)
                    model.fit(X_train, y_train)

                if self.scoring == "average_precision":
                    # Use predict_proba for probability-based metrics
                    y_pred_test = model.predict_proba(X_test)[:, 1]  # type: ignore # It's a numpy array, I don't care about the linter here
                    y_pred_train = model.predict_proba(X_train)[:, 1]  # type: ignore
                    prauc_test_scores.append(
                        average_precision_score(y_test, y_pred_test)
                    )
                    prauc_train_scores.append(
                        average_precision_score(y_train, y_pred_train)
                    )
                else:
                    # Get the appropriate scorer from the scoring module
                    scorer = get_scorer(self.scoring)
                    prauc_test_scores.append(scorer(model, X_test, y_test))
                    prauc_train_scores.append(scorer(model, X_train, y_train))

            prauc_test = sum(prauc_test_scores) / len(prauc_test_scores)
            prauc_train = sum(prauc_train_scores) / len(prauc_train_scores)

        else:
            X_train = X.iloc[cv_folds[fold_index]["X_train"]]
            X_eval = X.iloc[cv_folds[fold_index]["X_validation"]]
            X_test = X.iloc[cv_folds[fold_index]["X_test"]]

            y_train = y.iloc[cv_folds[fold_index]["y_train"]]
            y_eval = y.iloc[cv_folds[fold_index]["y_validation"]]
            y_test = y.iloc[cv_folds[fold_index]["y_test"]]

            if self.estimator_name == "lightgbm":
                model = lgb.LGBMClassifier(**self.model_params)
                model.fit(
                    X_train,
                    y_train,
                    eval_set=[(X_eval, y_eval)],
                    eval_metric="average_precision",
                    eval_names=["valid"],
                )
            elif self.estimator_name == "xgboost":
                model = xgb.XGBClassifier(**self.model_params)
                model.fit(X_train, y_train, eval_set=[(X_eval, y_eval)], verbose=False)
            else:
                model = RandomForestClassifier(**self.model_params)
                model.fit(X_train, y_train)

            if self.scoring == "average_precision":
                # Use predict_proba for probability-based metrics
                y_pred_test = model.predict_proba(X_test)[:, 1]  # type: ignore # It's a numpy array, I don't care about the linter here
                y_pred_train = model.predict_proba(X_train)[:, 1]  # type: ignore
                prauc_test = average_precision_score(y_test, y_pred_test)
                prauc_train = average_precision_score(y_train, y_pred_train)
            else:
                # Get the appropriate scorer from the scoring module
                scorer = get_scorer(self.scoring)
                prauc_test = scorer(model, X_test, y_test)
                prauc_train = scorer(model, X_train, y_train)

        if self.verbose > 0:
            print("Features kept:", len(features_to_use))
            print(f"{self.scoring} on train set:", prauc_train)
            print(f"{self.scoring} on test set:", prauc_test)
            print("\n")
            (
                print(
                    f"PRAUC Fold Scores:\nTrain: {prauc_train_scores}\nTest: {prauc_test_scores}"
                )
                if self.cross_validate_prauc
                else None
            )

        return prauc_test  # type: ignore

    def _get_score(self) -> None:
        pass

    def get_feature_importances(self) -> pd.DataFrame:
        """
        Get the importance scores for each feature.
        """
        if self.rankings is None:
            raise ValueError("Feature rankings are not available. Call 'fit' first.")
        return self.rankings
