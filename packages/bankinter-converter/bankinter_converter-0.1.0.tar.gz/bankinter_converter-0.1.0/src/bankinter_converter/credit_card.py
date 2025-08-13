"""Bankinter credit card converter implementation."""

from pathlib import Path

import pandas as pd


class CreditCardConverter:
    """Convert Bankinter credit card statements from XLS files to CSV."""

    def convert_statement(
        self,
        input_file: str | Path,
        output_file: str | Path,
        verbose: bool = False,
    ) -> None:
        """
        Convert Bankinter credit card statement from XLS file to CSV.

        Args:
            input_file: Path to input XLS file
            output_file: Path to output CSV file
            verbose: Enable verbose output
        """
        input_path = Path(input_file)
        output_path = Path(output_file)

        if verbose:
            print(f"Reading credit card statement: {input_path}")

        # Read the Excel file
        try:
            df = pd.read_excel(
                input_path,
                sheet_name=0,  # First sheet
                header=None,  # Don't use any row as header
            )
        except Exception as e:
            raise ValueError(f"Failed to read Excel file: {e}")

        if verbose:
            print(f"Original shape: {df.shape}")

        # Process the credit card statement structure
        processed_df = self._process_credit_card_statement(df, verbose)

        if verbose:
            print(f"Processed shape: {processed_df.shape}")

        # Save to CSV
        try:
            processed_df.to_csv(output_path, index=False, header=False)
        except Exception as e:
            raise ValueError(f"Failed to save CSV file: {e}")

        if verbose:
            print("Credit card statement converted successfully")

    def _process_credit_card_statement(
        self, df: pd.DataFrame, verbose: bool = False
    ) -> pd.DataFrame:
        """
        Process Bankinter credit card statement structure.

        Extracts transaction data by:
        1. Finding the header row
        2. Identifying transaction boundaries
        3. Detecting column structure (with/without Type column)
        4. Cleaning and formatting the output
        """
        if verbose:
            print("Processing credit card statement structure...")

        # Find the main transaction section
        transaction_section = self._find_transaction_section(df, verbose)

        if verbose:
            print(f"Transaction section shape: {transaction_section.shape}")

        # Extract headers and transaction data
        headers = transaction_section.iloc[0]
        transaction_data = transaction_section.iloc[1:]

        # Determine column structure based on actual transaction data
        has_type_column = self._has_type_column_in_transactions(
            transaction_data, verbose
        )

        if verbose:
            print(f"Has type column in transactions: {has_type_column}")

        # Filter columns based on structure
        if has_type_column:
            # Columns A-D: Date, Description, Type, Amount
            headers = headers.iloc[:4]
            transaction_data = transaction_data.iloc[:, :4]
            if verbose:
                print("Using columns A-D: Date, Description, Type, Amount")
        else:
            # Columns A-C: Date, Description, Amount
            headers = headers.iloc[:3]
            transaction_data = transaction_data.iloc[:, :3]
            if verbose:
                print("Using columns A-C: Date, Description, Amount")

        # Clean up the data - remove completely empty rows
        transaction_data = transaction_data.dropna(how="all")

        # Combine headers with transaction data
        result_df = pd.concat(
            [headers.to_frame().T, transaction_data], ignore_index=True
        )

        if verbose:
            print(f"Final transaction data shape: {result_df.shape}")
            print("Final transaction data:")
            print(result_df.to_string())

        return result_df

    def _has_type_column_in_transactions(
        self, data: pd.DataFrame, verbose: bool = False
    ) -> bool:
        """
        Check if Column D (index 3) contains meaningful text in transaction rows.

        Returns:
            True if Column D has content (indicating Date, Description, Type, Amount structure)
            False if Column D is empty (indicating Date, Description, Amount structure)
        """
        if data.empty or data.shape[1] < 4:
            return False

        # Check the first few non-empty rows to see if Column D has content
        non_empty_rows = data.dropna(how="all")
        if len(non_empty_rows) == 0:
            return False

        sample_rows = non_empty_rows.head(3)
        for idx, row in sample_rows.iterrows():
            column_d_value = row.iloc[3] if len(row) > 3 else None
            if pd.notna(column_d_value) and str(column_d_value).strip():
                if verbose:
                    print(f"Row {idx} Column D has content: '{column_d_value}'")
                return True

        if verbose:
            print("Column D has content in transactions: False")

        return False

    def _find_transaction_section(
        self, df: pd.DataFrame, verbose: bool = False
    ) -> pd.DataFrame:
        """
        Find the main transaction section by locating the header row and extracting
        all data until totals or pending transactions are encountered.
        """
        # Find the header row
        header_row_idx = self._find_header_row(df, verbose)
        if header_row_idx is None:
            raise ValueError("Could not find header row in credit card statement")

        # Find where transaction data ends (before totals)
        end_row_idx = self._find_transaction_end(df, header_row_idx, verbose)

        # Extract the transaction section
        if end_row_idx is not None:
            transaction_section = df.iloc[header_row_idx:end_row_idx].reset_index(
                drop=True
            )
        else:
            transaction_section = df.iloc[header_row_idx:].reset_index(drop=True)

        if verbose:
            print(f"Transaction section shape: {transaction_section.shape}")

        return transaction_section

    def _find_header_row(self, df: pd.DataFrame, verbose: bool = False) -> int:
        """Find the header row by looking for common header indicators."""
        header_indicators = [
            "date",
            "fecha",
            "description",
            "descripción",
            "concepto",
            "amount",
            "importe",
            "type",
            "tipo",
            "debit",
            "débito",
            "credit",
            "crédito",
            "commerce",
            "movement",
        ]

        for idx, row in df.iterrows():
            if row.isna().all():
                continue

            row_text = " ".join(str(cell).lower() for cell in row if pd.notna(cell))

            if any(indicator in row_text for indicator in header_indicators):
                if verbose:
                    print(f"Found header row at index {idx}: {row_text}")
                return idx

        return None

    def _find_transaction_end(
        self, df: pd.DataFrame, start_idx: int, verbose: bool = False
    ) -> int:
        """Find the end of transaction data by looking for total/pending indicators."""
        end_indicators = [
            "total credit",
            "total debit",
            "total crédito",
            "total débito",
            "pending transactions",
            "transacciones pendientes",
            "movimientos pendientes",
        ]

        for idx, row in df.iloc[start_idx + 1 :].iterrows():
            row_text = " ".join(str(cell).lower() for cell in row if pd.notna(cell))

            if any(indicator in row_text for indicator in end_indicators):
                if verbose:
                    print(f"Found end of transactions at index {idx}: {row_text}")
                return idx

        return None
