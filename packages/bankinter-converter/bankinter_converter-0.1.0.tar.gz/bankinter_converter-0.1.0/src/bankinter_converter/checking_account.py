"""Bankinter checking account converter implementation."""

import re
from pathlib import Path

import pandas as pd


class CheckingAccountConverter:
    """Convert Bankinter checking account statements from XLS files to CSV."""

    def convert_statement(
        self,
        input_file: str | Path,
        output_file: str | Path,
        skip_rows: int = 3,
        columns: str = "A:E",
        sheet: str | int = 0,
        verbose: bool = False,
    ) -> None:
        """
        Convert Bankinter checking account statement from XLS file to CSV.

        Args:
            input_file: Path to input XLS file
            output_file: Path to output CSV file
            skip_rows: Number of rows to skip from beginning
            columns: Column range to include (e.g., "A:E", "A,C,E", "1:5")
            sheet: Sheet name or index to process
            verbose: Enable verbose output
        """
        input_path = Path(input_file)
        output_path = Path(output_file)

        if verbose:
            print(f"Reading file: {input_path}")
            print(f"Sheet: {sheet}")
            print(f"Skipping {skip_rows} rows")
            print(f"Columns: {columns}")

        # Read the Excel file
        try:
            df = pd.read_excel(
                input_path,
                sheet_name=sheet,
                header=None,  # Don't use any row as header
            )
        except Exception as e:
            raise ValueError(f"Failed to read Excel file: {e}")

        if verbose:
            print(f"Original shape: {df.shape}")

        # Skip specified number of rows
        if skip_rows > 0:
            df = df.iloc[skip_rows:]
            if verbose:
                print(f"After skipping {skip_rows} rows: {df.shape}")

        # Filter columns
        column_indices = self._parse_column_spec(columns, df.shape[1])
        df = df.iloc[:, column_indices]

        if verbose:
            print(f"After column filtering: {df.shape}")

        # Save to CSV
        try:
            df.to_csv(output_path, index=False, header=False)
        except Exception as e:
            raise ValueError(f"Failed to save CSV file: {e}")

    def _parse_column_spec(self, columns: str, max_cols: int) -> list[int]:
        """
        Parse column specification and return list of column indices.

        Args:
            columns: Column specification (e.g., "A:E", "A,C,E", "1:5")
            max_cols: Maximum number of columns in the dataframe

        Returns:
            List of column indices to include
        """
        # Remove whitespace and convert to uppercase
        columns = columns.replace(" ", "").upper()

        # Check if it's a range (e.g., "A:E" or "1:5")
        if ":" in columns:
            return self._parse_column_range(columns, max_cols)

        # Check if it's a comma-separated list
        if "," in columns:
            return self._parse_column_list(columns, max_cols)

        # Single column
        return [self._column_to_index(columns, max_cols)]

    def _parse_column_range(self, range_spec: str, max_cols: int) -> list[int]:
        """Parse column range like 'A:E' or '1:5'."""
        start, end = range_spec.split(":")

        # Handle numeric ranges (1:5)
        if start.isdigit() and end.isdigit():
            start_idx = int(start) - 1  # Convert to 0-based
            end_idx = int(end)
            return list(range(start_idx, end_idx))

        # Handle letter ranges (A:E)
        start_idx = self._column_to_index(start, max_cols)
        end_idx = self._column_to_index(end, max_cols) + 1
        return list(range(start_idx, end_idx))

    def _parse_column_list(self, list_spec: str, max_cols: int) -> list[int]:
        """Parse comma-separated column list like 'A,C,E'."""
        columns = list_spec.split(",")
        return [self._column_to_index(col, max_cols) for col in columns]

    def _column_to_index(self, column: str, max_cols: int) -> int:
        """
        Convert Excel column letter to 0-based index.

        Args:
            column: Excel column letter (e.g., 'A', 'B', 'AA') or number
            max_cols: Maximum number of columns for validation

        Returns:
            0-based column index

        Raises:
            ValueError: If column specification is invalid or out of range
        """
        # Handle numeric column specification
        if column.isdigit():
            idx = int(column) - 1  # Convert to 0-based
            if idx < 0 or idx >= max_cols:
                raise ValueError(
                    f"Column index {column} out of range (0-{max_cols - 1})"
                )
            return idx

        # Handle letter column specification
        if not re.match(r"^[A-Z]+$", column):
            raise ValueError(f"Invalid column specification: {column}")

        # Convert Excel column letter to index
        result = 0
        for char in column:
            result = result * 26 + (ord(char) - ord("A") + 1)

        idx = result - 1  # Convert to 0-based

        if idx < 0 or idx >= max_cols:
            raise ValueError(f"Column {column} out of range (max: {max_cols} columns)")

        return idx
