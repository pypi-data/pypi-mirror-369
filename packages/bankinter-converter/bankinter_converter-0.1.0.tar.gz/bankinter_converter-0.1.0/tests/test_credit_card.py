"""Tests for CreditCardConverter class."""

import tempfile
from pathlib import Path

import pandas as pd

from bankinter_converter.credit_card import CreditCardConverter


class TestCreditCardConverter:
    """Test cases for CreditCardConverter class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = CreditCardConverter()

        # Create sample data for testing credit card statements with Type column
        data_with_type = [
            ["Card Number: 1234 5678 9012 3456", "", "", ""],  # Row 1: Card number
            ["Available Balance: 1,234.56", "", "", ""],  # Row 2: Available balance
            ["Arranged Balance: 2,345.67", "", "", ""],  # Row 3: Arranged balance
            ["", "", "", ""],  # Row 4: Blank space
            ["Date", "Description", "Type", "Amount"],  # Headers (Type in 3rd column)
            ["2024-01-01", "Purchase 1", "Debit", "100.00"],  # Transaction 1
            ["2024-01-02", "Purchase 2", "Credit", "-50.00"],  # Transaction 2
            ["2024-01-03", "Purchase 3", "Debit", "75.50"],  # Transaction 3
            ["Total Debit: 125.50", "", "", ""],  # Total row
            ["", "", "", ""],  # Empty row
            ["Pending Movements:", "", "", ""],  # Pending movements section
            ["2024-01-04", "Pending Purchase", "", "25.00"],  # Pending transaction
        ]
        self.sample_data_with_type = pd.DataFrame(
            data_with_type, columns=["A", "B", "C", "D"]
        )

        # Create sample data without Type column
        data_without_type = [
            ["Card Number: 1234 5678 9012 3456", "", "", ""],  # Row 1: Card number
            ["Available Balance: 1,234.56", "", "", ""],  # Row 2: Available balance
            ["Arranged Balance: 2,345.67", "", "", ""],  # Row 3: Arranged balance
            ["", "", "", ""],  # Row 4: Blank space
            ["Date", "Description", "Amount", ""],  # Headers (Amount in 3rd column)
            ["2024-01-01", "Purchase 1", "100.00", ""],  # Transaction 1
            ["2024-01-02", "Purchase 2", "-50.00", ""],  # Transaction 2
            ["2024-01-03", "Purchase 3", "75.50", ""],  # Transaction 3
            ["Total Debit: 125.50", "", "", ""],  # Total row
            ["", "", "", ""],  # Empty row
            ["Pending Movements:", "", "", ""],  # Pending movements section
            ["2024-01-04", "Pending Purchase", "25.00", ""],  # Pending transaction
        ]
        self.sample_data_without_type = pd.DataFrame(
            data_without_type, columns=["A", "B", "C", "D"]
        )

    def test_convert_credit_card_statement_with_type(self):
        """Test convert of credit card statement with Type column."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_xlsx:
            self.sample_data_with_type.to_excel(
                tmp_xlsx.name, index=False, header=False
            )
            xlsx_path = Path(tmp_xlsx.name)

        try:
            with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp_csv:
                csv_path = Path(tmp_csv.name)

            # Test convert
            self.converter.convert_statement(
                input_file=xlsx_path,
                output_file=csv_path,
                verbose=False,
            )

            # Read the result and verify
            result_df = pd.read_csv(csv_path, header=None)

            # Should have 4 rows (1 header + 3 transaction rows)
            assert len(result_df) == 4

            # Should have 4 columns (Date, Description, Type, Amount)
            assert len(result_df.columns) == 4

            # Verify first row contains headers
            assert result_df.iloc[0, 0] == "Date"
            assert result_df.iloc[0, 1] == "Description"
            assert result_df.iloc[0, 2] == "Type"
            assert result_df.iloc[0, 3] == "Amount"

        finally:
            # Clean up
            xlsx_path.unlink(missing_ok=True)
            csv_path.unlink(missing_ok=True)

    def test_convert_credit_card_statement_without_type(self):
        """Test convert of credit card statement without Type column."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_xlsx:
            self.sample_data_without_type.to_excel(
                tmp_xlsx.name, index=False, header=False
            )
            xlsx_path = Path(tmp_xlsx.name)

        try:
            with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp_csv:
                csv_path = Path(tmp_csv.name)

            # Test convert
            self.converter.convert_statement(
                input_file=xlsx_path,
                output_file=csv_path,
                verbose=False,
            )

            # Read the result and verify
            result_df = pd.read_csv(csv_path, header=None)

            # Should have 4 rows (1 header + 3 transaction rows)
            assert len(result_df) == 4

            # Should have 3 columns (Date, Description, Amount)
            assert len(result_df.columns) == 3

            # Verify first row contains headers
            assert result_df.iloc[0, 0] == "Date"
            assert result_df.iloc[0, 1] == "Description"
            assert result_df.iloc[0, 2] == "Amount"

        finally:
            # Clean up
            xlsx_path.unlink(missing_ok=True)
            csv_path.unlink(missing_ok=True)

    def test_convert_with_verbose_output(self):
        """Test convert with verbose output enabled."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_xlsx:
            self.sample_data_with_type.to_excel(
                tmp_xlsx.name, index=False, header=False
            )
            xlsx_path = Path(tmp_xlsx.name)

        try:
            with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp_csv:
                csv_path = Path(tmp_csv.name)

            # Test convert with verbose output
            self.converter.convert_statement(
                input_file=xlsx_path,
                output_file=csv_path,
                verbose=True,
            )

            # Read the result and verify
            result_df = pd.read_csv(csv_path, header=None)

            # Should have 4 rows (1 header + 3 transaction rows)
            assert len(result_df) == 4

            # Should have 4 columns (Date, Description, Type, Amount)
            assert len(result_df.columns) == 4

            # Verify first row contains headers
            assert result_df.iloc[0, 0] == "Date"
            assert result_df.iloc[0, 1] == "Description"
            assert result_df.iloc[0, 2] == "Type"
            assert result_df.iloc[0, 3] == "Amount"

        finally:
            # Clean up
            xlsx_path.unlink(missing_ok=True)
            csv_path.unlink(missing_ok=True)
