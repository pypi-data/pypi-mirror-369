"""Tests for CheckingAccountConverter class."""

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from bankinter_converter.checking_account import CheckingAccountConverter


class TestCheckingAccountConverter:
    """Test cases for CheckingAccountConverter class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = CheckingAccountConverter()

        # Create a sample DataFrame for testing
        self.sample_data = pd.DataFrame(
            {
                "A": ["Header1", "Header2", "Header3", "Data1", "Data2", "Data3"],
                "B": ["Col1", "Col2", "Col3", "Value1", "Value2", "Value3"],
                "C": ["Col1", "Col2", "Col3", "Value4", "Value5", "Value6"],
                "D": ["Col1", "Col2", "Col3", "Value7", "Value8", "Value9"],
                "E": ["Col1", "Col2", "Col3", "Value10", "Value11", "Value12"],
                "F": ["Col1", "Col2", "Col3", "Value13", "Value14", "Value15"],
            }
        )

    def test_column_to_index_letters(self):
        """Test conversion of Excel column letters to indices."""
        assert self.converter._column_to_index("A", 10) == 0
        assert self.converter._column_to_index("B", 10) == 1
        assert self.converter._column_to_index("Z", 30) == 25
        assert self.converter._column_to_index("AA", 30) == 26
        assert self.converter._column_to_index("AB", 30) == 27

    def test_column_to_index_numbers(self):
        """Test conversion of numeric column specifications to indices."""
        assert self.converter._column_to_index("1", 10) == 0
        assert self.converter._column_to_index("5", 10) == 4
        assert self.converter._column_to_index("10", 10) == 9

    def test_column_to_index_invalid(self):
        """Test invalid column specifications."""
        with pytest.raises(ValueError, match="Invalid column specification"):
            self.converter._column_to_index("A1", 10)

        with pytest.raises(ValueError, match="Column index 15 out of range"):
            self.converter._column_to_index("15", 10)

    def test_parse_column_range_letters(self):
        """Test parsing of letter-based column ranges."""
        indices = self.converter._parse_column_range("A:E", 10)
        assert indices == [0, 1, 2, 3, 4]

    def test_parse_column_range_numbers(self):
        """Test parsing of number-based column ranges."""
        indices = self.converter._parse_column_range("1:5", 10)
        assert indices == [0, 1, 2, 3, 4]

    def test_parse_column_list(self):
        """Test parsing of comma-separated column lists."""
        indices = self.converter._parse_column_list("A,C,E", 10)
        assert indices == [0, 2, 4]

    def test_parse_column_spec(self):
        """Test parsing of various column specifications."""
        # Range
        assert self.converter._parse_column_spec("A:C", 10) == [0, 1, 2]

        # List
        assert self.converter._parse_column_spec("A,C,E", 10) == [0, 2, 4]

        # Single column
        assert self.converter._parse_column_spec("B", 10) == [1]

    def test_convert_with_excel_file(self):
        """Test convert with actual Excel file."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_xlsx:
            self.sample_data.to_excel(tmp_xlsx.name, index=False, header=False)
            xlsx_path = Path(tmp_xlsx.name)

        try:
            with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp_csv:
                csv_path = Path(tmp_csv.name)

            # Test convert
            self.converter.convert_statement(
                input_file=xlsx_path,
                output_file=csv_path,
                skip_rows=3,
                columns="A:E",
                verbose=False,
            )

            # Read the result and verify
            result_df = pd.read_csv(csv_path, header=None)

            # Should have 3 rows (skipped first 3)
            assert len(result_df) == 3

            # Should have 5 columns (A-E)
            assert len(result_df.columns) == 5

        finally:
            # Clean up
            xlsx_path.unlink(missing_ok=True)
            csv_path.unlink(missing_ok=True)

    def test_convert_with_custom_columns(self):
        """Test convert with custom column selection."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_xlsx:
            self.sample_data.to_excel(tmp_xlsx.name, index=False, header=False)
            xlsx_path = Path(tmp_xlsx.name)

        try:
            with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp_csv:
                csv_path = Path(tmp_csv.name)

            # Test convert with specific columns
            self.converter.convert_statement(
                input_file=xlsx_path,
                output_file=csv_path,
                skip_rows=3,
                columns="A,C,E",
                verbose=False,
            )

            # Read the result and verify
            result_df = pd.read_csv(csv_path, header=None)

            # Should have 3 rows (skipped first 3)
            assert len(result_df) == 3

            # Should have 3 columns (A, C, E)
            assert len(result_df.columns) == 3

        finally:
            # Clean up
            xlsx_path.unlink(missing_ok=True)
            csv_path.unlink(missing_ok=True)
