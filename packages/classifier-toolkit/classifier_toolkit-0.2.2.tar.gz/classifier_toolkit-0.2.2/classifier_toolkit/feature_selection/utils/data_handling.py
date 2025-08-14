from typing import Dict, List, Literal, Optional, Tuple

import numpy as np
import pandas as pd
from catboost import Pool
from sklearn.model_selection import KFold, train_test_split

from classifier_toolkit.eda.feature_engineering import FeatureEngineering


def create_cross_validation_folds(
    X: pd.DataFrame,
    y: pd.Series,
    n_splits: int = 5,
    test_size: float = 0.2,
    random_state: int = 42,
) -> Dict:
    """
    Create cross-validation folds with train, validation, and test indices.

    Parameters
    ----------
    X : pd.DataFrame
        The feature matrix.
    y : pd.Series
        The target variable.
    n_splits : int, optional
        Number of folds, by default 5.
    test_size : float, optional
        Proportion of dataset to include in test split, by default 0.2.
    random_state : int, optional
        Random state for reproducibility, by default 42.

    Returns
    -------
    Dict
        Dictionary containing train, validation, and test indices for each fold.
    """
    # Create an array of indices
    indices = np.arange(len(X))

    # First, split the data into train+val and test
    trainval_indices, test_indices = train_test_split(
        indices, test_size=test_size, random_state=random_state, stratify=y
    )

    # Initialize KFold
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)

    cv_folds = {}

    # Create folds
    for fold, (train_idx, val_idx) in enumerate(kf.split(trainval_indices)):
        # Convert to actual indices in the original dataset
        train_indices = trainval_indices[train_idx]
        val_indices = trainval_indices[val_idx]

        cv_folds[fold] = {
            "X_train": train_indices,
            "y_train": train_indices,  # Using same indices for X and y
            "X_validation": val_indices,
            "y_validation": val_indices,  # Using same indices for X and y
            "X_test": test_indices,
            "y_test": test_indices,  # Using same indices for X and y
        }

    return cv_folds


def encode_datasets(
    X: pd.DataFrame,
    y: pd.Series,
    cv_folds: Dict,
    target_col: str,
    features_num: List[str],
    features_cat: List[str],
    encoding_method: Literal[
        "one_hot", "distribution", "woe", "catboost"
    ] = "distribution",
    verbose: bool = False,
) -> Tuple[pd.DataFrame, pd.Series, Dict]:
    """
    Encode datasets using the specified encoding method.

    Parameters
    ----------
    X : pd.DataFrame
        The feature matrix.
    y : pd.Series
        The target variable.
    cv_folds : Dict
        Cross-validation fold indices.
    target_col : str
        Name of the target column.
    features_num : List[str]
        List of numerical feature names.
    features_cat : List[str]
        List of categorical feature names.
    encoding_method : {'one_hot', 'distribution', 'woe', 'catboost'}, optional
        Method to use for encoding, by default 'distribution'.
    verbose : bool, optional
        Whether to print progress information, by default False.

    Returns
    -------
    Tuple[pd.DataFrame, pd.Series, Dict]
        Encoded features, target variable, and updated cross-validation folds.
    """
    encoded_df = X.copy()

    for i, fold in cv_folds.items():
        print(f"Encoding fold {i}")
        # Create train pool with target
        train_pool = X.iloc[fold["X_train"]].copy()
        train_pool[target_col] = y.iloc[fold["y_train"]]

        # Initialize FeatureEngineering with train data
        fe = FeatureEngineering(train_pool, target_col, features_num, features_cat)

        # Encode train data
        encoded_train = fe.encoding_categorical(
            encoding_method, fit=True, verbose=verbose
        )
        encoded_df.loc[fold["X_train"], features_cat] = encoded_train[features_cat]

        # Encode validation data
        eval_pool = X.iloc[fold["X_validation"]].copy()
        eval_pool[target_col] = y.iloc[fold["y_validation"]]
        encoded_eval = fe.encoding_categorical(
            encoding_method, data=eval_pool, fit=False, verbose=verbose
        )
        encoded_df.loc[fold["X_validation"], features_cat] = encoded_eval[features_cat]

        # Encode test data
        test_pool = X.iloc[fold["X_test"]].copy()
        test_pool[target_col] = y.iloc[fold["y_test"]]
        encoded_test = fe.encoding_categorical(
            encoding_method, data=test_pool, fit=False, verbose=verbose
        )
        encoded_df.loc[fold["X_test"], features_cat] = encoded_test[features_cat]

    # Convert object columns to numeric
    object_columns = encoded_df.select_dtypes(include=["object"]).columns
    encoded_df[object_columns] = (
        encoded_df[object_columns]
        .apply(pd.to_numeric, errors="coerce")
        .astype("float64")
    )

    return encoded_df, y, cv_folds


