import logging
from typing import Dict, List, Literal, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from lightgbm import LGBMClassifier
from scipy import stats
from sklearn.base import BaseEstimator
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.utils import check_random_state
from xgboost import XGBClassifier

from classifier_toolkit.feature_selection.base import FeatureSelectionError


class BorutaSelector:
    """
    Boruta feature selection method with support for multiple estimators.

    This implementation supports Random Forest, XGBoost, LightGBM, and CatBoost
    classifiers for feature selection using the Boruta algorithm.
    """

    @staticmethod
    def _validate_importances(importances: np.ndarray) -> None:
        """Validate feature importance scores."""
        if np.any(np.isnan(importances)) or np.any(np.isinf(importances)):
            raise ValueError("Feature importances contain NaN or infinite values")

    @staticmethod
    def _fdr_correction(
        pvalues: np.ndarray, alpha: float = 0.05
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        This method implements the Benjamini-Hochberg (BH) method for False Discovery
        Rate (FDR) correction. It ranks and adjusts p-values to control the FDR.
        """
        pvalues = np.asarray(pvalues)
        n_tests = len(pvalues)

        sorted_indices = np.argsort(pvalues)
        sorted_pvalues = pvalues[sorted_indices]
        critical_values = np.arange(1, n_tests + 1) * alpha / n_tests

        reject = sorted_pvalues <= critical_values
        if reject.any():
            max_reject = np.max(np.where(reject)[0])
            reject[: max_reject + 1] = True

        corrected_pvalues = np.minimum.accumulate(
            sorted_pvalues * n_tests / np.arange(1, n_tests + 1)
        )
        corrected_pvalues = np.minimum(corrected_pvalues, 1)

        reject_mask = np.zeros_like(reject)
        corrected_pvalues_final = np.zeros_like(corrected_pvalues)
        reject_mask[sorted_indices] = reject
        corrected_pvalues_final[sorted_indices] = corrected_pvalues

        return reject_mask, corrected_pvalues_final

    # Class constants
    SUPPORTED_ESTIMATORS = {  # noqa: RUF012
        "random_forest": RandomForestClassifier,
        "xgboost": XGBClassifier,
        "lightgbm": LGBMClassifier,
        "catboost": CatBoostClassifier,
    }

    DEFAULT_IMPORTANCE_TYPES = {  # noqa: RUF012
        "xgboost": "gain",
        "lightgbm": "gain",
        "catboost": "PredictionValuesChange",
    }

    MIN_SHADOW_FEATURES = 5
    SHADOW_MULTIPLIER = 1.2
    SHADOW_STD_THRESHOLD = 3

    def __init__(
        self,
        estimator_name: Literal[
            "random_forest", "xgboost", "lightgbm", "catboost"
        ] = "random_forest",
        estimator_params: Optional[Dict] = None,
        importance_type: Optional[str] = None,
        n_estimators: Union[int, str] = "auto",
        perc: int = 99,
        alpha: float = 0.001,
        max_iter: int = 100,
        early_stopping: bool = False,
        n_iter_no_change: int = 20,
        two_step_correction: bool = True,
        random_state: Optional[int] = None,
        verbose: int = 0,
    ):
        """Initialize BorutaSelector.

        Parameters
        ----------
        estimator_name : str
            Type of estimator to use
        estimator_params : dict
            Parameters for the estimator
        importance_type : str
            Type of feature importance to use
        n_estimators : int
            Number of trees in the forest
        perc : float
            Percentile for feature selection
        alpha : float
            Significance level
        max_iter : int
            Maximum number of iterations
        early_stopping : bool
            Whether to use early stopping
        n_iter_no_change : int
            Number of iterations with no change for early stopping
        two_step_correction : bool
            Whether to use two-step correction
        random_state : int
            Random state for reproducibility
        verbose : int
            Verbosity level
        """
        self._validate_init_params(estimator_name, alpha, max_iter, n_iter_no_change)

        self.estimator_name = estimator_name
        self.estimator_params = self._prepare_estimator_params(
            estimator_params or {}, importance_type
        )
        self.importance_type = importance_type
        self.n_estimators = n_estimators
        self.perc = perc
        self.alpha = alpha
        self.max_iter = max_iter
        self.early_stopping = early_stopping
        self.n_iter_no_change = n_iter_no_change
        self.two_step_correction = two_step_correction
        self.random_state = random_state
        self.verbose = verbose

        self.estimator = self._initialize_estimator()
        self.logger = self._setup_logger()

    def _validate_init_params(
        self, estimator_name: str, alpha: float, max_iter: int, n_iter_no_change: int
    ) -> None:
        """Validate initialization parameters."""
        if estimator_name not in self.SUPPORTED_ESTIMATORS:
            raise ValueError(
                f"estimator_name must be one of: {list(self.SUPPORTED_ESTIMATORS.keys())}"
            )
        if not 0 < alpha < 1:
            raise ValueError("alpha must be between 0 and 1")
        if max_iter < 1:
            raise ValueError("max_iter must be positive")
        if n_iter_no_change < 1:
            raise ValueError("n_iter_no_change must be positive")

    def _prepare_estimator_params(
        self, params: Dict, importance_type: Optional[str]
    ) -> Dict:
        """Prepare estimator parameters."""
        if importance_type and self.estimator_name in ["xgboost", "lightgbm"]:
            params["importance_type"] = importance_type
        return params

    def _setup_logger(self) -> logging.Logger:
        """Setup logger with appropriate verbosity."""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO if self.verbose else logging.WARNING)
        return logger

    def _get_feature_importances(self, estimator: BaseEstimator) -> np.ndarray:
        """Extract feature importances from various types of estimators."""
        try:
            if hasattr(estimator, "feature_importances_"):
                importances = estimator.feature_importances_
                self._validate_importances(importances)
                return importances

            if isinstance(estimator, XGBClassifier):
                importance_type = (
                    self.importance_type or self.DEFAULT_IMPORTANCE_TYPES["xgboost"]
                )
                return np.array(
                    list(
                        estimator.get_booster()
                        .get_score(importance_type=importance_type)
                        .values()
                    )
                )

            if isinstance(estimator, LGBMClassifier):
                importance_type = (
                    self.importance_type or self.DEFAULT_IMPORTANCE_TYPES["lightgbm"]
                )
                return estimator.booster_.feature_importance(
                    importance_type=importance_type
                )

            if isinstance(estimator, CatBoostClassifier):
                importance_type = (
                    self.importance_type or self.DEFAULT_IMPORTANCE_TYPES["catboost"]
                )
                return estimator.get_feature_importance(type=importance_type)

        except Exception as e:
            raise FeatureSelectionError(  # noqa: B904
                f"Failed to extract feature importances from estimator of type {type(estimator)}: {str(e)}"  # noqa: RUF010
            )

        raise FeatureSelectionError(
            f"Estimator of type {type(estimator)} doesn't support feature importance extraction"
        )

    def get_feature_importances(self) -> pd.Series:
        """Get mean feature importances across all iterations."""
        if not hasattr(self, "importance_history_"):
            raise FeatureSelectionError("Call fit() before get_feature_importances()")
        mean_importance = np.nanmean(self.importance_history_, axis=0)
        return pd.Series(mean_importance, index=self.feature_names_)

    def _initialize_estimator(self) -> BaseEstimator:
        """Initialize the estimator with appropriate parameters."""
        if self.n_estimators != "auto":
            self.estimator_params["n_estimators"] = self.n_estimators

        if self.estimator_name == "catboost":
            params = {
                k: v
                for k, v in self.estimator_params.items()
                if k not in ["importance_type", "cat_features"]
            }
            return CatBoostClassifier(**params)

        return self.SUPPORTED_ESTIMATORS[self.estimator_name](**self.estimator_params)

    def _get_tree_num(self, n_feat: int) -> int:
        """Calculate the number of trees needed."""
        try:
            depth = self.estimator.get_params().get("max_depth", 10)
            if self.estimator_name == "lightgbm":
                num_leaves = self.estimator.get_params().get("num_leaves", 31)
                depth = int(np.log2(num_leaves))
            elif self.estimator_name == "catboost":
                depth = self.estimator.get_params().get("depth", 6)
        except KeyError:
            depth = 10

        feature_consideration_target = 100
        multiplier = (n_feat * 2) / (np.sqrt(n_feat * 2) * depth)
        return max(10, int(multiplier * feature_consideration_target))

    def _create_shadow_features(
        self, X: pd.DataFrame, dec_reg: np.ndarray
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Create shadow features for importance comparison.

        Args:
            X: Input features DataFrame
            dec_reg: Decision register for features

        Returns:
            Tuple containing active features DataFrame and shadow features DataFrame

        Raises:
            FeatureSelectionError: If no active features are available
        """
        active_features = np.where(dec_reg >= 0)[0]
        if len(active_features) == 0:
            raise FeatureSelectionError(
                "No active features available to create shadow features."
            )

        X_active = X.iloc[:, active_features]
        n_active = X_active.shape[1]

        X_shadow = X_active.copy()
        shadow_names = [f"shadow_{i}" for i in range(n_active)]
        X_shadow.columns = shadow_names

        # Use RandomState directly instead of default_rng
        random_state = check_random_state(self.random_state)
        for col in X_shadow.columns:
            X_shadow[col] = random_state.permutation(X_shadow[col].values)

        if n_active < self.MIN_SHADOW_FEATURES:
            n_duplications = int(np.ceil(self.MIN_SHADOW_FEATURES / n_active))
            shadow_copies = []

            for i in range(n_duplications):
                additional = X_shadow.copy()
                additional.columns = [
                    f"shadow_{j + (i+1)*n_active}" for j in range(n_active)
                ]
                for col in additional.columns:
                    additional[col] = random_state.permutation(additional[col].values)
                shadow_copies.append(additional)

            X_shadow = pd.concat([X_shadow] + shadow_copies, axis=1)  # noqa: RUF005
            X_shadow = X_shadow.iloc[:, : self.MIN_SHADOW_FEATURES]

        return X_active, X_shadow

    def _get_feature_importance(self, X: pd.DataFrame, y: pd.Series) -> np.ndarray:
        """Get feature importance scores."""
        if self.n_estimators == "auto":
            current_params = self.estimator.get_params()
            n_trees = self._get_tree_num(X.shape[1])
            current_params["n_estimators"] = n_trees

            if self.estimator_name == "lightgbm":
                current_params.setdefault("num_leaves", 31)

            if self.estimator_name == "catboost":
                self.estimator = self._initialize_estimator()
                self.estimator.set_params(**current_params)
            else:
                self.estimator.set_params(**current_params)

        X_prepared = self._prepare_catboost_data(X)
        self.estimator.fit(X_prepared, y)
        return self._get_feature_importances(self.estimator)

    def _update_importance_history(  # Check this
        self,
        importance_history: List[np.ndarray],
        current_importance: np.ndarray,
        dec_reg: np.ndarray,
    ) -> List[np.ndarray]:
        """Update the history of feature importances."""
        imp = np.full(len(dec_reg), np.nan)
        active_features = np.where(dec_reg >= 0)[0]
        imp[active_features] = current_importance
        importance_history.append(imp)
        return importance_history

    def _do_statistical_test(
        self,
        hit_reg: np.ndarray,
        dec_reg: np.ndarray,
        iteration: int,
    ) -> np.ndarray:
        """Perform statistical tests to determine feature importance."""
        active_features = np.where(dec_reg >= 0)[0]
        hits = hit_reg[active_features]

        accept_pvals = stats.binom.sf(hits - 1, iteration, 0.75)
        reject_pvals = stats.binom.cdf(hits, iteration, 0.25)

        if self.two_step_correction:
            accept_mask = self._fdr_correction(accept_pvals, self.alpha / 2)[0]
            reject_mask = self._fdr_correction(reject_pvals, self.alpha / 2)[0]

            accept_mask &= accept_pvals <= (self.alpha / (iteration * 2))
            reject_mask &= reject_pvals <= (self.alpha / (iteration * 2))
        else:
            n_features = len(dec_reg)
            accept_mask = accept_pvals <= (self.alpha / (n_features * 2))
            reject_mask = reject_pvals <= (self.alpha / (n_features * 2))

        tentative_features = np.where(dec_reg[active_features] == 0)[0]
        dec_reg[
            active_features[tentative_features[accept_mask[tentative_features]]]
        ] = 1
        dec_reg[
            active_features[tentative_features[reject_mask[tentative_features]]]
        ] = -1

        return dec_reg

    def fit(self, X: pd.DataFrame, y: pd.Series) -> "BorutaSelector":
        """
        Fit the feature selector.

        Parameters
        ----------
        X : pd.DataFrame
            Input features DataFrame
        y : pd.Series
            Target variable

        Returns
        -------
        self : BaseFeatureSelector
            The fitted selector
        """
        if not isinstance(X, pd.DataFrame):
            raise ValueError("X must be a pandas DataFrame")
        if not isinstance(y, pd.Series):
            raise ValueError("y must be a pandas Series")

        if (
            self.estimator_name == "catboost"
            and "cat_features" in self.estimator_params
        ):
            cat_features = self.estimator_params["cat_features"]
            if isinstance(cat_features[0], int):
                cat_features = [X.columns[i] for i in cat_features]
            self.estimator_params["cat_features"] = cat_features
            self.estimator.set_params(cat_features=cat_features)

        self.random_state = check_random_state(self.random_state)
        _, n_features = X.shape

        dec_reg = np.zeros(n_features, dtype=int)
        hit_reg = np.zeros(n_features, dtype=int)
        importance_history = []
        shadow_max_history = []

        if self.early_stopping:
            no_change_count = 0
            last_dec_reg = None

        for iteration in range(1, self.max_iter + 1):
            if self.verbose:
                print(f"\nIteration {iteration}/{self.max_iter}")

            X_active, X_shadow = self._create_shadow_features(X, dec_reg)
            X_combined = pd.concat([X_active, X_shadow], axis=1)
            importances = self._get_feature_importance(X_combined, y)

            real_imp = importances[: X_active.shape[1]]
            shadow_imp = importances[X_active.shape[1] :]

            shadow_mean = np.mean(shadow_imp)
            shadow_std = np.std(shadow_imp)
            shadow_max = np.max(shadow_imp)
            shadow_threshold = np.maximum(shadow_max, shadow_mean + 3 * shadow_std)
            shadow_max_history.append(shadow_threshold)

            if self.verbose >= 2:
                print(f"Shadow mean: {shadow_mean:.6f}")
                print(f"Shadow std: {shadow_std:.6f}")
                print(f"Shadow max: {shadow_max:.6f}")
                print(f"Shadow threshold: {shadow_threshold:.6f}")
                print(f"Real importances: {real_imp}")
                print(f"Shadow importances: {shadow_imp}")

            active_features = np.where(dec_reg >= 0)[0]
            hits = real_imp > (shadow_threshold * 1.2)
            hit_reg[active_features[hits]] += 1

            imp = np.zeros(len(dec_reg))
            imp[:] = np.nan
            imp[active_features] = real_imp
            importance_history.append(imp)

            dec_reg = self._do_statistical_test(hit_reg, dec_reg, iteration)

            if self.early_stopping:
                if last_dec_reg is not None and np.array_equal(dec_reg, last_dec_reg):
                    no_change_count += 1
                    if no_change_count >= self.n_iter_no_change:
                        if self.verbose:
                            print(f"Early stopping at iteration {iteration}")
                        break
                else:
                    no_change_count = 0
                last_dec_reg = dec_reg.copy()

            if np.all(dec_reg != 0):
                if self.verbose:
                    print(f"All features decided at iteration {iteration}")
                break

        confirmed = np.where(dec_reg == 1)[0]
        tentative = np.where(dec_reg == 0)[0]

        if len(tentative) > 0:
            tentative_median = np.nanmedian(
                np.array(importance_history)[:, tentative], axis=0
            )
            shadow_median = np.median(shadow_max_history)
            shadow_median_std = np.std(shadow_max_history)
            tentative_threshold = shadow_median + 2 * shadow_median_std
            max_importance = np.max(np.nanmedian(np.array(importance_history), axis=0))
            relative_threshold = max_importance * 0.3

            tentative_confirmed = tentative[
                (tentative_median > tentative_threshold)
                & (tentative_median > relative_threshold)
            ]
            tentative = tentative[
                (tentative_median <= tentative_threshold)
                | (tentative_median <= relative_threshold)
            ]

            confirmed = np.concatenate([confirmed, tentative_confirmed])

        self.support_ = np.zeros(n_features, dtype=bool)
        self.support_[confirmed] = True
        self.support_weak_ = np.zeros(n_features, dtype=bool)
        self.support_weak_[tentative] = True

        self.ranking_ = np.ones(n_features, dtype=int) * 3
        self.ranking_[confirmed] = 1
        self.ranking_[tentative] = 2

        self.n_features_ = confirmed.shape[0]
        self.feature_names_ = X.columns.tolist()
        self.importance_history_ = np.array(importance_history)

        if self.verbose:
            self._print_results()

        return self

    def _log_iteration_stats(  # Check this
        self,
        shadow_mean: float,
        shadow_std: float,
        shadow_max: float,
        shadow_threshold: float,
        real_imp: np.ndarray,
        shadow_imp: np.ndarray,
    ) -> None:
        """Log detailed statistics for current iteration."""
        self.logger.info(f"Shadow mean: {shadow_mean:.6f}")  # noqa: G004
        self.logger.info(f"Shadow std: {shadow_std:.6f}")  # noqa: G004
        self.logger.info(f"Shadow max: {shadow_max:.6f}")  # noqa: G004
        self.logger.info(f"Shadow threshold: {shadow_threshold:.6f}")  # noqa: G004
        self.logger.info(f"Real importances: {real_imp}")  # noqa: G004
        self.logger.info(f"Shadow importances: {shadow_imp}")  # noqa: G004

    def _check_early_stopping(
        self,
        dec_reg: np.ndarray,
        last_dec_reg: Optional[np.ndarray],
        no_change_count: int,
        iteration: int,
    ) -> bool:
        """Check if early stopping criteria are met."""
        if not self.early_stopping:
            return False

        if last_dec_reg is not None and np.array_equal(dec_reg, last_dec_reg):
            no_change_count += 1
            if no_change_count >= self.n_iter_no_change:
                if self.verbose:
                    self.logger.info(
                        f"Early stopping at iteration {iteration}"  # noqa: G004
                    )
                return True
        else:
            no_change_count = 0

        return False

    def _finalize_selection(
        self,
        X: pd.DataFrame,  # Add X as parameter
        dec_reg: np.ndarray,
        importance_history: List[np.ndarray],
        shadow_max_history: List[float],
        n_features: int,
    ) -> None:
        """Finalize feature selection results.

        Args:
            X: Input features DataFrame
            dec_reg: Decision register for features
            importance_history: History of feature importances
            shadow_max_history: History of shadow maximum values
            n_features: Number of features
        """
        confirmed = np.where(dec_reg == 1)[0]
        tentative = np.where(dec_reg == 0)[0]

        if len(tentative) > 0:
            tentative_median = np.nanmedian(
                np.array(importance_history)[:, tentative], axis=0
            )
            shadow_median = np.median(shadow_max_history)
            shadow_median_std = np.std(shadow_max_history)
            tentative_threshold = shadow_median + 2 * shadow_median_std
            max_importance = np.max(np.nanmedian(np.array(importance_history), axis=0))
            relative_threshold = max_importance * 0.3

            tentative_confirmed = tentative[
                (tentative_median > tentative_threshold)
                & (tentative_median > relative_threshold)
            ]
            tentative = tentative[
                (tentative_median <= tentative_threshold)
                | (tentative_median <= relative_threshold)
            ]

            confirmed = np.concatenate([confirmed, tentative_confirmed])

        self.support_ = np.zeros(n_features, dtype=bool)
        self.support_[confirmed] = True
        self.support_weak_ = np.zeros(n_features, dtype=bool)
        self.support_weak_[tentative] = True

        self.ranking_ = np.ones(n_features, dtype=int) * 3
        self.ranking_[confirmed] = 1
        self.ranking_[tentative] = 2

        self.n_features_ = confirmed.shape[0]
        self.feature_names_ = X.columns.tolist()
        self.importance_history_ = np.array(importance_history)

    def _prepare_catboost_data(self, X: pd.DataFrame) -> pd.DataFrame:
        """Prepare data for CatBoost by converting categorical features."""
        if (
            self.estimator_name != "catboost"
            or "cat_features" not in self.estimator_params
        ):
            return X

        X_prepared = X.copy()
        cat_features = self.estimator_params["cat_features"]
        cat_columns = (
            [X.columns[i] for i in cat_features]
            if isinstance(cat_features[0], int)
            else cat_features
        )

        for col in cat_columns:
            X_prepared[col] = X_prepared[col].astype(str)

        return X_prepared

    def _print_results(self) -> None:
        """Print feature selection results."""
        self.logger.info("\nBoruta Feature Selection Results:")
        self.logger.info(f"Selected features ({np.sum(self.support_)}):")  # noqa: G004
        if hasattr(self, "feature_names_"):
            self.logger.info(", ".join(np.array(self.feature_names_)[self.support_]))

        self.logger.info(
            f"\nTentative features ({np.sum(self.support_weak_)}):"  # noqa: G004
        )
        if hasattr(self, "feature_names_"):
            self.logger.info(
                ", ".join(np.array(self.feature_names_)[self.support_weak_])
            )

        self.logger.info(
            f"\nRejected features ({np.sum(~(self.support_ | self.support_weak_))}):"  # noqa: G004
        )
        if hasattr(self, "feature_names_"):
            self.logger.info(
                ", ".join(
                    np.array(self.feature_names_)[~(self.support_ | self.support_weak_)]
                )
            )

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Transform X by selecting chosen features."""
        if not isinstance(X, pd.DataFrame):
            raise ValueError("X must be a pandas DataFrame")
        if not hasattr(self, "support_"):
            raise FeatureSelectionError("Call fit() before transform()")
        return X.iloc[:, self.support_]

    def get_selected_features(self, include_tentative: bool = False) -> List[str]:
        """Get names of selected features."""
        if not hasattr(self, "support_"):
            raise FeatureSelectionError("Call fit() before getting selected features")
        mask = (
            self.support_ | self.support_weak_ if include_tentative else self.support_
        )
        return list(np.array(self.feature_names_)[mask])

    def get_selection_stability(self) -> pd.DataFrame:
        """Get feature selection stability metrics."""
        if not hasattr(self, "importance_history_"):
            raise FeatureSelectionError("Call fit() before checking stability")

        importance_history = pd.DataFrame(
            self.importance_history_, columns=self.feature_names_
        )

        stability = pd.DataFrame(
            {
                "mean_importance": importance_history.mean(),
                "std_importance": importance_history.std(),
                "cv": importance_history.std() / importance_history.mean(),
                "selected": self.support_,
                "tentative": self.support_weak_,
            }
        )

        return stability.sort_values("mean_importance", ascending=False)

    def compare_multiple_methods(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        method_params: Optional[Dict[str, Dict]] = None,
        scale_features: bool = True,
    ) -> Dict:
        """
        Compare feature selection results across multiple methods.

        Parameters
        ----------
        X : pd.DataFrame
            Input features DataFrame
        y : pd.Series
            Target variable Series
        method_params : dict
            Dictionary of parameter dictionaries for each method
            e.g. {"rf_params": {...}, "xgb_params": {...}}
        scale_features : bool
            Whether to scale features before selection

        Returns
        -------
        dict
            Dictionary containing results for each method
        """
        results = {}

        # Prepare methods and their parameters
        default_methods = {
            "random_forest": "rf_params",
            "xgboost": "xgb_params",
            "lightgbm": "lgb_params",
            "catboost": "cat_params",
        }

        # Use provided parameters or empty dict if none provided
        method_params = method_params or {}

        # Scale features if requested
        X_prepared = X.copy()
        if scale_features:
            scaler = StandardScaler()
            X_prepared = pd.DataFrame(
                scaler.fit_transform(X), columns=X.columns, index=X.index
            )

        # Run selection for each method
        for method_name, param_key in default_methods.items():
            if param_key in method_params:
                selector = BorutaSelector(
                    estimator_name=method_name,
                    estimator_params=method_params[param_key],
                    n_estimators="auto",
                    verbose=self.verbose,
                )

                if self.verbose:
                    print(f"\nRunning {method_name} Boruta Feature Selection...")

                selector.fit(X_prepared, y)

                selected = selector.get_selected_features()
                tentative = selector.get_selected_features(include_tentative=True)
                stability = selector.get_selection_stability()

                results[method_name] = {
                    "selected_features": selected,
                    "tentative_features": [f for f in tentative if f not in selected],
                    "n_selected": len(selected),
                    "n_tentative": len([f for f in tentative if f not in selected]),
                    "stability": stability,
                }

                if self.verbose:
                    print(f"\n{method_name} Results:")
                    print(f"Selected features ({len(selected)}):", selected)
                    print(
                        f"Tentative features ({len([f for f in tentative if f not in selected])}):",
                        [f for f in tentative if f not in selected],
                    )

        return results

    def plot_comparison_results(self, results: Dict, X: pd.DataFrame) -> None:
        """
        Plot comparison of feature selection results across methods using Matplotlib.

        Parameters
        ----------
        results : dict
            Results dictionary from compare_multiple_methods
        X : pd.DataFrame
            Original feature DataFrame for feature names
        """
        comparison_data = []

        for method, result in results.items():
            total_importance = result["stability"]["mean_importance"].sum()

            for feature in X.columns:
                status = (
                    "Selected"
                    if feature in result["selected_features"]
                    else (
                        "Tentative"
                        if feature in result["tentative_features"]
                        else "Rejected"
                    )
                )
                importance = (
                    result["stability"].loc[feature, "mean_importance"]
                    / total_importance
                    * 100
                )
                comparison_data.append(
                    {
                        "Method": method,
                        "Feature": feature,
                        "Status": status,
                        "Importance (%)": importance,
                    }
                )

        comparison_df = pd.DataFrame(comparison_data)

        fig, ax = plt.subplots(figsize=(15, 10))

        colors = {"Selected": "green", "Tentative": "orange", "Rejected": "red"}

        for status in colors.keys():  # noqa: SIM118
            subset = comparison_df[comparison_df["Status"] == status]
            ax.scatter(
                subset["Feature"],
                subset["Method"],
                s=subset["Importance (%)"] * 10,
                c=colors[status],
                label=status,
                alpha=0.6,
                edgecolors="w",
                linewidth=0.5,
            )

        ax.legend(title="Status", bbox_to_anchor=(1.05, 1), loc="upper left")
        ax.set_title("Feature Selection Comparison Across Methods")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.show()

        if self.verbose:
            print("\nTop 5 Most Important Features by Method:")
            for method in comparison_df["Method"].unique():
                method_data = comparison_df[comparison_df["Method"] == method]
                top_5 = method_data.nlargest(5, "Importance (%)")
                print(f"\n{method}:")
                for _, row in top_5.iterrows():
                    print(
                        f"{row['Feature']}: {row['Importance (%)']:.2f}% ({row['Status']})"
                    )

    def get_selection_agreement(self, results: Dict) -> Dict:
        """
        Calculate agreement statistics between different selection methods.

        Parameters
        ----------
        results : dict
            Results dictionary from compare_multiple_methods

        Returns
        -------
        dict
            Dictionary containing agreement statistics
        """
        all_selected = set.intersection(
            *[set(result["selected_features"]) for result in results.values()]
        )

        any_selected = set.union(
            *[set(result["selected_features"]) for result in results.values()]
        )

        agreement_stats = {
            "features_selected_by_all": sorted(all_selected),
            "features_selected_by_any": sorted(any_selected),
            "n_features_selected_by_all": len(all_selected),
            "n_features_selected_by_any": len(any_selected),
            "agreement_percentage": (
                len(all_selected) / len(any_selected) * 100 if any_selected else 0
            ),
        }

        if self.verbose:
            print("\nFeature Selection Agreement:")
            print(
                f"Features selected by all methods ({len(all_selected)}):",
                sorted(all_selected),
            )
            print(
                f"Features selected by at least one method ({len(any_selected)}):",
                sorted(any_selected),
            )
            print(
                f"\nSelection agreement: {agreement_stats['agreement_percentage']:.1f}%"
            )

        return agreement_stats
