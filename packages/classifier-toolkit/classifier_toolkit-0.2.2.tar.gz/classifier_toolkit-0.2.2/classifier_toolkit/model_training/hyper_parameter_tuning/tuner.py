from typing import Any, Dict, Optional

import optuna
import pandas as pd
from catboost import CatBoostClassifier
from lightgbm import LGBMClassifier
from optuna.storages import JournalFileStorage, JournalStorage
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.utils.class_weight import compute_sample_weight
from xgboost import XGBClassifier

from classifier_toolkit.model_training.utils.params import ModelParams, ParamRange


class ModelWrapper:
    """Wrapper class for different model types."""

    def __init__(self, model_name: str, params: Optional[Dict[str, Any]] = None):
        self.model_name = model_name
        self.params = params if params else {}

    def get_model(self):
        if self.model_name == "xgboost":
            params = self.params.copy()
            params["eval_metric"] = "auc"  # add here, not in fit()
            return XGBClassifier(**params)
        elif self.model_name == "lightgbm":
            return LGBMClassifier(**self.params)
        elif self.model_name == "catboost":
            return CatBoostClassifier(**self.params)
        elif self.model_name == "random_forest":
            return RandomForestClassifier(**self.params)
        else:
            raise ValueError(f"Model {self.model_name} is not supported.")


def evaluate_metrics(y_true, y_pred, y_pred_proba=None, staging=True):
    """Evaluate model performance metrics."""
    if staging:
        metrics = {
            "roc_auc": roc_auc_score(y_true, y_pred_proba),  # type: ignore
            "pr_auc": average_precision_score(y_true, y_pred_proba),  # type: ignore
        }
    else:
        metrics = {
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred),
            "recall": recall_score(y_true, y_pred),
            "f1": f1_score(y_true, y_pred),
        }
        if y_pred_proba is not None:
            metrics.update(
                {
                    "roc_auc": roc_auc_score(y_true, y_pred_proba),
                    "pr_auc": average_precision_score(y_true, y_pred_proba),
                }
            )
    return metrics


class Plotter:
    """Class for real-time plotting of model training progress."""

    def __init__(
        self,
        metric_name: str = "roc_auc",
        trial_number: Optional[int] = None,
        use_widgets: bool = False,
    ):
        """
        Initialize the Plotter.

        Parameters
        ----------
        metric_name : str, optional
            Name of the metric to plot, by default "roc_auc"
        trial_number : Optional[int], optional
            Current trial number, by default None
        use_widgets : bool, optional
            Whether to use ipywidgets for plotting, by default False
        """
        self.metric_name = metric_name
        self.trial_number = trial_number
        self.use_widgets = use_widgets
        self.train_scores = []
        self.eval_scores = []

        if use_widgets:
            try:
                import ipywidgets as widgets
                import plotly.graph_objs as go
                from IPython.display import clear_output, display

                self.widgets = widgets
                self.clear_output = clear_output
                self.display = display
                self.go = go
                self.output_widget = widgets.Output()
            except ImportError:
                print("ipywidgets not available, falling back to matplotlib")
                self.use_widgets = False
                import matplotlib.pyplot as plt

                self.plt = plt
        else:
            import matplotlib.pyplot as plt

            self.plt = plt

    def update(self, train_score: float, eval_score: float) -> None:
        """
        Update the plot with new scores.

        Parameters
        ----------
        train_score : float
            Training score
        eval_score : float
            Validation score
        """
        self.train_scores.append(train_score)
        self.eval_scores.append(eval_score)

        if self.use_widgets:
            self._update_widget_plot()
        else:
            self._update_matplotlib_plot()

    def _update_widget_plot(self) -> None:
        """Update the plot using plotly widgets."""
        self.fig = self.go.Figure()
        self.fig.add_trace(
            self.go.Scatter(y=self.train_scores, mode="lines", name="Train")
        )
        self.fig.add_trace(
            self.go.Scatter(y=self.eval_scores, mode="lines", name="Eval")
        )

        trial_info = (
            f" (Trial {self.trial_number})" if self.trial_number is not None else ""
        )
        self.fig.update_layout(
            title=f"Training Progress{trial_info} - {self.metric_name}",
            xaxis_title="Epoch",
            yaxis_title=self.metric_name,
        )

        with self.output_widget:
            self.clear_output(wait=True)
            self.display(self.fig)
            print(f"Trial {self.trial_number} - Training in progress...")
            print(f"Current epoch: {len(self.train_scores)}")

    def _update_matplotlib_plot(self) -> None:
        """Update the plot using matplotlib."""
        self.plt.clf()
        self.plt.plot(self.train_scores, label="Train")
        self.plt.plot(self.eval_scores, label="Eval")
        self.plt.title(
            f"Training Progress - {self.metric_name}"
            + (f" (Trial {self.trial_number})" if self.trial_number is not None else "")
        )
        self.plt.xlabel("Epoch")
        self.plt.ylabel(self.metric_name)
        self.plt.legend()
        self.plt.grid(True)
        self.plt.draw()
        self.plt.pause(0.01)