def prepare_data_for_modeling(
    X: pd.DataFrame,
    y: pd.Series,
    y_name: str,
    n_splits: int = 5,
    test_size: float = 0.2,
    random_state: int = 42,
    encoding_method: Literal[
        "one_hot", "distribution", "woe", "catboost"
    ] = "distribution",
    numerical_features: Optional[List[str]] = None,
    categorical_features: Optional[List[str]] = None,
    verbose: bool = False,
) -> Tuple[pd.DataFrame, pd.Series, Dict]:
    """Prepare data for modeling by creating cross-validation folds and encoding datasets.

    Parameters
    ----------
    X : pd.DataFrame
        The feature dataframe.
    y : pd.Series
        The target series.
    n_splits : int
        Number of cross-validation splits.
    test_size : float
        Proportion of data to use for testing.
    random_state : int
        Random state for reproducibility.
    encoding_method : str
        Method to use for encoding categorical variables.

    Returns
    -------
    tuple
        A tuple containing:
        - pd.DataFrame : Encoded X
        - pd.Series : Encoded y
        - dict : Encoded cv_folds
    """
    cv_folds = create_cross_validation_folds(X, y, n_splits, test_size, random_state)

    features_num = (
        X.select_dtypes(include=["int64", "float64"]).columns.tolist()
        if numerical_features is None
        else numerical_features
    )
    features_cat = (
        X.select_dtypes(include=["object", "category"]).columns.tolist()
        if categorical_features is None
        else categorical_features
    )

    encoded_X, encoded_y, encoded_cv_folds = encode_datasets(
        X,
        y,
        cv_folds,
        y_name,
        features_num,
        features_cat,
        encoding_method,
        verbose=verbose,
    )

    return encoded_X, encoded_y, encoded_cv_folds


def create_catboost_pools(
    X: pd.DataFrame,
    y: pd.Series,
    cv_folds: Dict,
    cat_features: List[str],
    fold_index: int = 0,
) -> Dict[str, Pool]:
    """Create CatBoost Pool objects for train, validation, and test sets."""
    # Get indices for the specified fold
    train_indices = cv_folds[fold_index]["X_train"]
    val_indices = cv_folds[fold_index]["X_validation"]
    test_indices = cv_folds[fold_index]["X_test"]

    # Create X and y subsets
    X_train = X.iloc[train_indices]
    y_train = y.iloc[train_indices]
    X_val = X.iloc[val_indices]
    y_val = y.iloc[val_indices]
    X_test = X.iloc[test_indices]
    y_test = y.iloc[test_indices]

    # Get categorical feature indices relative to current feature set
    cat_feature_indices = [i for i, col in enumerate(X.columns) if col in cat_features]

    # Create Pool objects with correct categorical feature indices
    train_pool = Pool(data=X_train, label=y_train, cat_features=cat_feature_indices)
    eval_pool = Pool(data=X_val, label=y_val, cat_features=cat_feature_indices)
    test_pool = Pool(data=X_test, label=y_test, cat_features=cat_feature_indices)

    return {
        "train_pool": train_pool,
        "eval_pool": eval_pool,
        "test_pool": test_pool,
    }


def basic_encoder(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
    target_col: str,
    features_num: list,
    features_cat: list,
    encoding_method: Literal[
        "one_hot", "distribution", "woe", "catboost"
    ] = "distribution",
    verbose: bool = False,
):
    encoded_train = X_train.copy()
    encoded_train[target_col] = y_train

    encoded_test = X_test.copy()
    encoded_test[target_col] = y_test

    fe = FeatureEngineering(encoded_train, target_col, features_num, features_cat)

    # Encode train data
    encoded_train = fe.encoding_categorical(encoding_method, fit=True, verbose=verbose)
    encoded_train[features_cat] = encoded_train[features_cat]

    # Encode test data
    encoded_test = fe.encoding_categorical(
        encoding_method, data=encoded_test, fit=False, verbose=verbose
    )

    encoded_test[features_cat] = encoded_test[features_cat]

    return encoded_train, encoded_test
