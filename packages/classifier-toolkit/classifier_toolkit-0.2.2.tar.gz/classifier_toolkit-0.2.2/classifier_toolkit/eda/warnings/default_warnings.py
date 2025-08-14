from typing import Dict, List, Optional, Protocol

import numpy as np
import pandas as pd
from scipy import stats


class EDAWarning(Protocol):
    df: pd.DataFrame

    def run(self) -> List[Dict[str, str]]: ...


class NegativeValuesWarning:
    def __init__(
        self,
        df: pd.DataFrame,
        numerical_columns: Optional[List[str]] = None,
        can_be_negative: Optional[List[str]] = None,
    ):
        self.df = df
        self.numerical_columns = numerical_columns
        self.can_be_negative = can_be_negative

    def run(self) -> List[Dict[str, str]]:
        warnings = []
        if self.numerical_columns:
            for col in self.numerical_columns:
                if (
                    self.can_be_negative is None or col not in self.can_be_negative
                ) and (self.df[col] < 0).any():
                    neg_count = (self.df[col] < 0).sum()
                    warnings.append(
                        {
                            "warning_type": "Negative",
                            "message": f"Negative values found in column '{col}' ({neg_count} negative values)",
                        }
                    )
        return warnings


class OutliersWarning:
    def __init__(
        self, df: pd.DataFrame, numerical_columns: List[str], distance: float = 1.5
    ):
        self.df = df
        self.numerical_columns = numerical_columns
        self.distance = distance

    def run(self) -> List[Dict[str, str]]:
        warnings = []
        for col in self.numerical_columns:
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - self.distance * IQR
            upper_bound = Q3 + self.distance * IQR
            outliers = self.df[
                (self.df[col] < lower_bound) | (self.df[col] > upper_bound)
            ]
            if not outliers.empty:
                warnings.append(
                    {
                        "warning_type": "Outlier",
                        "message": f"Outliers detected in column '{col}' ({len(outliers)} outliers)",
                    }
                )
        return warnings


class MissingValuesWarning:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def run(self) -> List[Dict[str, str]]:
        missing = self.df.isnull().sum()
        if missing.sum() > 0:
            return [
                {
                    "warning_type": "data_quality",
                    "message": f"Missing values detected in columns: {missing[missing > 0].index.tolist()}",
                }
            ]
        return []


class CardinalityWarning:
    def __init__(
        self,
        df: pd.DataFrame,
        numerical_columns: List[str],
        exclusion: List[str],
        low_threshold: int = 10,
    ):
        self.df = df
        self.numerical_columns = numerical_columns
        self.exclusion = exclusion
        self.low_threshold = low_threshold

    def run(self) -> List[Dict[str, str]]:
        warnings = []
        for col in self.df.columns:
            if col not in self.numerical_columns and col not in self.exclusion:
                value_counts = len(self.df[col].value_counts())
                if value_counts == 1:
                    warnings.append(
                        {
                            "warning_type": "Cardinality",
                            "message": f"Column '{col}' has only one unique value",
                        }
                    )
                elif value_counts <= self.low_threshold:
                    warnings.append(
                        {
                            "warning_type": "Cardinality",
                            "message": f"Low cardinality in column '{col}' ({value_counts} unique values)",
                        }
                    )
                else:
                    warnings.append(
                        {
                            "warning_type": "Cardinality",
                            "message": f"High cardinality in column '{col}' ({value_counts} unique values)",
                        }
                    )
        return warnings


class DuplicatesWarning:
    def __init__(self, df: pd.DataFrame, id_column: Optional[str] = None):
        self.df = df
        self.id_column = id_column

    def run(self) -> List[Dict[str, str]]:
        warnings = []
        if self.id_column:
            duplicates = self.df[
                self.df.duplicated(subset=[self.id_column], keep=False)
            ]
            if not duplicates.empty:
                warnings.append(
                    {
                        "warning_type": "Duplicate",
                        "message": f"{len(duplicates)} duplicate entries found based on '{self.id_column}'",
                    }
                )
        else:
            duplicates = self.df[self.df.duplicated(keep=False)]
            if not duplicates.empty:
                warnings.append(
                    {
                        "warning_type": "Duplicate",
                        "message": f"{len(duplicates)} duplicate rows found",
                    }
                )
        return warnings


