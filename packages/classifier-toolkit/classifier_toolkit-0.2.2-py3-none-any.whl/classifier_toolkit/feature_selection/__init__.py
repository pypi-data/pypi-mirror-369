"""Feature selection public API with lazy imports to avoid heavy dependencies at import time.

This module exposes a stable public API while delaying imports of optional heavy
backends (e.g., LightGBM, XGBoost, CatBoost, Matplotlib) until the corresponding
symbols are actually accessed. This prevents import-time failures in
environments where optional system libraries are not present and speeds up
package import for utilities.
"""

from importlib import import_module
from typing import Any, Dict

_EXPORTS: Dict[str, str] = {
    # Core/base and meta
    "BaseFeatureSelector": "classifier_toolkit.feature_selection.base",
    "MetaSelector": "classifier_toolkit.feature_selection.meta_selector",
    "FeatureStability": "classifier_toolkit.feature_selection.feature_stability",
    # Embedded methods
    "ElasticNetLogisticSelector": "classifier_toolkit.feature_selection.embedded_methods.elastic_net",
    # Utils
    "plot_feature_importances": "classifier_toolkit.feature_selection.utils.plottings",
    "plot_rfecv_results": "classifier_toolkit.feature_selection.utils.plottings",
    "get_scorer": "classifier_toolkit.feature_selection.utils.scoring",
    "false_positive_rate": "classifier_toolkit.feature_selection.utils.scoring",
    "true_positive_rate": "classifier_toolkit.feature_selection.utils.scoring",
    # Wrapper methods
    "BayesianFeatureSelector": "classifier_toolkit.feature_selection.wrapper_methods.bayesian_search",
    "BorutaSelector": "classifier_toolkit.feature_selection.wrapper_methods.boruta",
    "RFESelector": "classifier_toolkit.feature_selection.wrapper_methods.rfe",
    "RFECatBoostSelector": "classifier_toolkit.feature_selection.wrapper_methods.rfe_catboost",
    "SequentialSelector": "classifier_toolkit.feature_selection.wrapper_methods.sequential_selection",
}

__all__ = list(_EXPORTS.keys())


def __getattr__(name: str) -> Any:  # pragma: no cover - simple lazy loader
    """Dynamically import and return the requested symbol on first access.

    This keeps the package import light and avoids importing optional
    dependencies unless they are actually needed by the user.
    """
    module_path = _EXPORTS.get(name)
    if module_path is None:
        raise AttributeError(
            f"module 'classifier_toolkit.feature_selection' has no attribute '{name}'"
        )

    module = import_module(module_path)
    try:
        return getattr(module, name)
    except AttributeError as exc:  # Provide a clearer error if symbol moved/renamed
        raise AttributeError(
            f"'{name}' not found in '{module_path}'. The public API mapping may be outdated."
        ) from exc


def __dir__():  # pragma: no cover - trivial
    return sorted(list(globals().keys()) + __all__)
