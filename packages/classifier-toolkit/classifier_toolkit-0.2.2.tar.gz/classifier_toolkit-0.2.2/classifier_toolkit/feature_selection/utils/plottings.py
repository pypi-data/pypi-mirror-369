from typing import List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from classifier_toolkit.feature_selection.base import BaseFeatureSelector


def plot_prauc(feature_count: int, prauc_scores: List[float], model_name: str) -> None:
    """
    Plot PRAUC scores against number of features.

    Parameters
    ----------
    feature_count : int
        Total number of features.
    prauc_scores : List[float]
        List of PRAUC scores.
    model_name : str
        Name of the model used.
    """
    plt.figure(figsize=(10, 6))
    plt.plot(range(feature_count, 1, -1), prauc_scores)
    plt.xlabel("Number of Features Kept")
    plt.ylabel("Average PRAUC")
    plt.title(f"{model_name} PRAUC vs Number of Features Kept")
    plt.grid(True)
    plt.show()


def plot_feature_importances(selector: BaseFeatureSelector) -> None:
    """
    Plot feature importance scores.

    Parameters
    ----------
    selector : BaseFeatureSelector
        Fitted feature selector instance.
    """
    importances = selector.get_feature_importances().sort_values(ascending=True)
    selected_features = set(selector.selected_features_)  # type: ignore

    plt.figure(figsize=(10, max(8, len(importances) * 0.3)))
    y_pos = np.arange(len(importances))

    colors = [
        "#03fc49" if feature in selected_features else "#FFD6BE"
        for feature in importances.index
    ]

    plt.barh(y_pos, np.array(importances.values), color=colors)
    plt.yticks(y_pos, importances.index.astype(str).tolist())
    plt.xlabel("Importance")
    plt.title("Feature Importances")
    plt.tight_layout()
    plt.show()


def plot_rfecv_results(selector: BaseFeatureSelector) -> None:
    assert hasattr(
        selector, "rfecv"
    ), "This plot is only available for RFECV-based selectors."
    assert (
        selector.rfecv is not None
    ), "RFECV results are not available. Make sure to fit the selector first."
    assert hasattr(
        selector.rfecv, "cv_results_"
    ), "The selector's RFECV doesn't have cv_results_. Make sure to fit the selector first."

    n_features_total = len(selector.get_feature_importances())

    grid_scores = selector.rfecv.cv_results_["mean_test_score"]
    std_errors = selector.rfecv.cv_results_["std_test_score"]

    n_features = np.arange(1, n_features_total + 1)

    plt.figure(figsize=(12, 6))
    plt.title("Feature Selection using RFECV")
    plt.xlabel("Number of features selected")
    plt.ylabel("Cross-validation score")
    plt.plot(n_features, grid_scores)
    plt.fill_between(
        n_features, grid_scores - std_errors, grid_scores + std_errors, alpha=0.2
    )
    plt.axvline(
        selector.rfecv.n_features_,
        color="red",
        linestyle="--",
        label=f"Optimal number of features ({selector.rfecv.n_features_})",
    )
    plt.legend()
    plt.tight_layout()
    plt.show()

    # Plot feature importances
    importances = selector.get_feature_importances().sort_values(ascending=False)
    selected_features = set(selector.selected_features_)  # type: ignore

    plt.figure(figsize=(12, 8))
    plt.title("Feature Importances")

    colors = [
        "#03fc49" if feature in selected_features else "#FFD6BE"
        for feature in importances.index
    ]

    importances.plot(kind="bar", color=colors)
    plt.xlabel("Features")
    plt.ylabel("Importance")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()


def plot_exhaustive_search_results(
    best_features_list: List[List[str]], scores: List[float], static: bool = False
) -> None:
    """
    Plot results from exhaustive feature search.

    Parameters
    ----------
    best_features_list : List[List[str]]
        List of best feature combinations.
    scores : List[float]
        Corresponding scores for each feature combination.
    static : bool, optional
        Whether to create a static plot, by default False.
    """
    n_features = [len(features) for features in best_features_list]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=n_features,
            y=scores,
            mode="lines+markers",
            name="Performance",
            hovertemplate="<b>Number of features</b>: %{x}<br>"
            + "<b>Score</b>: %{y:.4f}<br>"
            + "<b>Features</b>: %{text}",
            text=[", ".join(features) for features in best_features_list],
        )
    )

    fig.update_layout(
        title="Exhaustive Search Results",
        xaxis_title="Number of Features",
        yaxis_title="Performance Score",
        hovermode="closest",
    )

    fig.show()

    if static:
        plt.figure(figsize=(12, 6))
        plt.plot(n_features, scores, marker="o")
        plt.title("Exhaustive Search Results")
        plt.xlabel("Number of Features")
        plt.ylabel("Performance Score")
        plt.grid(True)
        plt.tight_layout()
        plt.show()


def marginal_feature_importance(
    feature_count: int, prauc_scores: List[float]
) -> pd.DataFrame:
    df = pd.DataFrame(
        {"Feature_Count": range(feature_count, 0, -1), "PRAUC_Score": prauc_scores}
    )

    df = df.iloc[::-1].reset_index(drop=True)

    df["Percentage_Difference"] = df["PRAUC_Score"].pct_change() * 100

    df["Percentage_Difference"] = df["Percentage_Difference"].apply(
        lambda x: f"{x:.2f}%" if pd.notnull(x) else "N/A"
    )
    return df


def plot_marginal_feature_importance(
    feature_count: int, prauc_scores: List[float]
) -> None:
    df = marginal_feature_importance(feature_count, prauc_scores)

    plt.figure(figsize=(12, 6))
    plt.plot(df["Feature_Count"], df["PRAUC_Score"], marker="o")
    plt.title("Marginal Feature Importance")
    plt.xlabel("Number of Features")
    plt.ylabel("PRAUC Score")
    plt.grid(True)

    for i, row in df.iterrows():
        if i > 0:  # type: ignore # Skip the first point as it doesn't have a percentage difference
            plt.annotate(
                f"{row['Percentage_Difference']}",
                (row["Feature_Count"], row["PRAUC_Score"]),
                textcoords="offset points",
                xytext=(0, 10),
                ha="center",
            )

    plt.tight_layout()
    plt.show()
