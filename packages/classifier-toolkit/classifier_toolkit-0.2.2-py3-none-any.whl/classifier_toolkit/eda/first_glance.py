from typing import List, Optional

import pandas as pd
from colorama import Fore, Style, init
from tabulate import tabulate

init(autoreset=True)  # Initialize colorama


class FirstGlance:
    def __init__(
        self,
        dataframe: pd.DataFrame,
        numerical_columns: Optional[List[str]],
        categorical_columns: Optional[List[str]],
        exclude_columns: Optional[List[str]] = None,
        id_column: Optional[str] = None,
    ) -> None:
        """
        Initialize the FirstGlance class with data and configuration.

        Parameters
        ----------
        dataframe : pd.DataFrame
            The data to be analyzed.
        numerical_columns : Optional[List[str]]
            List of numerical columns.
        categorical_columns : Optional[List[str]]
            List of categorical columns.
        exclude_columns : Optional[List[str]], optional
            List of columns to exclude from analysis, by default None.
        id_column : Optional[str], optional
            Column to identify duplicates, by default None.
        """
        self.data = dataframe
        self.numerical_columns = numerical_columns or []
        self.categorical_columns = categorical_columns or []
        self.exclude_columns = exclude_columns or []
        self.id_column = id_column

        # Define the numerical and categorical columns using the _get_analysis_columns method
        self.numerical_columns = self._get_analysis_columns(numerical_columns)
        self.categorical_columns = self._get_analysis_columns(categorical_columns)
        self.columns = self._get_analysis_columns()

    def _get_analysis_columns(self, column_list: Optional[List] = None) -> List[str]:
        """
        Get the columns to analyze based on the provided column list.

        Parameters
        ----------
        column_list : Optional[List], optional
            List of columns to analyze, by default None.

        Returns
        -------
        List[str]
            List of columns to analyze.
        """
        if column_list is None:
            return [col for col in self.data.columns if col not in self.exclude_columns]
        else:
            return [col for col in column_list if col not in self.exclude_columns]

    def generate_first_glance(self) -> None:
        """
        Display the first few rows and summary statistics of the data.
        """
        print(Fore.GREEN + "First few rows:")
        print(self.data.head().to_string())
        print("-" * 60)
        print(Fore.GREEN + "Summary statistics:")
        print(self.data.describe().to_string())

    def check_duplicates(self) -> None:
        """
        Check for duplicates based on the provided id column.
        """
        dup_count = self.data[self.id_column].duplicated().sum()
        total_rows = len(self.data)
        print(
            Fore.RED
            + f"""
WARNING! There are {dup_count:,} duplicates based on the provided id.
For context, there are {total_rows:,} rows in this dataframe.
Duplicate percentage: {(dup_count / total_rows) * 100:.2f}% To see the duplicate
values in more detail, please call the see_duplicates method
"""
        )

    def check_data_types(self) -> None:
        """
        Check the data types of each column in the dataframe.
        """
        for col, dtype in self.data.dtypes.items():
            print(f"{col}: {dtype}")

    def check_unique_values(self) -> None:
        """
        Display the number of unique values in each column.
        """
        for col in self.columns:
            unique_count = self.data[col].nunique()
            print(f"{col}: {unique_count:,}")

    def check_value_counts(self, top_n: int = 10) -> None:
        """
        Display the value counts of the top n values in each column.

        Parameters
        ----------
        top_n : int, optional
            Number of top values to display, by default 10.
        """
        for col in self.categorical_columns:
            print(Fore.GREEN + f"\nColumn: {col}")
            value_counts = self.data[col].value_counts().head(top_n)
            for value, count in value_counts.items():
                print(f"{value}: {count:,}")
            if len(self.data[col].unique()) > top_n:
                print("...")
            print("-" * 60)

    def see_duplicates(self) -> None:
        """
        Display the duplicate rows in the dataframe.
        """
        # Count occurrences of each ID
        id_counts = self.data[self.id_column].value_counts()

        # Filter for IDs that appear more than once
        duplicate_counts = id_counts[id_counts > 1]

        if duplicate_counts.empty:
            print("No duplicates found.")
        else:
            print(
                f"Duplicates found. Number of duplicates grouped by {self.id_column}:\n"
            )
            print(duplicate_counts)

    def super_vision(self) -> None:
        """
        Perform a complete analysis, including all checks and prints.
        """
        print(Fore.CYAN + Style.BRIGHT + "=== Data Overview ===")
        print(f"Total rows: {len(self.data):,}")
        print(f"Total columns: {len(self.data.columns):,}")
        print(f"Memory usage: {self.data.memory_usage(deep=True).sum() / 1e6:.2f} MB")
        print("\n" + "=" * 50 + "\n")

        print(Fore.CYAN + Style.BRIGHT + "=== First Glance ===")
        self.generate_first_glance()
        print("\n" + "=" * 50 + "\n")

        print(
            Fore.CYAN
            + Style.BRIGHT
            + f"=== Duplicate Checks Based on {self.id_column} ==="
        )
        self.check_duplicates()
        print("\n" + "=" * 50 + "\n")

        print(Fore.CYAN + Style.BRIGHT + "=== Quality Checks ===")
        self.get_column_statistics()
        print("\n" + "=" * 50 + "\n")

        print(Fore.CYAN + Style.BRIGHT + "=== Value Counts (Top 10) ===")
        self.check_value_counts(top_n=10)

    def get_column_statistics(self) -> None:
        stats: List[List[str]] = []
        max_col_length = max(len(col) for col in self.columns)

        for col in self.columns:
            null_count = self.data[col].isnull().sum()
            dtype = self.data[col].dtype
            unique_count = self.data[col].nunique()
            negative_count: Optional[int] = None

            if col in self.numerical_columns:
                negative_count = (self.data[col] < 0).sum()

            # Format numbers with thousand separators
            null_count_str = f"{null_count:,}".rjust(10)
            unique_count_str = f"{unique_count:,}".rjust(15)

            # Handle numpy.int64 and other numeric types
            if negative_count is not None:
                negative_count_str = f"{negative_count:,}".rjust(15)
            else:
                negative_count_str = "N/A".rjust(15)

            stats.append(
                [
                    col.ljust(max_col_length),
                    null_count_str,
                    str(dtype).ljust(10),
                    unique_count_str,
                    negative_count_str,
                ]
            )

        headers = [
            "Column",
            "Null Count",
            "Data Type",
            "Unique Values",
            "Negative Values",
        ]
        table = tabulate(stats, headers=headers, tablefmt="grid")

        lines = table.split("\n")
        for i, line in enumerate(lines):
            if i <= 2:  # Header lines including the top border
                print(Fore.CYAN + line)
            else:
                cells = line.split("|")
                if len(cells) > 1:
                    null_count_str = cells[2].strip()
                    negative_count_str = cells[5].strip()

                    if null_count_str != "0":
                        cells[2] = (
                            Fore.RED
                            + Style.BRIGHT
                            + null_count_str.center(14)
                            + Style.RESET_ALL
                        )

                    if negative_count_str not in ["0", "N/A"]:
                        cells[5] = (
                            Fore.RED
                            + Style.BRIGHT
                            + negative_count_str.center(14)
                            + Style.RESET_ALL
                        )

                    formatted_line = f"| {cells[1].strip().ljust(max_col_length)} | {cells[2].center(10)} | {cells[3].strip().ljust(10)} | {cells[4].strip().rjust(15)} | {cells[5].strip().rjust(15)} |"
                    print(Fore.WHITE + formatted_line)

        print(Fore.WHITE + lines[-1])  # Bottom border

    def __str__(self) -> str:
        """
        Return a string representation of the FirstGlance object.

        Returns
        -------
        str
            String representation of the FirstGlance object.
        """
        return f"FirstGlance object with shape: {self.data.shape}"
