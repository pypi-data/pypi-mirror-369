from typing import Dict, List, Literal, Optional

import lightgbm as lgb
import pandas as pd
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score

from classifier_toolkit.feature_selection.utils.scoring import get_scorer
from classifier_toolkit.model_training.models.base import (
    BaseModel,
)


class EnsembleModel(BaseModel):
    """
    Recursive Feature Elimination selector using various estimators.

    This class implements feature selection using recursive feature elimination
    with support for multiple estimators and SHAP values.

    Parameters
    ----------
    estimator_name : {'xgboost', 'random_forest', 'lightgbm'}, optional
        The estimator to use, by default 'lightgbm'.
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

    Attributes
    ----------
    model_performance: float
        The performance of the model on the validation set based on the selected metric.
    """

    def __init__(
        self,
        estimator_name: Literal["xgboost", "random_forest", "lightgbm"] = "lightgbm",
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
    ):
        super().__init__(
            estimator=None,
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

    def fit(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        cv_folds: Dict,
    ) -> "EnsembleModel":
        if self.estimator_name == "xgboost":
            self.rankings = self.rank_features(  # type: ignore
                X, y, cv_folds, xgb.XGBClassifier, self.model_params
            )
        elif self.estimator_name == "lightgbm":
            self.rankings = self.rank_features(  # type: ignore
                X, y, cv_folds, lgb.LGBMClassifier, self.model_params
            )
        elif self.estimator_name == "random_forest":
            self.rankings = self.rank_features(  # type: ignore
                X, y, cv_folds, RandomForestClassifier, self.model_params
            )
        else:
            raise ValueError(f"Unknown estimator: {self.estimator_name}")

        return self

    def model_evaluate(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        cv_folds: Dict,
        features_to_use: List[str],
        fold_index: int = 0,
    ) -> float:
        """Evaluate the model on each fold using metric with existing fold structure."""

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