class NormalityWarning:
    def __init__(
        self,
        df: pd.DataFrame,
        numerical_columns: List[str],
        significance_level: float = 0.05,
    ):
        self.df = df
        self.numerical_columns = numerical_columns
        self.significance_level = significance_level

    def run(self) -> List[Dict[str, str]]:
        warnings = []
        for col in self.numerical_columns:
            _, p_value = stats.normaltest(self.df[col].dropna())
            if p_value < self.significance_level:
                warnings.append(
                    {
                        "warning_type": "Normality",
                        "message": f"Column '{col}' may not be normally distributed (p-value: {p_value:.4f})",
                    }
                )
        return warnings


class ImbalanceWarning:
    def __init__(self, df: pd.DataFrame, target_column: str, threshold: float = 0.75):
        self.df = df
        self.target_column = target_column
        self.threshold = threshold

    def run(self) -> List[Dict[str, str]]:
        warnings = []
        if self.target_column in self.df.columns:
            value_counts = self.df[self.target_column].value_counts(normalize=True)
            if (value_counts > self.threshold).any():  # type: ignore
                majority_class = value_counts.index[0]
                majority_percentage = value_counts.iloc[0] * 100
                warnings.append(
                    {
                        "warning_type": "Imbalance",
                        "message": f"Target variable '{self.target_column}' is imbalanced. "
                        f"Majority class '{majority_class}' represents {majority_percentage:.2f}% of the data",
                    }
                )
        return warnings


class CorrelationsWarning:
    def __init__(
        self, df: pd.DataFrame, numerical_columns: List[str], threshold: float = 0.8
    ):
        self.df = df
        self.numerical_columns = numerical_columns
        self.threshold = threshold

    def run(self) -> List[Dict[str, str]]:
        warnings = []
        if len(self.numerical_columns) > 1:
            corr_matrix = self.df[self.numerical_columns].corr()
            high_corr = np.where(np.abs(corr_matrix) > self.threshold)
            high_corr_pairs = [
                (corr_matrix.index[x], corr_matrix.columns[y])
                for x, y in zip(*high_corr)
                if x != y and x < y
            ]
            for pair in high_corr_pairs:
                warnings.append(
                    {
                        "warning_type": "Correlation",
                        "message": f"High correlation ({corr_matrix.loc[pair[0], pair[1]]:.2f}) "
                        f"between '{pair[0]}' and '{pair[1]}'",
                    }
                )
        return warnings


def get_default_warnings(
    df: pd.DataFrame,
    target_column: str,
    can_be_negative: List[str],
    numerical_columns: List[str],
    cardinality_exclusion: List[str],
    correlation_threshold: float = 0.8,
    outlier_distance: float = 1.5,
    imbalance_threshold: float = 0.75,
    normality_significance_level: float = 0.05,
    cardinality_low_threshold: int = 10,
    id_column: Optional[str] = None,
) -> Dict[str, EDAWarning]:
    return {
        "negative_values": NegativeValuesWarning(
            df,
            numerical_columns=numerical_columns,
            can_be_negative=can_be_negative,
        ),
        "outliers": OutliersWarning(
            df,
            numerical_columns=numerical_columns,
            distance=outlier_distance,
        ),
        "missing_values": MissingValuesWarning(df),
        "cardinality": CardinalityWarning(
            df,
            numerical_columns=numerical_columns,
            exclusion=cardinality_exclusion,
            low_threshold=cardinality_low_threshold,
        ),
        "duplicates": DuplicatesWarning(
            df,
            id_column=id_column,
        ),
        "normality": NormalityWarning(
            df,
            numerical_columns=numerical_columns,
            significance_level=normality_significance_level,
        ),
        "imbalance": ImbalanceWarning(
            df,
            target_column=target_column,
            threshold=imbalance_threshold,
        ),
        "correlations": CorrelationsWarning(
            df,
            numerical_columns=numerical_columns,
            threshold=correlation_threshold,
        ),
    }
