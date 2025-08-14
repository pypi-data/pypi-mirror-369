from typing import Callable, Dict, Union

import numpy as np
from numpy.typing import ArrayLike, NDArray
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    make_scorer,
    precision_score,
    recall_score,
    roc_auc_score,
)

# Define scorers with updated best practices
SCORERS = {
    "accuracy": make_scorer(accuracy_score),
    "f1": make_scorer(f1_score, average="weighted"),
    "precision": make_scorer(precision_score, average="weighted"),
    "recall": make_scorer(recall_score, average="weighted"),
    "roc_auc": make_scorer(roc_auc_score, response_method="predict_proba"),
    "average_precision": make_scorer(
        average_precision_score, response_method="predict_proba"
    ),
}

# Keep the original scoring functions for backward compatibility
SCORING_FUNCTIONS: Dict[str, Callable] = {
    "accuracy": accuracy_score,
    "f1": f1_score,
    "precision": precision_score,
    "recall": recall_score,
    "roc_auc": roc_auc_score,
    "average_precision": average_precision_score,
}


def get_scorer(metric: Union[str, Callable]) -> Callable:
    """
    Get a scorer function for the specified metric.

    Parameters
    ----------
    metric : Union[str, Callable]
        The metric to use for scoring. Can be a string identifier or a callable.

    Returns
    -------
    Callable
        A scorer function compatible with scikit-learn.

    Raises
    ------
    ValueError
        If the metric is not recognized.
    """
    if isinstance(metric, str):
        if metric in SCORERS:
            return SCORERS[metric]
        elif metric in SCORING_FUNCTIONS:
            # For backward compatibility
            return make_scorer(SCORING_FUNCTIONS[metric])
        else:
            raise ValueError(
                f"Unrecognized metric: {metric}. Available metrics are: {', '.join(SCORERS.keys())}"
            )
    elif callable(metric):
        return make_scorer(metric)
    else:
        raise ValueError("metric must be either a string or a callable")


def false_positive_rate(y_true: ArrayLike, y_pred: ArrayLike) -> float:
    """
    Calculate the false positive rate.

    Parameters
    ----------
    y_true : ArrayLike
        True labels.
    y_pred : ArrayLike
        Predicted labels.

    Returns
    -------
    float
        False positive rate.
    """
    tn, fp, _, _ = confusion_matrix(y_true, y_pred).ravel()
    return fp / (fp + tn)


def true_positive_rate(
    y_true: ArrayLike, y_pred: ArrayLike
) -> Union[float, NDArray[np.float64]]:
    """
    Calculate the true positive rate (recall/sensitivity).

    Parameters
    ----------
    y_true : ArrayLike
        True labels.
    y_pred : ArrayLike
        Predicted labels.

    Returns
    -------
    Union[float, NDArray[np.float64]]
        True positive rate.
    """
    return recall_score(y_true, y_pred)  # type: ignore


# Add custom scorers for FPR and TPR
SCORERS["fpr"] = make_scorer(false_positive_rate, greater_is_better=False)
SCORERS["tpr"] = make_scorer(true_positive_rate, greater_is_better=True)

# Add to SCORING_FUNCTIONS for backward compatibility
SCORING_FUNCTIONS["fpr"] = false_positive_rate
SCORING_FUNCTIONS["tpr"] = true_positive_rate