class Tuner:
    """Class for hyperparameter tuning using Optuna."""

    def __init__(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        cv_folds: Dict,
        model_name: str,
        n_trials: int = 5,
        custom_param_ranges: Optional[Dict[str, ParamRange]] = None,
        custom_fixed_params: Optional[Dict[str, Any]] = None,
        study_folder_name: Optional[str] = None,
        seed: int = 42,
        monitor_fold: int = 0,
        use_plotting: bool = False,
        use_widgets: bool = False,
    ):
        """
        Initialize the Tuner.

        Parameters
        ----------
        X : pd.DataFrame
            Features of the dataset
        y : pd.Series
            Target of the dataset
        cv_folds : Dict
            Cross-validation folds
        model_name : str
            Name of the model to tune ('xgboost', 'lightgbm', 'catboost', or 'random_forest')
        n_trials : int, optional
            Number of trials for hyperparameter optimization, by default 5
        custom_param_ranges : Optional[Dict[str, ParamRange]], optional
            Custom parameter ranges to override defaults, by default None
        custom_fixed_params : Optional[Dict[str, Any]], optional
            Custom fixed parameters to override defaults, by default None
        study_folder_name : Optional[str], optional
            Name of the folder where the studies will be saved, by default None
        seed : int, optional
            Random seed for reproducibility, by default 42
        monitor_fold : int, optional
            Fold to monitor during training, by default 0
        use_plotting : bool, optional
            Whether to use real-time plotting, by default False
        use_widgets : bool, optional
            Whether to use ipywidgets for plotting, by default False
        """
        self.X = X
        self.y = y
        self.cv_folds = cv_folds
        self.model_name = model_name
        self.n_trials = n_trials
        self.custom_param_ranges = custom_param_ranges
        self.custom_fixed_params = custom_fixed_params
        self.study_folder_name = study_folder_name
        self.seed = seed
        self.monitor_fold = monitor_fold
        self.use_plotting = use_plotting
        self.use_widgets = use_widgets

        # Initialize accordion for trial organization
        self.accordion = None
        self.trial_outputs = []
        if self.use_widgets and self.use_plotting:
            self._setup_accordion()

    def _setup_accordion(self):
        """Setup accordion widget for organizing trials."""
        try:
            import ipywidgets as widgets
            from IPython.display import display

            self.accordion = widgets.Accordion()
            self.trial_outputs = []
            display(self.accordion)
        except ImportError:
            print("ipywidgets not available, falling back to simple output")
            self.accordion = None

    def _add_trial_to_accordion(self, trial_number: int):
        """Add a new trial to the accordion."""
        if self.accordion is None:
            return None

        try:
            import ipywidgets as widgets

            # Create output widget for this trial
            output_widget = widgets.Output()
            self.trial_outputs.append(output_widget)

            # Update accordion children
            self.accordion.children = tuple(self.trial_outputs)

            # Set title for this trial
            self.accordion.set_title(trial_number, f"Trial {trial_number}")

            # Open the current trial
            self.accordion.selected_index = trial_number

            return output_widget
        except ImportError:
            return None

    def _update_trial_title(
        self, trial_number: int, score: float, status: str = "completed"
    ):
        """Update the accordion title with trial results."""
        if self.accordion is None:
            return

        try:
            title = f"Trial {trial_number} - {status.title()}"
            if status == "completed":
                title += f" (Score: {score:.4f})"
            self.accordion.set_title(trial_number, title)
        except Exception:
            pass

    def _get_sample_weights(self, y: pd.Series) -> pd.Series:
        """Calculate sample weights for imbalanced datasets."""
        return pd.Series(compute_sample_weight("balanced", y), index=y.index)

    def _objective(self, trial: optuna.Trial) -> float:
        """Optuna objective function for hyperparameter optimization."""
        # Get parameters for this trial
        params = ModelParams.get_param_space(
            self.model_name, trial, self.custom_param_ranges, self.custom_fixed_params
        )

        # Initialize scores for folds
        fold_scores = []

        # Create plotter if needed (skip for CatBoost - it has its own plotting)
        plotter = None
        if self.use_plotting and self.model_name != "catboost":
            # Create or get output widget for this trial
            output_widget = None
            if self.use_widgets:
                output_widget = self._add_trial_to_accordion(trial.number)
                # Update title to show trial is running
                self._update_trial_title(trial.number, 0.0, "running")

            plotter = Plotter(
                metric_name="roc_auc",
                trial_number=trial.number,
                use_widgets=self.use_widgets,
            )

            # Set the output widget if using widgets
            if self.use_widgets and output_widget:
                plotter.output_widget = output_widget

        # Train model for each fold
        for fold_idx, fold in self.cv_folds.items():
            train_idx = fold["X_train"]
            val_idx = fold["X_validation"]
            X_train, X_val = self.X.iloc[train_idx], self.X.iloc[val_idx]
            y_train, y_val = self.y.iloc[train_idx], self.y.iloc[val_idx]

            # Create and train model
            model = ModelWrapper(self.model_name, params).get_model()

            if self.model_name == "xgboost":
                if plotter and fold_idx == self.monitor_fold:
                    # For XGBoost, train with eval_set and update plotter in real-time
                    with plotter.output_widget if plotter.use_widgets else None:  # type: ignore
                        if plotter.use_widgets:
                            print(f"\nTraining model for Trial {plotter.trial_number}:")
                            print(f"Parameters: {trial.params}")

                    model.fit(
                        X_train,
                        y_train,
                        eval_set=[(X_train, y_train), (X_val, y_val)],  # type: ignore
                        verbose=False,  # type: ignore
                    )

                    # Get the evaluation results after training and simulate real-time updates
                    evals_result = model.evals_result()  # type: ignore
                    train_scores = evals_result["validation_0"]["auc"]
                    eval_scores = evals_result["validation_1"]["auc"]

                    # Update plotter with all scores to simulate real-time
                    import time

                    for train_score, eval_score in zip(train_scores, eval_scores):
                        plotter.update(train_score, eval_score)
                        time.sleep(0.05)  # Small delay for visualization

                    if plotter.use_widgets:
                        with plotter.output_widget:
                            print(
                                f"Actual epochs trained: {len(evals_result['validation_0']['auc'])}"
                            )
                            if hasattr(model, "best_iteration"):
                                print(f"Best iteration: {model.best_iteration}")  # type: ignore
                else:
                    model.fit(
                        X_train,
                        y_train,
                        eval_set=[(X_val, y_val)],  # type: ignore
                        verbose=False,  # type: ignore
                    )

            elif self.model_name == "lightgbm":
                if plotter and fold_idx == self.monitor_fold:
                    # For LightGBM, use real-time callback
                    if plotter.use_widgets:
                        with plotter.output_widget:
                            print(f"\nTraining model for Trial {plotter.trial_number}:")
                            print(f"Parameters: {trial.params}")

                    # Create a custom callback to collect metrics after each iteration
                    def collect_metrics(env):
                        iteration = env.iteration

                        # Only compute metrics occasionally to speed things up
                        if iteration % 1 == 0:
                            # Get current model
                            current_model = env.model

                            # Make predictions
                            train_preds = current_model.predict(
                                X_train,  # noqa: B023
                                num_iteration=iteration,
                            )
                            val_preds = current_model.predict(
                                X_val,  # noqa: B023
                                num_iteration=iteration,
                            )

                            # Calculate AUC
                            train_auc = roc_auc_score(y_train, train_preds)  # noqa: B023
                            val_auc = roc_auc_score(y_val, val_preds)  # noqa: B023

                            # Update plot
                            plotter.update(train_auc, val_auc)  # type: ignore

                        # Continue training
                        return False

                    # Train the model with our custom callback
                    model.fit(
                        X_train,
                        y_train,
                        eval_set=[(X_val, y_val)],  # type: ignore
                        eval_metric="auc",  # type: ignore
                        callbacks=[collect_metrics],  # type: ignore
                    )

                    if plotter.use_widgets:
                        with plotter.output_widget:
                            print(f"Actual epochs trained: {len(plotter.train_scores)}")
                            if hasattr(model, "best_iteration_"):
                                print(f"Best iteration: {model.best_iteration_}")  # type: ignore
                else:
                    model.fit(
                        X_train,
                        y_train,
                        eval_set=[(X_val, y_val)],  # type: ignore
                        eval_metric="auc",  # type: ignore
                    )

            elif self.model_name == "random_forest":
                if plotter and fold_idx == self.monitor_fold:
                    # For Random Forest, simulate progress with incremental training
                    if plotter.use_widgets:
                        with plotter.output_widget:
                            print(f"\nTraining model for Trial {plotter.trial_number}:")
                            print(f"Parameters: {trial.params}")

                    # Get the total number of trees
                    n_estimators = model.get_params()["n_estimators"]

                    # Determine the step size to create ~20 points on the plot
                    step_size = max(1, n_estimators // 20)
                    tree_counts = list(range(step_size, n_estimators + 1, step_size))
                    if n_estimators not in tree_counts:
                        tree_counts.append(n_estimators)

                    # Train models with increasing numbers of trees
                    for n_trees in tree_counts:
                        # Create a model with n_trees
                        rf_params = model.get_params()
                        rf_params["n_estimators"] = n_trees
                        temp_model = RandomForestClassifier(**rf_params)

                        # Train the model
                        temp_model.fit(X_train, y_train)

                        # Make predictions
                        train_preds = temp_model.predict_proba(X_train)[:, 1]
                        val_preds = temp_model.predict_proba(X_val)[:, 1]

                        # Calculate AUC
                        train_auc = roc_auc_score(y_train, train_preds)
                        val_auc = roc_auc_score(y_val, val_preds)

                        # Update plot
                        plotter.update(train_auc, val_auc)  # type: ignore

                        # Add a small delay for visualization
                        import time

                        time.sleep(0.1)

                    # Train the final model with all trees
                    model.fit(X_train, y_train)

                    if plotter.use_widgets:
                        with plotter.output_widget:
                            print(f"Trees trained: {n_estimators}")
                else:
                    model.fit(X_train, y_train)

            elif self.model_name == "catboost":
                # Calculate sample weights for CatBoost
                sample_weights = self._get_sample_weights(y_train)

                # For CatBoost, completely bypass custom plotting and use native display
                if fold_idx == self.monitor_fold:
                    # Use CatBoost's built-in verbose mode for live plotting
                    model.fit(
                        X_train,
                        y_train,
                        sample_weight=sample_weights,
                        eval_set=(X_val, y_val),  # type: ignore
                        verbose=True,  # Let CatBoost show its own progress # type: ignore
                        plot=True,  # Enable CatBoost's native plotting # type: ignore
                    )
                else:
                    model.fit(
                        X_train,
                        y_train,
                        sample_weight=sample_weights,
                        verbose=False,  # type: ignore
                    )

            # Evaluate model
            y_pred = model.predict(X_val)
            y_pred_proba = model.predict_proba(X_val)[:, 1]  # type: ignore
            fold_metrics = evaluate_metrics(y_val, y_pred, y_pred_proba)
            fold_scores.append(fold_metrics["roc_auc"])

            # Store metrics
            trial.set_user_attr(f"fold_{fold_idx}_metrics", fold_metrics)

        # Calculate mean score
        mean_score = sum(fold_scores) / len(fold_scores)

        # Update accordion title with final result
        if self.use_widgets and self.use_plotting:
            self._update_trial_title(trial.number, mean_score, "completed")

            # Add final summary to the trial output
            if plotter and plotter.output_widget:
                with plotter.output_widget:
                    print(f"\n=== Trial {trial.number} Summary ===")
                    print(f"Mean ROC-AUC: {mean_score:.4f}")
                    print(f"Parameters: {trial.params}")

        return mean_score

    def tune(self) -> Dict[str, Any]:
        """
        Perform hyperparameter tuning.

        Returns
        -------
        Dict[str, Any]
            Dictionary containing:
            - best_params: Best hyperparameters found
            - best_validation_score: Best validation score
            - test_metrics: Average test metrics across folds
            - study: Optuna study object
            - model: Best model trained on all data
        """
        # Create Optuna study
        if self.study_folder_name:
            storage = JournalStorage(
                JournalFileStorage(f"{self.study_folder_name}/{self.model_name}.log")
            )
            study = optuna.create_study(
                direction="maximize",
                storage=storage,
                study_name=f"hp_tuning_{self.model_name}",
                pruner=optuna.pruners.MedianPruner(),
            )
        else:
            study = optuna.create_study(
                direction="maximize",
                pruner=optuna.pruners.MedianPruner(),
            )

        # Optimize hyperparameters
        study.optimize(self._objective, n_trials=self.n_trials)

        # Get best model with optimized parameters
        best_params = study.best_params
        # Add fixed parameters to best parameters
        fixed_params = ModelParams.get_default_fixed_params(self.model_name)
        if self.custom_fixed_params:
            fixed_params.update(self.custom_fixed_params)
        best_params.update(fixed_params)

        best_model = ModelWrapper(self.model_name, best_params).get_model()

        # Evaluate on test set for each fold
        test_metrics_per_fold = []

        for _, fold in self.cv_folds.items():
            # Get indices
            train_idx = fold["X_train"]
            test_idx = fold["X_test"]

            # Split data
            X_train, X_test = self.X.iloc[train_idx], self.X.iloc[test_idx]
            y_train, y_test = self.y.iloc[train_idx], self.y.iloc[test_idx]

            # Train and evaluate
            if self.model_name == "xgboost":
                eval_set = [(X_test, y_test)]
                best_model.fit(X_train, y_train, eval_set=eval_set, verbose=False)  # type: ignore
            elif self.model_name == "lightgbm":
                eval_set = [(X_test, y_test)]
                best_model.fit(X_train, y_train, eval_set=eval_set, callbacks=None)  # type: ignore
            elif self.model_name == "catboost":
                eval_set = (X_test, y_test)
                sample_weights = self._get_sample_weights(y_train)
                best_model.fit(
                    X_train,
                    y_train,
                    sample_weight=sample_weights,
                    eval_set=eval_set,  # type: ignore
                    verbose=False,  # type: ignore
                )
            else:
                best_model.fit(X_train, y_train)

            # Get predictions
            y_pred = best_model.predict(X_test)
            y_pred_proba = best_model.predict_proba(X_test)[:, 1]  # type: ignore

            # Calculate and store metrics
            test_metrics = evaluate_metrics(y_test, y_pred, y_pred_proba)
            test_metrics_per_fold.append(test_metrics)

        # Calculate average test metrics across folds
        avg_test_metrics = {}
        for metric in test_metrics_per_fold[0]:
            avg_test_metrics[metric] = sum(
                fold_metrics[metric] for fold_metrics in test_metrics_per_fold
            ) / len(test_metrics_per_fold)

        return {
            "best_params": best_params,
            "best_validation_score": study.best_value,
            "test_metrics": avg_test_metrics,
            "study": study,
            "model": best_model,
        }
