from dataclasses import dataclass
from typing import Any, ClassVar, Dict, List, Optional, Union


@dataclass
class ParamRange:
    """Class to define parameter search ranges."""

    param_type: str  # 'int', 'float', or 'categorical'
    low: Union[int, float, None] = None
    high: Union[int, float, None] = None
    choices: Optional[List[Any]] = None
    log: bool = False


class ModelParams:
    """Base parameter configurations and search spaces for different models."""

    DEFAULT_PARAM_SPACES: ClassVar[Dict[str, Dict[str, ParamRange]]] = {
        "xgboost": {
            "n_estimators": ParamRange("int", 50, 500),
            "max_depth": ParamRange("int", 3, 10),
            "learning_rate": ParamRange("float", 0.01, 0.3, log=True),
            "subsample": ParamRange("float", 0.5, 1.0),
            "colsample_bytree": ParamRange("float", 0.5, 1.0),
            "min_child_weight": ParamRange("int", 1, 7),
            "gamma": ParamRange("float", 0, 0.5),
        },
        "lightgbm": {
            "n_estimators": ParamRange("int", 50, 500),
            "num_leaves": ParamRange("int", 20, 100),
            "learning_rate": ParamRange("float", 0.01, 0.3, log=True),
            "feature_fraction": ParamRange("float", 0.5, 1.0),
            "min_child_samples": ParamRange("int", 5, 100),
            "reg_alpha": ParamRange("float", 0.0, 1.0),
            "reg_lambda": ParamRange("float", 0.0, 1.0),
        },
        "catboost": {
            "iterations": ParamRange("int", 100, 1000),
            "depth": ParamRange("int", 4, 10),
            "learning_rate": ParamRange("float", 0.01, 0.3, log=True),
            "l2_leaf_reg": ParamRange("float", 1e-8, 10, log=True),
            "bagging_temperature": ParamRange("float", 0.0, 1.0),
            "random_strength": ParamRange("float", 1e-8, 10, log=True),
            "min_data_in_leaf": ParamRange("int", 1, 50),
            "leaf_estimation_iterations": ParamRange("int", 1, 10),
        },
        "random_forest": {
            "n_estimators": ParamRange("int", 50, 500),
            "max_depth": ParamRange("int", 3, 10),
            "max_features": ParamRange("float", 0.1, 1.0),
            "min_samples_split": ParamRange("int", 2, 20),
            "min_samples_leaf": ParamRange("int", 1, 10),
        },
    }

    DEFAULT_FIXED_PARAMS: ClassVar[Dict[str, Dict[str, Any]]] = {
        "xgboost": {
            "objective": "binary:logistic",
            "eval_metric": ["auc", "error"],
            "early_stopping_rounds": 50,
            "verbosity": 0,
        },
        "lightgbm": {
            "objective": "binary",
            "metric": ["auc", "binary_error"],
            "early_stopping_rounds": 10,
            "verbose": -1,
        },
        "catboost": {
            "objective": "Logloss",
            "eval_metric": "PRAUC:use_weights=False",
            "early_stopping_rounds": 10,
            "verbose": False,
            "random_seed": 42,
            "task_type": "CPU",
            "bootstrap_type": "Bayesian",
        },
        "random_forest": {
            "random_state": 42,
            "n_jobs": -1,
        },
    }

    @classmethod
    def get_param_space(
        cls,
        model_name: str,
        trial: Any,
        custom_param_ranges: Optional[Dict[str, ParamRange]] = None,
        custom_fixed_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Get parameter space for a given model, combining default and custom parameters.

        Args:
            model_name: Name of the model ('xgboost', 'lightgbm', 'catboost', or 'random_forest')
            trial: Optuna trial object
            custom_param_ranges: Custom parameter ranges to override defaults
            custom_fixed_params: Custom fixed parameters to override defaults

        Returns:
            Dictionary of parameters for the model
        """
        if model_name not in cls.DEFAULT_PARAM_SPACES:
            raise ValueError(f"Unsupported model: {model_name}")

        # Get default parameter spaces
        param_ranges = cls.DEFAULT_PARAM_SPACES[model_name].copy()

        # Update with custom parameter ranges if provided
        if custom_param_ranges:
            param_ranges.update(custom_param_ranges)

        # Convert param ranges to concrete values using trial
        params = {}
        for param_name, param_range in param_ranges.items():
            if param_range.param_type == "int":
                params[param_name] = trial.suggest_int(
                    param_name, param_range.low, param_range.high, log=param_range.log
                )
            elif param_range.param_type == "float":
                params[param_name] = trial.suggest_float(
                    param_name, param_range.low, param_range.high, log=param_range.log
                )
            elif param_range.param_type == "categorical":
                params[param_name] = trial.suggest_categorical(
                    param_name, param_range.choices
                )

        # Get fixed parameters
        fixed_params = cls.DEFAULT_FIXED_PARAMS[model_name].copy()

        # Update with custom fixed parameters if provided
        if custom_fixed_params:
            fixed_params.update(custom_fixed_params)

        # Combine tunable and fixed parameters
        params.update(fixed_params)

        return params

    @classmethod
    def get_default_param_ranges(cls, model_name: str) -> Dict[str, ParamRange]:
        """Get default parameter ranges for a model."""
        return cls.DEFAULT_PARAM_SPACES[model_name].copy()

    @classmethod
    def get_default_fixed_params(cls, model_name: str) -> Dict[str, Any]:
        """Get default fixed parameters for a model."""
        return cls.DEFAULT_FIXED_PARAMS[model_name].copy()
